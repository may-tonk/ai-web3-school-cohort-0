import pytest

from chainmind.orchestration.analyze_dune_token import (
    DuneQuerySet,
    DuneTokenAnalysisConfig,
    analyze_dune_token,
    load_query_ids_from_env,
    load_query_set_from_env,
)


QUERY_IDS = {
    "trading_activity": "query-trading",
    "five_minute_flow": "query-flow",
    "early_buyers": "query-buyers",
    "early_buyer_funding": "query-funding",
}


class FakeDuneClient:
    def __init__(self):
        self.executed_query_ids = []
        self.waited_execution_ids = []
        self.result_execution_ids = []

    def execute_query(self, query_id, token_address):
        self.executed_query_ids.append((query_id, token_address))
        return f"exec-{query_id}"

    def wait_for_execution(self, execution_id):
        self.waited_execution_ids.append(execution_id)

    def get_execution_results(self, execution_id):
        self.result_execution_ids.append(execution_id)
        return ROWS_BY_EXECUTION[execution_id]


class CacheOnlyClient:
    def execute_query(self, query_id, token_address):
        raise AssertionError("cached run should not execute Dune queries")

    def wait_for_execution(self, execution_id):
        raise AssertionError("cached run should not wait for Dune executions")

    def get_execution_results(self, execution_id):
        raise AssertionError("cached run should not fetch Dune results")


class FakeMarketClient:
    def get_token_pairs(self, chain, token_address):
        return [
            {
                "pairAddress": "0xPair",
                "dexId": "pancakeswap",
                "baseToken": {"address": token_address, "symbol": "TEST"},
                "liquidity": {"usd": "25000"},
                "volume": {"m5": "300"},
            }
        ]


class FakeSecurityClient:
    def get_token_security(self, chain, token_address):
        return {
            "result": {
                token_address.lower(): {
                    "is_honeypot": "1",
                    "sell_tax": "0.25",
                    "owner_address": "0xOwner",
                    "holder_count": "100",
                }
            }
        }


class FakeRpcClient:
    def get_contract_readonly_state(self, token_address):
        return {
            "owner": "0x0000000000000000000000000000000000000000",
            "total_supply": 1_000_000,
            "buy_tax_rate": 400,
            "sell_tax_rate": 500,
        }


class FakeHoneypotClient:
    def get_honeypot_status(self, chain, token_address):
        return {
            "honeypotResult": {"isHoneypot": False},
            "simulationResult": {"buyTax": 3, "sellTax": 4},
        }


class FakeIntelligenceClient:
    def get_token_intelligence(self, chain, token_address):
        return {
            "smart_money_holdings": {
                "data": [
                    {
                        "wallet_address": "0xSmart",
                        "token_address": token_address,
                        "balance_usd": 100,
                    }
                ]
            },
            "tgm_holders": {"data": []},
        }


class FakeGmgnClient:
    def get_token_intelligence(self, chain, token_address):
        return {
            "token_info": {"data": {"address": token_address, "symbol": "TEST"}},
            "token_security": {"data": {"is_honeypot": "0"}},
            "top_holders": {
                "data": [
                    {
                        "wallet_address": "0xSmart",
                        "labels": ["Smart Trader"],
                        "balance_usd": "1000",
                    }
                ]
            },
            "top_traders": {
                "data": [
                    {
                        "wallet": "0xSniper",
                        "is_sniper": True,
                        "pnl_usd": "123",
                    }
                ]
            },
        }


class FailingApiClient:
    def get_token_pairs(self, chain, token_address):
        raise RuntimeError("market unavailable")

    def get_token_security(self, chain, token_address):
        raise RuntimeError("security unavailable")

    def get_contract_readonly_state(self, token_address):
        raise RuntimeError("rpc unavailable")

    def get_honeypot_status(self, chain, token_address):
        raise RuntimeError("honeypot unavailable")

    def get_token_intelligence(self, chain, token_address):
        raise RuntimeError("nansen unavailable")


ROWS_BY_EXECUTION = {
    "exec-query-trading": [
        {
            "project": "pancakeswap",
            "version": "2",
            "trades": 12,
            "unique_traders": 8,
            "volume_usd": 1500,
            "project_volume_share": 1,
            "first_trade_time": "2026-05-31 00:00:00",
        }
    ],
    "exec-query-flow": [
        {
            "bucket_5m": "2026-05-31 00:05:00",
            "trades": 10,
            "unique_traders": 7,
            "buyers": 5,
            "sellers": 2,
            "buy_volume_usd": 900,
            "sell_volume_usd": 200,
            "net_buy_usd": 700,
        }
    ],
    "exec-query-buyers": [
        {
            "buyer_rank": 1,
            "buyer": "0xBuyer",
            "remaining_ratio": 0.7,
            "buy_usd": 100,
        }
    ],
    "exec-query-funding": [
        {
            "buyer": "0xbuyer",
            "funder": "0xFunder",
            "funded_selected_early_buyers": 1,
            "wallet_age_days_at_entry": 3,
            "tx_count_before_entry": 4,
        }
    ],
}


def test_analyze_dune_token_runs_queries_and_writes_reusable_cache(tmp_path):
    config = DuneTokenAnalysisConfig(chain="bnb", cache_dir=tmp_path)
    logs = []
    client = FakeDuneClient()

    result = analyze_dune_token(
        token_address="0xabc",
        client=client,
        query_ids=QUERY_IDS,
        config=config,
        log=logs.append,
    )

    assert result.snapshot["token"]["address"] == "0xabc"
    assert result.snapshot["flow_5m"][0]["net_buy_usd"] == 700.0
    assert result.analysis.token_address == "0xabc"
    assert len(client.executed_query_ids) == 4
    assert (tmp_path / "abc" / "trading_activity.json").exists()
    assert "Cached Dune rows: trading_activity (1 rows)" in logs

    cached_result = analyze_dune_token(
        token_address="0xabc",
        client=CacheOnlyClient(),
        query_ids=QUERY_IDS,
        config=config,
        log=logs.append,
    )

    assert cached_result.snapshot == result.snapshot
    assert "Using cached Dune rows: trading_activity (1 rows)" in logs


def test_analyze_dune_token_merges_optional_api_data(tmp_path):
    result = analyze_dune_token(
        token_address="0xabc",
        client=FakeDuneClient(),
        query_ids=QUERY_IDS,
        config=DuneTokenAnalysisConfig(chain="bnb", cache_dir=tmp_path),
        market_client=FakeMarketClient(),
        security_client=FakeSecurityClient(),
        honeypot_client=FakeHoneypotClient(),
        gmgn_client=FakeGmgnClient(),
        intelligence_client=FakeIntelligenceClient(),
        rpc_client=FakeRpcClient(),
    )

    assert result.snapshot["market"]["source"] == "dexscreener"
    assert result.snapshot["market"]["liquidity_usd"] == 25000.0
    assert result.snapshot["security"]["source"] == "goplus"
    assert result.snapshot["security"]["simulation_source"] == "honeypot.is"
    assert result.snapshot["security"]["high_risk"] is True
    assert result.snapshot["contract"]["owner"] == "0x0000000000000000000000000000000000000000"
    assert result.snapshot["contract"]["owner_renounced"] is True
    assert result.snapshot["security"]["sell_tax"] == 0.05
    assert result.snapshot["security"]["honeypot_sell_tax_raw"] == 4.0
    assert result.snapshot["intelligence"]["gmgn"]["has_wallet_signal"] is True
    assert result.snapshot["intelligence"]["gmgn"]["top_trader_count"] == 1
    assert result.snapshot["intelligence"]["gmgn"]["sniper_count"] == 1
    assert result.snapshot["intelligence"]["nansen"]["has_smart_money_signal"] is True
    assert result.snapshot["holders"]["holder_count"] == 100
    assert result.analysis.risk_score >= 70


def test_analyze_dune_token_records_api_warnings_without_failing(tmp_path):
    result = analyze_dune_token(
        token_address="0xabc",
        client=FakeDuneClient(),
        query_ids=QUERY_IDS,
        config=DuneTokenAnalysisConfig(chain="bnb", cache_dir=tmp_path),
        market_client=FailingApiClient(),
        security_client=FailingApiClient(),
        honeypot_client=FailingApiClient(),
        gmgn_client=FailingApiClient(),
        intelligence_client=FailingApiClient(),
        rpc_client=FailingApiClient(),
    )

    assert result.snapshot["token"]["address"] == "0xabc"
    assert "api_warnings" in result.snapshot["data_quality"]
    assert len(result.snapshot["data_quality"]["api_warnings"]) == 6
    assert any(
        "market unavailable" in warning
        for warning in result.analysis.data_quality["warnings"]
    )


def test_dune_query_set_validates_required_queries():
    query_set = DuneQuerySet.from_mapping(QUERY_IDS)

    assert query_set.trading_activity == "query-trading"
    assert query_set.get("early_buyer_funding") == "query-funding"
    assert query_set.to_mapping() == QUERY_IDS

    with pytest.raises(RuntimeError, match="Missing Dune query ids"):
        DuneQuerySet.from_mapping({"trading_activity": "query-trading"})

    with pytest.raises(RuntimeError, match="Unknown Dune query name"):
        query_set.get("holder_snapshot")


def test_load_query_set_from_env(monkeypatch):
    monkeypatch.setenv("DUNE_QUERY_TOKEN_TRADING_ACTIVITY", "query-trading")
    monkeypatch.setenv("DUNE_QUERY_FIVE_MINUTE_FLOW", "query-flow")
    monkeypatch.setenv("DUNE_QUERY_EARLY_BUYERS", "query-buyers")
    monkeypatch.setenv("DUNE_QUERY_EARLY_BUYER_FUNDING", "query-funding")

    query_set = load_query_set_from_env()

    assert query_set == DuneQuerySet.from_mapping(QUERY_IDS)


def test_load_query_ids_from_env_reports_missing_values(monkeypatch):
    monkeypatch.delenv("DUNE_QUERY_TOKEN_TRADING_ACTIVITY", raising=False)
    monkeypatch.delenv("DUNE_QUERY_FIVE_MINUTE_FLOW", raising=False)
    monkeypatch.delenv("DUNE_QUERY_EARLY_BUYERS", raising=False)
    monkeypatch.delenv("DUNE_QUERY_EARLY_BUYER_FUNDING", raising=False)

    with pytest.raises(RuntimeError, match="Missing Dune query id environment variables"):
        load_query_ids_from_env()
