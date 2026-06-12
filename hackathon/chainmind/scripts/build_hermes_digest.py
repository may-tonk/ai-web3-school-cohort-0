"""Build a Hermes digest payload from one or more Hermes alert payload files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from chainmind.alerts import build_digest_payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="build_hermes_digest",
        description="Build a Hermes digest JSON from Hermes token payload files.",
    )
    parser.add_argument(
        "payloads",
        nargs="+",
        type=Path,
        help="Hermes payload JSON files produced by analyze_dune_token.",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path to write the digest JSON payload.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    payloads = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in args.payloads
    ]
    digest = build_digest_payload(payloads)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(digest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
