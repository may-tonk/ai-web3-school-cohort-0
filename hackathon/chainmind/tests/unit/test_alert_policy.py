from chainmind.alerts import build_telegram_markdown, decide_alert_delivery


def test_decide_alert_delivery_maps_grade_and_action_to_delivery_level():
    assert decide_alert_delivery({"grade": "A", "action": "manual_review"}).to_mapping() == {
        "should_send": True,
        "delivery_level": "immediate",
        "reason": "A-grade or manual-review result should be sent immediately.",
    }

    b_decision = decide_alert_delivery({"grade": "B", "action": "watchlist"})
    assert b_decision.should_send is True
    assert b_decision.delivery_level == "digest"

    c_decision = decide_alert_delivery({"grade": "C", "action": "store_only"})
    assert c_decision.should_send is False
    assert c_decision.delivery_level == "store_only"

    d_decision = decide_alert_delivery({"grade": "D", "action": "filter"})
    assert d_decision.should_send is False
    assert d_decision.delivery_level == "filter"


def test_build_telegram_markdown_summarizes_scores_evidence_and_boundary():
    message = build_telegram_markdown(
        snapshot={
            "token": {"address": "0xToken", "symbol": "MEME", "chain": "bnb"},
            "market": {"base_token_symbol": "MEME"},
        },
        analysis={
            "token_address": "0xToken",
            "symbol": "MEME",
            "chain": "bnb",
            "grade": "B",
            "action": "watchlist",
            "risk_score": 45,
            "security_score": 10,
            "entity_cluster_score": 0,
            "copyability_score": 70,
            "priority_score": 72,
            "risk_evidence": [
                {
                    "rule_id": "negative_latest_net_buy",
                    "severity": "high",
                    "score_delta": 15,
                    "metric": "net_buy_usd",
                    "value": -1000,
                }
            ],
            "copyability_evidence": [
                {
                    "rule_id": "copyability_liquidity_strong",
                    "severity": "positive",
                    "score_delta": 15,
                    "metric": "liquidity_usd",
                    "value": 50000,
                }
            ],
        },
    )

    assert "[B] MEME / BNB" in message
    assert "Decision: watchlist (digest)" in message
    assert "Risk 45" in message
    assert "copyability_liquidity_strong" in message
    assert "negative_latest_net_buy" in message
    assert "evidence-only research alert" in message

    prohibited_terms = ["买入", "卖出", "仓位", "止盈", "止损"]
    assert all(term not in message for term in prohibited_terms)
