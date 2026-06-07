from chainmind.domain import TokenSnapshot
from chainmind.scoring.copyability import calculate_copyability_score


def _snapshot(**overrides):
    payload = {
        "token": {"address": "0xabc", "symbol": "TEST", "chain": "bnb"},
        "market": {
            "liquidity_usd": 60_000,
            "volume_24h_usd": 30_000,
        },
        "flow_5m": [
            {"buyers": 10, "sellers": 4, "net_buy_usd": 2_500},
        ],
        "early_buyers": [
            {"wallet": "0x1", "remaining_ratio": 0.8},
            {"wallet": "0x2", "remaining_ratio": 0.7},
            {"wallet": "0x3", "remaining_ratio": 0.6},
        ],
        "funding": {"shared_funders": []},
        "security": {
            "high_risk": False,
            "is_honeypot": False,
            "cannot_sell_all": False,
            "buy_tax": 0.03,
            "sell_tax": 0.03,
        },
    }
    payload.update(overrides)
    return TokenSnapshot.from_mapping(payload)


def _rule_ids(result):
    return {item["rule_id"] for item in result.evidence}


def test_healthy_market_and_positive_flow_raise_copyability():
    result = calculate_copyability_score(_snapshot())

    assert result.score > 80
    assert "copyability_liquidity_strong" in _rule_ids(result)
    assert "copyability_positive_latest_net_buy" in _rule_ids(result)
    assert "copyability_buyers_outnumber_sellers" in _rule_ids(result)


def test_low_liquidity_lowers_copyability():
    result = calculate_copyability_score(
        _snapshot(market={"liquidity_usd": 3_000, "volume_24h_usd": 30_000})
    )

    assert result.score < 70
    assert "copyability_liquidity_too_low" in _rule_ids(result)


def test_early_buyer_exit_lowers_copyability():
    baseline = calculate_copyability_score(_snapshot())
    result = calculate_copyability_score(
        _snapshot(
            early_buyers=[
                {"wallet": "0x1", "remaining_ratio": 0},
                {"wallet": "0x2", "remaining_ratio": 0.01},
                {"wallet": "0x3", "remaining_ratio": 0.02},
                {"wallet": "0x4", "remaining_ratio": 0.9},
            ]
        )
    )

    assert "copyability_early_buyer_exit_ratio_high" in _rule_ids(result)
    assert result.score < baseline.score


def test_shared_funder_cluster_lowers_copyability():
    baseline = calculate_copyability_score(_snapshot())
    result = calculate_copyability_score(
        _snapshot(
            funding={
                "shared_funders": [
                    {
                        "funder": "0xfunder",
                        "funded_early_buyers": 5,
                        "is_infrastructure": False,
                    }
                ]
            }
        )
    )

    assert "copyability_shared_funder_risk" in _rule_ids(result)
    assert result.score < baseline.score


def test_honeypot_or_cannot_sell_results_in_very_low_copyability():
    honeypot = calculate_copyability_score(
        _snapshot(security={"is_honeypot": True, "cannot_sell_all": False})
    )
    cannot_sell = calculate_copyability_score(
        _snapshot(security={"is_honeypot": False, "cannot_sell_all": True})
    )

    assert honeypot.score <= 30
    assert cannot_sell.score <= 30
    assert "copyability_honeypot" in _rule_ids(honeypot)
    assert "copyability_cannot_sell_all" in _rule_ids(cannot_sell)


def test_missing_flow_does_not_crash():
    result = calculate_copyability_score(_snapshot(flow_5m=[]))

    assert result.score >= 0
    assert "copyability_missing_flow" in _rule_ids(result)


def test_gmgn_smart_wallet_and_top_trader_signals_raise_copyability_slightly():
    baseline = calculate_copyability_score(_snapshot())
    result = calculate_copyability_score(
        _snapshot(
            intelligence={
                "gmgn": {
                    "smart_wallet_count": 1,
                    "top_trader_count": 3,
                    "sniper_count": 0,
                    "insider_count": 0,
                    "bundled_wallet_count": 0,
                }
            }
        )
    )

    assert "copyability_gmgn_smart_wallet_signal" in _rule_ids(result)
    assert "copyability_gmgn_top_trader_signal" in _rule_ids(result)
    assert result.score >= baseline.score


def test_gmgn_risky_wallet_signals_lower_copyability():
    base_snapshot = _snapshot(
        market={"liquidity_usd": 30_000, "volume_24h_usd": 10_000}
    )
    baseline = calculate_copyability_score(base_snapshot)
    result = calculate_copyability_score(
        _snapshot(
            market={"liquidity_usd": 30_000, "volume_24h_usd": 10_000},
            intelligence={
                "gmgn": {
                    "smart_wallet_count": 2,
                    "top_trader_count": 4,
                    "sniper_count": 1,
                    "insider_count": 1,
                    "bundled_wallet_count": 1,
                }
            },
        )
    )

    assert "copyability_gmgn_risky_wallet_signal" in _rule_ids(result)
    assert result.score < baseline.score
