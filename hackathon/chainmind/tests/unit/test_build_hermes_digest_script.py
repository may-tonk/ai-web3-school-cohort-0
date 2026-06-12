import importlib.util
import json
from pathlib import Path


def _load_script():
    script_path = Path(__file__).resolve().parents[2] / "scripts" / "build_hermes_digest.py"
    spec = importlib.util.spec_from_file_location("build_hermes_digest_script", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_build_hermes_digest_script_writes_digest_payload(tmp_path):
    module = _load_script()
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    output = tmp_path / "digest.json"

    first.write_text(
        json.dumps(
            {
                "should_send": True,
                "delivery_level": "digest",
                "summary": {
                    "token_address": "0xFirst",
                    "symbol": "FIRST",
                    "chain": "bnb",
                    "grade": "B",
                    "action": "watchlist",
                    "headline": "Watchlist candidate.",
                    "priority_score": 70,
                },
            }
        ),
        encoding="utf-8",
    )
    second.write_text(
        json.dumps(
            {
                "should_send": False,
                "delivery_level": "digest",
                "summary": {
                    "token_address": "0xSecond",
                    "symbol": "SECOND",
                    "chain": "bnb",
                    "grade": "B",
                    "action": "watchlist",
                    "headline": "Suppressed candidate.",
                    "priority_score": 99,
                },
            }
        ),
        encoding="utf-8",
    )

    result = module.main([str(first), str(second), "--output", str(output)])

    assert result == 0
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["send_count"] == 1
    assert payload["items"][0]["symbol"] == "FIRST"


def test_build_hermes_digest_script_parser_requires_output():
    module = _load_script()
    args = module.build_parser().parse_args(["first.json", "--output", "digest.json"])

    assert args.payloads == [Path("first.json")]
    assert args.output == Path("digest.json")
