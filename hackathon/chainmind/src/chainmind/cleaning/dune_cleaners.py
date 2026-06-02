"""Shared cleaners for Dune query rows."""

from __future__ import annotations

import math
from typing import Any


def clean_address(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip().lower()
    if not text:
        return None
    return text


def clean_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None

    try:
        result = float(value)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(result):
        return None
    return result


def clean_non_negative_float(value: Any) -> float | None:
    result = clean_float(value)
    if result is None:
        return None
    return max(result, 0)


def clean_int(value: Any) -> int | None:
    result = clean_float(value)
    if result is None:
        return None
    return int(result)


def clean_string(value: Any) -> str | None:
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None
    return text


def clean_timestamp(value: Any) -> str | None:
    return clean_string(value)
