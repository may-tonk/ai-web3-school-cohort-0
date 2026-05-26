from chainmind.domain import TokenSnapshot
from chainmind.scoring.data_quality import evaluate_data_quality


def test_complete_snapshot_has_good_quality():
    snapshot = TokenSnapshot.from_mapping(
        {
            "token": {"address": "0xabc", "symbol": "TEST", "chain": "bnb"},
            "market": {"liquidity_usd": 100000},
            "flow_5m": [
                {
                    "trades": 10,
                    "unique_traders": 8,
                    "buy_volume_usd": 5000,
                    "sell_volume_usd": 2000,
                    "net_buy_usd": 3000,
                }
            ],
            "early_buyers": [
                {"wallet": f"0x{i}", "current_balance_ratio": 0.8}
                for i in range(5)
            ],
            "funding": {"shared_funders": []},
            "security": {"high_risk": False},
        }
    )

    result = evaluate_data_quality(snapshot)

    assert result.level == "good"
    assert result.confidence == "high"
    assert result.missing_fields == []


def test_missing_flow_and_early_buyers_has_poor_quality():
    snapshot = TokenSnapshot.from_mapping(
        {
            "token": {"address": "0xabc", "symbol": "TEST", "chain": "bnb"},
            "market": {"liquidity_usd": 100000},
            "funding": {"shared_funders": []},
            "security": {"high_risk": False},
        }
    )

    result = evaluate_data_quality(snapshot)

    assert result.level == "poor"
    assert result.confidence == "low"
    assert "flow_5m" in result.missing_fields
    assert "early_buyers" in result.missing_fields


def test_missing_funding_has_partial_quality():
    snapshot = TokenSnapshot.from_mapping(
        {
            "token": {"address": "0xabc", "symbol": "TEST", "chain": "bnb"},
            "market": {"liquidity_usd": 100000},
            "flow_5m": [
                {
                    "buy_volume_usd": 5000,
                    "sell_volume_usd": 2000,
                    "net_buy_usd": 3000,
                }
            ],
            "early_buyers": [
                {"wallet": f"0x{i}", "current_balance_ratio": 0.8}
                for i in range(5)
            ],
            "security": {"high_risk": False},
        }
    )

    result = evaluate_data_quality(snapshot)

    assert result.level == "partial"
    assert result.confidence == "medium"
    assert "funding" in result.missing_fields
