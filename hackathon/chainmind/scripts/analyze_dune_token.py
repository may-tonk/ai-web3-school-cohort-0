"""Analyze a BNB token by running configured Dune queries."""

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
from chainmind.alerts.channels import build_hermes_payload
from chainmind.alerts.cooldown import (
    apply_cooldown,
    load_cooldown_state,
    save_cooldown_state,
)
from chainmind.orchestration.analyze_dune_token import (
    DuneTokenAnalysisConfig,
    analyze_dune_token,
    build_client_from_env,
    build_gmgn_client_from_env,
    build_honeypot_client_from_env,
    build_intelligence_client_from_env,
    build_market_client_from_env,
    build_rpc_client_from_env,
    build_security_client_from_env,
    load_query_set_from_env,
)
from chainmind.reports import generate_ai_explanation_prompt, generate_token_report


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
        "--report-output",
        type=Path,
        help="Optional path to save a deterministic Markdown analysis report.",
    )
    parser.add_argument(
        "--ai-prompt-output",
        type=Path,
        help="Optional path to save an AI-ready evidence explanation prompt JSON.",
    )
    parser.add_argument(
        "--hermes-output",
        type=Path,
        help="Optional path to save a Hermes-ready alert payload JSON.",
    )
    parser.add_argument(
        "--cooldown-state",
        type=Path,
        help="Optional JSON file used to suppress repeated Hermes alerts.",
    )
    parser.add_argument(
        "--cooldown-write",
        action="store_true",
        help="Persist cooldown state when --cooldown-state is provided.",
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
    if args.cooldown_write and not args.cooldown_state:
        raise SystemExit("--cooldown-write requires --cooldown-state.")

    load_dotenv(PROJECT_ROOT / ".env")

    result = analyze_dune_token(
        token_address=args.token_address,
        client=build_client_from_env(),
        query_ids=load_query_set_from_env(),
        config=DuneTokenAnalysisConfig(
            chain="bnb",
            cache_dir=args.cache_dir,
            refresh_cache=args.refresh_cache,
        ),
        market_client=build_market_client_from_env(),
        security_client=build_security_client_from_env(),
        honeypot_client=build_honeypot_client_from_env(),
        gmgn_client=build_gmgn_client_from_env(),
        intelligence_client=build_intelligence_client_from_env(),
        rpc_client=build_rpc_client_from_env(),
        log=print,
    )

    if args.save_snapshot:
        args.save_snapshot.parent.mkdir(parents=True, exist_ok=True)
        args.save_snapshot.write_text(
            json.dumps(result.snapshot, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    output = result.to_mapping()

    report = None
    if args.report_output or args.ai_prompt_output or args.hermes_output:
        report = generate_token_report(
            snapshot=output["snapshot"],
            analysis=output["analysis"],
        )

    if args.report_output:
        args.report_output.parent.mkdir(parents=True, exist_ok=True)
        args.report_output.write_text(report, encoding="utf-8")

    prompt = None
    if args.ai_prompt_output or args.hermes_output:
        prompt = generate_ai_explanation_prompt(
            snapshot=output["snapshot"],
            analysis=output["analysis"],
            report_markdown=report,
        )

    if args.ai_prompt_output:
        args.ai_prompt_output.parent.mkdir(parents=True, exist_ok=True)
        args.ai_prompt_output.write_text(
            json.dumps(prompt, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if args.hermes_output:
        hermes_payload = build_hermes_payload(
            snapshot=output["snapshot"],
            analysis=output["analysis"],
            report_markdown=report,
            ai_prompt=prompt,
        )
        if args.cooldown_state:
            cooldown_state = load_cooldown_state(args.cooldown_state)
            hermes_payload, cooldown_state = apply_cooldown(
                hermes_payload,
                cooldown_state,
                update_state=args.cooldown_write,
            )
            if args.cooldown_write:
                save_cooldown_state(args.cooldown_state, cooldown_state)

        args.hermes_output.parent.mkdir(parents=True, exist_ok=True)
        args.hermes_output.write_text(
            json.dumps(hermes_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print_human_output(output)
    return 0


def print_human_output(output: dict[str, Any]) -> None:
    snapshot = dict(output["snapshot"])
    analysis = dict(output["analysis"])
    market = dict(snapshot.get("market") or {})
    security = dict(snapshot.get("security") or {})
    contract = dict(snapshot.get("contract") or {})
    holders = dict(snapshot.get("holders") or {})
    gmgn = dict(dict(snapshot.get("intelligence") or {}).get("gmgn") or {})
    nansen = dict(dict(snapshot.get("intelligence") or {}).get("nansen") or {})

    symbol = market.get("base_token_symbol") or analysis.get("symbol") or "UNKNOWN"

    print("")
    print("Summary")
    print(f"Token: {analysis['token_address']} / BNB")
    print(f"Symbol: {symbol}")
    print(f"Grade: {analysis['grade']}")
    print(f"Action: {analysis['action']}")
    print(f"Risk Score: {analysis['risk_score']}")
    print(f"Security Score: {analysis['security_score']}")
    print(f"Entity Cluster Score: {analysis['entity_cluster_score']}")
    print(f"Opportunity Score: {analysis['opportunity_score']}")
    print(f"Copyability Score: {analysis['copyability_score']}")
    print(f"Priority Score: {analysis['priority_score']}")
    print(f"Data Quality: {analysis['data_quality']['level']} ({analysis['data_quality']['confidence']})")

    print("")
    print("Market")
    print(f"Pair: {_value(market.get('pair_address'))}")
    print(f"DEX: {_value(market.get('dex_id'))}")
    print(f"Price USD: {_money(market.get('price_usd'))}")
    print(f"Liquidity USD: {_money(market.get('liquidity_usd'))}")
    print(f"FDV USD: {_money(market.get('fdv_usd'))}")
    print(f"24h Volume USD: {_money(market.get('volume_24h_usd'))}")
    print(f"24h Txns: {_txns(market.get('txns_24h'))}")
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
    print(f"Security Sources: {_sources(security)}")

    print("")
    print("GMGN")
    print(f"Wallet Signal: {_value(gmgn.get('has_wallet_signal'))}")
    print(f"Top Holders: {_integer(gmgn.get('top_holder_count'))}")
    print(f"Top Traders: {_integer(gmgn.get('top_trader_count'))}")
    print(f"Smart Wallets: {_integer(gmgn.get('smart_wallet_count'))}")
    print(f"Snipers: {_integer(gmgn.get('sniper_count'))}")
    print(f"Insiders: {_integer(gmgn.get('insider_count'))}")
    print(f"Bundled Wallets: {_integer(gmgn.get('bundled_wallet_count'))}")

    print("")
    print("Nansen")
    print(f"Smart Money Signal: {_value(nansen.get('has_smart_money_signal'))}")
    print(f"Smart Money Holdings: {_integer(nansen.get('smart_money_holdings_count'))}")
    print(f"TGM Smart Money Holders: {_integer(nansen.get('tgm_smart_money_holder_count'))}")

    api_warnings = list(dict(snapshot.get("data_quality") or {}).get("api_warnings") or [])
    if api_warnings:
        print("")
        print("API Warnings")
        for warning in api_warnings:
            print(f"- {warning}")

    _print_evidence("Risk Evidence", analysis.get("risk_evidence") or [])
    _print_evidence("Security Evidence", analysis.get("security_evidence") or [])
    _print_evidence("Entity Evidence", analysis.get("entity_cluster_evidence") or [])
    _print_evidence("Copyability Evidence", analysis.get("copyability_evidence") or [])
    _print_evidence("Priority Evidence", analysis.get("priority_evidence") or [])


def _print_evidence(title: str, evidence: list[dict[str, Any]]) -> None:
    print("")
    print(title)
    if not evidence:
        print("- None")
        return
    for item in evidence:
        print(
            f"- {item.get('rule_id')}: "
            f"{item.get('metric')}={_value(item.get('value'))} "
            f"(severity={item.get('severity')}, score_delta={item.get('score_delta')})"
        )


def _sources(security: dict[str, Any]) -> str:
    sources = [
        security.get("source"),
        security.get("honeypot_source"),
        security.get("simulation_source"),
        security.get("rpc_source"),
    ]
    unique_sources = []
    for source in sources:
        if source and source not in unique_sources:
            unique_sources.append(str(source))
    return ", ".join(unique_sources) if unique_sources else "N/A"


def _txns(value: Any) -> str:
    if not isinstance(value, dict):
        return "N/A"
    return f"buys={_integer(value.get('buys'))}, sells={_integer(value.get('sells'))}"


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
