from chainmind.alerts import build_digest_markdown, build_digest_payload


def _payload(symbol, priority, *, should_send=True, delivery_level="digest"):
    return {
        "should_send": should_send,
        "delivery_level": delivery_level,
        "summary": {
            "token_address": f"0x{symbol}",
            "symbol": symbol,
            "chain": "bnb",
            "grade": "B",
            "action": "watchlist",
            "headline": "Watchlist candidate for continued observation.",
            "risk_score": 40,
            "copyability_score": 60,
            "priority_score": priority,
            "top_evidence": ["copyability_liquidity_strong"],
        },
        "telegram_markdown": f"[B] {symbol} / BNB\n",
    }


def test_build_digest_payload_filters_digest_candidates_and_sorts_by_priority():
    digest = build_digest_payload(
        [
            _payload("LOW", 55),
            _payload("HIGH", 80),
            _payload("SKIP", 90, should_send=False),
            _payload("NOW", 95, delivery_level="immediate"),
        ]
    )

    assert digest["version"] == "phase6b-digest-payload-v1"
    assert digest["candidate_count"] == 4
    assert digest["send_count"] == 2
    assert [item["symbol"] for item in digest["items"]] == ["HIGH", "LOW"]
    assert "ChainMind Watchlist Digest" in digest["digest_markdown"]
    assert "[B] HIGH / BNB" in digest["digest_markdown"]
    assert "SKIP" not in digest["digest_markdown"]


def test_build_digest_markdown_keeps_research_boundary():
    markdown = build_digest_markdown([_payload("MEME", 70)])

    assert "Boundary: evidence-only research digest" in markdown
    prohibited_terms = ["买入", "卖出", "仓位", "止盈", "止损"]
    assert all(term not in markdown for term in prohibited_terms)


def test_build_digest_markdown_handles_empty_digest():
    markdown = build_digest_markdown([])

    assert "No digest-ready candidates." in markdown
