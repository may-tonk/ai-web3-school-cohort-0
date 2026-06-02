"""File-backed Dune query result cache."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DuneQueryCache:
    cache_dir: Path

    def load_rows(
        self,
        *,
        token_address: str,
        query_name: str,
    ) -> list[dict[str, Any]] | None:
        path = self.rows_path(token_address=token_address, query_name=query_name)
        if not path.exists():
            return None

        payload = json.loads(path.read_text(encoding="utf-8"))
        rows = payload.get("rows", [])
        if not isinstance(rows, list):
            raise RuntimeError(f"Invalid Dune cache rows: {path}")
        return [dict(row) for row in rows]

    def save_rows(
        self,
        *,
        token_address: str,
        query_name: str,
        query_id: str,
        execution_id: str,
        rows: list[dict[str, Any]],
    ) -> None:
        path = self.rows_path(token_address=token_address, query_name=query_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "token_address": token_address,
                    "query_name": query_name,
                    "query_id": query_id,
                    "execution_id": execution_id,
                    "rows": rows,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def load_execution_id(
        self,
        *,
        token_address: str,
        query_name: str,
    ) -> str | None:
        path = self.execution_path(token_address=token_address, query_name=query_name)
        if not path.exists():
            return None

        payload = json.loads(path.read_text(encoding="utf-8"))
        return str(payload["execution_id"])

    def save_execution_id(
        self,
        *,
        token_address: str,
        query_name: str,
        query_id: str,
        execution_id: str,
    ) -> None:
        path = self.execution_path(token_address=token_address, query_name=query_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "token_address": token_address,
                    "query_name": query_name,
                    "query_id": query_id,
                    "execution_id": execution_id,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def rows_path(self, *, token_address: str, query_name: str) -> Path:
        return self._token_dir(token_address) / f"{query_name}.json"

    def execution_path(self, *, token_address: str, query_name: str) -> Path:
        return self._token_dir(token_address) / f"{query_name}.execution.json"

    def _token_dir(self, token_address: str) -> Path:
        token = token_address.lower().replace("0x", "")
        return self.cache_dir / token
