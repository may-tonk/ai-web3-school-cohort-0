"""Token-level copyability scoring.

Copyability v0 estimates whether a token still has a practical observation or
follow window. It does not claim that any wallet has proven historical alpha.
"""

from __future__ import annotations

from typing import Any

from chainmind.domain import TokenSnapshot
from chainmind.scoring.score_result import ScoreResult


BASE_COPYABILITY_SCORE = 50
MIN_COPYABILITY_SCORE = 0
MAX_COPYABILITY_SCORE = 100


def calculate_copyability_score(snapshot: TokenSnapshot) -> ScoreResult:
    evidence: list[dict[str, Any]] = []

    evidence.extend(_score_security(snapshot))
    evidence.extend(_score_market_depth(snapshot))
    evidence.extend(_score_latest_flow(snapshot))
    evidence.extend(_score_early_buyers(snapshot))
    evidence.extend(_score_funding(snapshot))
    evidence.extend(_score_gmgn_wallet_intelligence(snapshot))

    score = BASE_COPYABILITY_SCORE + sum(int(item["score_delta"]) for item in evidence)
    score = max(MIN_COPYABILITY_SCORE, min(score, MAX_COPYABILITY_SCORE))

    return ScoreResult(
        score=score,
        reasons=[_debug_reason(item) for item in evidence],
        evidence=evidence,
    )


def _score_security(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    security = snapshot.security
    evidence: list[dict[str, Any]] = []

    if bool(security.get("high_risk")):
        evidence.append(
            _evidence(
                rule_id="copyability_security_high_risk",
                severity="critical",
                score_delta=-80,
                metric="security.high_risk",
                value=True,
                threshold=False,
            )
        )

    if bool(security.get("is_honeypot")):
        evidence.append(
            _evidence(
                rule_id="copyability_honeypot",
                severity="critical",
                score_delta=-80,
                metric="is_honeypot",
                value=True,
                threshold=False,
            )
        )

    if bool(security.get("cannot_sell_all")):
        evidence.append(
            _evidence(
                rule_id="copyability_cannot_sell_all",
                severity="critical",
                score_delta=-80,
                metric="cannot_sell_all",
                value=True,
                threshold=False,
            )
        )

    for field_name in ("buy_tax", "sell_tax"):
        tax = _float_or_none(security.get(field_name))
        if tax is None:
            continue
        if tax >= 0.20:
            evidence.append(
                _evidence(
                    rule_id=f"copyability_extreme_{field_name}",
                    severity="critical",
                    score_delta=-40,
                    metric=field_name,
                    value=round(tax, 4),
                    threshold=0.20,
                )
            )
        elif tax >= 0.08:
            evidence.append(
                _evidence(
                    rule_id=f"copyability_high_{field_name}",
                    severity="medium",
                    score_delta=-15,
                    metric=field_name,
                    value=round(tax, 4),
                    threshold=0.08,
                )
            )

    return evidence


def _score_market_depth(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    liquidity_usd = _float_or_none(snapshot.market.get("liquidity_usd"))
    volume_24h_usd = _float_or_none(snapshot.market.get("volume_24h_usd"))

    if liquidity_usd is not None:
        if liquidity_usd < 5_000:
            evidence.append(
                _evidence(
                    rule_id="copyability_liquidity_too_low",
                    severity="high",
                    score_delta=-30,
                    metric="liquidity_usd",
                    value=liquidity_usd,
                    threshold=5_000,
                )
            )
        elif liquidity_usd < 20_000:
            evidence.append(
                _evidence(
                    rule_id="copyability_liquidity_weak",
                    severity="medium",
                    score_delta=-15,
                    metric="liquidity_usd",
                    value=liquidity_usd,
                    threshold=20_000,
                )
            )
        elif liquidity_usd >= 50_000:
            evidence.append(
                _evidence(
                    rule_id="copyability_liquidity_strong",
                    severity="positive",
                    score_delta=15,
                    metric="liquidity_usd",
                    value=liquidity_usd,
                    threshold=50_000,
                )
            )
        else:
            evidence.append(
                _evidence(
                    rule_id="copyability_liquidity_usable",
                    severity="positive",
                    score_delta=8,
                    metric="liquidity_usd",
                    value=liquidity_usd,
                    threshold=20_000,
                )
            )

    if volume_24h_usd is not None:
        if volume_24h_usd < 5_000:
            evidence.append(
                _evidence(
                    rule_id="copyability_volume_weak",
                    severity="medium",
                    score_delta=-10,
                    metric="volume_24h_usd",
                    value=volume_24h_usd,
                    threshold=5_000,
                )
            )
        elif volume_24h_usd >= 25_000:
            evidence.append(
                _evidence(
                    rule_id="copyability_volume_strong",
                    severity="positive",
                    score_delta=10,
                    metric="volume_24h_usd",
                    value=volume_24h_usd,
                    threshold=25_000,
                )
            )
        else:
            evidence.append(
                _evidence(
                    rule_id="copyability_volume_usable",
                    severity="positive",
                    score_delta=5,
                    metric="volume_24h_usd",
                    value=volume_24h_usd,
                    threshold=5_000,
                )
            )

    return evidence


def _score_latest_flow(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    if not snapshot.flow_5m:
        return [
            _evidence(
                rule_id="copyability_missing_flow",
                severity="low",
                score_delta=-5,
                metric="flow_5m",
                value=0,
                threshold="available",
            )
        ]

    evidence: list[dict[str, Any]] = []
    latest_flow = snapshot.flow_5m[-1]
    buyers = _float_or_none(latest_flow.get("buyers")) or 0
    sellers = _float_or_none(latest_flow.get("sellers")) or 0
    net_buy_usd = _float_or_none(latest_flow.get("net_buy_usd")) or 0

    if net_buy_usd > 0:
        evidence.append(
            _evidence(
                rule_id="copyability_positive_latest_net_buy",
                severity="positive",
                score_delta=15,
                metric="net_buy_usd",
                value=net_buy_usd,
                threshold=0,
            )
        )
    elif net_buy_usd < 0:
        evidence.append(
            _evidence(
                rule_id="copyability_negative_latest_net_buy",
                severity="medium",
                score_delta=-15,
                metric="net_buy_usd",
                value=net_buy_usd,
                threshold=0,
            )
        )

    if buyers > sellers:
        evidence.append(
            _evidence(
                rule_id="copyability_buyers_outnumber_sellers",
                severity="positive",
                score_delta=10,
                metric="buyers_vs_sellers",
                value={"buyers": buyers, "sellers": sellers},
                threshold="buyers > sellers",
            )
        )
    elif sellers > buyers:
        evidence.append(
            _evidence(
                rule_id="copyability_sellers_outnumber_buyers",
                severity="medium",
                score_delta=-10,
                metric="buyers_vs_sellers",
                value={"buyers": buyers, "sellers": sellers},
                threshold="buyers >= sellers",
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
                rule_id="copyability_repeated_negative_net_buy",
                severity="high",
                score_delta=-15,
                metric="negative_net_buy_buckets_last_3",
                value=len(negative_buckets),
                threshold=2,
            )
        )

    return evidence


def _score_early_buyers(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    if not snapshot.early_buyers:
        return []

    exited = [
        buyer
        for buyer in snapshot.early_buyers
        if _buyer_remaining_ratio(buyer) <= 0.05
    ]
    exited_ratio = len(exited) / len(snapshot.early_buyers)

    if exited_ratio > 0.6:
        return [
            _evidence(
                rule_id="copyability_early_buyer_exit_ratio_high",
                severity="high",
                score_delta=-20,
                metric="early_buyer_exit_ratio",
                value=round(exited_ratio, 4),
                threshold=0.6,
                context={
                    "early_buyer_count": len(snapshot.early_buyers),
                    "exited_early_buyer_count": len(exited),
                },
            )
        ]

    if exited_ratio <= 0.3:
        return [
            _evidence(
                rule_id="copyability_early_buyer_retention_healthy",
                severity="positive",
                score_delta=10,
                metric="early_buyer_exit_ratio",
                value=round(exited_ratio, 4),
                threshold=0.3,
                context={"early_buyer_count": len(snapshot.early_buyers)},
            )
        ]

    return []


def _score_funding(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
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
        funded = int(strongest.get("funded_early_buyers") or 0)
        evidence.append(
            _evidence(
                rule_id="copyability_shared_funder_risk",
                severity="high" if funded >= 5 else "medium",
                score_delta=-25 if funded >= 5 else -15,
                metric="funded_early_buyers",
                value=funded,
                threshold=2,
                context={"funder": strongest.get("funder")},
            )
        )

    new_wallet_ratio = _float_or_none(snapshot.funding.get("new_wallet_ratio"))
    if new_wallet_ratio is not None and new_wallet_ratio > 0.6:
        evidence.append(
            _evidence(
                rule_id="copyability_new_wallet_ratio_high",
                severity="medium",
                score_delta=-10,
                metric="new_wallet_ratio",
                value=round(new_wallet_ratio, 4),
                threshold=0.6,
            )
        )

    return evidence


def _score_gmgn_wallet_intelligence(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    gmgn = dict(snapshot.intelligence.get("gmgn") or {})
    if not gmgn:
        return []

    evidence: list[dict[str, Any]] = []
    smart_wallet_count = int(_float_or_none(gmgn.get("smart_wallet_count")) or 0)
    top_trader_count = int(_float_or_none(gmgn.get("top_trader_count")) or 0)
    sniper_count = int(_float_or_none(gmgn.get("sniper_count")) or 0)
    insider_count = int(_float_or_none(gmgn.get("insider_count")) or 0)
    bundled_wallet_count = int(_float_or_none(gmgn.get("bundled_wallet_count")) or 0)
    risky_wallet_count = sniper_count + insider_count + bundled_wallet_count

    if smart_wallet_count > 0:
        evidence.append(
            _evidence(
                rule_id="copyability_gmgn_smart_wallet_signal",
                severity="positive",
                score_delta=5,
                metric="gmgn.smart_wallet_count",
                value=smart_wallet_count,
                threshold=1,
            )
        )

    if top_trader_count >= 3:
        evidence.append(
            _evidence(
                rule_id="copyability_gmgn_top_trader_signal",
                severity="positive",
                score_delta=5,
                metric="gmgn.top_trader_count",
                value=top_trader_count,
                threshold=3,
            )
        )

    if risky_wallet_count > 0:
        evidence.append(
            _evidence(
                rule_id="copyability_gmgn_risky_wallet_signal",
                severity="high" if risky_wallet_count >= 3 else "medium",
                score_delta=-15 if risky_wallet_count >= 3 else -8,
                metric="gmgn.risky_wallet_count",
                value=risky_wallet_count,
                threshold=0,
                context={
                    "sniper_count": sniper_count,
                    "insider_count": insider_count,
                    "bundled_wallet_count": bundled_wallet_count,
                },
            )
        )

    return evidence


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
