from chainmind.reports import generate_ai_explanation_prompt


def test_generate_ai_explanation_prompt_wraps_report_and_structured_context():
    snapshot = {
        "token": {"address": "0xToken", "symbol": "MEME", "chain": "bnb"},
        "token_profile": {
            "type": "meme_candidate",
            "source": "default",
            "reason": "No mainstream or infrastructure context was detected.",
        },
        "intelligence": {
            "gmgn": {
                "has_wallet_signal": True,
                "smart_wallet_count": 1,
            }
        },
        "data_quality": {
            "api_warnings": ["GMGN API failed: temporary unavailable"],
        },
    }
    analysis = {
        "token_address": "0xToken",
        "symbol": "MEME",
        "chain": "bnb",
        "grade": "C",
        "action": "store_only",
        "risk_score": 65,
        "security_score": 10,
        "entity_cluster_score": 50,
        "opportunity_score": 35,
        "copyability_score": 33,
        "priority_score": 40,
        "data_quality": {
            "level": "good",
            "confidence": "high",
            "warnings": ["Security data is partial."],
        },
        "risk_evidence": [
            {
                "rule_id": "early_buyer_exit_ratio_high",
                "severity": "high",
                "score_delta": 30,
                "metric": "early_buyer_exit_ratio",
                "value": 0.8,
                "threshold": 0.6,
            }
        ],
        "security_evidence": [],
        "entity_cluster_evidence": [],
        "copyability_evidence": [],
        "priority_evidence": [],
    }

    prompt = generate_ai_explanation_prompt(snapshot=snapshot, analysis=analysis)

    assert prompt["version"] == "phase5c-ai-explanation-prompt-v1"
    assert "Do not invent token facts" in prompt["system_prompt"]
    assert "```markdown" in prompt["user_prompt"]
    assert "# ChainMind Token Analysis Report" in prompt["report_markdown"]
    assert prompt["structured_context"]["token"]["address"] == "0xToken"
    assert prompt["structured_context"]["scores"]["risk"] == 65
    assert prompt["structured_context"]["evidence"]["risk"] == [
        "early_buyer_exit_ratio_high"
    ]
    assert prompt["structured_context"]["wallet_intelligence"]["gmgn"][
        "smart_wallet_count"
    ] == 1
    assert prompt["structured_context"]["data_quality"]["api_warnings"] == [
        "GMGN API failed: temporary unavailable"
    ]


def test_generate_ai_explanation_prompt_accepts_prebuilt_report():
    prompt = generate_ai_explanation_prompt(
        snapshot={"token": {"address": "0xToken", "chain": "bnb"}},
        analysis={"token_address": "0xToken", "chain": "bnb"},
        report_markdown="# Existing Report\n",
    )

    assert prompt["report_markdown"] == "# Existing Report\n"
    assert "# Existing Report" in prompt["user_prompt"]
