from chainmind.data.bnb_rpc_client import (
    BnbRpcClient,
    BnbRpcConfig,
    OWNER_SIGNATURE,
    TOTAL_SUPPLY_SIGNATURE,
)


def test_bnb_rpc_client_eth_call_builds_json_rpc_payload(monkeypatch):
    calls = []

    def fake_post_json(url, **kwargs):
        calls.append((url, kwargs))
        return {"jsonrpc": "2.0", "id": 1, "result": "0x2a"}

    monkeypatch.setattr("chainmind.data.bnb_rpc_client.post_json", fake_post_json)

    client = BnbRpcClient(BnbRpcConfig(rpc_url="https://rpc.example"))
    result = client.eth_call(contract="0xToken", data=TOTAL_SUPPLY_SIGNATURE)

    assert result == "0x2a"
    assert calls[0][0] == "https://rpc.example"
    assert calls[0][1]["payload"]["method"] == "eth_call"
    assert calls[0][1]["payload"]["params"][0] == {
        "to": "0xToken",
        "data": TOTAL_SUPPLY_SIGNATURE,
    }


def test_bnb_rpc_client_decodes_optional_address_and_uint(monkeypatch):
    owner_result = (
        "0x000000000000000000000000"
        "1111111111111111111111111111111111111111"
    )

    def fake_post_json(url, **kwargs):
        data = kwargs["payload"]["params"][0]["data"]
        if data == OWNER_SIGNATURE:
            return {"result": owner_result}
        return {"result": "0x64"}

    monkeypatch.setattr("chainmind.data.bnb_rpc_client.post_json", fake_post_json)

    client = BnbRpcClient(BnbRpcConfig(rpc_url="https://rpc.example"))
    state = client.get_contract_readonly_state("0xToken")

    assert state["owner"] == "0x1111111111111111111111111111111111111111"
    assert state["total_supply"] == 100
