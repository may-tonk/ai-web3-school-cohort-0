from chainmind.domain import TokenSnapshot
from chainmind.orchestration import analyze_token
from chainmind.scoring.entity_cluster import calculate_entity_cluster_score


def _snapshot(**overrides):
    payload = {
        "token": {"address": "0xabc", "symbol": "TEST", "chain": "bnb"},
        "market": {"liquidity_usd": 100000},
        "flow_5m": [],
        "early_buyers": [],
        "funding": {},
        "security": {"high_risk": False},
    }
    payload.update(overrides)
    return TokenSnapshot.from_mapping(payload)


def _rule_ids(result):
    return {item["rule_id"] for item in result.evidence}


def test_shared_funder_adds_entity_cluster_evidence():
    result = calculate_entity_cluster_score(
        _snapshot(
            funding={
                "shared_funders": [
                    {
                        "funder": "0xfunder",
                        "funded_early_buyers": 4,
                        "is_infrastructure": False,
                    }
                ]
            }
        )
    )

    assert "entity_shared_funder" in _rule_ids(result)
    assert result.score >= 40


def test_infrastructure_funder_does_not_add_entity_cluster_evidence():
    result = calculate_entity_cluster_score(
        _snapshot(
            funding={
                "shared_funders": [
                    {
                        "funder": "0xrouter",
                        "funded_early_buyers": 10,
                        "is_infrastructure": True,
                    }
                ]
            }
        )
    )

    assert "entity_shared_funder" not in _rule_ids(result)


def test_new_wallet_ratio_adds_entity_cluster_evidence():
    result = calculate_entity_cluster_score(
        _snapshot(funding={"shared_funders": [], "new_wallet_ratio": 0.8})
    )

    assert "entity_new_wallet_ratio_high" in _rule_ids(result)


def test_buy_time_concentration_adds_entity_cluster_evidence():
    result = calculate_entity_cluster_score(
        _snapshot(
            early_buyers=[
                {"wallet": "0x1", "first_buy_time": "2026-05-31 00:00:00"},
                {"wallet": "0x2", "first_buy_time": "2026-05-31 00:00:12"},
                {"wallet": "0x3", "first_buy_time": "2026-05-31 00:00:25"},
                {"wallet": "0x4", "first_buy_time": "2026-05-31 00:00:40"},
                {"wallet": "0x5", "first_buy_time": "2026-05-31 00:00:55"},
            ]
        )
    )

    assert "entity_buy_time_concentrated" in _rule_ids(result)


def test_low_history_wallet_ratio_adds_entity_cluster_evidence():
    result = calculate_entity_cluster_score(
        _snapshot(
            early_buyers=[
                {"wallet": "0x1", "wallet_age_days": 0, "tx_count_before_entry": 1},
                {"wallet": "0x2", "wallet_age_days": 0, "tx_count_before_entry": 1},
                {"wallet": "0x3", "wallet_age_days": 0, "tx_count_before_entry": 1},
                {"wallet": "0x4", "wallet_age_days": 10, "tx_count_before_entry": 20},
            ]
        )
    )

    assert "entity_low_history_wallet_ratio_high" in _rule_ids(result)


def test_analyze_token_includes_entity_cluster_result():
    result = analyze_token(
        _snapshot(funding={"shared_funders": [], "new_wallet_ratio": 0.9})
    )

    assert result.entity_cluster_score == 20
    assert result.to_mapping()["entity_cluster_score"] == 20
    assert result.to_mapping()["entity_cluster_evidence"]
