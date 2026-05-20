"""CLI for analyzing a token snapshot JSON file."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from chainmind.domain import TokenSnapshot
from chainmind.orchestration import analyze_token


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chainmind-analyze-token",
        description="Analyze a ChainMind token snapshot JSON file.",
    )
    parser.add_argument("snapshot", type=Path, help="Path to a token snapshot JSON file.")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the analysis result as JSON instead of text.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payload = json.loads(args.snapshot.read_text(encoding="utf-8"))
    snapshot = TokenSnapshot.from_mapping(payload)
    result = analyze_token(snapshot)

    if args.json:
        print(json.dumps(result.to_mapping(), ensure_ascii=False, indent=2))
        return 0

    print(f"Token: {result.symbol} / {result.chain.upper()}")
    print(f"Address: {result.token_address}")
    print(f"Grade: {result.grade}")
    print(f"Action: {result.action}")
    print(f"Risk Score: {result.risk_score}")
    print(f"Opportunity Score: {result.opportunity_score}")
    print("")
    print("Reasons:")
    for reason in result.reasons:
        print(f"- {reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
