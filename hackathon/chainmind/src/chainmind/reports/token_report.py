"""Deterministic Markdown reports for token analysis results."""

from __future__ import annotations

import json
from typing import Any


REVIEW_GUIDANCE = {
    "manual_review": "Escalate to manual research review. Do not automate execution.",
    "watchlist": "Place on the observation list and wait for stronger follow-up evidence.",
    "store_only": "Store the result for calibration and review only when new evidence appears.",
    "filter": "Filter by default unless a human reviewer has extra off-chain context.",
}


def generate_token_report(snapshot: dict[str, Any], analysis: dict[str, Any]) -> str:
    """Render a deterministic Markdown report from structured analysis output."""

    snapshot = dict(snapshot or {})
    analysis = dict(analysis or {})
    market = dict(snapshot.get("market") or {})
    data_quality = dict(analysis.get("data_quality") or snapshot.get("data_quality") or {})
    gmgn = dict(dict(snapshot.get("intelligence") or {}).get("gmgn") or {})

    sections = [
        "# ChainMind Token Analysis Report",
        _summary_section(snapshot, analysis, market, data_quality),
        _decision_section(analysis),
        _profile_section(snapshot),
        _market_section(market),
        _opportunity_section(analysis),
        _risk_section(analysis),
        _copyability_section(analysis),
        _wallet_intelligence_section(gmgn),
        _data_quality_section(snapshot, data_quality),
        _follow_up_section(analysis),
        _appendix_section(analysis),
    ]
    return "\n\n".join(section for section in sections if section).rstrip() + "\n"


def _summary_section(
    snapshot: dict[str, Any],
    analysis: dict[str, Any],
    market: dict[str, Any],
    data_quality: dict[str, Any],
) -> str:
    token = dict(snapshot.get("token") or {})
    rows = [
        ("Token", analysis.get("token_address") or token.get("address")),
        ("Symbol", market.get("base_token_symbol") or analysis.get("symbol")),
        ("Chain", analysis.get("chain") or token.get("chain")),
        ("Grade", analysis.get("grade")),
        ("Action", analysis.get("action")),
        ("Risk Score", analysis.get("risk_score")),
        ("Security Score", analysis.get("security_score")),
        ("Entity Cluster Score", analysis.get("entity_cluster_score")),
        ("Opportunity Score", analysis.get("opportunity_score")),
        ("Copyability Score", analysis.get("copyability_score")),
        ("Priority Score", analysis.get("priority_score")),
        ("Data Quality", _data_quality_label(data_quality)),
    ]
    return "## 1. Summary\n" + _bullet_rows(rows)


def _decision_section(analysis: dict[str, Any]) -> str:
    action = str(analysis.get("action") or "").strip()
    grade = str(analysis.get("grade") or "N/A")
    guidance = REVIEW_GUIDANCE.get(
        action,
        "Use the grade and evidence for research triage only.",
    )
    return (
        "## 2. Decision\n"
        f"- Grade: {_value(grade)}\n"
        f"- Action: {_value(action)}\n"
        f"- Review guidance: {guidance}\n"
        "- Boundary: ChainMind reports explain structured evidence and do not "
        "provide execution instructions."
    )


def _profile_section(snapshot: dict[str, Any]) -> str:
    profile = dict(snapshot.get("token_profile") or {})
    profile_type = str(profile.get("type") or "meme_candidate")
    lines = [
        "## 3. Interpretation Context",
        f"- Token Profile: {_value(profile_type)}",
        f"- Profile Source: {_value(profile.get('source'))}",
        f"- Profile Reason: {_value(profile.get('reason'))}",
    ]
    if profile_type != "meme_candidate":
        lines.append(
            "- Boundary: This token should not be interpreted as a BNB meme "
            "candidate without additional manual context."
        )
    else:
        lines.append(
            "- Boundary: This report uses the BNB meme-token research lens."
        )
    return "\n".join(lines)


def _market_section(market: dict[str, Any]) -> str:
    rows = [
        ("Pair", market.get("pair_address")),
        ("DEX", market.get("dex_id")),
        ("Price USD", _money(market.get("price_usd"))),
        ("Liquidity USD", _money(market.get("liquidity_usd"))),
        ("FDV USD", _money(market.get("fdv_usd"))),
        ("24h Volume USD", _money(market.get("volume_24h_usd"))),
        ("24h Price Change", _percent(market.get("price_change_24h_pct"), already_percent=True)),
    ]
    return "## 4. Market Snapshot\n" + _bullet_rows(rows)


def _opportunity_section(analysis: dict[str, Any]) -> str:
    positive = _positive_evidence(analysis)
    lines = ["## 5. Opportunity Signals"]
    lines.append(
        f"- Opportunity Score: {_value(analysis.get('opportunity_score'))}"
    )
    lines.append(
        f"- Priority Score: {_value(analysis.get('priority_score'))}"
    )
    lines.extend(_evidence_bullets(positive, empty="- No positive evidence was recorded."))
    return "\n".join(lines)


def _risk_section(analysis: dict[str, Any]) -> str:
    risk_items = _risk_evidence(analysis)
    lines = ["## 6. Main Risks"]
    lines.extend(_evidence_bullets(risk_items, empty="- No high-severity risk evidence was recorded."))
    return "\n".join(lines)


def _copyability_section(analysis: dict[str, Any]) -> str:
    evidence = list(analysis.get("copyability_evidence") or [])
    lines = [
        "## 7. Copyability",
        f"- Copyability Score: {_value(analysis.get('copyability_score'))}",
        "- Interpretation: Copyability v0 estimates whether an observation or "
        "follow window remains practical. It is not a proven wallet-alpha score.",
    ]
    lines.extend(_evidence_bullets(evidence, empty="- No copyability evidence was recorded."))
    return "\n".join(lines)


def _wallet_intelligence_section(gmgn: dict[str, Any]) -> str:
    rows = [
        ("Source", gmgn.get("source")),
        ("Wallet Signal", gmgn.get("has_wallet_signal")),
        ("Risk Wallet Signal", gmgn.get("has_risk_wallet_signal")),
        ("Top Holders", gmgn.get("top_holder_count")),
        ("Top Traders", gmgn.get("top_trader_count")),
        ("Smart Wallets", gmgn.get("smart_wallet_count")),
        ("Snipers", gmgn.get("sniper_count")),
        ("Insiders", gmgn.get("insider_count")),
        ("Bundled Wallets", gmgn.get("bundled_wallet_count")),
    ]
    return "## 8. Wallet Intelligence\n" + _bullet_rows(rows)


def _data_quality_section(snapshot: dict[str, Any], data_quality: dict[str, Any]) -> str:
    api_warnings = list(dict(snapshot.get("data_quality") or {}).get("api_warnings") or [])
    warnings = list(data_quality.get("warnings") or [])
    lines = [
        "## 9. Data Quality And Uncertainty",
        f"- Level: {_value(data_quality.get('level'))}",
        f"- Confidence: {_value(data_quality.get('confidence'))}",
    ]
    for warning in [*warnings, *api_warnings]:
        lines.append(f"- Warning: {_value(warning)}")
    if len(lines) == 3:
        lines.append("- No data-quality warning was recorded.")
    return "\n".join(lines)


def _follow_up_section(analysis: dict[str, Any]) -> str:
    conditions = _follow_up_conditions(analysis)
    lines = ["## 10. Follow-up Watch Conditions"]
    lines.extend(f"- {condition}" for condition in conditions)
    return "\n".join(lines)


def _appendix_section(analysis: dict[str, Any]) -> str:
    evidence = _all_evidence(analysis)
    lines = ["## 11. Evidence Appendix"]
    if not evidence:
        lines.append("No evidence entries were recorded.")
        return "\n".join(lines)

    lines.append("| Rule | Metric | Value | Threshold | Severity | Delta |")
    lines.append("|---|---|---:|---:|---|---:|")
    for item in evidence:
        lines.append(
            "| "
            f"{_cell(item.get('rule_id'))} | "
            f"{_cell(item.get('metric'))} | "
            f"{_cell(item.get('value'))} | "
            f"{_cell(item.get('threshold'))} | "
            f"{_cell(item.get('severity'))} | "
            f"{_cell(item.get('score_delta'))} |"
        )
    return "\n".join(lines)


def _positive_evidence(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        item
        for item in _all_evidence(analysis)
        if _severity(item) == "positive" and int(item.get("score_delta") or 0) > 0
    ]


def _risk_evidence(analysis: dict[str, Any]) -> list[dict[str, Any]]:
    risky_severities = {"critical", "high", "negative"}
    return [
        item
        for item in _all_evidence(analysis)
        if _severity(item) in risky_severities or int(item.get("score_delta") or 0) < 0
    ]


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


def _follow_up_conditions(analysis: dict[str, Any]) -> list[str]:
    rule_ids = {str(item.get("rule_id")) for item in _all_evidence(analysis)}
    conditions = []
    if "copyability_negative_latest_net_buy" in rule_ids:
        conditions.append("Recheck short-window net flow before raising priority.")
    if "copyability_repeated_negative_net_buy" in rule_ids:
        conditions.append("Watch whether repeated negative net flow continues.")
    if "copyability_early_buyer_exit_ratio_high" in rule_ids:
        conditions.append("Recheck early-buyer retention before manual escalation.")
    if "copyability_shared_funder_risk" in rule_ids or "shared_funder_cluster" in rule_ids:
        conditions.append("Inspect shared-funder clustering before trusting wallet signals.")
    if "priority_gmgn_positive_signal_blocked_by_risk" in rule_ids:
        conditions.append("Treat GMGN positive wallet signals as blocked until risk decreases.")
    if not conditions:
        conditions.append("Keep monitoring flow, holder behavior, and security warnings.")
    return conditions


def _evidence_bullets(items: list[dict[str, Any]], *, empty: str) -> list[str]:
    if not items:
        return [empty]
    return [
        "- "
        f"{_value(item.get('rule_id'))}: "
        f"{_value(item.get('metric'))}={_value(item.get('value'))} "
        f"(severity={_value(item.get('severity'))}, "
        f"score_delta={_value(item.get('score_delta'))})"
        for item in items
    ]


def _bullet_rows(rows: list[tuple[str, Any]]) -> str:
    return "\n".join(f"- {label}: {_value(value)}" for label, value in rows)


def _data_quality_label(data_quality: dict[str, Any]) -> str:
    level = data_quality.get("level")
    confidence = data_quality.get("confidence")
    if level and confidence:
        return f"{level} ({confidence})"
    return _value(level or confidence)


def _money(value: Any) -> str:
    number = _float(value)
    if number is None:
        return "N/A"
    return f"{number:,.6f}" if abs(number) < 1 else f"{number:,.2f}"


def _percent(value: Any, *, already_percent: bool = False) -> str:
    number = _float(value)
    if number is None:
        return "N/A"
    if not already_percent:
        number *= 100
    return f"{number:.2f}%"


def _float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _severity(item: dict[str, Any]) -> str:
    return str(item.get("severity") or "").lower()


def _cell(value: Any) -> str:
    return _value(value).replace("|", "\\|").replace("\n", " ")


def _value(value: Any) -> str:
    if value is None or value == "":
        return "N/A"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.6f}".rstrip("0").rstrip(".")
    if isinstance(value, int):
        return str(value)
    if isinstance(value, dict | list):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)
