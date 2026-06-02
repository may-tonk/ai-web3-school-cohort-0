"""Nansen API client."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from chainmind.data.chain_ids import nansen_chain_id
from chainmind.data.http_json import post_json


@dataclass(frozen=True)
class NansenConfig:
    base_url: str = "https://api.nansen.ai/api/v1"
    api_key: str | None = None
    timeout_seconds: int = 60


class NansenClient:
    def __init__(self, config: NansenConfig | None = None) -> None:
        self.config = config or NansenConfig()

    @classmethod
    def from_env(cls) -> "NansenClient | None":
        api_key = os.environ.get("NANSEN_API_KEY") or None
        if not api_key:
            return None
        return cls(
            NansenConfig(
                base_url=os.environ.get(
                    "NANSEN_BASE_URL",
                    "https://api.nansen.ai/api/v1",
                ).rstrip("/"),
                api_key=api_key,
            )
        )

    def get_token_intelligence(
        self,
        *,
        chain: str,
        token_address: str,
        per_page: int = 5,
    ) -> dict[str, Any]:
        return {
            "smart_money_holdings": self.get_smart_money_holdings(
                chain=chain,
                token_address=token_address,
                per_page=per_page,
            ),
            "tgm_holders": self.get_tgm_holders(
                chain=chain,
                token_address=token_address,
                per_page=per_page,
            ),
        }

    def get_smart_money_holdings(
        self,
        *,
        chain: str,
        token_address: str,
        per_page: int = 5,
    ) -> dict[str, Any]:
        chain_id = nansen_chain_id(chain)
        return self._post(
            "/smart-money/holdings",
            {
                "chains": [chain_id],
                "filters": {"token_address": [token_address]},
                "pagination": {"page": 1, "per_page": per_page},
            },
        )

    def get_tgm_holders(
        self,
        *,
        chain: str,
        token_address: str,
        per_page: int = 5,
    ) -> dict[str, Any]:
        chain_id = nansen_chain_id(chain)
        return self._post(
            "/tgm/holders",
            {
                "chain": chain_id,
                "token_address": token_address,
                "label_type": "smart_money",
                "filters": {},
                "pagination": {"page": 1, "per_page": per_page},
                "premium_labels": False,
            },
        )

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        if not self.config.api_key:
            raise RuntimeError("NANSEN_API_KEY is not set.")

        response = post_json(
            f"{self.config.base_url}{path}",
            payload=payload,
            headers={"apiKey": self.config.api_key},
            timeout_seconds=self.config.timeout_seconds,
        )
        if not isinstance(response, dict):
            raise RuntimeError(f"Nansen response is not an object: {response}")
        return response
