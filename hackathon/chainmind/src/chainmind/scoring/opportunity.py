"""Initial opportunity scoring."""

from __future__ import annotations

from chainmind.domain import TokenSnapshot
from chainmind.scoring.score_result import ScoreResult


def calculate_opportunity_score(snapshot: TokenSnapshot) -> ScoreResult:
    score = 20
    reasons: list[str] = []

    if snapshot.market.get("volume_5m_usd"):
        score += 10
        reasons.append("Recent 5m volume is available.")

    flow_score, flow_reasons = _score_latest_flow(snapshot)
    early_buyer_score, early_buyer_reasons = _score_early_buyers(snapshot)

    score += flow_score + early_buyer_score
    reasons.extend(flow_reasons)
    reasons.extend(early_buyer_reasons)

    return ScoreResult(score=min(score, 100), reasons=reasons)


def _score_latest_flow(snapshot: TokenSnapshot) -> tuple[int, list[str]]:
    if not snapshot.flow_5m:
        return 0, []

    score = 0
    reasons: list[str] = []
    latest_flow = snapshot.flow_5m[-1]
    buyers = int(latest_flow.get("buyers") or 0)
    sellers = int(latest_flow.get("sellers") or 0)
    net_buy_usd = float(latest_flow.get("net_buy_usd") or 0)

    if buyers > sellers:
        score += 15
        reasons.append("Buyers outnumber sellers in the latest 5m bucket.")

    if net_buy_usd > 0:
        score += 15
        reasons.append("Latest 5m net buy is positive.")

    return score, reasons


def _score_early_buyers(snapshot: TokenSnapshot) -> tuple[int, list[str]]:
    if not snapshot.early_buyers:
        return 0, []

    holders = [
        buyer
        for buyer in snapshot.early_buyers
        if float(buyer.get("current_balance_ratio") or 0) >= 0.5
    ]
    holder_ratio = len(holders) / len(snapshot.early_buyers)
    if holder_ratio >= 0.5:
        return 15, [f"Most early buyer records still hold material balance ({holder_ratio:.0%})."]

    return 0, []
