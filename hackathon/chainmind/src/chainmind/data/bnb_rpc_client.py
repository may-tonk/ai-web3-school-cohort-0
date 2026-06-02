"""BNB Chain JSON-RPC read-only client."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from chainmind.data.http_json import post_json


OWNER_SIGNATURE = "0x8da5cb5b"
TOTAL_SUPPLY_SIGNATURE = "0x18160ddd"
BUY_TAX_RATE_SIGNATURE = "0x6d9a640a"
SELL_TAX_RATE_SIGNATURE = "0xe590cf91"


@dataclass(frozen=True)
class BnbRpcConfig:
    rpc_url: str
    timeout_seconds: int = 30


class BnbRpcClient:
    def __init__(self, config: BnbRpcConfig) -> None:
        self.config = config
        self._request_id = 0

    @classmethod
    def from_env(cls) -> "BnbRpcClient | None":
        rpc_url = os.environ.get("BNB_RPC_URL")
        if not rpc_url:
            return None
        return cls(BnbRpcConfig(rpc_url=rpc_url))

    def get_contract_readonly_state(self, token_address: str) -> dict[str, Any]:
        return {
            "source": "bnb_rpc",
            "owner": self.call_optional_address(token_address, OWNER_SIGNATURE),
            "total_supply": self.call_optional_uint(token_address, TOTAL_SUPPLY_SIGNATURE),
            "buy_tax_rate": self.call_optional_uint(token_address, BUY_TAX_RATE_SIGNATURE),
            "sell_tax_rate": self.call_optional_uint(token_address, SELL_TAX_RATE_SIGNATURE),
        }

    def call_optional_address(self, contract: str, data: str) -> str | None:
        result = self.call_optional(contract, data)
        if not result or result == "0x":
            return None
        hex_value = result.removeprefix("0x")
        if len(hex_value) < 40:
            return None
        return f"0x{hex_value[-40:]}".lower()

    def call_optional_uint(self, contract: str, data: str) -> int | None:
        result = self.call_optional(contract, data)
        if not result or result == "0x":
            return None
        try:
            return int(result, 16)
        except ValueError:
            return None

    def call_optional(self, contract: str, data: str) -> str | None:
        try:
            return self.eth_call(contract=contract, data=data)
        except RuntimeError:
            return None

    def eth_call(self, *, contract: str, data: str) -> str:
        self._request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "id": self._request_id,
            "method": "eth_call",
            "params": [
                {
                    "to": contract,
                    "data": data,
                },
                "latest",
            ],
        }
        response = post_json(
            self.config.rpc_url,
            payload=payload,
            timeout_seconds=self.config.timeout_seconds,
        )
        if not isinstance(response, dict):
            raise RuntimeError(f"RPC response is not an object: {response}")
        if response.get("error"):
            raise RuntimeError(f"RPC eth_call failed: {response['error']}")
        result = response.get("result")
        if not isinstance(result, str):
            raise RuntimeError(f"RPC eth_call result is invalid: {response}")
        return result
