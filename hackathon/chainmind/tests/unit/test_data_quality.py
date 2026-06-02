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


def test_negative_early_buyer_balance_adds_quality_warning():
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
                {"wallet": f"0x{i}", "current_balance": -1, "remaining_ratio": 0}
                for i in range(5)
            ],
            "funding": {"shared_funders": []},
            "security": {"high_risk": False},
        }
    )

    result = evaluate_data_quality(snapshot)

    assert result.level == "good"
    assert any("current_balance values are negative" in warning for warning in result.warnings)


def test_input_api_warnings_are_exposed_in_data_quality_result():
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
            "funding": {"shared_funders": []},
            "security": {"high_risk": False, "warnings": ["security warning"]},
            "data_quality": {"api_warnings": ["DexScreener API failed"]},
        }
    )

    result = evaluate_data_quality(snapshot)

    assert "DexScreener API failed" in result.warnings
    assert "security warning" in result.warnings


def test_missing_holders_and_contract_add_warnings_without_lowering_level():
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
            "funding": {"shared_funders": []},
            "security": {"high_risk": False},
        }
    )

    result = evaluate_data_quality(snapshot)

    assert result.level == "good"
    assert any("holder distribution" in warning for warning in result.warnings)
    assert any("contract metadata" in warning for warning in result.warnings)
