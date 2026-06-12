"""Hermes-facing payload builder."""

from __future__ import annotations

from typing import Any

from chainmind.alerts.alert_policy import decide_alert_delivery
from chainmind.alerts.digest_builder import build_telegram_markdown
from chainmind.reports import generate_ai_explanation_prompt, generate_token_report


HERMES_PAYLOAD_VERSION = "phase6a-hermes-payload-v1"


def build_hermes_payload(
    *,
    snapshot: dict[str, Any],
    analysis: dict[str, Any],
    report_markdown: str | None = None,
    ai_prompt: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a stable JSON payload for Hermes to consume."""

    snapshot = dict(snapshot or {})
    analysis = dict(analysis or {})
    report = report_markdown or generate_token_report(snapshot=snapshot, analysis=analysis)
    prompt = ai_prompt or generate_ai_explanation_prompt(
        snapshot=snapshot,
        analysis=analysis,
        report_markdown=report,
    )
    decision = decide_alert_delivery(analysis)

    return {
        "version": HERMES_PAYLOAD_VERSION,
        "channel": "hermes",
        "should_send": decision.should_send,
        "delivery_level": decision.delivery_level,
        "delivery_reason": decision.reason,
        "grade": analysis.get("grade"),
        "action": analysis.get("action"),
        "summary": _summary(snapshot=snapshot, analysis=analysis),
        "telegram_markdown": build_telegram_markdown(
            snapshot=snapshot,
            analysis=analysis,
            decision=decision,
        ),
        "report_markdown": report,
        "ai_prompt": prompt,
        "snapshot": snapshot,
        "analysis": analysis,
    }


def _summary(*, snapshot: dict[str, Any], analysis: dict[str, Any]) -> dict[str, Any]:
    token = dict(snapshot.get("token") or {})
    market = dict(snapshot.get("market") or {})
    profile = dict(snapshot.get("token_profile") or {})
    symbol = (
        market.get("base_token_symbol")
        or analysis.get("symbol")
        or token.get("symbol")
        or "UNKNOWN"
    )
    grade = str(analysis.get("grade") or "N/A")
    action = str(analysis.get("action") or "N/A")
    return {
        "token_address": analysis.get("token_address") or token.get("address"),
        "symbol": symbol,
        "chain": analysis.get("chain") or token.get("chain"),
        "token_profile": profile.get("type") or "meme_candidate",
        "grade": grade,
        "action": action,
        "headline": _headline(grade=grade, action=action),
        "risk_score": analysis.get("risk_score"),
        "security_score": analysis.get("security_score"),
        "entity_cluster_score": analysis.get("entity_cluster_score"),
        "opportunity_score": analysis.get("opportunity_score"),
        "copyability_score": analysis.get("copyability_score"),
        "priority_score": analysis.get("priority_score"),
        "data_quality": dict(analysis.get("data_quality") or {}),
        "top_evidence": _top_evidence(analysis),
    }


def _headline(*, grade: str, action: str) -> str:
    if grade == "A" or action == "manual_review":
        return "High-priority manual research candidate."
    if grade == "B" or action == "watchlist":
        return "Watchlist candidate for continued observation."
    if grade == "D" or action == "filter":
        return "Filtered by default due to risk evidence."
    return "Store for calibration and later review."


def _top_evidence(analysis: dict[str, Any]) -> list[str]:
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

    ranked = sorted(
        evidence,
        key=lambda item: abs(int(item.get("score_delta") or 0)),
        reverse=True,
    )
    return [
        str(item.get("rule_id"))
        for item in ranked[:5]
        if item.get("rule_id")
    ]
