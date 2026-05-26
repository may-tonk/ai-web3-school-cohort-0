"""Analyze a BNB token by running configured Dune queries."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from chainmind.data.dune_client import DuneClient, DuneConfig
from chainmind.data.dune_mappers import build_snapshot_from_dune_results
from chainmind.data.env import load_dotenv
from chainmind.domain import TokenSnapshot
from chainmind.orchestration import analyze_token


QUERY_ENV_KEYS = {
    "trading_activity": "DUNE_QUERY_TOKEN_TRADING_ACTIVITY",
    "five_minute_flow": "DUNE_QUERY_FIVE_MINUTE_FLOW",
    "early_buyers": "DUNE_QUERY_EARLY_BUYERS",
    "early_buyer_funding": "DUNE_QUERY_EARLY_BUYER_FUNDING",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="analyze_dune_token",
        description="Run Dune queries for a BNB meme token and analyze it.",
    )
    parser.add_argument("token_address", help="BNB token contract address.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument(
        "--save-snapshot",
        type=Path,
        help="Optional path to save the generated TokenSnapshot JSON.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=PROJECT_ROOT / "experiments" / "week2-token-risk-score" / "dune-query-cache",
        help="Directory for per-query Dune result cache.",
    )
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Ignore cached Dune rows and fetch every query again.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_dotenv(PROJECT_ROOT / ".env")

    client = _build_client()
    query_ids = _load_query_ids()

    trading_rows = _load_or_run_query(
        client,
        query_ids["trading_activity"],
        args.token_address,
        "trading_activity",
        args.cache_dir,
        args.refresh_cache,
    )
    flow_rows = _load_or_run_query(
        client,
        query_ids["five_minute_flow"],
        args.token_address,
        "five_minute_flow",
        args.cache_dir,
        args.refresh_cache,
    )
    early_buyer_rows = _load_or_run_query(
        client,
        query_ids["early_buyers"],
        args.token_address,
        "early_buyers",
        args.cache_dir,
        args.refresh_cache,
    )
    funding_rows = _load_or_run_query(
        client,
        query_ids["early_buyer_funding"],
        args.token_address,
        "early_buyer_funding",
        args.cache_dir,
        args.refresh_cache,
    )

    snapshot_payload = build_snapshot_from_dune_results(
        token_address=args.token_address,
        chain="bnb",
        trading_activity_rows=trading_rows,
        flow_5m_rows=flow_rows,
        early_buyer_rows=early_buyer_rows,
        funding_rows=funding_rows,
    )

    if args.save_snapshot:
        args.save_snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.save_snapshot.write_text(
            json.dumps(snapshot_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    result = analyze_token(TokenSnapshot.from_mapping(snapshot_payload))
    output = {
        "snapshot": snapshot_payload,
        "analysis": result.to_mapping(),
    }

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        analysis = result.to_mapping()
        print(f"Token: {analysis['token_address']} / BNB")
        print(f"Grade: {analysis['grade']}")
        print(f"Action: {analysis['action']}")
        print(f"Risk Score: {analysis['risk_score']}")
        print(f"Data Quality: {analysis['data_quality']['level']}")
        print("Risk Evidence:")
        for item in analysis["risk_evidence"]:
            print(f"- {item['rule_id']}: {item['metric']}={item['value']}")
    return 0


def _build_client() -> DuneClient:
    api_key = os.environ.get("DUNE_API_KEY")
    if not api_key:
        raise RuntimeError("DUNE_API_KEY is not set.")
    return DuneClient(DuneConfig(api_key=api_key))


def _load_query_ids() -> dict[str, str]:
    query_ids = {}
    missing = []
    for name, env_key in QUERY_ENV_KEYS.items():
        value = os.environ.get(env_key)
        if not value:
            missing.append(env_key)
        else:
            query_ids[name] = value
    if missing:
        raise RuntimeError(f"Missing Dune query id environment variables: {missing}")
    return query_ids


def _load_or_run_query(
    client: DuneClient,
    query_id: str,
    token_address: str,
    query_name: str,
    cache_dir: Path,
    refresh_cache: bool,
) -> list[dict[str, object]]:
    cache_path = _cache_path(cache_dir, token_address, query_name)
    execution_path = _execution_path(cache_dir, token_address, query_name)
    if cache_path.exists() and not refresh_cache:
        payload = json.loads(cache_path.read_text(encoding="utf-8"))
        rows = payload.get("rows", [])
        if not isinstance(rows, list):
            raise RuntimeError(f"Invalid Dune cache rows: {cache_path}")
        print(f"Using cached Dune rows: {query_name} ({len(rows)} rows)")
        return [dict(row) for row in rows]

    if execution_path.exists() and not refresh_cache:
        execution_payload = json.loads(execution_path.read_text(encoding="utf-8"))
        execution_id = str(execution_payload["execution_id"])
        print(f"Resuming Dune execution: {query_name} ({execution_id})")
    else:
        print(f"Running Dune query: {query_name}")
        execution_id = client.execute_query(query_id, token_address)
        execution_path.parent.mkdir(parents=True, exist_ok=True)
        execution_path.write_text(
            json.dumps(
                {
                    "token_address": token_address,
                    "query_name": query_name,
                    "query_id": query_id,
                    "execution_id": execution_id,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    client.wait_for_execution(execution_id)
    rows = client.get_execution_results(execution_id)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_payload = {
        "token_address": token_address,
        "query_name": query_name,
        "query_id": query_id,
        "execution_id": execution_id,
        "rows": rows,
    }
    cache_path.write_text(
        json.dumps(cache_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Cached Dune rows: {query_name} ({len(rows)} rows)")
    return rows


def _cache_path(cache_dir: Path, token_address: str, query_name: str) -> Path:
    token = token_address.lower().replace("0x", "")
    return cache_dir / token / f"{query_name}.json"


def _execution_path(cache_dir: Path, token_address: str, query_name: str) -> Path:
    token = token_address.lower().replace("0x", "")
    return cache_dir / token / f"{query_name}.execution.json"


if __name__ == "__main__":
    raise SystemExit(main())
