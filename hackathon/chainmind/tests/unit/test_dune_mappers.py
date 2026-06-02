from chainmind.data.dune_mappers import build_snapshot_from_dune_results


def test_build_snapshot_from_dune_results_maps_core_fields():
    snapshot = build_snapshot_from_dune_results(
        token_address="0xabc",
        chain="bnb",
        trading_activity_rows=[
            {
                "project": "pancakeswap",
                "version": "2",
                "trades": 10,
                "unique_traders": 7,
                "volume_usd": 1234.5,
                "project_volume_share": 1,
                "first_trade_time": "2026-05-26 00:00:00",
            }
        ],
        flow_5m_rows=[
            {
                "bucket_5m": "2026-05-26 00:05:00",
                "trades": 20,
                "unique_traders": 10,
                "buyers": 6,
                "sellers": 4,
                "buy_volume_usd": 1000,
                "sell_volume_usd": 500,
                "net_buy_usd": 500,
            }
        ],
        early_buyer_rows=[
            {
                "buyer_rank": 1,
                "buyer": "0xBuyer",
                "remaining_ratio": 0.8,
                "buy_usd": 100,
            }
        ],
        funding_rows=[
            {
                "buyer": "0xbuyer",
                "funder": "0xFunder",
                "funded_selected_early_buyers": 2,
                "wallet_age_days_at_entry": 0,
                "tx_count_before_entry": 1,
            }
        ],
    )

    assert snapshot["token"]["address"] == "0xabc"
    assert snapshot["market"]["volume_source_dune_usd"] == 1234.5
    assert snapshot["flow_5m"][0]["net_buy_usd"] == 500.0
    assert snapshot["early_buyers"][0]["first_funder"] == "0xfunder"
    assert snapshot["funding"]["shared_funders"][0]["funded_early_buyers"] == 2


def test_build_snapshot_from_dune_results_handles_dirty_numeric_rows():
    snapshot = build_snapshot_from_dune_results(
        token_address="0xabc",
        chain="bnb",
        trading_activity_rows=[
            {
                "project": "broken",
                "volume_usd": "nan",
                "trades": "bad",
                "unique_traders": "",
            },
            {
                "project": "pancakeswap",
                "volume_usd": "2500",
                "trades": "10",
                "unique_traders": "8",
            },
        ],
        flow_5m_rows=[
            {
                "bucket_5m": " 2026-05-26 00:05:00 ",
                "trades": "bad",
                "net_buy_usd": "inf",
            }
        ],
        early_buyer_rows=[
            {
                "buyer": " 0xBuyer ",
                "remaining_ratio": "nan",
            }
        ],
        funding_rows=[
            {
                "buyer": " 0xbuyer ",
                "funder": "",
            }
        ],
    )

    assert snapshot["market"]["project"] == "pancakeswap"
    assert snapshot["market"]["volume_source_dune_usd"] == 2500.0
    assert snapshot["flow_5m"][0]["trades"] is None
    assert snapshot["flow_5m"][0]["net_buy_usd"] is None
    assert snapshot["early_buyers"][0]["wallet"] == "0xbuyer"
    assert snapshot["early_buyers"][0]["remaining_ratio"] is None


def test_build_snapshot_from_dune_results_clamps_negative_remaining_ratio():
    snapshot = build_snapshot_from_dune_results(
        token_address="0xabc",
        chain="bnb",
        trading_activity_rows=[],
        flow_5m_rows=[],
        early_buyer_rows=[
            {
                "buyer": "0xBuyer",
                "current_balance": "-5",
                "remaining_ratio": "-0.2",
            }
        ],
        funding_rows=[],
    )

    assert snapshot["early_buyers"][0]["current_balance"] == -5.0
    assert snapshot["early_buyers"][0]["remaining_ratio"] == 0
