"""Shared score result object."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ScoreResult:
    score: int
    reasons: list[str]
    evidence: list[dict[str, Any]] = field(default_factory=list)
