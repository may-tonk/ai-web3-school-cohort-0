"""Alert delivery policy for analyzed token results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AlertDecision:
    """Hermes-facing delivery decision for one analysis result."""

    should_send: bool
    delivery_level: str
    reason: str

    def to_mapping(self) -> dict[str, Any]:
        return {
            "should_send": self.should_send,
            "delivery_level": self.delivery_level,
            "reason": self.reason,
        }


def decide_alert_delivery(analysis: dict[str, Any]) -> AlertDecision:
    """Map ChainMind grade/action into a first-pass Hermes delivery policy."""

    grade = str(analysis.get("grade") or "").strip().upper()
    action = str(analysis.get("action") or "").strip().lower()

    if grade == "A" or action == "manual_review":
        return AlertDecision(
            should_send=True,
            delivery_level="immediate",
            reason="A-grade or manual-review result should be sent immediately.",
        )
    if grade == "B" or action == "watchlist":
        return AlertDecision(
            should_send=True,
            delivery_level="digest",
            reason="B-grade or watchlist result should be included in a digest.",
        )
    if grade == "D" or action == "filter":
        return AlertDecision(
            should_send=False,
            delivery_level="filter",
            reason="D-grade or filter result should not be sent.",
        )
    return AlertDecision(
        should_send=False,
        delivery_level="store_only",
        reason="Result should be stored for review but not actively sent.",
    )
