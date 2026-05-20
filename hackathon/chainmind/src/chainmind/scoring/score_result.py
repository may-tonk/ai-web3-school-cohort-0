"""Shared score result object."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreResult:
    score: int
    reasons: list[str]
