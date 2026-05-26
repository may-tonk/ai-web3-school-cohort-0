"""Dune API client for saved query execution."""

from __future__ import annotations

import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover - requests is an optional transport.
    requests = None  # type: ignore[assignment]


@dataclass(frozen=True)
class DuneConfig:
    api_key: str
    base_url: str = "https://api.dune.com/api/v1"
    poll_interval_seconds: int = 5
    timeout_seconds: int = 180
    max_result_rows: int = 5000
    force_tls12: bool = True
    request_timeout_seconds: int = 30
    max_retries: int = 6
    retry_backoff_seconds: int = 5


class DuneClient:
    def __init__(self, config: DuneConfig) -> None:
        self.config = config

    def run_query(self, query_id: str, token_address: str) -> list[dict[str, Any]]:
        execution_id = self.execute_query(query_id, token_address)
        self.wait_for_execution(execution_id)
        return self.get_execution_results(execution_id)

    def execute_query(self, query_id: str, token_address: str) -> str:
        payload = {
            "query_parameters": {
                "token_address": token_address,
            }
        }
        response = self._request_json(
            "POST",
            f"/query/{query_id}/execute",
            payload=payload,
        )
        execution_id = response.get("execution_id")
        if not execution_id:
            raise RuntimeError(f"Dune execute response missing execution_id: {response}")
        return str(execution_id)

    def wait_for_execution(self, execution_id: str) -> None:
        deadline = time.monotonic() + self.config.timeout_seconds
        while True:
            response = self._request_json("GET", f"/execution/{execution_id}/status")
            state = str(response.get("state", "")).upper()

            if state in {"QUERY_STATE_COMPLETED", "COMPLETED"}:
                return
            if state in {
                "QUERY_STATE_FAILED",
                "QUERY_STATE_CANCELLED",
                "FAILED",
                "CANCELLED",
            }:
                raise RuntimeError(f"Dune execution failed: {response}")
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Dune execution timed out: {execution_id}")

            time.sleep(self.config.poll_interval_seconds)

    def get_execution_results(self, execution_id: str) -> list[dict[str, Any]]:
        response = self._request_json(
            "GET",
            f"/execution/{execution_id}/results",
            query={
                "limit": str(self.config.max_result_rows),
            },
        )
        rows = (
            response.get("result", {})
            .get("rows", [])
        )
        if not isinstance(rows, list):
            raise RuntimeError(f"Dune result rows missing or invalid: {response}")
        return [dict(row) for row in rows]

    def _request_json(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        query: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.config.base_url}{path}"
        if query:
            url = f"{url}?{urllib.parse.urlencode(query)}"

        data = None
        headers = {
            "X-Dune-API-Key": self.config.api_key,
            "Content-Type": "application/json",
            "Connection": "close",
        }
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")

        request = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method,
        )

        transient_errors = self._transient_errors()
        for attempt in range(self.config.max_retries + 1):
            try:
                if requests is not None:
                    return self._request_json_with_requests(
                        url=url,
                        method=method,
                        headers=headers,
                        payload=payload,
                    )

                return self._request_json_with_urllib(request)
            except urllib.error.HTTPError as exc:
                body = exc.read().decode("utf-8", errors="replace")
                raise RuntimeError(f"Dune API HTTP {exc.code}: {body}") from exc
            except transient_errors as exc:
                if attempt >= self.config.max_retries:
                    raise RuntimeError(f"Dune API request failed after retries: {exc}") from exc
                time.sleep(self.config.retry_backoff_seconds * (attempt + 1))

        raise RuntimeError("Dune API request failed unexpectedly.")

    def _request_json_with_requests(
        self,
        *,
        url: str,
        method: str,
        headers: dict[str, str],
        payload: dict[str, Any] | None,
    ) -> dict[str, Any]:
        assert requests is not None
        response = requests.request(
            method,
            url,
            headers=headers,
            json=payload,
            timeout=self.config.request_timeout_seconds,
        )
        if response.status_code >= 400:
            raise RuntimeError(f"Dune API HTTP {response.status_code}: {response.text}")
        return dict(response.json())

    def _request_json_with_urllib(
        self,
        request: urllib.request.Request,
    ) -> dict[str, Any]:
        with urllib.request.urlopen(
            request,
            timeout=self.config.request_timeout_seconds,
            context=self._ssl_context(),
        ) as response:
            return json.loads(response.read().decode("utf-8"))

    def _transient_errors(self) -> tuple[type[BaseException], ...]:
        errors: tuple[type[BaseException], ...] = (
            TimeoutError,
            urllib.error.URLError,
            ssl.SSLError,
        )
        if requests is not None:
            errors = errors + (requests.exceptions.RequestException,)
        return errors

    def _ssl_context(self) -> ssl.SSLContext | None:
        if not self.config.force_tls12:
            return None

        context = ssl.create_default_context()
        if hasattr(ssl, "TLSVersion"):
            context.minimum_version = ssl.TLSVersion.TLSv1_2
            context.maximum_version = ssl.TLSVersion.TLSv1_2
        return context
