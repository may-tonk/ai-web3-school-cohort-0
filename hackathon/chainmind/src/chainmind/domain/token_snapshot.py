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
    funding: dict[str, Any] = field(default_factory=dict)
    security: dict[str, Any] = field(default_factory=dict)
    holders: dict[str, Any] = field(default_factory=dict)
    contract: dict[str, Any] = field(default_factory=dict)
    intelligence: dict[str, Any] = field(default_factory=dict)
    data_quality: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, payload: dict[str, Any]) -> "TokenSnapshot":
        return cls(
            token=dict(payload.get("token", {})),
            market=dict(payload.get("market", {})),
            flow_5m=list(payload.get("flow_5m", [])),
            early_buyers=list(payload.get("early_buyers", [])),
            funding=dict(payload.get("funding", {})),
            security=dict(payload.get("security", {})),
            holders=dict(payload.get("holders", {})),
            contract=dict(payload.get("contract", {})),
            intelligence=dict(payload.get("intelligence", {})),
            data_quality=dict(payload.get("data_quality", {})),
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
    data_quality: dict[str, Any]
    risk_evidence: list[dict[str, Any]]
    reasons: list[str]
    security_score: int = 0
    security_evidence: list[dict[str, Any]] = field(default_factory=list)
    entity_cluster_score: int = 0
    entity_cluster_evidence: list[dict[str, Any]] = field(default_factory=list)
    copyability_score: int = 0
    copyability_evidence: list[dict[str, Any]] = field(default_factory=list)
    priority_score: int = 0
    priority_evidence: list[dict[str, Any]] = field(default_factory=list)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "token_address": self.token_address,
            "symbol": self.symbol,
            "chain": self.chain,
            "grade": self.grade,
            "action": self.action,
            "risk_score": self.risk_score,
            "opportunity_score": self.opportunity_score,
            "security_score": self.security_score,
            "entity_cluster_score": self.entity_cluster_score,
            "copyability_score": self.copyability_score,
            "priority_score": self.priority_score,
            "data_quality": dict(self.data_quality),
            "risk_evidence": list(self.risk_evidence),
            "security_evidence": list(self.security_evidence),
            "entity_cluster_evidence": list(self.entity_cluster_evidence),
            "copyability_evidence": list(self.copyability_evidence),
            "priority_evidence": list(self.priority_evidence),
            "reasons": list(self.reasons),
        }
