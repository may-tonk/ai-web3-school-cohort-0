"""Entity cluster scoring for early-buyer coordination signals."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from chainmind.domain import TokenSnapshot
from chainmind.scoring.score_result import ScoreResult


MAX_ENTITY_CLUSTER_SCORE = 100


def calculate_entity_cluster_score(snapshot: TokenSnapshot) -> ScoreResult:
    evidence: list[dict[str, Any]] = []

    evidence.extend(_score_shared_funders(snapshot))
    evidence.extend(_score_new_wallet_ratio(snapshot))
    evidence.extend(_score_buy_time_concentration(snapshot))
    evidence.extend(_score_low_history_ratio(snapshot))

    score = min(
        sum(int(item["score_delta"]) for item in evidence),
        MAX_ENTITY_CLUSTER_SCORE,
    )

    return ScoreResult(
        score=score,
        reasons=[_debug_reason(item) for item in evidence],
        evidence=evidence,
    )


def _score_shared_funders(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    shared_funders = snapshot.funding.get("shared_funders") or []
    relevant = [
        funder
        for funder in shared_funders
        if not bool(funder.get("is_infrastructure"))
        and int(funder.get("funded_early_buyers") or 0) >= 2
    ]
    if not relevant:
        return []

    strongest = max(
        relevant,
        key=lambda funder: int(funder.get("funded_early_buyers") or 0),
    )
    funded = int(strongest.get("funded_early_buyers") or 0)
    score_delta = min(20 + (funded - 2) * 10, 50)
    return [
        _evidence(
            rule_id="entity_shared_funder",
            severity="high" if funded >= 3 else "medium",
            score_delta=score_delta,
            metric="funded_early_buyers",
            value=funded,
            threshold=2,
            context={"funder": strongest.get("funder")},
        )
    ]


def _score_new_wallet_ratio(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    ratio = _float_or_none(snapshot.funding.get("new_wallet_ratio"))
    if ratio is None or ratio <= 0.6:
        return []

    return [
        _evidence(
            rule_id="entity_new_wallet_ratio_high",
            severity="medium",
            score_delta=20,
            metric="new_wallet_ratio",
            value=round(ratio, 4),
            threshold=0.6,
        )
    ]


def _score_buy_time_concentration(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    timestamps = [
        parsed
        for parsed in (_parse_time(buyer.get("first_buy_time")) for buyer in snapshot.early_buyers)
        if parsed is not None
    ]
    if len(timestamps) < 3:
        return []

    timestamps.sort()
    window_seconds = (timestamps[min(4, len(timestamps) - 1)] - timestamps[0]).total_seconds()
    if window_seconds > 60:
        return []

    return [
        _evidence(
            rule_id="entity_buy_time_concentrated",
            severity="medium",
            score_delta=20,
            metric="first_early_buyers_window_seconds",
            value=int(window_seconds),
            threshold=60,
            context={"buyer_count_in_window": min(5, len(timestamps))},
        )
    ]


def _score_low_history_ratio(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    buyers_with_history = [
        buyer
        for buyer in snapshot.early_buyers
        if buyer.get("tx_count_before_entry") is not None
        or buyer.get("wallet_age_days") is not None
    ]
    if len(buyers_with_history) < 3:
        return []

    low_history = [
        buyer
        for buyer in buyers_with_history
        if _is_low_history_wallet(buyer)
    ]
    ratio = len(low_history) / len(buyers_with_history)
    if ratio <= 0.6:
        return []

    return [
        _evidence(
            rule_id="entity_low_history_wallet_ratio_high",
            severity="medium",
            score_delta=20,
            metric="low_history_wallet_ratio",
            value=round(ratio, 4),
            threshold=0.6,
            context={"buyers_with_history": len(buyers_with_history)},
        )
    ]


def _is_low_history_wallet(buyer: dict[str, Any]) -> bool:
    wallet_age_days = _float_or_none(buyer.get("wallet_age_days"))
    tx_count = _float_or_none(buyer.get("tx_count_before_entry"))
    return (
        wallet_age_days is not None and wallet_age_days <= 1
    ) or (
        tx_count is not None and tx_count <= 2
    )


def _parse_time(value: Any) -> datetime | None:
    if value is None:
        return None
    text = str(value).strip().replace("Z", "+00:00")
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        pass
    try:
        return datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


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


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
