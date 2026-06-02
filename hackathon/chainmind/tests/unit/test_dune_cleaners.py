import math

from chainmind.cleaning.dune_cleaners import (
    clean_address,
    clean_float,
    clean_int,
    clean_non_negative_float,
    clean_string,
    clean_timestamp,
)


def test_clean_address_normalizes_case_and_empty_values():
    assert clean_address("  0xAbC  ") == "0xabc"
    assert clean_address("") is None
    assert clean_address(None) is None


def test_clean_float_rejects_invalid_and_non_finite_values():
    assert clean_float("12.5") == 12.5
    assert clean_float(7) == 7.0
    assert clean_float(True) is None
    assert clean_float("not-a-number") is None
    assert clean_float(math.inf) is None
    assert clean_float(math.nan) is None


def test_clean_int_converts_numeric_values():
    assert clean_int("12.9") == 12
    assert clean_int(None) is None
    assert clean_int("bad") is None


def test_clean_non_negative_float_clamps_negative_values():
    assert clean_non_negative_float("1.5") == 1.5
    assert clean_non_negative_float("-1.5") == 0
    assert clean_non_negative_float("bad") is None


def test_clean_string_and_timestamp_trim_empty_values():
    assert clean_string("  pancakeswap  ") == "pancakeswap"
    assert clean_string(" ") is None
    assert clean_timestamp(" 2026-05-31 00:00:00 ") == "2026-05-31 00:00:00"
