from chainmind.domain import TokenSnapshot
from chainmind.orchestration import analyze_token


def test_analyze_token_returns_minimal_result():
    snapshot = TokenSnapshot.from_mapping(
        {
            "token": {
                "address": "0xabc",
                "symbol": "TEST",
                "chain": "bnb",
            },
            "market": {
                "liquidity_usd": 100000,
                "volume_5m_usd": 10000,
            },
            "flow_5m": [
                {
                    "trades": 40,
                    "unique_traders": 20,
                    "buyers": 14,
                    "sellers": 6,
                    "net_buy_usd": 5000,
                }
            ],
            "early_buyers": [
                {
                    "wallet": "0x1",
                    "current_balance_ratio": 0.8,
                }
            ],
        }
    )

    result = analyze_token(snapshot)

    assert result.symbol == "TEST"
    assert result.chain == "bnb"
    assert result.grade in {"A", "B", "C", "D"}
    assert result.risk_score >= 0
    assert result.opportunity_score >= 0
