"""Domain objects for token analysis snapshots."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TokenSnapshot:
    """Structured input for one token analysis run."""

    token: dict[str, Any]
    market: dict[str, Any] = field(default_factory=dict)
    flow_5m: list[dict[str, Any]] = field(default_factory=list)
    early_buyers: list[dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "TokenSnapshot":
        return cls(
            token=dict(payload.get("token", {})),
            market=dict(payload.get("market", {})),
            flow_5m=list(payload.get("flow_5m", [])),
            early_buyers=list(payload.get("early_buyers", [])),
        )

    @property
    def address(self) -> str:
        return str(self.token.get("address", "unknown"))

    @property
    def symbol(self) -> str:
        return str(self.token.get("symbol", "UNKNOWN"))

    @property
    def chain(self) -> str:
        return str(self.token.get("chain", "bnb"))


@dataclass(frozen=True)
class AnalysisResult:
    """Minimal result returned by the first runnable ChainMind workflow."""

    token_address: str
    symbol: str
    chain: str
    grade: str
    action: str
    risk_score: int
    opportunity_score: int
    reasons: list[str]

    def to_mapping(self) -> dict[str, Any]:
        return {
            "token_address": self.token_address,
            "symbol": self.symbol,
            "chain": self.chain,
            "grade": self.grade,
            "action": self.action,
            "risk_score": self.risk_score,
            "opportunity_score": self.opportunity_score,
            "reasons": list(self.reasons),
        }
