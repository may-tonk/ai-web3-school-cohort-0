"""Honeypot.is API client."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from chainmind.data.chain_ids import honeypot_chain_id
from chainmind.data.http_json import get_json


@dataclass(frozen=True)
class HoneypotConfig:
    base_url: str = "https://api.honeypot.is"
    timeout_seconds: int = 45


class HoneypotClient:
    def __init__(self, config: HoneypotConfig | None = None) -> None:
        self.config = config or HoneypotConfig()

    @classmethod
    def from_env(cls) -> "HoneypotClient":
        return cls(
            HoneypotConfig(
                base_url=os.environ.get(
                    "HONEYPOT_BASE_URL",
                    "https://api.honeypot.is",
                ).rstrip("/"),
            )
        )

    def get_honeypot_status(self, *, chain: str, token_address: str) -> dict[str, Any]:
        chain_id = honeypot_chain_id(chain)
        payload = get_json(
            f"{self.config.base_url}/v2/IsHoneypot",
            query={"address": token_address, "chainID": chain_id},
            timeout_seconds=self.config.timeout_seconds,
        )
        if not isinstance(payload, dict):
            raise RuntimeError(f"Honeypot.is response is not an object: {payload}")
        return payload
