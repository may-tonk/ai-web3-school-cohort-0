"""Security evidence scoring for token snapshots."""

from __future__ import annotations

from typing import Any

from chainmind.domain import TokenSnapshot
from chainmind.scoring.score_result import ScoreResult


MAX_SECURITY_SCORE = 100


def calculate_security_score(snapshot: TokenSnapshot) -> ScoreResult:
    evidence: list[dict[str, Any]] = []

    evidence.extend(_score_honeypot(snapshot))
    evidence.extend(_score_sellability(snapshot))
    evidence.extend(_score_tax(snapshot))
    evidence.extend(_score_owner_and_permissions(snapshot))

    score = min(
        sum(int(item["score_delta"]) for item in evidence),
        MAX_SECURITY_SCORE,
    )
    return ScoreResult(
        score=score,
        reasons=[_debug_reason(item) for item in evidence],
        evidence=evidence,
    )


def _score_honeypot(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    if snapshot.security.get("is_honeypot") is True:
        return [
            _evidence(
                rule_id="security_honeypot",
                severity="critical",
                score_delta=60,
                metric="security.is_honeypot",
                value=True,
                threshold=False,
            )
        ]
    return []


def _score_sellability(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    if snapshot.security.get("cannot_sell_all") is True:
        evidence.append(
            _evidence(
                rule_id="security_cannot_sell_all",
                severity="critical",
                score_delta=40,
                metric="security.cannot_sell_all",
                value=True,
                threshold=False,
            )
        )
    if snapshot.security.get("is_blacklisted") is True:
        evidence.append(
            _evidence(
                rule_id="security_blacklist_present",
                severity="high",
                score_delta=30,
                metric="security.is_blacklisted",
                value=True,
                threshold=False,
            )
        )
    return evidence


def _score_tax(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    buy_tax = _float_or_none(snapshot.security.get("buy_tax"))
    sell_tax = _float_or_none(snapshot.security.get("sell_tax"))

    if buy_tax is not None and buy_tax >= 0.2:
        evidence.append(
            _evidence(
                rule_id="security_high_buy_tax",
                severity="high",
                score_delta=25,
                metric="security.buy_tax",
                value=round(buy_tax, 4),
                threshold=0.2,
            )
        )

    if sell_tax is not None and sell_tax >= 0.2:
        evidence.append(
            _evidence(
                rule_id="security_high_sell_tax",
                severity="high",
                score_delta=30,
                metric="security.sell_tax",
                value=round(sell_tax, 4),
                threshold=0.2,
            )
        )

    return evidence


def _score_owner_and_permissions(snapshot: TokenSnapshot) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    owner_renounced = snapshot.contract.get("owner_renounced")

    if owner_renounced is False:
        evidence.append(
            _evidence(
                rule_id="security_owner_not_renounced",
                severity="medium",
                score_delta=15,
                metric="contract.owner_renounced",
                value=False,
                threshold=True,
                context={"owner": snapshot.contract.get("owner")},
            )
        )

    if snapshot.contract.get("is_mintable") is True:
        evidence.append(
            _evidence(
                rule_id="security_mintable",
                severity="high",
                score_delta=25,
                metric="contract.is_mintable",
                value=True,
                threshold=False,
            )
        )

    if snapshot.contract.get("hidden_owner") is True:
        evidence.append(
            _evidence(
                rule_id="security_hidden_owner",
                severity="high",
                score_delta=30,
                metric="contract.hidden_owner",
                value=True,
                threshold=False,
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


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
