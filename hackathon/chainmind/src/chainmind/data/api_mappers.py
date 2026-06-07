"""Map external API payloads into TokenSnapshot sections."""

from __future__ import annotations

from typing import Any

from chainmind.cleaning.dune_cleaners import clean_address, clean_float, clean_int, clean_string


def map_dexscreener_pairs_to_market(pairs: list[dict[str, Any]]) -> dict[str, Any]:
    if not pairs:
        return {}

    pair = max(pairs, key=_pair_liquidity_usd)
    liquidity = dict(pair.get("liquidity") or {})
    volume = dict(pair.get("volume") or {})
    txns = dict(pair.get("txns") or {})
    price_change = dict(pair.get("priceChange") or {})
    base_token = dict(pair.get("baseToken") or {})
    quote_token = dict(pair.get("quoteToken") or {})

    return {
        "source": "dexscreener",
        "pair_address": clean_address(pair.get("pairAddress")),
        "dex_id": clean_string(pair.get("dexId")),
        "url": clean_string(pair.get("url")),
        "base_token_address": clean_address(base_token.get("address")),
        "base_token_symbol": clean_string(base_token.get("symbol")),
        "quote_token_address": clean_address(quote_token.get("address")),
        "quote_token_symbol": clean_string(quote_token.get("symbol")),
        "price_usd": clean_float(pair.get("priceUsd")),
        "price_native": clean_float(pair.get("priceNative")),
        "liquidity_usd": clean_float(liquidity.get("usd")),
        "liquidity_base": clean_float(liquidity.get("base")),
        "liquidity_quote": clean_float(liquidity.get("quote")),
        "fdv_usd": clean_float(pair.get("fdv")),
        "market_cap_usd": clean_float(pair.get("marketCap")),
        "pair_created_at": clean_int(pair.get("pairCreatedAt")),
        "volume_5m_usd": clean_float(volume.get("m5")),
        "volume_1h_usd": clean_float(volume.get("h1")),
        "volume_6h_usd": clean_float(volume.get("h6")),
        "volume_24h_usd": clean_float(volume.get("h24")),
        "txns_5m": _map_txn_window(txns.get("m5")),
        "txns_1h": _map_txn_window(txns.get("h1")),
        "txns_6h": _map_txn_window(txns.get("h6")),
        "txns_24h": _map_txn_window(txns.get("h24")),
        "price_change_5m_pct": clean_float(price_change.get("m5")),
        "price_change_1h_pct": clean_float(price_change.get("h1")),
        "price_change_6h_pct": clean_float(price_change.get("h6")),
        "price_change_24h_pct": clean_float(price_change.get("h24")),
    }


def map_goplus_token_security(
    payload: dict[str, Any],
    *,
    token_address: str,
) -> dict[str, dict[str, Any]]:
    result = dict(payload.get("result") or {})
    token = result.get(token_address.lower()) or result.get(token_address) or {}
    if not isinstance(token, dict):
        token = {}

    security = {
        "source": "goplus",
        "high_risk": _is_high_risk_goplus_token(token),
        "is_honeypot": _flag(token.get("is_honeypot")),
        "buy_tax": clean_float(token.get("buy_tax")),
        "sell_tax": clean_float(token.get("sell_tax")),
        "cannot_buy": _flag(token.get("cannot_buy")),
        "cannot_sell_all": _flag(token.get("cannot_sell_all")),
        "is_blacklisted": _flag(token.get("is_blacklisted")),
        "is_open_source": _flag(token.get("is_open_source")),
        "warnings": _goplus_warnings(token),
    }

    contract = {
        "source": "goplus",
        "owner": clean_address(token.get("owner_address")),
        "creator_address": clean_address(token.get("creator_address")),
        "is_proxy": _flag(token.get("is_proxy")),
        "is_mintable": _flag(token.get("is_mintable")),
        "can_take_back_ownership": _flag(token.get("can_take_back_ownership")),
        "hidden_owner": _flag(token.get("hidden_owner")),
        "selfdestruct": _flag(token.get("selfdestruct")),
        "external_call": _flag(token.get("external_call")),
    }

    holders = {
        "source": "goplus",
        "holder_count": clean_int(token.get("holder_count")),
        "lp_holder_count": clean_int(token.get("lp_holder_count")),
        "lp_total_supply": clean_float(token.get("lp_total_supply")),
    }

    return {
        "security": security,
        "contract": contract,
        "holders": holders,
    }


def map_bnb_rpc_contract_state(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    owner = clean_address(state.get("owner"))
    zero_address = "0x0000000000000000000000000000000000000000"
    buy_tax_rate = clean_int(state.get("buy_tax_rate"))
    sell_tax_rate = clean_int(state.get("sell_tax_rate"))

    contract = {
        "rpc_source": "bnb_rpc",
        "owner": owner,
        "owner_renounced": owner == zero_address if owner is not None else None,
        "total_supply_raw": clean_int(state.get("total_supply")),
        "buy_tax_rate_raw": buy_tax_rate,
        "sell_tax_rate_raw": sell_tax_rate,
        "buy_tax_rate_bps": buy_tax_rate,
        "sell_tax_rate_bps": sell_tax_rate,
    }

    security: dict[str, Any] = {
        "rpc_source": "bnb_rpc",
        "buy_tax_bps": buy_tax_rate,
        "sell_tax_bps": sell_tax_rate,
    }
    if buy_tax_rate is not None:
        security["buy_tax"] = buy_tax_rate / 10_000
    if sell_tax_rate is not None:
        security["sell_tax"] = sell_tax_rate / 10_000

    return {
        "contract": contract,
        "security": security,
    }


def map_honeypot_status(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    honeypot = dict(payload.get("honeypotResult") or {})
    simulation = dict(payload.get("simulationResult") or {})

    is_honeypot = _flag(honeypot.get("isHoneypot"))
    buy_tax_raw = clean_float(simulation.get("buyTax"))
    sell_tax_raw = clean_float(simulation.get("sellTax"))

    security = {
        "honeypot_source": "honeypot.is",
        "simulation_source": "honeypot.is",
        "high_risk": True if is_honeypot is True else None,
        "is_honeypot": is_honeypot,
        "buy_tax": _normalize_tax(buy_tax_raw),
        "sell_tax": _normalize_tax(sell_tax_raw),
        "honeypot_buy_tax_raw": buy_tax_raw,
        "honeypot_sell_tax_raw": sell_tax_raw,
        "cannot_sell_all": True if is_honeypot is True else None,
        "warnings": _honeypot_warnings(payload, is_honeypot),
    }
    return {"security": security}


def map_nansen_token_intelligence(payload: dict[str, Any]) -> dict[str, Any]:
    smart_money_holdings = dict(payload.get("smart_money_holdings") or {})
    tgm_holders = dict(payload.get("tgm_holders") or {})

    smart_money_rows = _rows(smart_money_holdings)
    tgm_holder_rows = _rows(tgm_holders)

    return {
        "source": "nansen",
        "smart_money_holdings_count": len(smart_money_rows),
        "tgm_smart_money_holder_count": len(tgm_holder_rows),
        "has_smart_money_signal": bool(smart_money_rows or tgm_holder_rows),
        "smart_money_holdings_sample": [_compact_nansen_row(row) for row in smart_money_rows[:5]],
        "tgm_holders_sample": [_compact_nansen_row(row) for row in tgm_holder_rows[:5]],
    }


def map_gmgn_token_intelligence(payload: dict[str, Any]) -> dict[str, Any]:
    token_info = payload.get("token_info") or {}
    token_security = payload.get("token_security") or {}
    top_holders = _gmgn_rows(payload.get("top_holders"))
    top_traders = _gmgn_rows(payload.get("top_traders"))
    wallet_rows = top_holders + top_traders

    return {
        "source": "gmgn",
        "top_holder_count": len(top_holders),
        "top_trader_count": len(top_traders),
        "smart_wallet_count": _count_gmgn_signal(wallet_rows, "smart"),
        "sniper_count": _count_gmgn_signal(wallet_rows, "sniper"),
        "insider_count": _count_gmgn_signal(wallet_rows, "insider"),
        "bundled_wallet_count": _count_gmgn_signal(wallet_rows, "bundled"),
        "has_wallet_signal": bool(top_holders or top_traders),
        "has_risk_wallet_signal": any(
            _count_gmgn_signal(wallet_rows, signal) > 0
            for signal in ("sniper", "insider", "bundled")
        ),
        "token_info_sample": _compact_gmgn_object(token_info),
        "token_security_sample": _compact_gmgn_object(token_security),
        "top_holders_sample": [_compact_gmgn_wallet_row(row) for row in top_holders[:5]],
        "top_traders_sample": [_compact_gmgn_wallet_row(row) for row in top_traders[:5]],
    }


def _map_txn_window(value: Any) -> dict[str, int | None]:
    data = dict(value or {})
    return {
        "buys": clean_int(data.get("buys")),
        "sells": clean_int(data.get("sells")),
    }


def _pair_liquidity_usd(pair: dict[str, Any]) -> float:
    liquidity = dict(pair.get("liquidity") or {})
    return clean_float(liquidity.get("usd")) or 0


def _flag(value: Any) -> bool | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes"}


def _is_high_risk_goplus_token(token: dict[str, Any]) -> bool:
    high_risk_flags = [
        "is_honeypot",
        "cannot_buy",
        "cannot_sell_all",
        "is_blacklisted",
        "hidden_owner",
        "selfdestruct",
    ]
    if any(_flag(token.get(name)) is True for name in high_risk_flags):
        return True

    sell_tax = clean_float(token.get("sell_tax"))
    if sell_tax is not None and sell_tax >= 0.2:
        return True

    buy_tax = clean_float(token.get("buy_tax"))
    return bool(buy_tax is not None and buy_tax >= 0.2)


def _normalize_tax(value: float | None) -> float | None:
    if value is None:
        return None
    if value > 1:
        return value / 100
    return value


def _goplus_warnings(token: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    if _flag(token.get("is_honeypot")) is True:
        warnings.append("GoPlus marks this token as a honeypot.")
    if _flag(token.get("cannot_sell_all")) is True:
        warnings.append("GoPlus indicates holders may not be able to sell all tokens.")
    if _flag(token.get("is_blacklisted")) is True:
        warnings.append("GoPlus indicates blacklist behavior is present.")
    if _flag(token.get("hidden_owner")) is True:
        warnings.append("GoPlus indicates a hidden owner risk.")
    return warnings


def _honeypot_warnings(payload: dict[str, Any], is_honeypot: bool | None) -> list[str]:
    warnings: list[str] = []
    if is_honeypot is True:
        warnings.append("Honeypot.is simulation marks this token as a honeypot.")

    simulation_error = payload.get("simulationError")
    if simulation_error:
        warnings.append(f"Honeypot.is simulation error: {simulation_error}")

    return warnings


def _rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("data")
    if isinstance(rows, list):
        return [dict(row) for row in rows if isinstance(row, dict)]
    return []


def _gmgn_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [dict(row) for row in payload if isinstance(row, dict)]
    if not isinstance(payload, dict):
        return []

    for key in (
        "data",
        "result",
        "rows",
        "items",
        "list",
        "tokens",
        "holders",
        "traders",
    ):
        value = payload.get(key)
        if isinstance(value, list):
            return [dict(row) for row in value if isinstance(row, dict)]
        if isinstance(value, dict):
            nested = _gmgn_rows(value)
            if nested:
                return nested
    return []


def _compact_nansen_row(row: dict[str, Any]) -> dict[str, Any]:
    preferred_keys = [
        "address",
        "wallet_address",
        "owner_address",
        "token_address",
        "token_symbol",
        "label",
        "labels",
        "smart_money_labels",
        "balance",
        "balance_usd",
        "amount_usd",
        "chain",
    ]
    compact = {
        key: row.get(key)
        for key in preferred_keys
        if row.get(key) is not None
    }
    if compact:
        return compact
    return dict(list(row.items())[:8])


def _compact_gmgn_object(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return {}

    data = value
    for key in ("data", "result", "token"):
        nested = data.get(key)
        if isinstance(nested, dict):
            data = nested
            break

    preferred_keys = [
        "address",
        "token_address",
        "symbol",
        "name",
        "price",
        "price_usd",
        "market_cap",
        "market_cap_usd",
        "fdv",
        "liquidity",
        "liquidity_usd",
        "volume_24h",
        "volume_24h_usd",
        "holder_count",
        "is_honeypot",
        "buy_tax",
        "sell_tax",
        "renounced",
        "open_source",
    ]
    compact = {
        key: _clean_gmgn_value(key, data.get(key))
        for key in preferred_keys
        if data.get(key) is not None
    }
    if compact:
        return compact
    return dict(list(data.items())[:8])


def _compact_gmgn_wallet_row(row: dict[str, Any]) -> dict[str, Any]:
    preferred_keys = [
        "address",
        "wallet",
        "wallet_address",
        "label",
        "labels",
        "tags",
        "balance",
        "balance_usd",
        "amount",
        "amount_usd",
        "holding_percentage",
        "percentage",
        "pnl",
        "pnl_usd",
        "realized_pnl",
        "realized_profit",
        "win_rate",
        "profit_rate",
        "volume_usd",
        "buy_volume_usd",
        "sell_volume_usd",
        "buys",
        "sells",
        "tx_count",
        "is_smart_wallet",
        "is_smart_money",
        "is_sniper",
        "is_insider",
        "is_bundled",
    ]
    compact = {
        key: _clean_gmgn_value(key, row.get(key))
        for key in preferred_keys
        if row.get(key) is not None
    }
    if compact:
        return compact
    return dict(list(row.items())[:8])


def _clean_gmgn_value(key: str, value: Any) -> Any:
    if key in {"address", "wallet", "wallet_address", "token_address"}:
        return clean_address(value)
    if key.startswith("is_") or key in {"renounced", "open_source"}:
        return _flag(value)
    if key in {
        "balance",
        "balance_usd",
        "amount",
        "amount_usd",
        "holding_percentage",
        "percentage",
        "pnl",
        "pnl_usd",
        "realized_pnl",
        "realized_profit",
        "win_rate",
        "profit_rate",
        "volume_usd",
        "buy_volume_usd",
        "sell_volume_usd",
        "price",
        "price_usd",
        "market_cap",
        "market_cap_usd",
        "fdv",
        "liquidity",
        "liquidity_usd",
        "volume_24h",
        "volume_24h_usd",
        "buy_tax",
        "sell_tax",
    }:
        return clean_float(value)
    if key in {"buys", "sells", "tx_count", "holder_count"}:
        return clean_int(value)
    return value


def _count_gmgn_signal(rows: list[dict[str, Any]], signal: str) -> int:
    return sum(1 for row in rows if _has_gmgn_signal(row, signal))


def _has_gmgn_signal(row: dict[str, Any], signal: str) -> bool:
    boolean_keys = {
        "smart": ("is_smart_wallet", "is_smart_money", "smart_wallet", "smart_money"),
        "sniper": ("is_sniper", "sniper"),
        "insider": ("is_insider", "insider"),
        "bundled": ("is_bundled", "bundled", "bundle"),
    }[signal]
    if any(_flag(row.get(key)) is True for key in boolean_keys):
        return True

    labels: list[str] = []
    for key in ("label", "labels", "tag", "tags", "wallet_type", "type"):
        value = row.get(key)
        if isinstance(value, list):
            labels.extend(str(item).lower() for item in value)
        elif value:
            labels.append(str(value).lower())

    joined = " ".join(labels)
    if signal == "smart":
        return "smart" in joined or "kol" in joined or "alpha" in joined
    if signal == "bundled":
        return "bundled" in joined or "bundle" in joined
    return signal in joined
