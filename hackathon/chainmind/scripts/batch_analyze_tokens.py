"""Batch analyze BNB tokens with the ChainMind Dune-backed workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable, Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from chainmind.data.env import load_dotenv
from chainmind.orchestration.analyze_dune_token import (
    DuneTokenAnalysisConfig,
    analyze_dune_token,
    build_client_from_env,
    build_honeypot_client_from_env,
    build_intelligence_client_from_env,
    build_market_client_from_env,
    build_rpc_client_from_env,
    build_security_client_from_env,
    load_query_set_from_env,
)


DEFAULT_CACHE_DIR = PROJECT_ROOT / "experiments" / "week2-token-risk-score" / "dune-query-cache"

TABLE_COLUMNS = [
    "token",
    "status",
    "symbol",
    "grade",
    "action",
    "risk",
    "security",
    "entity",
    "data_quality",
    "liquidity_usd",
    "volume_24h_usd",
    "price_change_24h_pct",
    "honeypot",
    "buy_tax",
    "sell_tax",
    "owner_renounced",
    "holder_count",
    "nansen_signal",
    "risk_rules",
    "security_rules",
    "entity_rules",
    "error",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="batch_analyze_tokens",
        description="Batch analyze BNB tokens and print a compact comparison table.",
    )
    parser.add_argument("token_addresses", nargs="*", help="BNB token contract addresses.")
    parser.add_argument(
        "--file",
        type=Path,
        help="Optional text file with one token address per line. Blank lines and # comments are ignored.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=DEFAULT_CACHE_DIR,
        help="Directory for per-query Dune result cache.",
    )
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Ignore cached Dune rows and fetch every query again.",
    )
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to save the table or JSON output.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print per-token enrichment logs while analyzing.",
    )
    return parser


def read_token_file(path: Path) -> list[str]:
    tokens: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if line:
            tokens.append(line)
    return tokens


def collect_tokens(positional_tokens: Sequence[str], file_path: Path | None) -> list[str]:
    tokens = list(positional_tokens)
    if file_path is not None:
        tokens.extend(read_token_file(file_path))

    unique_tokens: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        normalized = token.strip()
        key = normalized.lower()
        if normalized and key not in seen:
            unique_tokens.append(normalized)
            seen.add(key)
    return unique_tokens


def analyze_batch(
    tokens: Sequence[str],
    *,
    cache_dir: Path,
    refresh_cache: bool = False,
    log: Callable[[str], None] | None = None,
) -> list[dict[str, Any]]:
    client = build_client_from_env()
    query_set = load_query_set_from_env()
    market_client = build_market_client_from_env()
    security_client = build_security_client_from_env()
    honeypot_client = build_honeypot_client_from_env()
    intelligence_client = build_intelligence_client_from_env()
    rpc_client = build_rpc_client_from_env()

    rows: list[dict[str, Any]] = []
    for token in tokens:
        try:
            result = analyze_dune_token(
                token_address=token,
                client=client,
                query_ids=query_set,
                config=DuneTokenAnalysisConfig(
                    chain="bnb",
                    cache_dir=cache_dir,
                    refresh_cache=refresh_cache,
                ),
                market_client=market_client,
                security_client=security_client,
                honeypot_client=honeypot_client,
                intelligence_client=intelligence_client,
                rpc_client=rpc_client,
                log=log,
            )
            rows.append(summarize_analysis(result.to_mapping()))
        except Exception as exc:  # noqa: BLE001 - one failed token should not stop the batch.
            rows.append(error_row(token, exc))
    return rows


def summarize_analysis(output: dict[str, Any]) -> dict[str, Any]:
    snapshot = dict(output.get("snapshot") or {})
    analysis = dict(output.get("analysis") or {})
    market = dict(snapshot.get("market") or {})
    security = dict(snapshot.get("security") or {})
    contract = dict(snapshot.get("contract") or {})
    holders = dict(snapshot.get("holders") or {})
    nansen = dict(dict(snapshot.get("intelligence") or {}).get("nansen") or {})

    return {
        "token": analysis.get("token_address") or dict(snapshot.get("token") or {}).get("address"),
        "status": "OK",
        "symbol": market.get("base_token_symbol") or analysis.get("symbol"),
        "grade": analysis.get("grade"),
        "action": analysis.get("action"),
        "risk": analysis.get("risk_score"),
        "security": analysis.get("security_score"),
        "entity": analysis.get("entity_cluster_score"),
        "data_quality": _data_quality_label(analysis.get("data_quality")),
        "liquidity_usd": _round(market.get("liquidity_usd"), 2),
        "volume_24h_usd": _round(market.get("volume_24h_usd"), 2),
        "price_change_24h_pct": _round(market.get("price_change_24h_pct"), 2),
        "honeypot": security.get("is_honeypot"),
        "buy_tax": _round_percent(security.get("buy_tax")),
        "sell_tax": _round_percent(security.get("sell_tax")),
        "owner_renounced": contract.get("owner_renounced"),
        "holder_count": holders.get("holder_count"),
        "nansen_signal": nansen.get("has_smart_money_signal"),
        "risk_rules": _rule_ids(analysis.get("risk_evidence")),
        "security_rules": _rule_ids(analysis.get("security_evidence")),
        "entity_rules": _rule_ids(analysis.get("entity_cluster_evidence")),
        "error": "",
    }


def error_row(token: str, exc: Exception) -> dict[str, Any]:
    return {
        "token": token,
        "status": "ERROR",
        "symbol": "",
        "grade": "",
        "action": "",
        "risk": "",
        "security": "",
        "entity": "",
        "data_quality": "",
        "liquidity_usd": "",
        "volume_24h_usd": "",
        "price_change_24h_pct": "",
        "honeypot": "",
        "buy_tax": "",
        "sell_tax": "",
        "owner_renounced": "",
        "holder_count": "",
        "nansen_signal": "",
        "risk_rules": "",
        "security_rules": "",
        "entity_rules": "",
        "error": _safe_error(exc),
    }


def format_table(rows: Sequence[dict[str, Any]]) -> str:
    table_rows = [TABLE_COLUMNS]
    table_rows.extend([[format_cell(row.get(column)) for column in TABLE_COLUMNS] for row in rows])
    widths = [
        max(len(str(row[index])) for row in table_rows)
        for index in range(len(TABLE_COLUMNS))
    ]
    lines = [
        " | ".join(str(cell).ljust(widths[index]) for index, cell in enumerate(table_rows[0])),
        "-+-".join("-" * width for width in widths),
    ]
    for row in table_rows[1:]:
        lines.append(" | ".join(str(cell).ljust(widths[index]) for index, cell in enumerate(row)))
    return "\n".join(lines)


def format_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def write_output(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _data_quality_label(value: Any) -> str:
    if not isinstance(value, dict):
        return ""
    level = value.get("level") or ""
    confidence = value.get("confidence") or ""
    if level and confidence:
        return f"{level}/{confidence}"
    return str(level or confidence)


def _rule_ids(evidence: Any) -> str:
    if not isinstance(evidence, list):
        return ""
    return ",".join(
        str(item.get("rule_id"))
        for item in evidence
        if isinstance(item, dict) and item.get("rule_id")
    )


def _round(value: Any, digits: int) -> float | str:
    number = _float(value)
    if number is None:
        return ""
    return round(number, digits)


def _round_percent(value: Any) -> float | str:
    number = _float(value)
    if number is None:
        return ""
    return round(number * 100, 2)


def _float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_error(exc: Exception) -> str:
    message = str(exc)
    if "DUNE_API_KEY" in message:
        return message
    if "Missing Dune query" in message:
        return message
    if "Free API access is not supported for this chain" in message:
        return "Etherscan free API access is not supported for BNB Chain."
    return message[:240]


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_dotenv(PROJECT_ROOT / ".env")

    tokens = collect_tokens(args.token_addresses, args.file)
    if not tokens:
        raise SystemExit("No token addresses provided.")

    rows = analyze_batch(
        tokens,
        cache_dir=args.cache_dir,
        refresh_cache=args.refresh_cache,
        log=print if args.verbose else None,
    )

    if args.json:
        content = json.dumps(rows, ensure_ascii=False, indent=2)
    else:
        content = format_table(rows)

    print(content)
    if args.output:
        write_output(args.output, content)

    return 1 if any(row.get("status") == "ERROR" for row in rows) else 0


if __name__ == "__main__":
    raise SystemExit(main())
