"""GoPlus Token Security API client."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from chainmind.data.chain_ids import goplus_chain_id
from chainmind.data.http_json import get_json


@dataclass(frozen=True)
class GoPlusConfig:
    base_url: str = "https://api.gopluslabs.io"
    api_key: str | None = None
    timeout_seconds: int = 30


class GoPlusClient:
    def __init__(self, config: GoPlusConfig | None = None) -> None:
        self.config = config or GoPlusConfig()

    @classmethod
    def from_env(cls) -> "GoPlusClient":
        api_key = os.environ.get("GOPLUS_ACCESS_TOKEN") or None
        return cls(
            GoPlusConfig(
                base_url=os.environ.get(
                    "GOPLUS_BASE_URL",
                    "https://api.gopluslabs.io",
                ).rstrip("/"),
                api_key=api_key,
            )
        )

    def get_token_security(self, *, chain: str, token_address: str) -> dict[str, Any]:
        chain_id = goplus_chain_id(chain)
        url = f"{self.config.base_url}/api/v1/token_security/{chain_id}"
        headers = {}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        payload = get_json(
            url,
            query={"contract_addresses": token_address},
            headers=headers,
            timeout_seconds=self.config.timeout_seconds,
        )
        if not isinstance(payload, dict):
            raise RuntimeError(f"GoPlus token security response is not an object: {payload}")
        return payload
