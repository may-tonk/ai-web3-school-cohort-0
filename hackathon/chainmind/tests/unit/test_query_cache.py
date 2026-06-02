import json

import pytest

from chainmind.data.query_cache import DuneQueryCache


def test_dune_query_cache_saves_and_loads_rows_and_execution_id(tmp_path):
    cache = DuneQueryCache(tmp_path)
    rows = [{"buyer": "0xabc", "net_buy_usd": 123}]

    cache.save_execution_id(
        token_address="0xABC",
        query_name="five_minute_flow",
        query_id="query-1",
        execution_id="exec-1",
    )
    cache.save_rows(
        token_address="0xABC",
        query_name="five_minute_flow",
        query_id="query-1",
        execution_id="exec-1",
        rows=rows,
    )

    assert cache.load_execution_id(
        token_address="0xabc",
        query_name="five_minute_flow",
    ) == "exec-1"
    assert cache.load_rows(
        token_address="0xabc",
        query_name="five_minute_flow",
    ) == rows
    assert cache.rows_path(
        token_address="0xABC",
        query_name="five_minute_flow",
    ) == tmp_path / "abc" / "five_minute_flow.json"


def test_dune_query_cache_returns_none_for_missing_entries(tmp_path):
    cache = DuneQueryCache(tmp_path)

    assert cache.load_rows(token_address="0xabc", query_name="missing") is None
    assert cache.load_execution_id(token_address="0xabc", query_name="missing") is None


def test_dune_query_cache_rejects_invalid_rows_payload(tmp_path):
    cache = DuneQueryCache(tmp_path)
    path = cache.rows_path(token_address="0xabc", query_name="broken")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"rows": {"not": "a list"}}),
        encoding="utf-8",
    )

    with pytest.raises(RuntimeError, match="Invalid Dune cache rows"):
        cache.load_rows(token_address="0xabc", query_name="broken")
