"""File-backed cooldown helpers for Hermes alert payloads."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


COOLDOWN_STATE_VERSION = "phase6b-cooldown-state-v1"
DEFAULT_IMMEDIATE_COOLDOWN_SECONDS = 60 * 60
DEFAULT_DIGEST_COOLDOWN_SECONDS = 8 * 60 * 60


def empty_cooldown_state() -> dict[str, Any]:
    return {
        "version": COOLDOWN_STATE_VERSION,
        "items": {},
    }


def load_cooldown_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return empty_cooldown_state()

    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        return empty_cooldown_state()

    state = empty_cooldown_state()
    state["version"] = str(payload.get("version") or COOLDOWN_STATE_VERSION)
    state["items"] = dict(payload.get("items") or {})
    return state


def save_cooldown_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(_normalize_state(state), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def apply_cooldown(
    payload: dict[str, Any],
    state: dict[str, Any],
    *,
    now: datetime | None = None,
    update_state: bool = True,
    immediate_cooldown_seconds: int = DEFAULT_IMMEDIATE_COOLDOWN_SECONDS,
    digest_cooldown_seconds: int = DEFAULT_DIGEST_COOLDOWN_SECONDS,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply cooldown state to a Hermes payload and return updated copies."""

    current_time = _utc(now)
    result = dict(payload or {})
    updated_state = _normalize_state(state)
    items = updated_state.setdefault("items", {})

    if result.get("should_send") is not True:
        result["cooldown"] = {
            "suppressed": False,
            "reason": "Payload is not sendable, so cooldown was not applied.",
            "checked_at": _format_time(current_time),
        }
        return result, updated_state

    delivery_level = str(result.get("delivery_level") or "").strip().lower()
    cooldown_seconds = _cooldown_seconds(
        delivery_level=delivery_level,
        immediate_cooldown_seconds=immediate_cooldown_seconds,
        digest_cooldown_seconds=digest_cooldown_seconds,
    )
    if cooldown_seconds is None:
        result["cooldown"] = {
            "suppressed": False,
            "reason": f"No cooldown policy is configured for {delivery_level or 'unknown'}.",
            "checked_at": _format_time(current_time),
        }
        return result, updated_state

    key = _cooldown_key(result, delivery_level)
    existing = dict(items.get(key) or {})
    next_allowed_at = _parse_time(existing.get("next_allowed_at"))
    if next_allowed_at is not None and next_allowed_at > current_time:
        result["should_send"] = False
        result["delivery_level"] = "suppressed"
        result["cooldown"] = {
            "suppressed": True,
            "reason": f"Token is still in {delivery_level} cooldown.",
            "key": key,
            "original_delivery_level": delivery_level,
            "last_sent_at": existing.get("last_sent_at"),
            "next_allowed_at": _format_time(next_allowed_at),
            "checked_at": _format_time(current_time),
        }
        return result, updated_state

    allowed_next_time = current_time + timedelta(seconds=cooldown_seconds)
    result["cooldown"] = {
        "suppressed": False,
        "reason": "No cooldown hit.",
        "key": key,
        "next_allowed_at": _format_time(allowed_next_time),
        "checked_at": _format_time(current_time),
    }
    if update_state:
        items[key] = {
            "last_sent_at": _format_time(current_time),
            "next_allowed_at": _format_time(allowed_next_time),
            "delivery_level": delivery_level,
        }
    return result, updated_state


def _normalize_state(state: dict[str, Any] | None) -> dict[str, Any]:
    payload = dict(state or {})
    return {
        "version": str(payload.get("version") or COOLDOWN_STATE_VERSION),
        "items": dict(payload.get("items") or {}),
    }


def _cooldown_seconds(
    *,
    delivery_level: str,
    immediate_cooldown_seconds: int,
    digest_cooldown_seconds: int,
) -> int | None:
    if delivery_level == "immediate":
        return immediate_cooldown_seconds
    if delivery_level == "digest":
        return digest_cooldown_seconds
    return None


def _cooldown_key(payload: dict[str, Any], delivery_level: str) -> str:
    summary = dict(payload.get("summary") or {})
    snapshot = dict(payload.get("snapshot") or {})
    token = dict(snapshot.get("token") or {})
    chain = (
        summary.get("chain")
        or dict(payload.get("analysis") or {}).get("chain")
        or token.get("chain")
        or "unknown"
    )
    address = (
        summary.get("token_address")
        or dict(payload.get("analysis") or {}).get("token_address")
        or token.get("address")
        or "unknown"
    )
    return f"{str(chain).lower()}:{str(address).lower()}:{delivery_level}"


def _utc(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(UTC)
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _format_time(value: datetime) -> str:
    return _utc(value).isoformat().replace("+00:00", "Z")


def _parse_time(value: Any) -> datetime | None:
    if not value:
        return None
    text = str(value).strip().replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text).astimezone(UTC)
    except ValueError:
        return None
