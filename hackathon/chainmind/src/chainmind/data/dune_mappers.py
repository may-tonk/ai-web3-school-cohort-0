"""Map Dune query rows into ChainMind token snapshots."""

from __future__ import annotations

from typing import Any

from chainmind.cleaning.dune_cleaners import (
    clean_address,
    clean_float,
    clean_int,
    clean_non_negative_float,
    clean_string,
    clean_timestamp,
)


def build_snapshot_from_dune_results(
    *,
    token_address: str,
    chain: str,
    trading_activity_rows: list[dict[str, Any]],
    flow_5m_rows: list[dict[str, Any]],
    early_buyer_rows: list[dict[str, Any]],
    funding_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "sample_meta": {
            "sample_type": "real",
            "purpose": "phase2_dune_api_validation",
            "is_real_onchain_data": True,
            "sources": ["dune"],
        },
        "token": {
            "address": token_address,
            "symbol": "UNKNOWN",
            "chain": chain,
            "first_trade_time": _first_value(trading_activity_rows, "first_trade_time"),
        },
        "market": _map_market(trading_activity_rows),
        "flow_5m": [_map_flow_row(row) for row in flow_5m_rows],
        "early_buyers": _map_early_buyers(early_buyer_rows, funding_rows),
        "funding": _map_funding(funding_rows),
        "security": {
            "source": "not_connected",
            "high_risk": False,
            "warnings": ["Security API is not connected in this Dune-only snapshot."],
        },
        "data_quality": {},
    }


def _map_market(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}

    top_row = max(rows, key=_volume_sort_key)
    return {
        "volume_source_dune_usd": clean_float(top_row.get("volume_usd")),
        "unique_traders_30d": clean_int(top_row.get("unique_traders")),
        "trades_30d": clean_int(top_row.get("trades")),
        "project": top_row.get("project"),
        "version": top_row.get("version"),
        "project_volume_share": clean_float(top_row.get("project_volume_share")),
    }


def _map_flow_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "bucket": clean_timestamp(row.get("bucket_5m") or row.get("bucket")),
        "trades": clean_int(row.get("trades")),
        "unique_traders": clean_int(row.get("unique_traders")),
        "buy_trades": clean_int(row.get("buy_trades")),
        "sell_trades": clean_int(row.get("sell_trades")),
        "buyers": clean_int(row.get("buyers")),
        "sellers": clean_int(row.get("sellers")),
        "buy_volume_usd": clean_float(row.get("buy_volume_usd")),
        "sell_volume_usd": clean_float(row.get("sell_volume_usd")),
        "net_buy_usd": clean_float(row.get("net_buy_usd")),
    }


def _map_early_buyers(
    early_buyer_rows: list[dict[str, Any]],
    funding_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    funding_by_buyer: dict[str, dict[str, Any]] = {}
    for row in funding_rows:
        buyer = clean_address(row.get("buyer"))
        if buyer and buyer not in funding_by_buyer:
            funding_by_buyer[buyer] = row

    buyers = []
    for row in early_buyer_rows:
        wallet = clean_address(row.get("buyer") or row.get("wallet"))
        funding = funding_by_buyer.get(wallet or "", {})
        buyers.append(
            {
                "wallet": wallet,
                "rank": clean_int(row.get("buyer_rank") or row.get("rank")),
                "first_buy_time": clean_timestamp(row.get("first_buy_time")),
                "buy_trades": clean_int(row.get("buy_trades")),
                "tokens_bought": clean_float(row.get("tokens_bought")),
                "buy_usd": clean_float(row.get("buy_usd")),
                "current_balance": clean_float(row.get("current_balance")),
                "remaining_ratio": clean_non_negative_float(row.get("remaining_ratio")),
                "first_funder": clean_address(funding.get("funder")),
                "wallet_age_days": clean_int(funding.get("wallet_age_days_at_entry")),
                "tx_count_before_entry": clean_int(funding.get("tx_count_before_entry")),
            }
        )
    return buyers


def _map_funding(rows: list[dict[str, Any]]) -> dict[str, Any]:
    if not rows:
        return {}

    by_funder: dict[str, dict[str, Any]] = {}
    new_wallet_count = 0
    buyers_seen: set[str] = set()

    for row in rows:
        buyer = clean_address(row.get("buyer"))
        if buyer:
            buyers_seen.add(buyer)
        wallet_age_days = clean_int(row.get("wallet_age_days_at_entry"))
        tx_count = clean_int(row.get("tx_count_before_entry"))
        if wallet_age_days is not None and wallet_age_days <= 1:
            new_wallet_count += 1
        elif tx_count is not None and tx_count <= 2:
            new_wallet_count += 1

        funder = clean_address(row.get("funder"))
        if not funder:
            continue
        existing = by_funder.get(funder)
        funded_early_buyers = clean_int(row.get("funded_selected_early_buyers")) or 1
        total_funded_bnb = clean_float(row.get("total_funded_bnb"))
        is_infrastructure = bool(row.get("infrastructure_label"))
        if existing is None or funded_early_buyers > existing["funded_early_buyers"]:
            by_funder[funder] = {
                "funder": funder,
                "funded_early_buyers": funded_early_buyers,
                "is_infrastructure": is_infrastructure,
                "infrastructure_label": row.get("infrastructure_label"),
                "total_funded_bnb": total_funded_bnb,
            }

    buyer_count = max(len(buyers_seen), 1)
    return {
        "shared_funders": list(by_funder.values()),
        "new_wallet_ratio": new_wallet_count / buyer_count,
    }


def _first_value(rows: list[dict[str, Any]], key: str) -> Any:
    for row in rows:
        if row.get(key) is not None:
            return clean_string(row.get(key))
    return None


def _volume_sort_key(row: dict[str, Any]) -> float:
    return clean_float(row.get("volume_usd")) or 0
