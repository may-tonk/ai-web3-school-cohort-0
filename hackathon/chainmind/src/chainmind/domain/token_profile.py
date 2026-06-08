"""Lightweight token profile inference for report interpretation boundaries."""

from __future__ import annotations

from typing import Any


PROFILE_MEME_CANDIDATE = "meme_candidate"
PROFILE_MAINSTREAM_CONTROL = "mainstream_control"
PROFILE_INFRASTRUCTURE = "infrastructure"

KNOWN_MAINSTREAM_CONTROL_ADDRESSES = {
    "0x55d398326f99059ff775485246999027b3197955": "USDT stablecoin control",
    "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d": "USDC stablecoin control",
    "0xe9e7cea3dedca5984780bafc599bd69add087d56": "BUSD stablecoin control",
}

KNOWN_INFRASTRUCTURE_ADDRESSES = {
    "0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c": "WBNB wrapped native asset",
    "0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82": "CAKE ecosystem token",
}

MAINSTREAM_SYMBOLS = {"USDT", "USDC", "BUSD", "DAI", "FDUSD", "TUSD"}
INFRASTRUCTURE_SYMBOLS = {"WBNB", "CAKE"}


def infer_token_profile(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Infer a conservative interpretation profile from known token context."""

    explicit = _explicit_profile(snapshot.get("token_profile"))
    if explicit is not None:
        return explicit

    token = dict(snapshot.get("token") or {})
    market = dict(snapshot.get("market") or {})
    sample_meta = dict(snapshot.get("sample_meta") or {})

    sample_type = str(sample_meta.get("sample_type") or "").strip().lower()
    if sample_type in {"mainstream", "mainstream_control"}:
        return _profile(
            PROFILE_MAINSTREAM_CONTROL,
            source="sample_meta",
            reason="Sample metadata marks this token as a mainstream control.",
        )

    address = str(token.get("address") or "").strip().lower()
    if address in KNOWN_MAINSTREAM_CONTROL_ADDRESSES:
        return _profile(
            PROFILE_MAINSTREAM_CONTROL,
            source="known_address",
            reason=KNOWN_MAINSTREAM_CONTROL_ADDRESSES[address],
        )
    if address in KNOWN_INFRASTRUCTURE_ADDRESSES:
        return _profile(
            PROFILE_INFRASTRUCTURE,
            source="known_address",
            reason=KNOWN_INFRASTRUCTURE_ADDRESSES[address],
        )

    symbol = _symbol(token, market)
    if symbol in MAINSTREAM_SYMBOLS:
        return _profile(
            PROFILE_MAINSTREAM_CONTROL,
            source="symbol_heuristic",
            reason=f"Symbol {symbol} is a known stablecoin/control symbol.",
        )
    if symbol in INFRASTRUCTURE_SYMBOLS:
        return _profile(
            PROFILE_INFRASTRUCTURE,
            source="symbol_heuristic",
            reason=f"Symbol {symbol} is a known infrastructure/ecosystem symbol.",
        )

    return _profile(
        PROFILE_MEME_CANDIDATE,
        source="default",
        reason="No mainstream or infrastructure context was detected.",
    )


def _explicit_profile(value: Any) -> dict[str, Any] | None:
    if isinstance(value, str) and value.strip():
        return _profile(
            value.strip(),
            source="explicit",
            reason="Token profile was provided explicitly.",
        )
    if not isinstance(value, dict):
        return None

    profile_type = (
        value.get("type")
        or value.get("profile")
        or value.get("token_profile")
        or value.get("sample_type")
    )
    if not profile_type:
        return None

    payload = dict(value)
    payload["type"] = str(profile_type)
    payload.setdefault("source", "explicit")
    payload.setdefault("reason", "Token profile was provided explicitly.")
    return payload


def _symbol(token: dict[str, Any], market: dict[str, Any]) -> str:
    value = market.get("base_token_symbol") or token.get("symbol") or ""
    return str(value).strip().upper()


def _profile(profile_type: str, *, source: str, reason: str) -> dict[str, Any]:
    return {
        "type": profile_type,
        "source": source,
        "reason": reason,
    }
