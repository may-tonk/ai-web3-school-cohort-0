"""Small JSON HTTP helper for API clients."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


def get_json(
    url: str,
    *,
    query: dict[str, str] | None = None,
    headers: dict[str, str] | None = None,
    timeout_seconds: int = 30,
    retries: int = 2,
) -> dict[str, Any] | list[Any]:
    if query:
        url = f"{url}?{urllib.parse.urlencode(query)}"

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "ChainMind/0.1",
            **(headers or {}),
        },
        method="GET",
    )
    return _open_json(request, url=url, timeout_seconds=timeout_seconds, retries=retries)


def post_json(
    url: str,
    *,
    payload: dict[str, Any],
    headers: dict[str, str] | None = None,
    timeout_seconds: int = 30,
    retries: int = 2,
) -> dict[str, Any] | list[Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "ChainMind/0.1",
            **(headers or {}),
        },
        method="POST",
    )
    return _open_json(request, url=url, timeout_seconds=timeout_seconds, retries=retries)


def _open_json(
    request: urllib.request.Request,
    *,
    url: str,
    timeout_seconds: int,
    retries: int,
) -> dict[str, Any] | list[Any]:
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code not in {429, 500, 502, 503, 504} or attempt >= retries:
                body = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"HTTP {exc.code} for {url}: {body}") from exc
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt >= retries:
                raise RuntimeError(f"HTTP request failed for {url}: {exc}") from exc

        time.sleep(0.5 * (attempt + 1))

    raise RuntimeError(f"HTTP request failed for {url}: {last_error}")
