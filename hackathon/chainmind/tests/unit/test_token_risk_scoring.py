from chainmind.domain import TokenSnapshot
from chainmind.scoring.token_risk import calculate_token_risk


def _snapshot(**overrides):
    payload = {
        "token": {"address": "0xabc", "symbol": "TEST", "chain": "bnb"},
        "market": {"liquidity_usd": 100000},
        "flow_5m": [
            {
                "trades": 20,
                "unique_traders": 15,
                "buyers": 10,
                "sellers": 5,
                "buy_volume_usd": 5000,
                "sell_volume_usd": 1000,
                "net_buy_usd": 4000,
            }
        ],
        "early_buyers": [
            {"wallet": f"0x{i}", "current_balance_ratio": 0.8}
            for i in range(5)
        ],
        "funding": {"shared_funders": [], "new_wallet_ratio": 0},
        "security": {"high_risk": False},
    }
    payload.update(overrides)
    return TokenSnapshot.from_mapping(payload)


def _rule_ids(result):
    return {item["rule_id"] for item in result.evidence}


def test_low_liquidity_adds_structured_evidence():
    result = calculate_token_risk(_snapshot(market={"liquidity_usd": 12000}))

    assert "low_liquidity" in _rule_ids(result)
    assert result.score >= 40


def test_negative_flow_and_sell_pressure_add_evidence():
    result = calculate_token_risk(
        _snapshot(
            flow_5m=[
                {
                    "trades": 260,
                    "unique_traders": 21,
                    "buyers": 9,
                    "sellers": 16,
                    "buy_volume_usd": 2500,
                    "sell_volume_usd": 8400,
                    "net_buy_usd": -5900,
                }
            ]
        )
    )

    assert "high_trade_density" in _rule_ids(result)
    assert "negative_latest_net_buy" in _rule_ids(result)
    assert "sell_pressure_dominates" in _rule_ids(result)


def test_repeated_negative_net_buy_adds_evidence():
    result = calculate_token_risk(
        _snapshot(
            flow_5m=[
                {"net_buy_usd": -100, "trades": 10, "unique_traders": 10},
                {"net_buy_usd": -200, "trades": 10, "unique_traders": 10},
                {"net_buy_usd": 50, "trades": 10, "unique_traders": 10},
            ]
        )
    )

    assert "repeated_negative_net_buy" in _rule_ids(result)


def test_early_buyer_exit_ratio_adds_evidence():
    result = calculate_token_risk(
        _snapshot(
            early_buyers=[
                {"wallet": f"0x{i}", "current_balance_ratio": 0}
                for i in range(4)
            ]
            + [{"wallet": "0x5", "current_balance_ratio": 0.8}]
        )
    )

    assert "early_buyer_exit_ratio_high" in _rule_ids(result)


def test_shared_funder_and_new_wallet_ratio_add_evidence():
    result = calculate_token_risk(
        _snapshot(
            funding={
                "shared_funders": [
                    {
                        "funder": "0xfunder",
                        "funded_early_buyers": 3,
                        "is_infrastructure": False,
                    }
                ],
                "new_wallet_ratio": 1,
            }
        )
    )

    assert "shared_funder_cluster" in _rule_ids(result)
    assert "new_wallet_ratio_high" in _rule_ids(result)


def test_infrastructure_funder_does_not_add_shared_funder_evidence():
    result = calculate_token_risk(
        _snapshot(
            funding={
                "shared_funders": [
                    {
                        "funder": "0xrouter",
                        "funded_early_buyers": 10,
                        "is_infrastructure": True,
                    }
                ],
                "new_wallet_ratio": 0,
            }
        )
    )

    assert "shared_funder_cluster" not in _rule_ids(result)


def test_security_high_risk_adds_critical_evidence():
    result = calculate_token_risk(
        _snapshot(security={"high_risk": True, "source": "manual_test"})
    )

    assert "security_high_risk" in _rule_ids(result)
    assert result.score >= 70
