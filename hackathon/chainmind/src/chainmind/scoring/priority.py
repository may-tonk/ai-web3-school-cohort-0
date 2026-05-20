"""Priority grading from component scores."""

from __future__ import annotations


def grade_from_scores(risk_score: int, opportunity_score: int) -> tuple[str, str]:
    if risk_score >= 80:
        return "D", "filter"
    if risk_score >= 60:
        return "C", "store_only"
    if opportunity_score >= 65 and risk_score < 40:
        return "A", "manual_review"
    if opportunity_score >= 45:
        return "B", "watchlist"
    return "C", "store_only"
