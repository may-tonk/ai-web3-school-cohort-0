"""Inspect one wallet's token transfers against a PancakeSwap pair."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from chainmind.data.env import load_dotenv


TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
BALANCE_OF = "0x70a08231"
DECIMALS = "0x313ce567"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inspect_token_wallet",
        description="Inspect token transfers for one wallet and classify pair buys/sells.",
    )
    parser.add_argument("token_address")
    parser.add_argument("wallet_address")
    parser.add_argument("--pair", default="", help="Optional DEX pair address.")
    parser.add_argument(
        "--rpc-url",
        default="",
        help="Optional RPC URL override. Useful when the configured RPC limits eth_getLogs ranges.",
    )
    parser.add_argument("--blocks", type=int, default=180_000, help="Lookback blocks.")
    parser.add_argument("--chunk-size", type=int, default=10_000, help="eth_getLogs chunk size.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_dotenv(PROJECT_ROOT / ".env")
    if args.rpc_url:
        os.environ["BNB_RPC_URL"] = args.rpc_url

    token = normalize(args.token_address)
    wallet = normalize(args.wallet_address)
    pair = normalize(args.pair) if args.pair else discover_pair(token)

    latest = int(rpc("eth_blockNumber", []), 16)
    from_block = max(0, latest - args.blocks)
    decimals = get_decimals(token)
    price_usd, symbol, pair_url = get_market(token)

    logs = collect_transfer_logs(
        token=token,
        wallet=wallet,
        from_block=from_block,
        to_block=latest,
        chunk_size=args.chunk_size,
    )
    events = classify_events(logs, wallet=wallet, pair=pair, decimals=decimals)
    balance = token_balance(token, wallet, decimals)

    summary = summarize(
        token=token,
        wallet=wallet,
        pair=pair,
        latest_block=latest,
        from_block=from_block,
        decimals=decimals,
        balance=balance,
        price_usd=price_usd,
        symbol=symbol,
        pair_url=pair_url,
        events=events,
    )

    print(json.dumps({"summary": summary, "events": events}, ensure_ascii=False, indent=2))
    return 0


def collect_transfer_logs(
    *,
    token: str,
    wallet: str,
    from_block: int,
    to_block: int,
    chunk_size: int,
) -> list[dict[str, Any]]:
    logs: list[dict[str, Any]] = []
    for from_topic, to_topic in [
        (address_topic(wallet), None),
        (None, address_topic(wallet)),
    ]:
        block = from_block
        while block <= to_block:
            end = min(block + chunk_size - 1, to_block)
            request = {
                "address": token,
                "fromBlock": hex(block),
                "toBlock": hex(end),
                "topics": [TRANSFER_TOPIC, from_topic, to_topic],
            }
            for item in rpc("eth_getLogs", [request]) or []:
                logs.append(dict(item))
            block = end + 1
            time.sleep(0.02)

    seen = set()
    unique: list[dict[str, Any]] = []
    for log in logs:
        key = (log.get("transactionHash"), log.get("logIndex"))
        if key not in seen:
            seen.add(key)
            unique.append(log)
    return sorted(
        unique,
        key=lambda log: (int(log["blockNumber"], 16), int(log["logIndex"], 16)),
    )


def classify_events(
    logs: list[dict[str, Any]],
    *,
    wallet: str,
    pair: str,
    decimals: int,
) -> list[dict[str, Any]]:
    events = []
    for log in logs:
        from_address = address_from_topic(log["topics"][1])
        to_address = address_from_topic(log["topics"][2])
        amount = int(log["data"], 16) / (10**decimals)
        if from_address == pair and to_address == wallet:
            label = "BUY_OR_PAIR_OUT"
        elif from_address == wallet and to_address == pair:
            label = "SELL_TO_PAIR"
        elif to_address == wallet:
            label = "TRANSFER_IN"
        elif from_address == wallet:
            label = "TRANSFER_OUT"
        else:
            label = "OTHER"
        events.append(
            {
                "block": int(log["blockNumber"], 16),
                "tx": log["transactionHash"],
                "from": from_address,
                "to": to_address,
                "amount": amount,
                "label": label,
            }
        )
    return events


def summarize(
    *,
    token: str,
    wallet: str,
    pair: str,
    latest_block: int,
    from_block: int,
    decimals: int,
    balance: float,
    price_usd: float | None,
    symbol: str | None,
    pair_url: str | None,
    events: list[dict[str, Any]],
) -> dict[str, Any]:
    bought = sum(event["amount"] for event in events if event["label"] == "BUY_OR_PAIR_OUT")
    sold = sum(event["amount"] for event in events if event["label"] == "SELL_TO_PAIR")
    transfer_in = sum(event["amount"] for event in events if event["label"] == "TRANSFER_IN")
    transfer_out = sum(event["amount"] for event in events if event["label"] == "TRANSFER_OUT")
    sell_events = [event for event in events if event["label"] == "SELL_TO_PAIR"]
    buy_events = [event for event in events if event["label"] == "BUY_OR_PAIR_OUT"]
    return {
        "token": token,
        "wallet": wallet,
        "pair": pair,
        "symbol": symbol,
        "pair_url": pair_url,
        "latest_block": latest_block,
        "from_block": from_block,
        "decimals": decimals,
        "events_found": len(events),
        "buy_events": len(buy_events),
        "sell_events": len(sell_events),
        "current_balance_token": balance,
        "current_balance_usd_est": None if price_usd is None else balance * price_usd,
        "total_bought_from_pair_token": bought,
        "total_sold_to_pair_token": sold,
        "total_transfer_in_token": transfer_in,
        "total_transfer_out_token": transfer_out,
        "sold_ratio_vs_pair_buys": None if bought <= 0 else sold / bought,
        "current_price_usd": price_usd,
    }


def discover_pair(token: str) -> str:
    payload = get_json(f"https://api.dexscreener.com/token-pairs/v1/bsc/{token}")
    if not isinstance(payload, list) or not payload:
        raise RuntimeError("DexScreener returned no pairs; pass --pair manually.")
    pair = max(payload, key=lambda item: float((item.get("liquidity") or {}).get("usd") or 0))
    return normalize(pair["pairAddress"])


def get_market(token: str) -> tuple[float | None, str | None, str | None]:
    try:
        payload = get_json(f"https://api.dexscreener.com/token-pairs/v1/bsc/{token}")
        if not isinstance(payload, list) or not payload:
            return None, None, None
        pair = max(payload, key=lambda item: float((item.get("liquidity") or {}).get("usd") or 0))
        price = float(pair.get("priceUsd") or 0)
        symbol = (pair.get("baseToken") or {}).get("symbol")
        return price, symbol, pair.get("url")
    except Exception:
        return None, None, None


def get_json(url: str) -> Any:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "ChainMind/0.1"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def get_decimals(token: str) -> int:
    try:
        return int(eth_call(token, DECIMALS), 16)
    except Exception:
        return 18


def token_balance(token: str, wallet: str, decimals: int) -> float:
    data = BALANCE_OF + wallet.removeprefix("0x").rjust(64, "0")
    return int(eth_call(token, data), 16) / (10**decimals)


def eth_call(to: str, data: str) -> str:
    return rpc("eth_call", [{"to": to, "data": data}, "latest"])


def rpc(method: str, params: list[Any]) -> Any:
    rpc_url = os.environ.get("BNB_RPC_URL")
    if not rpc_url:
        raise RuntimeError("BNB_RPC_URL is not set.")
    payload = None
    last_error: Exception | None = None
    for attempt in range(4):
        request = urllib.request.Request(
            rpc_url,
            data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(
                "utf-8"
            ),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "ChainMind/0.1",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                payload = json.loads(response.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {exc.code} from RPC for {method}: {body}") from exc
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt == 3:
                raise RuntimeError(f"RPC network error for {method}: {exc}") from exc
            time.sleep(0.5 * (attempt + 1))
    if payload is None:
        raise RuntimeError(f"RPC request failed for {method}: {last_error}")
    if payload.get("error"):
        raise RuntimeError(f"RPC error: {payload['error']}")
    return payload.get("result")


def normalize(value: str) -> str:
    if not value:
        return ""
    value = value.strip().lower()
    if not value.startswith("0x"):
        value = f"0x{value}"
    return value


def address_topic(address: str) -> str:
    return "0x" + "0" * 24 + address.removeprefix("0x").lower()


def address_from_topic(topic: str) -> str:
    return "0x" + topic[-40:].lower()


if __name__ == "__main__":
    raise SystemExit(main())
