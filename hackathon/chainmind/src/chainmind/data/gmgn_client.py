"""GMGN query-only CLI client."""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class GmgnConfig:
    api_key: str | None = None
    chain: str = "bsc"
    cli_command: tuple[str, ...] = field(default_factory=lambda: ("gmgn-cli",))
    timeout_seconds: int = 60


class GmgnClient:
    def __init__(self, config: GmgnConfig | None = None) -> None:
        self.config = config or GmgnConfig()

    @classmethod
    def from_env(cls) -> "GmgnClient | None":
        api_key = (os.environ.get("GMGN_API_KEY") or "").strip()
        if not api_key:
            return None

        command = tuple(
            shlex.split((os.environ.get("GMGN_CLI_COMMAND") or "gmgn-cli").strip())
        )
        return cls(
            GmgnConfig(
                api_key=api_key,
                chain=(os.environ.get("GMGN_CHAIN") or "bsc").strip() or "bsc",
                cli_command=command or ("gmgn-cli",),
            )
        )

    def get_token_intelligence(
        self,
        *,
        token_address: str,
        limit: int = 20,
        chain: str | None = None,
    ) -> dict[str, Any]:
        return {
            "token_info": self.get_token_info(token_address=token_address, chain=chain),
            "token_security": self.get_token_security(
                token_address=token_address,
                chain=chain,
            ),
            "top_holders": self.get_token_holders(
                token_address=token_address,
                chain=chain,
                limit=limit,
            ),
            "top_traders": self.get_token_traders(
                token_address=token_address,
                chain=chain,
                limit=limit,
            ),
        }

    def get_token_info(
        self,
        *,
        token_address: str,
        chain: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        return self._run(
            "token",
            "info",
            "--chain",
            self._chain(chain),
            "--address",
            token_address,
        )

    def get_token_security(
        self,
        *,
        token_address: str,
        chain: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        return self._run(
            "token",
            "security",
            "--chain",
            self._chain(chain),
            "--address",
            token_address,
        )

    def get_token_holders(
        self,
        *,
        token_address: str,
        chain: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any] | list[Any]:
        return self._run(
            "token",
            "holders",
            "--chain",
            self._chain(chain),
            "--address",
            token_address,
            "--limit",
            str(limit),
        )

    def get_token_traders(
        self,
        *,
        token_address: str,
        chain: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any] | list[Any]:
        return self._run(
            "token",
            "traders",
            "--chain",
            self._chain(chain),
            "--address",
            token_address,
            "--limit",
            str(limit),
        )

    def get_trending_tokens(
        self,
        *,
        chain: str | None = None,
        interval: str = "1h",
        limit: int = 10,
        order_by: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        args = [
            "market",
            "trending",
            "--chain",
            self._chain(chain),
            "--interval",
            interval,
            "--limit",
            str(limit),
        ]
        if order_by:
            args.extend(["--order-by", order_by])
        return self._run(*args)

    def get_wallet_holdings(
        self,
        *,
        wallet_address: str,
        chain: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any] | list[Any]:
        return self._run(
            "portfolio",
            "holdings",
            "--chain",
            self._chain(chain),
            "--wallet",
            wallet_address,
            "--limit",
            str(limit),
        )

    def get_wallet_activity(
        self,
        *,
        wallet_address: str,
        chain: str | None = None,
        token_address: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any] | list[Any]:
        args = [
            "portfolio",
            "activity",
            "--chain",
            self._chain(chain),
            "--wallet",
            wallet_address,
            "--limit",
            str(limit),
        ]
        if token_address:
            args.extend(["--token", token_address])
        return self._run(*args)

    def get_wallet_stats(
        self,
        *,
        wallet_address: str,
        chain: str | None = None,
    ) -> dict[str, Any] | list[Any]:
        return self._run(
            "portfolio",
            "stats",
            "--chain",
            self._chain(chain),
            "--wallet",
            wallet_address,
        )

    def _chain(self, chain: str | None) -> str:
        value = (chain or self.config.chain).strip().lower() or "bsc"
        if value == "bnb":
            return "bsc"
        return value

    def _run(self, *args: str) -> dict[str, Any] | list[Any]:
        if not self.config.api_key:
            raise RuntimeError("GMGN_API_KEY is not set.")

        command = [*self._resolved_cli_command(), *args, "--raw"]
        env = dict(os.environ)
        env["GMGN_API_KEY"] = self.config.api_key
        env.pop("GMGN_PRIVATE_KEY", None)
        env.pop("GMGN_PRIVATE_KEY_PATH", None)

        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=self.config.timeout_seconds,
                env=env,
                check=False,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "gmgn-cli executable was not found. Install gmgn-cli or set GMGN_CLI_COMMAND."
            ) from exc

        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout or "").strip()
            detail = detail.replace(self.config.api_key, "***")
            raise RuntimeError(f"GMGN CLI failed: {detail[:200] or 'no error detail'}")

        return _parse_json_output(completed.stdout)

    def _resolved_cli_command(self) -> list[str]:
        executable, *rest = self.config.cli_command
        resolved = shutil.which(executable)
        return [resolved or executable, *rest]


def _parse_json_output(output: str) -> dict[str, Any] | list[Any]:
    text = output.strip()
    if not text:
        raise RuntimeError("GMGN CLI returned empty output.")

    candidates = [text, *reversed(text.splitlines())]
    for candidate in candidates:
        candidate = candidate.strip()
        if not candidate or candidate[0] not in "[{":
            continue
        try:
            payload = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict | list):
            return payload

    raise RuntimeError("GMGN CLI output is not valid JSON.")
