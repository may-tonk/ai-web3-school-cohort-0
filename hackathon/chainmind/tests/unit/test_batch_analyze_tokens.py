import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[2] / "scripts" / "batch_analyze_tokens.py"
SPEC = importlib.util.spec_from_file_location("batch_analyze_tokens", SCRIPT_PATH)
batch = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(batch)


def test_collect_tokens_merges_file_and_deduplicates_case_insensitively(tmp_path):
    token_file = tmp_path / "tokens.txt"
    token_file.write_text(
        "\n".join(
            [
                "# comment",
                "0xBBB",
                "0xaaa # duplicate with different case",
                "",
            ]
        ),
        encoding="utf-8",
    )

    tokens = batch.collect_tokens(["0xAAA"], token_file)

    assert tokens == ["0xAAA", "0xBBB"]


def test_summarize_analysis_extracts_batch_columns():
    row = batch.summarize_analysis(
        {
            "snapshot": {
                "market": {
                    "base_token_symbol": "MEME",
                    "liquidity_usd": 1234.567,
                    "volume_24h_usd": 999.9,
                    "price_change_24h_pct": -4.321,
                },
                "security": {
                    "is_honeypot": False,
                    "buy_tax": 0.04,
                    "sell_tax": 0.0398,
                },
                "contract": {"owner_renounced": True},
                "holders": {"holder_count": 100},
                "intelligence": {
                    "nansen": {"has_smart_money_signal": False},
                },
            },
            "analysis": {
                "token_address": "0xToken",
                "symbol": "UNKNOWN",
                "grade": "D",
                "action": "filter",
                "risk_score": 100,
                "security_score": 0,
                "entity_cluster_score": 50,
                "data_quality": {"level": "good", "confidence": "high"},
                "risk_evidence": [{"rule_id": "risk_a"}, {"rule_id": "risk_b"}],
                "security_evidence": [],
                "entity_cluster_evidence": [{"rule_id": "entity_a"}],
            },
        }
    )

    assert row["status"] == "OK"
    assert row["symbol"] == "MEME"
    assert row["risk"] == 100
    assert row["liquidity_usd"] == 1234.57
    assert row["buy_tax"] == 4.0
    assert row["sell_tax"] == 3.98
    assert row["risk_rules"] == "risk_a,risk_b"
    assert row["entity_rules"] == "entity_a"


def test_error_row_keeps_token_and_error_message():
    row = batch.error_row("0xBad", RuntimeError("Dune timeout"))

    assert row["token"] == "0xBad"
    assert row["status"] == "ERROR"
    assert row["error"] == "Dune timeout"


def test_format_table_includes_headers_and_rows():
    table = batch.format_table(
        [
            {
                "token": "0xToken",
                "status": "OK",
                "symbol": "MEME",
                "grade": "D",
                "action": "filter",
                "risk": 100,
                "security": 0,
                "entity": 50,
                "data_quality": "good/high",
                "liquidity_usd": 1234.57,
                "volume_24h_usd": 999.9,
                "price_change_24h_pct": -4.32,
                "honeypot": False,
                "buy_tax": 4.0,
                "sell_tax": 3.98,
                "owner_renounced": True,
                "holder_count": 100,
                "nansen_signal": False,
                "risk_rules": "risk_a",
                "security_rules": "",
                "entity_rules": "entity_a",
                "error": "",
            }
        ]
    )

    assert "token" in table
    assert "0xToken" in table
    assert "risk_a" in table
    assert "false" in table
