"""AI explanation prompt packets for token reports.

This module prepares prompts only. It does not call an AI provider.
"""

from __future__ import annotations

from typing import Any

from chainmind.reports.token_report import generate_token_report


SYSTEM_PROMPT = """You are ChainMind's evidence explainer.

Explain only the structured evidence provided by ChainMind.
Do not invent token facts, wallet behavior, liquidity values, or security
properties. Do not replace ChainMind's rule engine. Do not provide execution
instructions, position sizing, targets, or stop instructions.

Return a concise research explanation with these sections:
- Conclusion
- Opportunity Sources
- Main Risks
- Copyability
- Follow-up Watch Conditions
- Uncertainty
"""


def generate_ai_explanation_prompt(
    *,
    snapshot: dict[str, Any],
    analysis: dict[str, Any],
    report_markdown: str | None = None,
) -> dict[str, Any]:
    """Build an AI-ready prompt packet from deterministic report inputs."""

    snapshot = dict(snapshot or {})
    analysis = dict(analysis or {})
    report = report_markdown or generate_token_report(snapshot=snapshot, analysis=analysis)
    context = _structured_context(snapshot=snapshot, analysis=analysis)

    return {
        "version": "phase5c-ai-explanation-prompt-v1",
        "purpose": "explain_structured_chainmind_evidence",
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": _user_prompt(context=context, report_markdown=report),
        "structured_context": context,
        "report_markdown": report,
    }


def _structured_context(
    *,
    snapshot: dict[str, Any],
    analysis: dict[str, Any],
) -> dict[str, Any]:
    token = dict(snapshot.get("token") or {})
    market = dict(snapshot.get("market") or {})
    token_profile = dict(snapshot.get("token_profile") or {})
    intelligence = dict(snapshot.get("intelligence") or {})
    data_quality = dict(analysis.get("data_quality") or snapshot.get("data_quality") or {})

    return {
        "token": {
            "address": analysis.get("token_address") or token.get("address"),
            "symbol": market.get("base_token_symbol") or analysis.get("symbol") or token.get("symbol"),
            "chain": analysis.get("chain") or token.get("chain"),
        },
        "token_profile": {
            "type": token_profile.get("type") or "meme_candidate",
            "source": token_profile.get("source"),
            "reason": token_profile.get("reason"),
        },
        "decision": {
            "grade": analysis.get("grade"),
            "action": analysis.get("action"),
        },
        "scores": {
            "risk": analysis.get("risk_score"),
            "security": analysis.get("security_score"),
            "entity_cluster": analysis.get("entity_cluster_score"),
            "opportunity": analysis.get("opportunity_score"),
            "copyability": analysis.get("copyability_score"),
            "priority": analysis.get("priority_score"),
        },
        "evidence": {
            "risk": _rule_ids(analysis.get("risk_evidence")),
            "security": _rule_ids(analysis.get("security_evidence")),
            "entity_cluster": _rule_ids(analysis.get("entity_cluster_evidence")),
            "copyability": _rule_ids(analysis.get("copyability_evidence")),
            "priority": _rule_ids(analysis.get("priority_evidence")),
        },
        "wallet_intelligence": {
            "gmgn": dict(intelligence.get("gmgn") or {}),
        },
        "data_quality": {
            "level": data_quality.get("level"),
            "confidence": data_quality.get("confidence"),
            "warnings": list(data_quality.get("warnings") or []),
            "api_warnings": list(dict(snapshot.get("data_quality") or {}).get("api_warnings") or []),
        },
    }


def _user_prompt(*, context: dict[str, Any], report_markdown: str) -> str:
    token = dict(context.get("token") or {})
    profile = dict(context.get("token_profile") or {})
    return (
        "Explain this ChainMind token analysis for a human research workflow.\n\n"
        f"Token: {token.get('symbol') or 'UNKNOWN'} / {token.get('chain') or 'unknown'}\n"
        f"Address: {token.get('address') or 'unknown'}\n"
        f"Token profile: {profile.get('type') or 'meme_candidate'}\n\n"
        "Use the deterministic report below as the only factual source.\n\n"
        "```markdown\n"
        f"{report_markdown.rstrip()}\n"
        "```"
    )


def _rule_ids(evidence: Any) -> list[str]:
    if not isinstance(evidence, list):
        return []
    return [
        str(item.get("rule_id"))
        for item in evidence
        if isinstance(item, dict) and item.get("rule_id")
    ]
