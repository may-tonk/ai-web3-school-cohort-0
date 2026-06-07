from chainmind.scoring.priority import calculate_priority_score, grade_from_scores


def test_priority_score_rewards_opportunity_and_copyability():
    result = calculate_priority_score(
        risk_score=20,
        opportunity_score=80,
        copyability_score=80,
        entity_cluster_score=10,
        security_score=0,
    )

    assert result.score >= 90
    assert result.evidence


def test_grade_a_requires_low_risk_opportunity_and_copyability():
    grade, action = grade_from_scores(
        30,
        70,
        copyability_score=70,
        entity_cluster_score=20,
        security_score=0,
    )

    assert (grade, action) == ("A", "manual_review")


def test_grade_d_for_extreme_risk_or_security():
    assert grade_from_scores(85, 90, copyability_score=90) == ("D", "filter")
    assert grade_from_scores(20, 90, copyability_score=90, security_score=90) == (
        "D",
        "filter",
    )


def test_entity_cluster_high_risk_downgrades_to_store_only():
    grade, action = grade_from_scores(
        35,
        80,
        copyability_score=80,
        entity_cluster_score=80,
    )

    assert (grade, action) == ("C", "store_only")


def test_legacy_grade_call_remains_compatible():
    assert grade_from_scores(30, 70) == ("A", "manual_review")
    assert grade_from_scores(30, 50) == ("B", "watchlist")


def _rule_ids(result):
    return {item["rule_id"] for item in result.evidence}


def test_priority_score_adds_small_gmgn_wallet_signal_bonus():
    baseline = calculate_priority_score(
        risk_score=20,
        opportunity_score=50,
        copyability_score=50,
        entity_cluster_score=0,
        security_score=0,
    )
    result = calculate_priority_score(
        risk_score=20,
        opportunity_score=50,
        copyability_score=50,
        entity_cluster_score=0,
        security_score=0,
        wallet_signal={"gmgn": {"smart_wallet_count": 1, "top_trader_count": 3}},
    )

    assert "priority_gmgn_smart_wallet_signal" in _rule_ids(result)
    assert "priority_gmgn_top_trader_signal" in _rule_ids(result)
    assert result.score > baseline.score


def test_priority_score_penalizes_gmgn_risky_wallet_signal():
    result = calculate_priority_score(
        risk_score=20,
        opportunity_score=70,
        copyability_score=70,
        entity_cluster_score=0,
        security_score=0,
        wallet_signal={
            "gmgn": {
                "smart_wallet_count": 1,
                "top_trader_count": 3,
                "sniper_count": 1,
                "insider_count": 1,
                "bundled_wallet_count": 0,
            }
        },
    )

    assert "priority_gmgn_risky_wallet_penalty" in _rule_ids(result)


def test_priority_score_blocks_positive_gmgn_signal_in_high_risk_context():
    result = calculate_priority_score(
        risk_score=80,
        opportunity_score=80,
        copyability_score=80,
        entity_cluster_score=0,
        security_score=0,
        wallet_signal={"gmgn": {"smart_wallet_count": 2, "top_trader_count": 5}},
    )

    assert "priority_gmgn_positive_signal_blocked_by_risk" in _rule_ids(result)
    assert "priority_gmgn_smart_wallet_signal" not in _rule_ids(result)
    assert "priority_gmgn_top_trader_signal" not in _rule_ids(result)
