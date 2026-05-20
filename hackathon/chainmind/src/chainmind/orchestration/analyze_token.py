"""First runnable token-analysis workflow."""

from __future__ import annotations

from chainmind.domain import AnalysisResult, TokenSnapshot
from chainmind.scoring.opportunity import calculate_opportunity_score
from chainmind.scoring.priority import grade_from_scores
from chainmind.scoring.token_risk import calculate_token_risk


def analyze_token(snapshot: TokenSnapshot) -> AnalysisResult:
    risk = calculate_token_risk(snapshot)
    opportunity = calculate_opportunity_score(snapshot)
    grade, action = grade_from_scores(risk.score, opportunity.score)
    reasons = _summary_reasons(snapshot, risk.score, opportunity.score)
    reasons.extend(risk.reasons)
    reasons.extend(opportunity.reasons)

    return AnalysisResult(
        token_address=snapshot.address,
        symbol=snapshot.symbol,
        chain=snapshot.chain,
        grade=grade,
        action=action,
        risk_score=risk.score,
        opportunity_score=opportunity.score,
        reasons=reasons,
    )


def _summary_reasons(
    snapshot: TokenSnapshot, risk_score: int, opportunity_score: int
) -> list[str]:
    reasons = [
        f"Placeholder risk score is {risk_score}; detailed token risk rules are next.",
        f"Placeholder opportunity score is {opportunity_score}; wallet alpha is not implemented yet.",
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
