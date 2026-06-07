"""Smoke test configured external APIs without printing secrets."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Callable, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from chainmind.data.env import load_dotenv
from chainmind.data.gmgn_client import GmgnClient
from chainmind.data.http_json import get_json, post_json


DEFAULT_BNB_TOKEN = "0x55d398326f99059ff775485246999027b3197955"
BNB_CHAIN_ID_HEX = "0x38"
TOTAL_SUPPLY_SIGNATURE = "0x18160ddd"


@dataclass(frozen=True)
class SmokeResult:
    service: str
    status: str
    detail: str


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def require_env(name: str) -> str | None:
    value = env(name)
    return value or None


def run_check(service: str, check: Callable[[], SmokeResult]) -> SmokeResult:
    try:
        return check()
    except Exception as exc:  # noqa: BLE001 - smoke tests should continue after failures.
        return SmokeResult(service, "FAIL", _safe_error(exc))


def _safe_error(exc: Exception) -> str:
    text = str(exc)
    if "Free API access is not supported for this chain" in text:
        return "free API access is not supported for this chain"
    if "deprecated V1 endpoint" in text:
        return "deprecated V1 endpoint"
    return "request failed"


def check_dune(timeout_seconds: int) -> SmokeResult:
    api_key = require_env("DUNE_API_KEY")
    query_id = require_env("DUNE_QUERY_TOKEN_TRADING_ACTIVITY")
    if not api_key or not query_id:
        return SmokeResult("Dune", "SKIP", "DUNE_API_KEY or query id is empty")

    payload = get_json(
        f"https://api.dune.com/api/v1/query/{query_id}/results",
        query={"limit": "1"},
        headers={"X-Dune-API-Key": api_key},
        timeout_seconds=timeout_seconds,
    )
    rows = []
    if isinstance(payload, dict):
        result = payload.get("result")
        if isinstance(result, dict) and isinstance(result.get("rows"), list):
            rows = result["rows"]
    return SmokeResult("Dune", "PASS", f"query results reachable; sample_rows={len(rows)}")


def check_dexscreener(token_address: str, timeout_seconds: int) -> SmokeResult:
    base_url = env("DEXSCREENER_BASE_URL", "https://api.dexscreener.com").rstrip("/")
    payload = get_json(
        f"{base_url}/token-pairs/v1/bsc/{token_address}",
        timeout_seconds=timeout_seconds,
    )
    if not isinstance(payload, list):
        return SmokeResult("DexScreener", "FAIL", "token pairs response is not a list")
    return SmokeResult("DexScreener", "PASS", f"token pairs reachable; pairs={len(payload)}")


def check_goplus(token_address: str, timeout_seconds: int) -> SmokeResult:
    base_url = env("GOPLUS_BASE_URL", "https://api.gopluslabs.io").rstrip("/")
    headers = {}
    access_token = require_env("GOPLUS_ACCESS_TOKEN")
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    payload = get_json(
        f"{base_url}/api/v1/token_security/56",
        query={"contract_addresses": token_address},
        headers=headers,
        timeout_seconds=timeout_seconds,
    )
    result = payload.get("result") if isinstance(payload, dict) else None
    token_result = False
    if isinstance(result, dict):
        token_result = token_address.lower() in {key.lower() for key in result}
    return SmokeResult(
        "GoPlus",
        "PASS",
        f"token security reachable; token_result={token_result}",
    )


def check_honeypot(token_address: str, timeout_seconds: int) -> SmokeResult:
    base_url = env("HONEYPOT_BASE_URL", "https://api.honeypot.is").rstrip("/")
    payload = get_json(
        f"{base_url}/v2/IsHoneypot",
        query={"address": token_address, "chainID": "56"},
        timeout_seconds=timeout_seconds,
    )
    if not isinstance(payload, dict):
        return SmokeResult("Honeypot.is", "FAIL", "response is not an object")
    honeypot = payload.get("honeypotResult")
    simulation = payload.get("simulationResult")
    is_honeypot = "unknown"
    buy_tax = "unknown"
    sell_tax = "unknown"
    if isinstance(honeypot, dict):
        is_honeypot = str(honeypot.get("isHoneypot", "unknown"))
    if isinstance(simulation, dict):
        buy_tax = str(simulation.get("buyTax", "unknown"))
        sell_tax = str(simulation.get("sellTax", "unknown"))
    return SmokeResult(
        "Honeypot.is",
        "PASS",
        f"IsHoneypot reachable; isHoneypot={is_honeypot}; buyTax={buy_tax}; sellTax={sell_tax}",
    )


def check_bnb_rpc(token_address: str, timeout_seconds: int) -> SmokeResult:
    rpc_url = require_env("BNB_RPC_URL")
    if not rpc_url:
        return SmokeResult("BNB RPC", "SKIP", "BNB_RPC_URL is empty")

    chain = post_json(
        rpc_url,
        payload={"jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []},
        timeout_seconds=timeout_seconds,
    )
    chain_id = chain.get("result") if isinstance(chain, dict) else None

    supply = post_json(
        rpc_url,
        payload={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "eth_call",
            "params": [
                {"to": token_address, "data": TOTAL_SUPPLY_SIGNATURE},
                "latest",
            ],
        },
        timeout_seconds=timeout_seconds,
    )
    supply_result = supply.get("result") if isinstance(supply, dict) else None
    has_supply = isinstance(supply_result, str) and supply_result != "0x"

    if chain_id != BNB_CHAIN_ID_HEX:
        return SmokeResult(
            "BNB RPC",
            "FAIL",
            f"eth_chainId={chain_id}; expected={BNB_CHAIN_ID_HEX}",
        )
    if not has_supply:
        return SmokeResult("BNB RPC", "FAIL", "eth_call totalSupply returned empty result")
    return SmokeResult("BNB RPC", "PASS", "eth_chainId=0x38; totalSupply readable")


def check_etherscan(timeout_seconds: int) -> SmokeResult:
    api_key = require_env("ETHERSCAN_API_KEY")
    if not api_key:
        return SmokeResult("Etherscan V2", "SKIP", "ETHERSCAN_API_KEY is empty")

    base_url = env("ETHERSCAN_BASE_URL", "https://api.etherscan.io/v2/api").rstrip("/")
    chain_id = env("ETHERSCAN_CHAIN_ID", "56")
    payload = get_json(
        base_url,
        query={
            "chainid": chain_id,
            "module": "account",
            "action": "balance",
            "address": DEFAULT_BNB_TOKEN,
            "tag": "latest",
            "apikey": api_key,
        },
        timeout_seconds=timeout_seconds,
    )
    if not isinstance(payload, dict):
        return SmokeResult("Etherscan V2", "FAIL", "response is not an object")
    if payload.get("status") == "1":
        return SmokeResult("Etherscan V2", "PASS", "BNB chain V2 request accepted")

    result = str(payload.get("result") or payload.get("message") or "request not accepted")
    if "Free API access is not supported for this chain" in result:
        return SmokeResult(
            "Etherscan V2",
            "WARN",
            "configured, but free API access is not supported for BNB Chain",
        )
    return SmokeResult("Etherscan V2", "FAIL", f"API returned: {result[:120]}")


def check_nansen(timeout_seconds: int) -> SmokeResult:
    api_key = require_env("NANSEN_API_KEY")
    if not api_key:
        return SmokeResult("Nansen", "SKIP", "NANSEN_API_KEY is empty")

    base_url = env("NANSEN_BASE_URL", "https://api.nansen.ai/api/v1").rstrip("/")
    chain = env("NANSEN_CHAIN", "bnb")
    payload = post_json(
        f"{base_url}/smart-money/holdings",
        payload={"chains": [chain], "pagination": {"page": 1, "per_page": 1}},
        headers={"apikey": api_key},
        timeout_seconds=timeout_seconds,
    )
    rows = 0
    if isinstance(payload, dict) and isinstance(payload.get("data"), list):
        rows = len(payload["data"])
    return SmokeResult("Nansen", "PASS", f"smart-money holdings reachable; rows={rows}")


def check_gmgn(timeout_seconds: int) -> SmokeResult:
    client = GmgnClient.from_env()
    if client is None:
        return SmokeResult("GMGN", "SKIP", "GMGN_API_KEY is empty")
    client = GmgnClient(replace(client.config, timeout_seconds=timeout_seconds))
    payload = client.get_trending_tokens(limit=3)
    rows = _count_nested_rows(payload)
    return SmokeResult("GMGN", "PASS", f"query-only trending reachable; rows={rows}")


def run_smoke_tests(token_address: str, timeout_seconds: int) -> list[SmokeResult]:
    checks: list[tuple[str, Callable[[], SmokeResult]]] = [
        ("Dune", lambda: check_dune(timeout_seconds)),
        ("DexScreener", lambda: check_dexscreener(token_address, timeout_seconds)),
        ("GoPlus", lambda: check_goplus(token_address, timeout_seconds)),
        ("Honeypot.is", lambda: check_honeypot(token_address, timeout_seconds)),
        ("BNB RPC", lambda: check_bnb_rpc(token_address, timeout_seconds)),
        ("Etherscan V2", lambda: check_etherscan(timeout_seconds)),
        ("Nansen", lambda: check_nansen(timeout_seconds)),
        ("GMGN", lambda: check_gmgn(timeout_seconds)),
    ]
    return [run_check(service, check) for service, check in checks]


def print_table(results: Sequence[SmokeResult]) -> None:
    service_width = max(len("Service"), *(len(item.service) for item in results))
    status_width = max(len("Status"), *(len(item.status) for item in results))
    print(f"{'Service':<{service_width}}  {'Status':<{status_width}}  Detail")
    print(f"{'-' * service_width}  {'-' * status_width}  {'-' * 60}")
    for item in results:
        print(f"{item.service:<{service_width}}  {item.status:<{status_width}}  {item.detail}")


def _count_nested_rows(value: Any) -> int:
    if isinstance(value, list):
        return len(value)
    if not isinstance(value, dict):
        return 0
    for key in ("data", "result", "tokens", "rank", "items", "rows"):
        rows = _count_nested_rows(value.get(key))
        if rows:
            return rows
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="smoke_test_apis",
        description="Smoke test configured ChainMind external APIs without printing secrets.",
    )
    parser.add_argument(
        "--token-address",
        default=DEFAULT_BNB_TOKEN,
        help="BNB token contract used for API probes. Defaults to BSC USDT.",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=45,
        help="Per-request timeout in seconds.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_dotenv(PROJECT_ROOT / ".env")

    results = run_smoke_tests(
        token_address=args.token_address,
        timeout_seconds=args.timeout,
    )
    if args.json:
        print(json.dumps([asdict(item) for item in results], ensure_ascii=False, indent=2))
    else:
        print_table(results)

    return 1 if any(item.status == "FAIL" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
