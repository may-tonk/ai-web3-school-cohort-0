"""Build short alert text for Hermes and Telegram surfaces."""

from __future__ import annotations

from typing import Any

from chainmind.alerts.alert_policy import AlertDecision, decide_alert_delivery


DIGEST_PAYLOAD_VERSION = "phase6b-digest-payload-v1"


def build_telegram_markdown(
    *,
    snapshot: dict[str, Any],
    analysis: dict[str, Any],
    decision: AlertDecision | None = None,
) -> str:
    """Render a compact, evidence-only Markdown message for Hermes delivery."""

    snapshot = dict(snapshot or {})
    analysis = dict(analysis or {})
    decision = decision or decide_alert_delivery(analysis)
    token = dict(snapshot.get("token") or {})
    market = dict(snapshot.get("market") or {})

    symbol = (
        market.get("base_token_symbol")
        or analysis.get("symbol")
        or token.get("symbol")
        or "UNKNOWN"
    )
    chain = analysis.get("chain") or token.get("chain") or "unknown"
    address = analysis.get("token_address") or token.get("address") or "unknown"
    grade = analysis.get("grade") or "N/A"
    action = analysis.get("action") or "N/A"

    lines = [
        f"[{grade}] {symbol} / {str(chain).upper()}",
        "",
        f"Decision: {action} ({decision.delivery_level})",
        (
            "Scores: "
            f"Risk {analysis.get('risk_score', 'N/A')} | "
            f"Security {analysis.get('security_score', 'N/A')} | "
            f"Entity {analysis.get('entity_cluster_score', 'N/A')} | "
            f"Copyability {analysis.get('copyability_score', 'N/A')} | "
            f"Priority {analysis.get('priority_score', 'N/A')}"
        ),
        f"Token: {address}",
        "",
        "Opportunity evidence:",
    ]
    lines.extend(_evidence_lines(_positive_evidence(analysis), "- None recorded."))
    lines.append("")
    lines.append("Risk evidence:")
    lines.extend(_evidence_lines(_risk_evidence(analysis), "- None recorded."))
    lines.append("")
    lines.append("Watch conditions:")
    lines.extend(f"- {condition}" for condition in _watch_conditions(analysis))
    lines.append("")
    lines.append("Boundary: evidence-only research alert; no execution instructions.")
    return "\n".join(lines).rstrip() + "\n"


def build_digest_payload(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    """Build a digest payload from sendable Hermes digest-level payloads."""

    items = [
        _digest_item(payload)
        for payload in payloads
        if _is_digest_candidate(payload)
    ]
    items.sort(key=lambda item: _number_or_zero(item.get("priority_score")), reverse=True)

    return {
        "version": DIGEST_PAYLOAD_VERSION,
        "channel": "hermes",
        "candidate_count": len(payloads),
        "send_count": len(items),
        "items": items,
        "digest_markdown": build_digest_markdown(items),
    }


def build_digest_markdown(items_or_payloads: list[dict[str, Any]]) -> str:
    """Render digest Markdown from digest items or raw Hermes payloads."""

    items = [
        _digest_item(item) if _is_hermes_payload(item) else dict(item)
        for item in items_or_payloads
        if not _is_hermes_payload(item) or _is_digest_candidate(item)
    ]
    items.sort(key=lambda item: _number_or_zero(item.get("priority_score")), reverse=True)

    lines = ["ChainMind Watchlist Digest", ""]
    if not items:
        lines.append("No digest-ready candidates.")
        lines.append("")
        lines.append("Boundary: evidence-only research digest; no execution instructions.")
        return "\n".join(lines).rstrip() + "\n"

    for index, item in enumerate(items, start=1):
        lines.extend(
            [
                f"{index}. [{_value(item.get('grade'))}] {_value(item.get('symbol'))} / {_value(item.get('chain')).upper()}",
                (
                    f"Priority {_value(item.get('priority_score'))} | "
                    f"Risk {_value(item.get('risk_score'))} | "
                    f"Copyability {_value(item.get('copyability_score'))}"
                ),
                f"Reason: {_value(item.get('headline'))}",
            ]
        )
        top_evidence = list(item.get("top_evidence") or [])
        if top_evidence:
            lines.append(f"Evidence: {', '.join(str(value) for value in top_evidence[:3])}")
        lines.append("")

    lines.append("Boundary: evidence-only research digest; no execution instructions.")
    return "\n".join(lines).rstrip() + "\n"


def _positive_evidence(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in _all_evidence(analysis)
        if _severity(item) == "positive" and int(item.get("score_delta") or 0) > 0
    ][:3]


def _risk_evidence(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    risky_severities = {"critical", "high", "negative"}
    return [
        item
        for item in _all_evidence(analysis)
        if _severity(item) in risky_severities or int(item.get("score_delta") or 0) < 0
    ][:3]


def _all_evidence(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    for key in (
        "risk_evidence",
        "security_evidence",
        "entity_cluster_evidence",
        "copyability_evidence",
        "priority_evidence",
    ):
        evidence.extend(
            dict(item)
            for item in list(analysis.get(key) or [])
            if isinstance(item, dict)
        )
    return evidence


def _evidence_lines(items: list[dict[str, Any]], empty: str) -> list[str]:
    if not items:
        return [empty]
    return [
        (
            "- "
            f"{_value(item.get('rule_id'))}: "
            f"{_value(item.get('metric'))}={_value(item.get('value'))} "
            f"(severity={_value(item.get('severity'))})"
        )
        for item in items
    ]


def _watch_conditions(analysis: dict[str, Any]) -> list[str]:
    rule_ids = {str(item.get("rule_id")) for item in _all_evidence(analysis)}
    conditions = []
    if "copyability_negative_latest_net_buy" in rule_ids:
        conditions.append("Recheck short-window net flow before raising priority.")
    if "copyability_early_buyer_exit_ratio_high" in rule_ids:
        conditions.append("Recheck early-buyer retention before manual escalation.")
    if "copyability_shared_funder_risk" in rule_ids or "shared_funder_cluster" in rule_ids:
        conditions.append("Inspect shared-funder clustering before trusting wallet signals.")
    if "priority_gmgn_positive_signal_blocked_by_risk" in rule_ids:
        conditions.append("Treat GMGN positive wallet signals as blocked until risk decreases.")
    if not conditions:
        conditions.append("Monitor flow, holder behavior, and security warnings.")
    return conditions


def _is_digest_candidate(payload: dict[str, Any]) -> bool:
    return (
        payload.get("should_send") is True
        and str(payload.get("delivery_level") or "").lower() == "digest"
    )


def _is_hermes_payload(payload: dict[str, Any]) -> bool:
    return "summary" in payload and "delivery_level" in payload


def _digest_item(payload: dict[str, Any]) -> dict[str, Any]:
    summary = dict(payload.get("summary") or payload)
    return {
        "token_address": summary.get("token_address"),
        "symbol": summary.get("symbol") or "UNKNOWN",
        "chain": summary.get("chain") or "unknown",
        "grade": summary.get("grade") or payload.get("grade"),
        "action": summary.get("action") or payload.get("action"),
        "headline": summary.get("headline"),
        "risk_score": summary.get("risk_score"),
        "copyability_score": summary.get("copyability_score"),
        "priority_score": summary.get("priority_score"),
        "top_evidence": list(summary.get("top_evidence") or []),
        "telegram_markdown": payload.get("telegram_markdown"),
    }


def _number_or_zero(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0


def _severity(item: dict[str, Any]) -> str:
    return str(item.get("severity") or "").lower()


def _value(value: Any) -> str:
    if value is None or value == "":
        return "N/A"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)
