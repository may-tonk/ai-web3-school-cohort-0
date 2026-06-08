from chainmind.reports import generate_token_report


def test_generate_token_report_renders_scores_evidence_and_gmgn_summary():
    snapshot = {
        "token": {
            "address": "0xToken",
            "symbol": "MEME",
            "chain": "bnb",
        },
        "market": {
            "base_token_symbol": "MEME",
            "pair_address": "0xPair",
            "dex_id": "pancakeswap",
            "liquidity_usd": 50000,
            "volume_24h_usd": 75000,
            "price_change_24h_pct": 12.5,
        },
        "intelligence": {
            "gmgn": {
                "source": "gmgn",
                "has_wallet_signal": True,
                "has_risk_wallet_signal": True,
                "top_holder_count": 20,
                "top_trader_count": 8,
                "smart_wallet_count": 2,
                "sniper_count": 1,
                "insider_count": 0,
                "bundled_wallet_count": 1,
            }
        },
        "data_quality": {
            "api_warnings": ["Nansen API failed: insufficient credits"],
        },
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
        "grade": "B",
        "action": "watchlist",
        "risk_score": 45,
        "security_score": 20,
        "entity_cluster_score": 30,
        "opportunity_score": 65,
        "copyability_score": 70,
        "priority_score": 72,
        "data_quality": {
            "level": "good",
            "confidence": "high",
            "warnings": ["Security enrichment is partial."],
        },
        "risk_evidence": [
            {
                "rule_id": "negative_latest_net_buy",
                "severity": "high",
                "score_delta": 20,
                "metric": "net_buy_usd",
                "value": -1000,
                "threshold": 0,
            }
        ],
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
            },
            {
                "rule_id": "copyability_gmgn_risky_wallet_signal",
                "severity": "medium",
                "score_delta": -8,
                "metric": "gmgn.risky_wallet_count",
                "value": 2,
                "threshold": 0,
            },
        ],
        "priority_evidence": [
            {
                "rule_id": "priority_gmgn_smart_wallet_signal",
                "severity": "positive",
                "score_delta": 5,
                "metric": "gmgn.smart_wallet_count",
                "value": 2,
                "threshold": 1,
            }
        ],
    }

    report = generate_token_report(snapshot=snapshot, analysis=analysis)

    assert "# ChainMind Token Analysis Report" in report
    assert "- Grade: B" in report
    assert "- Action: watchlist" in report
    assert "- Copyability Score: 70" in report
    assert "## 3. Interpretation Context" in report
    assert "- Token Profile: meme_candidate" in report
    assert "## 8. Wallet Intelligence" in report
    assert "- Smart Wallets: 2" in report
    assert "- Snipers: 1" in report
    assert "Nansen API failed: insufficient credits" in report
    assert "copyability_liquidity_strong" in report
    assert "priority_gmgn_smart_wallet_signal" in report
    assert "| negative_latest_net_buy | net_buy_usd | -1000 | 0 | high | 20 |" in report


def test_generate_token_report_keeps_trading_instruction_boundary():
    report = generate_token_report(
        snapshot={"token": {"address": "0xToken", "chain": "bnb"}},
        analysis={
            "token_address": "0xToken",
            "chain": "bnb",
            "grade": "D",
            "action": "filter",
            "risk_score": 100,
            "security_score": 0,
            "entity_cluster_score": 50,
            "opportunity_score": 20,
            "copyability_score": 0,
            "priority_score": 9,
            "data_quality": {"level": "good", "confidence": "high"},
            "risk_evidence": [],
            "security_evidence": [],
            "entity_cluster_evidence": [],
            "copyability_evidence": [],
            "priority_evidence": [],
        },
    )

    prohibited_terms = ["买入", "卖出", "仓位", "止盈", "止损"]
    assert all(term not in report for term in prohibited_terms)
    assert "do not provide execution instructions" in report


def test_generate_token_report_marks_non_meme_context_boundary():
    report = generate_token_report(
        snapshot={
            "token": {
                "address": "0x55d398326f99059ff775485246999027b3197955",
                "symbol": "USDT",
                "chain": "bnb",
            },
            "token_profile": {
                "type": "mainstream_control",
                "source": "known_address",
                "reason": "USDT stablecoin control",
            },
        },
        analysis={
            "token_address": "0x55d398326f99059ff775485246999027b3197955",
            "symbol": "USDT",
            "chain": "bnb",
            "grade": "B",
            "action": "watchlist",
            "risk_score": 45,
            "security_score": 40,
            "entity_cluster_score": 0,
            "opportunity_score": 60,
            "copyability_score": 80,
            "priority_score": 73,
            "data_quality": {"level": "good", "confidence": "high"},
            "risk_evidence": [],
            "security_evidence": [],
            "entity_cluster_evidence": [],
            "copyability_evidence": [],
            "priority_evidence": [],
        },
    )

    assert "- Token Profile: mainstream_control" in report
    assert "should not be interpreted as a BNB meme candidate" in report
