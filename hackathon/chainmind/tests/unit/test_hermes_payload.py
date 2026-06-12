from chainmind.alerts.channels import build_hermes_payload


def test_build_hermes_payload_wraps_report_prompt_and_delivery_decision():
    snapshot = {
        "token": {"address": "0xToken", "symbol": "MEME", "chain": "bnb"},
        "market": {"base_token_symbol": "MEME"},
        "token_profile": {
            "type": "meme_candidate",
            "source": "default",
            "reason": "No mainstream or infrastructure context was detected.",
        },
    }
    analysis = {
        "token_address": "0xToken",
        "symbol": "MEME",
        "chain": "bnb",
        "grade": "A",
        "action": "manual_review",
        "risk_score": 25,
        "security_score": 0,
        "entity_cluster_score": 0,
        "opportunity_score": 75,
        "copyability_score": 80,
        "priority_score": 85,
        "data_quality": {"level": "good", "confidence": "high"},
        "risk_evidence": [],
        "security_evidence": [],
        "entity_cluster_evidence": [],
        "copyability_evidence": [
            {
                "rule_id": "copyability_liquidity_strong",
                "severity": "positive",
                "score_delta": 15,
                "metric": "liquidity_usd",
                "value": 50000,
                "threshold": 50000,
            }
        ],
        "priority_evidence": [
            {
                "rule_id": "priority_gmgn_smart_wallet_signal",
                "severity": "positive",
                "score_delta": 5,
                "metric": "gmgn.smart_wallet_count",
                "value": 1,
                "threshold": 1,
            }
        ],
    }

    payload = build_hermes_payload(snapshot=snapshot, analysis=analysis)

    assert payload["version"] == "phase6a-hermes-payload-v1"
    assert payload["channel"] == "hermes"
    assert payload["should_send"] is True
    assert payload["delivery_level"] == "immediate"
    assert payload["summary"]["symbol"] == "MEME"
    assert payload["summary"]["headline"] == "High-priority manual research candidate."
    assert payload["summary"]["top_evidence"] == [
        "copyability_liquidity_strong",
        "priority_gmgn_smart_wallet_signal",
    ]
    assert "[A] MEME / BNB" in payload["telegram_markdown"]
    assert "# ChainMind Token Analysis Report" in payload["report_markdown"]
    assert payload["ai_prompt"]["version"] == "phase5c-ai-explanation-prompt-v1"
    assert payload["snapshot"] == snapshot
    assert payload["analysis"] == analysis


def test_build_hermes_payload_uses_prebuilt_report_and_prompt():
    prompt = {"version": "custom-prompt"}
    payload = build_hermes_payload(
        snapshot={"token": {"address": "0xToken", "chain": "bnb"}},
        analysis={
            "token_address": "0xToken",
            "chain": "bnb",
            "grade": "C",
            "action": "store_only",
        },
        report_markdown="# Existing Report\n",
        ai_prompt=prompt,
    )

    assert payload["should_send"] is False
    assert payload["delivery_level"] == "store_only"
    assert payload["report_markdown"] == "# Existing Report\n"
    assert payload["ai_prompt"] == prompt
