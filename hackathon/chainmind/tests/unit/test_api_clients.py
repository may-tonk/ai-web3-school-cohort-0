from chainmind.data.dexscreener_client import DexScreenerClient, DexScreenerConfig
from chainmind.data.gmgn_client import GmgnClient, GmgnConfig
from chainmind.data.goplus_client import GoPlusClient, GoPlusConfig
from chainmind.data.honeypot_client import HoneypotClient, HoneypotConfig
from chainmind.data.nansen_client import NansenClient, NansenConfig


def test_dexscreener_client_builds_token_pairs_request(monkeypatch):
    calls = []

    def fake_get_json(url, **kwargs):
        calls.append((url, kwargs))
        return [{"pairAddress": "0xpair"}]

    monkeypatch.setattr("chainmind.data.dexscreener_client.get_json", fake_get_json)

    client = DexScreenerClient(DexScreenerConfig(base_url="https://example.dex"))
    rows = client.get_token_pairs(chain="bnb", token_address="0xToken")

    assert rows == [{"pairAddress": "0xpair"}]
    assert calls[0][0] == "https://example.dex/token-pairs/v1/bsc/0xToken"


def test_goplus_client_builds_token_security_request_with_optional_key(monkeypatch):
    calls = []

    def fake_get_json(url, **kwargs):
        calls.append((url, kwargs))
        return {"code": 1, "result": {}}

    monkeypatch.setattr("chainmind.data.goplus_client.get_json", fake_get_json)

    client = GoPlusClient(
        GoPlusConfig(base_url="https://example.goplus", api_key="secret")
    )
    payload = client.get_token_security(chain="bnb", token_address="0xToken")

    assert payload == {"code": 1, "result": {}}
    assert calls[0][0] == "https://example.goplus/api/v1/token_security/56"
    assert calls[0][1]["query"] == {"contract_addresses": "0xToken"}
    assert calls[0][1]["headers"] == {"Authorization": "Bearer secret"}


def test_goplus_client_from_env_reads_access_token(monkeypatch):
    monkeypatch.setenv("GOPLUS_BASE_URL", "https://example.goplus/")
    monkeypatch.setenv("GOPLUS_ACCESS_TOKEN", "access-token")

    client = GoPlusClient.from_env()

    assert client.config.base_url == "https://example.goplus"
    assert client.config.api_key == "access-token"


def test_gmgn_client_from_env_reads_query_credentials_only(monkeypatch):
    monkeypatch.setenv("GMGN_API_KEY", "gmgn-key")
    monkeypatch.setenv("GMGN_CHAIN", "bsc")
    monkeypatch.setenv("GMGN_CLI_COMMAND", "npx gmgn-cli")
    monkeypatch.setenv("GMGN_PRIVATE_KEY_PATH", "runtime/keys/private.pem")

    client = GmgnClient.from_env()

    assert client is not None
    assert client.config.api_key == "gmgn-key"
    assert client.config.chain == "bsc"
    assert client.config.cli_command == ("npx", "gmgn-cli")


def test_gmgn_client_runs_query_only_cli_and_strips_private_key_env(monkeypatch):
    calls = []

    class Completed:
        returncode = 0
        stdout = '{"data":[{"address":"0xToken"}]}'
        stderr = ""

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return Completed()

    monkeypatch.setattr("chainmind.data.gmgn_client.subprocess.run", fake_run)
    monkeypatch.setenv("GMGN_PRIVATE_KEY_PATH", "runtime/keys/private.pem")
    monkeypatch.setenv("GMGN_PRIVATE_KEY", "private-key")

    client = GmgnClient(
        GmgnConfig(
            api_key="gmgn-key",
            chain="bsc",
            cli_command=("gmgn-cli",),
            timeout_seconds=12,
        )
    )
    payload = client.get_trending_tokens(limit=3)

    assert payload == {"data": [{"address": "0xToken"}]}
    assert calls[0][0] == [
        "gmgn-cli",
        "market",
        "trending",
        "--chain",
        "bsc",
        "--interval",
        "1h",
        "--limit",
        "3",
        "--raw",
    ]
    assert calls[0][1]["timeout"] == 12
    assert calls[0][1]["env"]["GMGN_API_KEY"] == "gmgn-key"
    assert "GMGN_PRIVATE_KEY_PATH" not in calls[0][1]["env"]
    assert "GMGN_PRIVATE_KEY" not in calls[0][1]["env"]


def test_gmgn_client_builds_token_intelligence_queries(monkeypatch):
    commands = []

    class Completed:
        returncode = 0
        stdout = '{"ok":true}'
        stderr = ""

    def fake_run(command, **kwargs):
        commands.append(command)
        return Completed()

    monkeypatch.setattr("chainmind.data.gmgn_client.subprocess.run", fake_run)

    client = GmgnClient(GmgnConfig(api_key="gmgn-key", cli_command=("gmgn-cli",)))
    payload = client.get_token_intelligence(token_address="0xToken", limit=5)

    assert payload == {
        "token_info": {"ok": True},
        "token_security": {"ok": True},
        "top_holders": {"ok": True},
        "top_traders": {"ok": True},
    }
    assert commands[0][:6] == ["gmgn-cli", "token", "info", "--chain", "bsc", "--address"]
    assert commands[1][:6] == [
        "gmgn-cli",
        "token",
        "security",
        "--chain",
        "bsc",
        "--address",
    ]
    assert commands[2][-3:] == ["--limit", "5", "--raw"]
    assert commands[3][-3:] == ["--limit", "5", "--raw"]


def test_honeypot_client_builds_status_request(monkeypatch):
    calls = []

    def fake_get_json(url, **kwargs):
        calls.append((url, kwargs))
        return {"honeypotResult": {"isHoneypot": False}}

    monkeypatch.setattr("chainmind.data.honeypot_client.get_json", fake_get_json)

    client = HoneypotClient(HoneypotConfig(base_url="https://example.honeypot"))
    payload = client.get_honeypot_status(chain="bnb", token_address="0xToken")

    assert payload == {"honeypotResult": {"isHoneypot": False}}
    assert calls[0][0] == "https://example.honeypot/v2/IsHoneypot"
    assert calls[0][1]["query"] == {"address": "0xToken", "chainID": "56"}


def test_nansen_client_builds_token_intelligence_requests(monkeypatch):
    calls = []

    def fake_post_json(url, **kwargs):
        calls.append((url, kwargs))
        return {"data": []}

    monkeypatch.setattr("chainmind.data.nansen_client.post_json", fake_post_json)

    client = NansenClient(
        NansenConfig(base_url="https://example.nansen/api/v1", api_key="secret")
    )
    payload = client.get_token_intelligence(
        chain="bnb",
        token_address="0xToken",
        per_page=3,
    )

    assert payload == {
        "smart_money_holdings": {"data": []},
        "tgm_holders": {"data": []},
    }
    assert calls[0][0] == "https://example.nansen/api/v1/smart-money/holdings"
    assert calls[0][1]["payload"]["chains"] == ["bnb"]
    assert calls[0][1]["payload"]["filters"] == {"token_address": ["0xToken"]}
    assert calls[0][1]["headers"] == {"apiKey": "secret"}
    assert calls[1][0] == "https://example.nansen/api/v1/tgm/holders"
    assert calls[1][1]["payload"]["token_address"] == "0xToken"
