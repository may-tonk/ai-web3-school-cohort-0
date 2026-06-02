"""Quick-screen a BNB token without waiting for Dune."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from chainmind.data.env import load_dotenv
from chainmind.orchestration.quick_screen_token import quick_screen_token_from_env


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="quick_screen_token",
        description="Run a low-latency BNB token screen without Dune.",
    )
    parser.add_argument("token_address", help="BNB token contract address.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_dotenv(PROJECT_ROOT / ".env")

    result = quick_screen_token_from_env(args.token_address)
    output = result.to_mapping()

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print_human_output(output)
    return 0


def print_human_output(output: dict[str, Any]) -> None:
    snapshot = dict(output.get("snapshot") or {})
    market = dict(snapshot.get("market") or {})
    security = dict(snapshot.get("security") or {})
    contract = dict(snapshot.get("contract") or {})
    holders = dict(snapshot.get("holders") or {})
    data_quality = dict(snapshot.get("data_quality") or {})

    print(f"Token: {output['token_address']} / BNB")
    print(f"Decision: {output['decision']}")

    print("")
    print("Market")
    print(f"Symbol: {_value(market.get('base_token_symbol'))}")
    print(f"Liquidity USD: {_money(market.get('liquidity_usd'))}")
    print(f"24h Volume USD: {_money(market.get('volume_24h_usd'))}")
    print(f"24h Price Change: {_percent(market.get('price_change_24h_pct'), already_percent=True)}")

    print("")
    print("Security")
    print(f"Honeypot: {_value(security.get('is_honeypot'))}")
    print(f"Buy Tax: {_percent(security.get('buy_tax'))}")
    print(f"Sell Tax: {_percent(security.get('sell_tax'))}")
    print(f"Cannot Sell All: {_value(security.get('cannot_sell_all'))}")
    print(f"Owner Renounced: {_value(contract.get('owner_renounced'))}")
    print(f"Mintable: {_value(contract.get('is_mintable'))}")
    print(f"Hidden Owner: {_value(contract.get('hidden_owner'))}")
    print(f"Holder Count: {_integer(holders.get('holder_count'))}")

    print("")
    print("Reasons")
    for reason in output.get("reasons") or []:
        print(f"- {reason}")

    api_warnings = data_quality.get("api_warnings") or []
    if api_warnings:
        print("")
        print("API Warnings")
        for warning in api_warnings:
            print(f"- {warning}")


def _money(value: Any) -> str:
    number = _float(value)
    if number is None:
        return "N/A"
    return f"{number:,.6f}" if abs(number) < 1 else f"{number:,.2f}"


def _percent(value: Any, *, already_percent: bool = False) -> str:
    number = _float(value)
    if number is None:
        return "N/A"
    if not already_percent:
        number *= 100
    return f"{number:.2f}%"


def _integer(value: Any) -> str:
    number = _float(value)
    if number is None:
        return "N/A"
    return f"{int(number):,}"


def _float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _value(value: Any) -> str:
    if value is None or value == "":
        return "N/A"
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
