"""Initial token risk scoring.

These are foundation heuristics. The next step will turn the documented risk
rules into configurable weights and richer evidence.
"""

from __future__ import annotations

from chainmind.domain import TokenSnapshot
from chainmind.scoring.score_result import ScoreResult


def calculate_token_risk(snapshot: TokenSnapshot) -> ScoreResult:
    score = 20
    reasons: list[str] = []

    liquidity_score, liquidity_reasons = _score_liquidity(snapshot)
    flow_score, flow_reasons = _score_latest_flow(snapshot)
    early_buyer_score, early_buyer_reasons = _score_early_buyers(snapshot)

    score += liquidity_score + flow_score + early_buyer_score
    reasons.extend(liquidity_reasons)
    reasons.extend(flow_reasons)
    reasons.extend(early_buyer_reasons)

    return ScoreResult(score=min(score, 100), reasons=reasons)


def _score_liquidity(snapshot: TokenSnapshot) -> tuple[int, list[str]]:
    liquidity_usd = float(snapshot.market.get("liquidity_usd") or 0)
    if liquidity_usd and liquidity_usd < 20_000:
        return 20, [f"Liquidity is low at {liquidity_usd:.0f} USD."]
    return 0, []


def _score_latest_flow(snapshot: TokenSnapshot) -> tuple[int, list[str]]:
    if not snapshot.flow_5m:
        return 0, []

    score = 0
    reasons: list[str] = []
    latest_flow = snapshot.flow_5m[-1]
    trades = float(latest_flow.get("trades") or 0)
    unique_traders = float(latest_flow.get("unique_traders") or 1)
    net_buy_usd = float(latest_flow.get("net_buy_usd") or 0)

    if trades / max(unique_traders, 1) > 5:
        score += 20
        reasons.append("Trades are high relative to unique traders.")

    if net_buy_usd < 0:
        score += 15
        reasons.append("Latest 5m net buy is negative.")

    return score, reasons


def _score_early_buyers(snapshot: TokenSnapshot) -> tuple[int, list[str]]:
    if not snapshot.early_buyers:
        return 0, []

    exited = [
        buyer
        for buyer in snapshot.early_buyers
        if float(buyer.get("current_balance_ratio") or 0) <= 0.05
    ]
    exited_ratio = len(exited) / len(snapshot.early_buyers)
    if exited_ratio > 0.6:
        return 25, [f"Early buyer exit ratio is high at {exited_ratio:.0%}."]

    return 0, []
