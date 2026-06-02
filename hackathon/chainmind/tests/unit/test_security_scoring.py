from chainmind.domain import TokenSnapshot
from chainmind.orchestration import analyze_token
from chainmind.scoring.security import calculate_security_score


def _snapshot(**overrides):
    payload = {
        "token": {"address": "0xabc", "symbol": "TEST", "chain": "bnb"},
        "security": {"high_risk": False},
        "contract": {},
    }
    payload.update(overrides)
    return TokenSnapshot.from_mapping(payload)


def _rule_ids(result):
    return {item["rule_id"] for item in result.evidence}


def test_honeypot_and_sellability_flags_add_security_evidence():
    result = calculate_security_score(
        _snapshot(
            security={
                "is_honeypot": True,
                "cannot_sell_all": True,
                "is_blacklisted": True,
            }
        )
    )

    assert "security_honeypot" in _rule_ids(result)
    assert "security_cannot_sell_all" in _rule_ids(result)
    assert "security_blacklist_present" in _rule_ids(result)
    assert result.score == 100


def test_high_tax_adds_security_evidence():
    result = calculate_security_score(
        _snapshot(security={"buy_tax": 0.2, "sell_tax": 0.25})
    )

    assert "security_high_buy_tax" in _rule_ids(result)
    assert "security_high_sell_tax" in _rule_ids(result)


def test_owner_and_permission_flags_add_security_evidence():
    result = calculate_security_score(
        _snapshot(
            contract={
                "owner": "0xowner",
                "owner_renounced": False,
                "is_mintable": True,
                "hidden_owner": True,
            }
        )
    )

    assert "security_owner_not_renounced" in _rule_ids(result)
    assert "security_mintable" in _rule_ids(result)
    assert "security_hidden_owner" in _rule_ids(result)


def test_analyze_token_includes_security_result():
    result = analyze_token(
        _snapshot(security={"is_honeypot": True, "high_risk": True})
    )

    assert result.security_score == 60
    assert result.to_mapping()["security_score"] == 60
    assert result.to_mapping()["security_evidence"]
