# ChainMind Phase 4B.1 GMGN Scoring Report

Date: 2026-06-07

## 1. Status

Current status:

```text
Phase 4B.1: completed
```

Phase 4B.1 adds conservative GMGN-derived scoring evidence.

The goal is not to make GMGN decide whether a token is safe or buyable. The goal
is to let GMGN wallet/trader signals slightly affect copyability and priority
while preserving the authority of risk, security, entity, and Dune evidence.

## 2. Rules Added

Copyability evidence:

```text
copyability_gmgn_smart_wallet_signal
copyability_gmgn_top_trader_signal
copyability_gmgn_risky_wallet_signal
```

Priority evidence:

```text
priority_gmgn_smart_wallet_signal
priority_gmgn_top_trader_signal
priority_gmgn_risky_wallet_penalty
priority_gmgn_positive_signal_blocked_by_risk
```

## 3. Scoring Principles

Positive GMGN signals are intentionally small:

```text
smart wallet signal -> small positive evidence
top trader signal -> small positive evidence
```

Risky GMGN signals are negative:

```text
sniper
insider
bundled wallet
```

Hard rule:

```text
GMGN positive signals cannot offset high risk or high security risk.
```

If `risk_score >= 70` or `security_score >= 70`, priority does not apply GMGN
positive wallet bonuses. Instead, it records:

```text
priority_gmgn_positive_signal_blocked_by_risk
```

## 4. Real Sample Validation

Sample:

```text
Token: 世界杯纪念币
Address: 0xf500d904b07ac6214be407b69fe817a82eac7777
Sample type: risky / meme
Snapshot: experiments/phase4-calibration/gmgn-scoring-sample-snapshot.json
```

Important output:

```text
GMGN Wallet Signal: True
Top Holders: 20
Top Traders: 20
Smart Wallets: 0
Snipers: 0
Insiders: 0
Bundled Wallets: 0
Risk Score: 100
Copyability Score: 0
Priority Score: 9
Grade: D
Action: filter
```

GMGN evidence appeared in Copyability:

```text
copyability_gmgn_top_trader_signal
gmgn.top_trader_count=20
score_delta=5
```

But Priority blocked positive GMGN signal because of high risk:

```text
priority_gmgn_positive_signal_blocked_by_risk
risk_score=100
score_delta=0
```

This is the intended behavior.

## 5. Tests

Full test suite:

```text
python -m pytest
84 passed
```

New test coverage:

```text
GMGN smart wallet / top trader signals add small copyability evidence.
GMGN sniper / insider / bundled signals reduce copyability.
GMGN wallet signals can add small priority evidence in normal contexts.
GMGN risky wallet signals reduce priority.
GMGN positive priority signals are blocked in high-risk contexts.
```

## 6. Conclusion

Phase 4B.1 is complete.

GMGN is now more than a passive data source:

```text
It appears in snapshot.intelligence.gmgn.
It appears in copyability_evidence.
It appears in priority_evidence.
It remains bounded by core risk and security rules.
```

This keeps ChainMind aligned with the original product principle:

```text
Smart money participation is useful evidence, but never a standalone buy signal.
```
