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
