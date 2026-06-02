"""Data quality checks for token analysis inputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from chainmind.domain import TokenSnapshot


@dataclass(frozen=True)
class DataQualityResult:
    level: str
    confidence: str
    missing_fields: list[str]
    warnings: list[str]

    def to_mapping(self) -> dict[str, Any]:
        return {
            "level": self.level,
            "confidence": self.confidence,
            "missing_fields": list(self.missing_fields),
            "warnings": list(self.warnings),
        }


def evaluate_data_quality(snapshot: TokenSnapshot) -> DataQualityResult:
    missing_fields: list[str] = []
    warnings: list[str] = _input_data_quality_warnings(snapshot.data_quality)

    if not snapshot.token.get("address"):
        missing_fields.append("token.address")
        warnings.append("Missing token address; analysis cannot be tied to a contract.")

    if not snapshot.market:
        missing_fields.append("market")
        warnings.append("Missing market data; liquidity and volume risks cannot be evaluated.")

    if not snapshot.flow_5m:
        missing_fields.append("flow_5m")
        warnings.append("Missing five-minute flow data; buy/sell quality cannot be evaluated.")
    else:
        warnings.extend(_flow_warnings(snapshot.flow_5m))

    if not snapshot.early_buyers:
        missing_fields.append("early_buyers")
        warnings.append("Missing early buyer data; early exit risk cannot be evaluated.")
    elif len(snapshot.early_buyers) < 5:
        warnings.append(
            "Early buyer sample has fewer than 5 records; early exit conclusions have lower confidence."
        )
        warnings.extend(_early_buyer_warnings(snapshot.early_buyers))
    else:
        warnings.extend(_early_buyer_warnings(snapshot.early_buyers))

    if not snapshot.funding:
        missing_fields.append("funding")
        warnings.append("Missing funding data; same-funder risk cannot be evaluated.")
    else:
        warnings.extend(_funding_warnings(snapshot.funding))

    if not snapshot.security:
        missing_fields.append("security")
        warnings.append("Missing security data; contract and LP risks cannot be evaluated.")
    else:
        warnings.extend(_security_warnings(snapshot.security))

    if not snapshot.holders:
        warnings.append("Missing holder distribution data; holder concentration cannot be evaluated.")

    if not snapshot.contract:
        warnings.append("Missing contract metadata; ownership and proxy risks cannot be fully evaluated.")

    level = _level_from_missing_fields(missing_fields)
    confidence = _confidence_from_level(level)

    return DataQualityResult(
        level=level,
        confidence=confidence,
        missing_fields=missing_fields,
        warnings=warnings,
    )


def _input_data_quality_warnings(data_quality: dict[str, Any]) -> list[str]:
    warnings = data_quality.get("warnings") or []
    api_warnings = data_quality.get("api_warnings") or []
    return [str(warning) for warning in [*warnings, *api_warnings]]


def _flow_warnings(flow_5m: list[dict[str, Any]]) -> list[str]:
    missing_usd_rows = [
        row
        for row in flow_5m
        if row.get("net_buy_usd") is None
        or row.get("buy_volume_usd") is None
        or row.get("sell_volume_usd") is None
    ]
    if len(missing_usd_rows) / max(len(flow_5m), 1) > 0.5:
        return [
            "More than half of five-minute flow rows are missing USD volume fields; net-buy signals have lower confidence."
        ]
    return []


def _early_buyer_warnings(early_buyers: list[dict[str, Any]]) -> list[str]:
    negative_balance_rows = [
        buyer
        for buyer in early_buyers
        if _to_float(buyer.get("current_balance")) is not None
        and (_to_float(buyer.get("current_balance")) or 0) < 0
    ]
    if negative_balance_rows:
        return [
            "Some early buyer current_balance values are negative; transfer-derived token balances may be unreliable for this token."
        ]
    return []


def _funding_warnings(funding: dict[str, Any]) -> list[str]:
    shared_funders = funding.get("shared_funders") or []
    infrastructure_funders = [
        funder
        for funder in shared_funders
        if bool(funder.get("is_infrastructure"))
    ]
    if infrastructure_funders:
        return [
            "Some shared funders are labeled as infrastructure; they should not be treated as same-entity evidence."
        ]
    return []


def _security_warnings(security: dict[str, Any]) -> list[str]:
    warnings = [str(warning) for warning in security.get("warnings") or []]
    if security.get("source") == "not_connected":
        warnings.append("Security API is not connected; contract and LP risk checks are limited.")
    return warnings


def _level_from_missing_fields(missing_fields: list[str]) -> str:
    critical_missing = {"token.address", "flow_5m", "early_buyers"}
    critical_count = len(critical_missing.intersection(missing_fields))

    if "token.address" in missing_fields or critical_count >= 2:
        return "poor"
    if missing_fields:
        return "partial"
    return "good"


def _confidence_from_level(level: str) -> str:
    if level == "good":
        return "high"
    if level == "partial":
        return "medium"
    return "low"


def _to_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
