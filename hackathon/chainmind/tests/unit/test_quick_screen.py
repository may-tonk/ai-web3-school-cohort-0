from chainmind.orchestration.quick_screen_token import quick_screen_token
from chainmind.scoring.quick_screen import quick_screen_decision


def test_quick_screen_blocks_honeypot():
    result = quick_screen_decision(
        {
            "market": {"liquidity_usd": 100_000, "volume_24h_usd": 50_000},
            "security": {"is_honeypot": True, "buy_tax": 0.04, "sell_tax": 0.04},
            "contract": {"owner_renounced": True},
            "holders": {"holder_count": 1_000},
        }
    )

    assert result.decision == "BLOCK"
    assert result.evidence[0]["rule_id"] == "quick_honeypot_block"


def test_quick_screen_watches_low_liquidity_and_tax():
    result = quick_screen_decision(
        {
            "market": {"liquidity_usd": 12_000, "volume_24h_usd": 4_000},
            "security": {"is_honeypot": False, "buy_tax": 0.09, "sell_tax": 0.04},
            "contract": {"owner_renounced": True},
            "holders": {"holder_count": 800},
        }
    )

    assert result.decision == "WATCH"
    assert {item["rule_id"] for item in result.evidence} == {
        "quick_low_liquidity_watch",
        "quick_low_volume_watch",
        "quick_high_buy_tax_watch",
    }


def test_quick_screen_passes_clean_snapshot():
    result = quick_screen_decision(
        {
            "market": {"liquidity_usd": 50_000, "volume_24h_usd": 20_000},
            "security": {"is_honeypot": False, "buy_tax": 0.04, "sell_tax": 0.04},
            "contract": {"owner_renounced": True, "is_mintable": False},
            "holders": {"holder_count": 1_000},
        }
    )

    assert result.decision == "PASS"


class FakeMarketClient:
    def get_token_pairs(self, chain, token_address):
        return [
            {
                "pairAddress": "0xPair",
                "baseToken": {"address": token_address, "symbol": "MEME"},
                "liquidity": {"usd": "1000"},
                "volume": {"h24": "100"},
            }
        ]


class FakeSecurityClient:
    def get_token_security(self, chain, token_address):
        return {
            "result": {
                token_address.lower(): {
                    "is_honeypot": "0",
                    "buy_tax": "0.04",
                    "sell_tax": "0.04",
                    "owner_address": "0xOwner",
                    "holder_count": "100",
                }
            }
        }


class FakeHoneypotClient:
    def get_honeypot_status(self, chain, token_address):
        return {
            "honeypotResult": {"isHoneypot": False},
            "simulationResult": {"buyTax": 4, "sellTax": 4},
        }


class FailingRpcClient:
    def get_contract_readonly_state(self, token_address):
        raise RuntimeError("rpc down")


def test_quick_screen_orchestration_uses_partial_data_when_api_fails():
    result = quick_screen_token(
        token_address="0xToken",
        market_client=FakeMarketClient(),
        security_client=FakeSecurityClient(),
        honeypot_client=FakeHoneypotClient(),
        rpc_client=FailingRpcClient(),
    )

    assert result.screen.decision == "BLOCK"
    assert result.snapshot["market"]["base_token_symbol"] == "MEME"
    assert result.snapshot["security"]["is_honeypot"] is False
    assert result.snapshot["holders"]["holder_count"] == 100
    assert result.snapshot["data_quality"]["api_warnings"] == ["BNB RPC failed: rpc down"]
