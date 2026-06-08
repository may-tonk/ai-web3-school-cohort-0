"""Realtime quick-screen orchestration for BNB tokens."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from chainmind.data.api_mappers import (
    map_bnb_rpc_contract_state,
    map_dexscreener_pairs_to_market,
    map_goplus_token_security,
    map_honeypot_status,
)
from chainmind.domain import infer_token_profile
from chainmind.orchestration.analyze_dune_token import (
    build_honeypot_client_from_env,
    build_market_client_from_env,
    build_rpc_client_from_env,
    build_security_client_from_env,
)
from chainmind.scoring.quick_screen import QuickScreenResult, quick_screen_decision


@dataclass(frozen=True)
class QuickScreenTokenResult:
    token_address: str
    chain: str
    snapshot: dict[str, Any]
    screen: QuickScreenResult

    def to_mapping(self) -> dict[str, Any]:
        return {
            "token_address": self.token_address,
            "chain": self.chain,
            "decision": self.screen.decision,
            "reasons": list(self.screen.reasons),
            "evidence": list(self.screen.evidence),
            "snapshot": dict(self.snapshot),
        }


def quick_screen_token(
    *,
    token_address: str,
    chain: str = "bnb",
    market_client: Any | None = None,
    security_client: Any | None = None,
    honeypot_client: Any | None = None,
    rpc_client: Any | None = None,
) -> QuickScreenTokenResult:
    snapshot: dict[str, Any] = {
        "token": {"address": token_address, "chain": chain},
        "market": {},
        "security": {},
        "contract": {},
        "holders": {},
        "data_quality": {"api_warnings": []},
    }

    if market_client is not None:
        try:
            pairs = market_client.get_token_pairs(
                chain=chain,
                token_address=token_address,
            )
            snapshot["market"].update(map_dexscreener_pairs_to_market(pairs))
        except Exception as exc:  # noqa: BLE001 - quick screen should use partial data.
            _append_warning(snapshot, f"DexScreener API failed: {exc}")

    if security_client is not None:
        try:
            payload = security_client.get_token_security(
                chain=chain,
                token_address=token_address,
            )
            mapped = map_goplus_token_security(payload, token_address=token_address)
            snapshot["security"].update(mapped["security"])
            snapshot["contract"].update(mapped["contract"])
            snapshot["holders"].update(mapped["holders"])
        except Exception as exc:  # noqa: BLE001 - quick screen should use partial data.
            _append_warning(snapshot, f"GoPlus API failed: {exc}")

    if honeypot_client is not None:
        try:
            payload = honeypot_client.get_honeypot_status(
                chain=chain,
                token_address=token_address,
            )
            mapped = map_honeypot_status(payload)
            _merge_security(snapshot, mapped["security"])
        except Exception as exc:  # noqa: BLE001 - quick screen should use partial data.
            _append_warning(snapshot, f"Honeypot.is API failed: {exc}")

    if rpc_client is not None:
        try:
            mapped = map_bnb_rpc_contract_state(
                rpc_client.get_contract_readonly_state(token_address)
            )
            snapshot["contract"].update(mapped["contract"])
            snapshot["security"].update(mapped["security"])
        except Exception as exc:  # noqa: BLE001 - quick screen should use partial data.
            _append_warning(snapshot, f"BNB RPC failed: {exc}")

    snapshot["token_profile"] = infer_token_profile(snapshot)
    screen = quick_screen_decision(snapshot)
    return QuickScreenTokenResult(
        token_address=token_address,
        chain=chain,
        snapshot=snapshot,
        screen=screen,
    )


def quick_screen_token_from_env(token_address: str, chain: str = "bnb") -> QuickScreenTokenResult:
    return quick_screen_token(
        token_address=token_address,
        chain=chain,
        market_client=build_market_client_from_env(),
        security_client=build_security_client_from_env(),
        honeypot_client=build_honeypot_client_from_env(),
        rpc_client=build_rpc_client_from_env(),
    )


def _merge_security(snapshot: dict[str, Any], update: dict[str, Any]) -> None:
    security = snapshot.setdefault("security", {})
    existing_warnings = list(security.get("warnings") or [])
    update_warnings = list(update.get("warnings") or [])
    security.update(
        {
            key: value
            for key, value in update.items()
            if key != "warnings" and value is not None
        }
    )
    if existing_warnings or update_warnings:
        security["warnings"] = existing_warnings + update_warnings


def _append_warning(snapshot: dict[str, Any], warning: str) -> None:
    snapshot.setdefault("data_quality", {}).setdefault("api_warnings", []).append(warning)
