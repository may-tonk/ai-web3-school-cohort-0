"""DexScreener API client."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from chainmind.data.chain_ids import dexscreener_chain_id
from chainmind.data.http_json import get_json


@dataclass(frozen=True)
class DexScreenerConfig:
    base_url: str = "https://api.dexscreener.com"
    timeout_seconds: int = 30


class DexScreenerClient:
    def __init__(self, config: DexScreenerConfig | None = None) -> None:
        self.config = config or DexScreenerConfig()

    @classmethod
    def from_env(cls) -> "DexScreenerClient":
        return cls(
            DexScreenerConfig(
                base_url=os.environ.get(
                    "DEXSCREENER_BASE_URL",
                    "https://api.dexscreener.com",
                ).rstrip("/"),
            )
        )

    def get_token_pairs(self, *, chain: str, token_address: str) -> list[dict[str, Any]]:
        chain_id = dexscreener_chain_id(chain)
        url = f"{self.config.base_url}/token-pairs/v1/{chain_id}/{token_address}"
        payload = get_json(url, timeout_seconds=self.config.timeout_seconds)
        if not isinstance(payload, list):
            raise RuntimeError(f"DexScreener token pairs response is not a list: {payload}")
        return [dict(item) for item in payload]
