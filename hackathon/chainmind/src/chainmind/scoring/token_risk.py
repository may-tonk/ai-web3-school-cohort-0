"""Token risk scoring with structured evidence.

The rule engine is responsible for numeric checks and evidence. AI reporting
can later turn the evidence into user-facing explanations.
"""

from __future__ import annotations

from typing import Any

from chainmind.domain import TokenSnapshot
from chainmind.scoring.score_result import ScoreResult


BASE_RISK_SCORE = 20
MAX_RISK_SCORE = 100


def calculate_token_risk(snapshot: TokenSnapshot) -> ScoreResult:
    evidence: list[dict[str, Any]] = []

    evidence.extend(_score_liquidity(snapshot))
    evidence.extend(_score_latest_flow(snapshot))
    evidence.extend(_score_early_buyers(snapshot))
    evidence.extend(_score_funding(snapshot))
    evidence.extend(_score_security(snapshot))

    score = BASE_RISK_SCORE + sum(int(item["score_delta"]) for item in evidence)
    reasons = [_debug_reason(item) for item in evidence]

    return ScoreResult(
        score=min(score, MAX_RISK_SCORE),
        reasons=reasons,
        evidence=evidence,
    )


def _score_liquidity(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    liquidity_usd = _float_or_none(snapshot.market.get("liquidity_usd"))
    if liquidity_usd is not None and liquidity_usd < 20_000:
        return [
            _evidence(
                rule_id="low_liquidity",
                severity="medium",
                score_delta=20,
                metric="liquidity_usd",
                value=liquidity_usd,
                threshold=20_000,
            )
        ]
    return []


def _score_latest_flow(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    if not snapshot.flow_5m:
        return []

    evidence: list[dict[str, Any]] = []
    latest_flow = snapshot.flow_5m[-1]
    trades = _float_or_none(latest_flow.get("trades")) or 0
    unique_traders = _float_or_none(latest_flow.get("unique_traders")) or 0
    buyers = _float_or_none(latest_flow.get("buyers")) or 0
    sellers = _float_or_none(latest_flow.get("sellers")) or 0
    buy_volume_usd = _float_or_none(latest_flow.get("buy_volume_usd")) or 0
    sell_volume_usd = _float_or_none(latest_flow.get("sell_volume_usd")) or 0
    net_buy_usd = _float_or_none(latest_flow.get("net_buy_usd")) or 0
    trades_per_unique = trades / max(unique_traders, 1)

    if trades_per_unique > 5:
        evidence.append(
            _evidence(
                rule_id="high_trade_density",
                severity="medium",
                score_delta=20,
                metric="trades_per_unique_trader",
                value=round(trades_per_unique, 4),
                threshold=5,
            )
        )

    if net_buy_usd < 0:
        evidence.append(
            _evidence(
                rule_id="negative_latest_net_buy",
                severity="medium",
                score_delta=15,
                metric="net_buy_usd",
                value=net_buy_usd,
                threshold=0,
            )
        )

    if sellers > buyers and sell_volume_usd > buy_volume_usd:
        evidence.append(
            _evidence(
                rule_id="sell_pressure_dominates",
                severity="medium",
                score_delta=15,
                metric="sell_volume_usd",
                value=sell_volume_usd,
                threshold=buy_volume_usd,
                context={
                    "buyers": buyers,
                    "sellers": sellers,
                    "buy_volume_usd": buy_volume_usd,
                },
            )
        )

    negative_buckets = [
        row
        for row in snapshot.flow_5m[-3:]
        if (_float_or_none(row.get("net_buy_usd")) or 0) < 0
    ]
    if len(negative_buckets) >= 2:
        evidence.append(
            _evidence(
                rule_id="repeated_negative_net_buy",
                severity="high",
                score_delta=20,
                metric="negative_net_buy_buckets_last_3",
                value=len(negative_buckets),
                threshold=2,
            )
        )

    return evidence


def _score_early_buyers(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    if not snapshot.early_buyers:
        return []

    evidence: list[dict[str, Any]] = []
    exited = [
        buyer
        for buyer in snapshot.early_buyers
        if _buyer_remaining_ratio(buyer) <= 0.05
    ]
    exited_ratio = len(exited) / len(snapshot.early_buyers)
    if exited_ratio > 0.6:
        evidence.append(
            _evidence(
                rule_id="early_buyer_exit_ratio_high",
                severity="high",
                score_delta=25,
                metric="early_buyer_exit_ratio",
                value=round(exited_ratio, 4),
                threshold=0.6,
                context={
                    "early_buyer_count": len(snapshot.early_buyers),
                    "exited_early_buyer_count": len(exited),
                },
            )
        )

    return evidence


def _score_funding(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    if not snapshot.funding:
        return []

    evidence: list[dict[str, Any]] = []
    shared_funders = snapshot.funding.get("shared_funders") or []
    relevant_shared_funders = [
        funder
        for funder in shared_funders
        if not bool(funder.get("is_infrastructure"))
        and int(funder.get("funded_early_buyers") or 0) >= 2
    ]

    if relevant_shared_funders:
        strongest = max(
            relevant_shared_funders,
            key=lambda funder: int(funder.get("funded_early_buyers") or 0),
        )
        funded_early_buyers = int(strongest.get("funded_early_buyers") or 0)
        evidence.append(
            _evidence(
                rule_id="shared_funder_cluster",
                severity="high",
                score_delta=20,
                metric="funded_early_buyers",
                value=funded_early_buyers,
                threshold=2,
                context={"funder": strongest.get("funder")},
            )
        )

    new_wallet_ratio = _float_or_none(snapshot.funding.get("new_wallet_ratio"))
    if new_wallet_ratio is not None and new_wallet_ratio > 0.6:
        evidence.append(
            _evidence(
                rule_id="new_wallet_ratio_high",
                severity="medium",
                score_delta=15,
                metric="new_wallet_ratio",
                value=round(new_wallet_ratio, 4),
                threshold=0.6,
            )
        )

    return evidence


def _score_security(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    if not snapshot.security:
        return []

    if bool(snapshot.security.get("high_risk")):
        return [
            _evidence(
                rule_id="security_high_risk",
                severity="critical",
                score_delta=50,
                metric="security.high_risk",
                value=True,
                threshold=False,
                context={"source": snapshot.security.get("source")},
            )
        ]

    return []


def _evidence(
    *,
    rule_id: str,
    severity: str,
    score_delta: int,
    metric: str,
    value: Any,
    threshold: Any,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "rule_id": rule_id,
        "severity": severity,
        "score_delta": score_delta,
        "metric": metric,
        "value": value,
        "threshold": threshold,
    }
    if context:
        payload["context"] = context
    return payload


def _debug_reason(evidence: dict[str, Any]) -> str:
    return (
        f"{evidence['rule_id']} triggered: "
        f"{evidence['metric']}={evidence['value']} "
        f"threshold={evidence['threshold']} "
        f"score_delta={evidence['score_delta']}."
    )


def _buyer_remaining_ratio(buyer: dict[str, Any]) -> float:
    value = buyer.get("current_balance_ratio", buyer.get("remaining_ratio"))
    return _float_or_none(value) or 0


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
