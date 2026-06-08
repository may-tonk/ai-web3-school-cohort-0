from chainmind.domain import TokenSnapshot, infer_token_profile


def test_infer_token_profile_respects_explicit_profile():
    profile = infer_token_profile(
        {
            "token_profile": {
                "type": "infrastructure",
                "source": "label",
                "reason": "Known ecosystem asset.",
            }
        }
    )

    assert profile["type"] == "infrastructure"
    assert profile["source"] == "label"


def test_infer_token_profile_detects_mainstream_control_by_address():
    profile = infer_token_profile(
        {
            "token": {
                "address": "0x55d398326f99059ff775485246999027b3197955",
                "symbol": "UNKNOWN",
                "chain": "bnb",
            }
        }
    )

    assert profile["type"] == "mainstream_control"
    assert profile["source"] == "known_address"


def test_infer_token_profile_detects_infrastructure_by_market_symbol():
    profile = infer_token_profile(
        {
            "token": {"address": "0xToken", "symbol": "UNKNOWN", "chain": "bnb"},
            "market": {"base_token_symbol": "WBNB"},
        }
    )

    assert profile["type"] == "infrastructure"
    assert profile["source"] == "symbol_heuristic"


def test_token_snapshot_from_mapping_adds_default_profile():
    snapshot = TokenSnapshot.from_mapping(
        {
            "token": {
                "address": "0xToken",
                "symbol": "MEME",
                "chain": "bnb",
            }
        }
    )

    assert snapshot.profile_type == "meme_candidate"
    assert snapshot.token_profile["source"] == "default"
