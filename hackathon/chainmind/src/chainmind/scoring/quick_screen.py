"""Low-latency quick screen rules for newly discovered tokens."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


BLOCK_LIQUIDITY_USD = 5_000
WATCH_LIQUIDITY_USD = 20_000
WATCH_VOLUME_24H_USD = 5_000
BLOCK_TAX = 0.20
WATCH_TAX = 0.08
WATCH_HOLDER_COUNT = 300


@dataclass(frozen=True)
class QuickScreenResult:
    decision: str
    reasons: list[str]
    evidence: list[dict[str, Any]] = field(default_factory=list)

    def to_mapping(self) -> dict[str, Any]:
        return {
            "decision": self.decision,
            "reasons": list(self.reasons),
            "evidence": list(self.evidence),
        }


def quick_screen_decision(snapshot: dict[str, Any]) -> QuickScreenResult:
    market = dict(snapshot.get("market") or {})
    security = dict(snapshot.get("security") or {})
    contract = dict(snapshot.get("contract") or {})
    holders = dict(snapshot.get("holders") or {})

    block: list[dict[str, Any]] = []
    watch: list[dict[str, Any]] = []

    _append_flag_block(block, security, "is_honeypot", "honeypot")
    _append_flag_block(block, security, "cannot_sell_all", "cannot_sell_all")
    _append_flag_block(block, security, "is_blacklisted", "blacklist")
    _append_flag_block(block, contract, "hidden_owner", "hidden_owner")
    _append_flag_block(block, contract, "is_mintable", "mintable")

    liquidity = _float(market.get("liquidity_usd"))
    if liquidity is not None:
        if liquidity < BLOCK_LIQUIDITY_USD:
            block.append(
                _evidence(
                    "quick_low_liquidity_block",
                    "liquidity_usd",
                    liquidity,
                    BLOCK_LIQUIDITY_USD,
                    "block",
                )
            )
        elif liquidity < WATCH_LIQUIDITY_USD:
            watch.append(
                _evidence(
                    "quick_low_liquidity_watch",
                    "liquidity_usd",
                    liquidity,
                    WATCH_LIQUIDITY_USD,
                    "watch",
                )
            )

    volume_24h = _float(market.get("volume_24h_usd"))
    if volume_24h is not None and volume_24h < WATCH_VOLUME_24H_USD:
        watch.append(
            _evidence(
                "quick_low_volume_watch",
                "volume_24h_usd",
                volume_24h,
                WATCH_VOLUME_24H_USD,
                "watch",
            )
        )

    for field_name in ("buy_tax", "sell_tax"):
        tax = _float(security.get(field_name))
        if tax is None:
            continue
        if tax >= BLOCK_TAX:
            block.append(
                _evidence(
                    f"quick_high_{field_name}_block",
                    field_name,
                    round(tax, 4),
                    BLOCK_TAX,
                    "block",
                )
            )
        elif tax >= WATCH_TAX:
            watch.append(
                _evidence(
                    f"quick_high_{field_name}_watch",
                    field_name,
                    round(tax, 4),
                    WATCH_TAX,
                    "watch",
                )
            )

    owner_renounced = contract.get("owner_renounced")
    if owner_renounced is not True:
        watch.append(
            _evidence(
                "quick_owner_not_renounced_watch",
                "owner_renounced",
                owner_renounced,
                True,
                "watch",
            )
        )

    holder_count = _float(holders.get("holder_count"))
    if holder_count is not None and holder_count < WATCH_HOLDER_COUNT:
        watch.append(
            _evidence(
                "quick_low_holder_count_watch",
                "holder_count",
                int(holder_count),
                WATCH_HOLDER_COUNT,
                "watch",
            )
        )

    if block:
        return QuickScreenResult("BLOCK", [_reason(item) for item in block], block)
    if watch:
        return QuickScreenResult("WATCH", [_reason(item) for item in watch], watch)
    return QuickScreenResult(
        "PASS",
        ["No quick-screen block/watch rules triggered."],
        [],
    )


def _append_flag_block(
    evidence: list[dict[str, Any]],
    payload: dict[str, Any],
    field_name: str,
    rule_suffix: str,
) -> None:
    if payload.get(field_name) is True:
        evidence.append(
            _evidence(
                f"quick_{rule_suffix}_block",
                field_name,
                True,
                False,
                "block",
            )
        )


def _evidence(
    rule_id: str,
    metric: str,
    value: Any,
    threshold: Any,
    level: str,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "level": level,
        "metric": metric,
        "value": value,
        "threshold": threshold,
    }


def _reason(evidence: dict[str, Any]) -> str:
    return (
        f"{evidence['rule_id']}: "
        f"{evidence['metric']}={evidence['value']} "
        f"threshold={evidence['threshold']}"
    )


def _float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
