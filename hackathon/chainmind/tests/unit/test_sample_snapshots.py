import json
from pathlib import Path

from chainmind.domain import TokenSnapshot
from chainmind.orchestration import analyze_token


SAMPLES_DIR = Path(__file__).resolve().parents[2] / "samples" / "tokens"


def test_all_token_samples_are_analyzable():
    sample_paths = sorted(SAMPLES_DIR.glob("*.json"))

    assert sample_paths

    for sample_path in sample_paths:
        payload = json.loads(sample_path.read_text(encoding="utf-8"))
        result = analyze_token(TokenSnapshot.from_mapping(payload))

        assert result.token_address
        assert result.symbol
        assert result.grade in {"A", "B", "C", "D"}
        assert 0 <= result.risk_score <= 100
        assert 0 <= result.opportunity_score <= 100
        assert result.data_quality["level"] in {"good", "partial", "poor"}


def test_synthetic_samples_trigger_expected_rules():
    for sample_path in sorted(SAMPLES_DIR.glob("*.json")):
        payload = json.loads(sample_path.read_text(encoding="utf-8"))
        sample_meta = payload.get("sample_meta", {})
        expected_rules = set(sample_meta.get("expected_primary_rules", []))

        if not expected_rules:
            continue

        result = analyze_token(TokenSnapshot.from_mapping(payload))
        actual_rules = {item["rule_id"] for item in result.risk_evidence}

        assert expected_rules.issubset(actual_rules), sample_path.name


def test_samples_with_expected_data_quality_match_level():
    for sample_path in sorted(SAMPLES_DIR.glob("*.json")):
        payload = json.loads(sample_path.read_text(encoding="utf-8"))
        expected_level = payload.get("sample_meta", {}).get("expected_data_quality")

        if not expected_level:
            continue

        result = analyze_token(TokenSnapshot.from_mapping(payload))

        assert result.data_quality["level"] == expected_level, sample_path.name
