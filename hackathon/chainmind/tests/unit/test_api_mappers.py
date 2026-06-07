from chainmind.data.api_mappers import (
    map_bnb_rpc_contract_state,
    map_dexscreener_pairs_to_market,
    map_gmgn_token_intelligence,
    map_goplus_token_security,
    map_honeypot_status,
    map_nansen_token_intelligence,
)


def test_map_dexscreener_pairs_to_market_selects_highest_liquidity_pair():
    market = map_dexscreener_pairs_to_market(
        [
            {
                "pairAddress": "0xLow",
                "liquidity": {"usd": 1000},
                "volume": {"m5": 10},
            },
            {
                "pairAddress": "0xHigh",
                "dexId": "pancakeswap",
                "url": "https://dexscreener.com/bsc/0xHigh",
                "baseToken": {"address": "0xToken", "symbol": "MEME"},
                "quoteToken": {"address": "0xWBNB", "symbol": "WBNB"},
                "priceUsd": "0.01",
                "priceNative": "0.00001",
                "liquidity": {"usd": "5000", "base": "100", "quote": "2"},
                "fdv": "100000",
                "marketCap": "90000",
                "pairCreatedAt": 1710000000000,
                "volume": {"m5": "20", "h1": "100", "h6": "600", "h24": "2400"},
                "txns": {
                    "m5": {"buys": 2, "sells": 1},
                    "h1": {"buys": 10, "sells": 4},
                },
                "priceChange": {"m5": "1.5", "h1": "-2.5"},
            },
        ]
    )

    assert market["source"] == "dexscreener"
    assert market["pair_address"] == "0xhigh"
    assert market["liquidity_usd"] == 5000.0
    assert market["volume_24h_usd"] == 2400.0
    assert market["txns_5m"] == {"buys": 2, "sells": 1}
    assert market["price_change_1h_pct"] == -2.5


def test_map_goplus_token_security_maps_risk_sections():
    mapped = map_goplus_token_security(
        {
            "result": {
                "0xtoken": {
                    "is_honeypot": "1",
                    "buy_tax": "0.05",
                    "sell_tax": "0.25",
                    "cannot_sell_all": "1",
                    "is_blacklisted": "0",
                    "is_open_source": "1",
                    "owner_address": "0xOwner",
                    "creator_address": "0xCreator",
                    "is_proxy": "0",
                    "is_mintable": "1",
                    "hidden_owner": "0",
                    "holder_count": "1234",
                    "lp_holder_count": "8",
                }
            }
        },
        token_address="0xToken",
    )

    assert mapped["security"]["source"] == "goplus"
    assert mapped["security"]["high_risk"] is True
    assert mapped["security"]["is_honeypot"] is True
    assert mapped["security"]["buy_tax"] == 0.05
    assert mapped["security"]["sell_tax"] == 0.25
    assert mapped["contract"]["owner"] == "0xowner"
    assert mapped["contract"]["is_mintable"] is True
    assert mapped["holders"]["holder_count"] == 1234


def test_map_bnb_rpc_contract_state_maps_owner_and_tax_fields():
    mapped = map_bnb_rpc_contract_state(
        {
            "owner": "0x0000000000000000000000000000000000000000",
            "total_supply": 1_000_000,
            "buy_tax_rate": 400,
            "sell_tax_rate": 500,
        }
    )

    assert mapped["contract"]["owner_renounced"] is True
    assert mapped["contract"]["total_supply_raw"] == 1_000_000
    assert mapped["contract"]["buy_tax_rate_bps"] == 400
    assert mapped["security"]["buy_tax"] == 0.04
    assert mapped["security"]["sell_tax"] == 0.05


def test_map_honeypot_status_maps_simulation_security_fields():
    mapped = map_honeypot_status(
        {
            "honeypotResult": {"isHoneypot": True},
            "simulationResult": {"buyTax": 4, "sellTax": 25},
            "simulationError": "sell failed",
        }
    )

    security = mapped["security"]
    assert security["honeypot_source"] == "honeypot.is"
    assert security["simulation_source"] == "honeypot.is"
    assert security["high_risk"] is True
    assert security["is_honeypot"] is True
    assert security["cannot_sell_all"] is True
    assert security["buy_tax"] == 0.04
    assert security["sell_tax"] == 0.25
    assert "Honeypot.is simulation marks this token as a honeypot." in security["warnings"]


def test_map_nansen_token_intelligence_summarizes_rows():
    mapped = map_nansen_token_intelligence(
        {
            "smart_money_holdings": {
                "data": [
                    {
                        "wallet_address": "0xSmart",
                        "token_address": "0xToken",
                        "token_symbol": "MEME",
                        "balance_usd": 123.45,
                    }
                ]
            },
            "tgm_holders": {
                "data": [
                    {
                        "address": "0xHolder",
                        "labels": ["Smart Trader"],
                        "balance": "1000",
                    }
                ]
            },
        }
    )

    assert mapped["source"] == "nansen"
    assert mapped["smart_money_holdings_count"] == 1
    assert mapped["tgm_smart_money_holder_count"] == 1
    assert mapped["has_smart_money_signal"] is True
    assert mapped["smart_money_holdings_sample"][0]["wallet_address"] == "0xSmart"


def test_map_gmgn_token_intelligence_summarizes_wallet_signals():
    mapped = map_gmgn_token_intelligence(
        {
            "token_info": {
                "data": {
                    "address": "0xToken",
                    "symbol": "MEME",
                    "liquidity_usd": "50000",
                }
            },
            "token_security": {"data": {"is_honeypot": "0", "sell_tax": "0.03"}},
            "top_holders": {
                "data": [
                    {
                        "wallet_address": "0xSmart",
                        "labels": ["Smart Trader"],
                        "balance_usd": "1000",
                    },
                    {
                        "wallet_address": "0xBundle",
                        "tags": ["bundled"],
                    },
                ]
            },
            "top_traders": {
                "result": {
                    "traders": [
                        {
                            "wallet": "0xSniper",
                            "is_sniper": True,
                            "pnl_usd": "123.45",
                            "win_rate": "0.66",
                        },
                        {
                            "wallet": "0xInsider",
                            "label": "insider",
                        },
                    ]
                }
            },
        }
    )

    assert mapped["source"] == "gmgn"
    assert mapped["top_holder_count"] == 2
    assert mapped["top_trader_count"] == 2
    assert mapped["smart_wallet_count"] == 1
    assert mapped["sniper_count"] == 1
    assert mapped["insider_count"] == 1
    assert mapped["bundled_wallet_count"] == 1
    assert mapped["has_wallet_signal"] is True
    assert mapped["has_risk_wallet_signal"] is True
    assert mapped["token_info_sample"]["liquidity_usd"] == 50000.0
    assert mapped["top_traders_sample"][0]["wallet"] == "0xsniper"
