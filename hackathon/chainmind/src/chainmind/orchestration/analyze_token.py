"""First runnable token-analysis workflow."""

from __future__ import annotations

from chainmind.domain import AnalysisResult, TokenSnapshot
from chainmind.scoring.data_quality import evaluate_data_quality
from chainmind.scoring.entity_cluster import calculate_entity_cluster_score
from chainmind.scoring.opportunity import calculate_opportunity_score
from chainmind.scoring.priority import grade_from_scores
from chainmind.scoring.security import calculate_security_score
from chainmind.scoring.token_risk import calculate_token_risk


def analyze_token(snapshot: TokenSnapshot) -> AnalysisResult:
    data_quality = evaluate_data_quality(snapshot)
    risk = calculate_token_risk(snapshot)
    security = calculate_security_score(snapshot)
    entity_cluster = calculate_entity_cluster_score(snapshot)
    opportunity = calculate_opportunity_score(snapshot)
    grade, action = grade_from_scores(risk.score, opportunity.score)
    reasons = _summary_reasons(
        snapshot, risk.score, opportunity.score, data_quality.confidence
    )
    reasons.extend(data_quality.warnings)
    reasons.extend(risk.reasons)
    reasons.extend(security.reasons)
    reasons.extend(entity_cluster.reasons)
    reasons.extend(opportunity.reasons)

    return AnalysisResult(
        token_address=snapshot.address,
        symbol=snapshot.symbol,
        chain=snapshot.chain,
        grade=grade,
        action=action,
        risk_score=risk.score,
        opportunity_score=opportunity.score,
        data_quality=data_quality.to_mapping(),
        risk_evidence=risk.evidence,
        security_score=security.score,
        security_evidence=security.evidence,
        entity_cluster_score=entity_cluster.score,
        entity_cluster_evidence=entity_cluster.evidence,
        reasons=reasons,
    )


def _summary_reasons(
    snapshot: TokenSnapshot,
    risk_score: int,
    opportunity_score: int,
    data_confidence: str,
) -> list[str]:
    reasons = [
        f"Placeholder risk score is {risk_score}; detailed token risk rules are next.",
        f"Placeholder opportunity score is {opportunity_score}; wallet alpha is not implemented yet.",
        f"Data confidence is {data_confidence}.",
    ]

    if snapshot.flow_5m:
        latest_flow = snapshot.flow_5m[-1]
        reasons.append(
            "Latest 5m flow: "
            f"buyers={latest_flow.get('buyers')}, "
            f"sellers={latest_flow.get('sellers')}, "
            f"net_buy_usd={latest_flow.get('net_buy_usd')}."
        )

    if snapshot.early_buyers:
        reasons.append(f"Loaded {len(snapshot.early_buyers)} early buyer records.")

    return reasons
