"""Dune-backed token analysis orchestration."""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from chainmind.data.api_mappers import (
    map_bnb_rpc_contract_state,
    map_dexscreener_pairs_to_market,
    map_goplus_token_security,
    map_honeypot_status,
    map_nansen_token_intelligence,
)
from chainmind.data.bnb_rpc_client import BnbRpcClient
from chainmind.data.dexscreener_client import DexScreenerClient
from chainmind.data.dune_client import DuneClient, DuneConfig
from chainmind.data.dune_mappers import build_snapshot_from_dune_results
from chainmind.data.goplus_client import GoPlusClient
from chainmind.data.honeypot_client import HoneypotClient
from chainmind.data.nansen_client import NansenClient
from chainmind.data.query_cache import DuneQueryCache
from chainmind.domain import AnalysisResult, TokenSnapshot
from chainmind.orchestration.analyze_token import analyze_token


REQUIRED_DUNE_QUERIES = (
    "trading_activity",
    "five_minute_flow",
    "early_buyers",
    "early_buyer_funding",
)

QUERY_ENV_KEYS = {
    "trading_activity": "DUNE_QUERY_TOKEN_TRADING_ACTIVITY",
    "five_minute_flow": "DUNE_QUERY_FIVE_MINUTE_FLOW",
    "early_buyers": "DUNE_QUERY_EARLY_BUYERS",
    "early_buyer_funding": "DUNE_QUERY_EARLY_BUYER_FUNDING",
}


@dataclass(frozen=True)
class DuneTokenAnalysisConfig:
    chain: str
    cache_dir: Path
    refresh_cache: bool = False


@dataclass(frozen=True)
class DuneQuerySet:
    trading_activity: str
    five_minute_flow: str
    early_buyers: str
    early_buyer_funding: str

    @classmethod
    def from_mapping(cls, query_ids: dict[str, str]) -> "DuneQuerySet":
        missing = [name for name in REQUIRED_DUNE_QUERIES if not query_ids.get(name)]
        if missing:
            raise RuntimeError(f"Missing Dune query ids: {missing}")

        return cls(
            trading_activity=query_ids["trading_activity"],
            five_minute_flow=query_ids["five_minute_flow"],
            early_buyers=query_ids["early_buyers"],
            early_buyer_funding=query_ids["early_buyer_funding"],
        )

    def to_mapping(self) -> dict[str, str]:
        return {
            "trading_activity": self.trading_activity,
            "five_minute_flow": self.five_minute_flow,
            "early_buyers": self.early_buyers,
            "early_buyer_funding": self.early_buyer_funding,
        }

    def get(self, query_name: str) -> str:
        try:
            return self.to_mapping()[query_name]
        except KeyError as exc:
            raise RuntimeError(f"Unknown Dune query name: {query_name}") from exc


@dataclass(frozen=True)
class DuneTokenAnalysisResult:
    snapshot: dict[str, Any]
    analysis: AnalysisResult

    def to_mapping(self) -> dict[str, Any]:
        return {
            "snapshot": dict(self.snapshot),
            "analysis": self.analysis.to_mapping(),
        }


def analyze_dune_token(
    *,
    token_address: str,
    client: DuneClient,
    query_ids: DuneQuerySet | dict[str, str],
    config: DuneTokenAnalysisConfig,
    market_client: Any | None = None,
    security_client: Any | None = None,
    honeypot_client: Any | None = None,
    intelligence_client: Any | None = None,
    rpc_client: Any | None = None,
    log: Callable[[str], None] | None = None,
) -> DuneTokenAnalysisResult:
    """Run configured Dune queries and return a ChainMind analysis result."""

    query_set = _coerce_query_set(query_ids)
    query_cache = DuneQueryCache(config.cache_dir)

    trading_rows = _load_or_run_query(
        client,
        query_set.get("trading_activity"),
        token_address,
        "trading_activity",
        query_cache,
        config.refresh_cache,
        log,
    )
    flow_rows = _load_or_run_query(
        client,
        query_set.get("five_minute_flow"),
        token_address,
        "five_minute_flow",
        query_cache,
        config.refresh_cache,
        log,
    )
    early_buyer_rows = _load_or_run_query(
        client,
        query_set.get("early_buyers"),
        token_address,
        "early_buyers",
        query_cache,
        config.refresh_cache,
        log,
    )
    funding_rows = _load_or_run_query(
        client,
        query_set.get("early_buyer_funding"),
        token_address,
        "early_buyer_funding",
        query_cache,
        config.refresh_cache,
        log,
    )

    snapshot_payload = build_snapshot_from_dune_results(
        token_address=token_address,
        chain=config.chain,
        trading_activity_rows=trading_rows,
        flow_5m_rows=flow_rows,
        early_buyer_rows=early_buyer_rows,
        funding_rows=funding_rows,
    )
    _merge_optional_api_data(
        snapshot_payload=snapshot_payload,
        token_address=token_address,
        chain=config.chain,
        market_client=market_client,
        security_client=security_client,
        honeypot_client=honeypot_client,
        intelligence_client=intelligence_client,
        rpc_client=rpc_client,
        log=log,
    )

    analysis = analyze_token(TokenSnapshot.from_mapping(snapshot_payload))
    return DuneTokenAnalysisResult(snapshot=snapshot_payload, analysis=analysis)


def build_client_from_env() -> DuneClient:
    api_key = os.environ.get("DUNE_API_KEY")
    if not api_key:
        raise RuntimeError("DUNE_API_KEY is not set.")
    return DuneClient(DuneConfig(api_key=api_key))


def build_market_client_from_env() -> DexScreenerClient:
    return DexScreenerClient.from_env()


def build_security_client_from_env() -> GoPlusClient:
    return GoPlusClient.from_env()


def build_honeypot_client_from_env() -> HoneypotClient:
    return HoneypotClient.from_env()


def build_intelligence_client_from_env() -> NansenClient | None:
    return NansenClient.from_env()


def build_rpc_client_from_env() -> BnbRpcClient | None:
    return BnbRpcClient.from_env()


def load_query_set_from_env() -> DuneQuerySet:
    return DuneQuerySet.from_mapping(load_query_ids_from_env())


def load_query_ids_from_env() -> dict[str, str]:
    query_ids = {}
    missing = []
    for name, env_key in QUERY_ENV_KEYS.items():
        value = os.environ.get(env_key)
        if not value:
            missing.append(env_key)
        else:
            query_ids[name] = value
    if missing:
        raise RuntimeError(f"Missing Dune query id environment variables: {missing}")
    return query_ids


def _coerce_query_set(query_ids: DuneQuerySet | dict[str, str]) -> DuneQuerySet:
    if isinstance(query_ids, DuneQuerySet):
        return query_ids
    return DuneQuerySet.from_mapping(query_ids)


def _load_or_run_query(
    client: DuneClient,
    query_id: str,
    token_address: str,
    query_name: str,
    query_cache: DuneQueryCache,
    refresh_cache: bool,
    log: Callable[[str], None] | None,
) -> list[dict[str, Any]]:
    if not refresh_cache:
        rows = query_cache.load_rows(
            token_address=token_address,
            query_name=query_name,
        )
    else:
        rows = None

    if rows is not None:
        _log(log, f"Using cached Dune rows: {query_name} ({len(rows)} rows)")
        return rows

    execution_id = None
    if not refresh_cache:
        execution_id = query_cache.load_execution_id(
            token_address=token_address,
            query_name=query_name,
        )

    if execution_id:
        _log(log, f"Resuming Dune execution: {query_name} ({execution_id})")
    else:
        _log(log, f"Running Dune query: {query_name}")
        execution_id = client.execute_query(query_id, token_address)
        query_cache.save_execution_id(
            token_address=token_address,
            query_name=query_name,
            query_id=query_id,
            execution_id=execution_id,
        )

    client.wait_for_execution(execution_id)
    rows = client.get_execution_results(execution_id)
    query_cache.save_rows(
        token_address=token_address,
        query_name=query_name,
        query_id=query_id,
        execution_id=execution_id,
        rows=rows,
    )
    _log(log, f"Cached Dune rows: {query_name} ({len(rows)} rows)")
    return rows


def _merge_optional_api_data(
    *,
    snapshot_payload: dict[str, Any],
    token_address: str,
    chain: str,
    market_client: Any | None,
    security_client: Any | None,
    honeypot_client: Any | None,
    intelligence_client: Any | None,
    rpc_client: Any | None,
    log: Callable[[str], None] | None,
) -> None:
    if market_client is not None:
        try:
            pairs = market_client.get_token_pairs(
                chain=chain,
                token_address=token_address,
            )
            market = map_dexscreener_pairs_to_market(pairs)
            if market:
                snapshot_payload.setdefault("market", {}).update(market)
                _log(log, "Merged DexScreener market data.")
        except Exception as exc:  # noqa: BLE001 - API enrichment must not stop analysis.
            _append_api_warning(snapshot_payload, f"DexScreener API failed: {exc}")
            _log(log, f"DexScreener API failed: {exc}")

    if security_client is not None:
        try:
            payload = security_client.get_token_security(
                chain=chain,
                token_address=token_address,
            )
            mapped = map_goplus_token_security(payload, token_address=token_address)
            snapshot_payload["security"] = mapped["security"]
            snapshot_payload["contract"] = mapped["contract"]
            snapshot_payload["holders"] = mapped["holders"]
            _log(log, "Merged GoPlus token security data.")
        except Exception as exc:  # noqa: BLE001 - API enrichment must not stop analysis.
            _append_api_warning(snapshot_payload, f"GoPlus API failed: {exc}")
            snapshot_payload.setdefault("security", {}).setdefault("warnings", []).append(
                f"GoPlus API failed: {exc}"
            )
            _log(log, f"GoPlus API failed: {exc}")

    if honeypot_client is not None:
        try:
            payload = honeypot_client.get_honeypot_status(
                chain=chain,
                token_address=token_address,
            )
            mapped = map_honeypot_status(payload)
            _merge_security(snapshot_payload, mapped["security"])
            _log(log, "Merged Honeypot.is simulation data.")
        except Exception as exc:  # noqa: BLE001 - API enrichment must not stop analysis.
            _append_api_warning(snapshot_payload, f"Honeypot.is API failed: {exc}")
            snapshot_payload.setdefault("security", {}).setdefault("warnings", []).append(
                f"Honeypot.is API failed: {exc}"
            )
            _log(log, f"Honeypot.is API failed: {exc}")

    if intelligence_client is not None:
        try:
            payload = intelligence_client.get_token_intelligence(
                chain=chain,
                token_address=token_address,
            )
            nansen = map_nansen_token_intelligence(payload)
            snapshot_payload.setdefault("intelligence", {})["nansen"] = nansen
            _log(log, "Merged Nansen intelligence data.")
        except Exception as exc:  # noqa: BLE001 - API enrichment must not stop analysis.
            _append_api_warning(snapshot_payload, f"Nansen API failed: {exc}")
            _log(log, f"Nansen API failed: {exc}")

    if rpc_client is not None:
        try:
            state = rpc_client.get_contract_readonly_state(token_address)
            mapped = map_bnb_rpc_contract_state(state)
            snapshot_payload.setdefault("contract", {}).update(mapped["contract"])
            snapshot_payload.setdefault("security", {}).update(mapped["security"])
            _log(log, "Merged BNB RPC contract state.")
        except Exception as exc:  # noqa: BLE001 - API enrichment must not stop analysis.
            _append_api_warning(snapshot_payload, f"BNB RPC failed: {exc}")
            snapshot_payload.setdefault("security", {}).setdefault("warnings", []).append(
                f"BNB RPC failed: {exc}"
            )
            _log(log, f"BNB RPC failed: {exc}")


def _merge_security(snapshot_payload: dict[str, Any], update: dict[str, Any]) -> None:
    security = snapshot_payload.setdefault("security", {})
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


def _append_api_warning(snapshot_payload: dict[str, Any], warning: str) -> None:
    data_quality = snapshot_payload.setdefault("data_quality", {})
    data_quality.setdefault("api_warnings", []).append(warning)


def _log(log: Callable[[str], None] | None, message: str) -> None:
    if log is not None:
        log(message)
