"""Priority grading from component scores."""

from __future__ import annotations

from typing import Any

from chainmind.scoring.score_result import ScoreResult


def calculate_priority_score(
    *,
    risk_score: int,
    opportunity_score: int,
    copyability_score: int = 0,
    entity_cluster_score: int = 0,
    security_score: int = 0,
    wallet_signal: dict[str, Any] | None = None,
) -> ScoreResult:
    evidence: list[dict[str, Any]] = []

    evidence.append(
        _evidence(
            rule_id="priority_opportunity_component",
            severity="positive",
            score_delta=round(opportunity_score * 0.35),
            metric="opportunity_score",
            value=opportunity_score,
            threshold="weighted",
        )
    )
    evidence.append(
        _evidence(
            rule_id="priority_copyability_component",
            severity="positive",
            score_delta=round(copyability_score * 0.35),
            metric="copyability_score",
            value=copyability_score,
            threshold="weighted",
        )
    )
    evidence.append(
        _evidence(
            rule_id="priority_risk_penalty",
            severity="negative",
            score_delta=-round(risk_score * 0.40),
            metric="risk_score",
            value=risk_score,
            threshold="weighted",
        )
    )
    evidence.append(
        _evidence(
            rule_id="priority_entity_penalty",
            severity="negative",
            score_delta=-round(entity_cluster_score * 0.15),
            metric="entity_cluster_score",
            value=entity_cluster_score,
            threshold="weighted",
        )
    )
    evidence.append(
        _evidence(
            rule_id="priority_security_penalty",
            severity="negative",
            score_delta=-round(security_score * 0.20),
            metric="security_score",
            value=security_score,
            threshold="weighted",
        )
    )
    evidence.extend(
        _score_wallet_signal(
            wallet_signal=wallet_signal or {},
            risk_score=risk_score,
            security_score=security_score,
        )
    )

    score = 50 + sum(int(item["score_delta"]) for item in evidence)
    score = max(0, min(score, 100))

    return ScoreResult(
        score=score,
        reasons=[_debug_reason(item) for item in evidence],
        evidence=evidence,
    )


def grade_from_scores(
    risk_score: int,
    opportunity_score: int,
    *,
    copyability_score: int | None = None,
    entity_cluster_score: int = 0,
    security_score: int = 0,
) -> tuple[str, str]:
    if copyability_score is None:
        copyability_score = opportunity_score

    if security_score >= 80 or risk_score >= 80:
        return "D", "filter"
    if entity_cluster_score >= 70 or risk_score >= 60:
        return "C", "store_only"
    if opportunity_score >= 65 and copyability_score >= 65 and risk_score < 40:
        return "A", "manual_review"
    if opportunity_score >= 45 and copyability_score >= 45 and risk_score < 60:
        return "B", "watchlist"
    return "C", "store_only"


def _evidence(
    *,
    rule_id: str,
    severity: str,
    score_delta: int,
    metric: str,
    value: Any,
    threshold: Any,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "severity": severity,
        "score_delta": score_delta,
        "metric": metric,
        "value": value,
        "threshold": threshold,
    }


def _score_wallet_signal(
    *,
    wallet_signal: dict[str, Any],
    risk_score: int,
    security_score: int,
) -> list[dict[str, Any]]:
    gmgn = dict(wallet_signal.get("gmgn") or {})
    if not gmgn:
        return []

    evidence: list[dict[str, Any]] = []
    smart_wallet_count = int(_number_or_zero(gmgn.get("smart_wallet_count")))
    top_trader_count = int(_number_or_zero(gmgn.get("top_trader_count")))
    sniper_count = int(_number_or_zero(gmgn.get("sniper_count")))
    insider_count = int(_number_or_zero(gmgn.get("insider_count")))
    bundled_wallet_count = int(_number_or_zero(gmgn.get("bundled_wallet_count")))
    risky_wallet_count = sniper_count + insider_count + bundled_wallet_count
    high_risk_context = security_score >= 70 or risk_score >= 70

    if smart_wallet_count > 0 and not high_risk_context:
        evidence.append(
            _evidence(
                rule_id="priority_gmgn_smart_wallet_signal",
                severity="positive",
                score_delta=5,
                metric="gmgn.smart_wallet_count",
                value=smart_wallet_count,
                threshold=1,
            )
        )

    if top_trader_count >= 3 and not high_risk_context:
        evidence.append(
            _evidence(
                rule_id="priority_gmgn_top_trader_signal",
                severity="positive",
                score_delta=3,
                metric="gmgn.top_trader_count",
                value=top_trader_count,
                threshold=3,
            )
        )

    if risky_wallet_count > 0:
        evidence.append(
            _evidence(
                rule_id="priority_gmgn_risky_wallet_penalty",
                severity="negative",
                score_delta=-8,
                metric="gmgn.risky_wallet_count",
                value=risky_wallet_count,
                threshold=0,
            )
        )

    if high_risk_context and (smart_wallet_count > 0 or top_trader_count >= 3):
        evidence.append(
            _evidence(
                rule_id="priority_gmgn_positive_signal_blocked_by_risk",
                severity="neutral",
                score_delta=0,
                metric="risk_or_security_score",
                value={"risk_score": risk_score, "security_score": security_score},
                threshold="<70",
            )
        )

    return evidence


def _number_or_zero(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0


def _debug_reason(evidence: dict[str, Any]) -> str:
    return (
        f"{evidence['rule_id']} applied: "
        f"{evidence['metric']}={evidence['value']} "
        f"weight={evidence['threshold']} "
        f"score_delta={evidence['score_delta']}."
    )
