# ChainMind Phase 4 Completion Report

Date: 2026-06-05

## 1. Current Phase 4 Status

Current status:

```text
Phase 4A: completed
Phase 4A.1: calibration started
Phase 4B: not started
```

This means ChainMind has completed the first executable Phase 4 scoring
upgrade:

```text
complete scoring package + Copyability v0
```

The project is not yet at full Wallet Alpha. Full Wallet Alpha is intentionally
deferred until wallet-history data is available and stable.

## 2. Phase 4 Scope

Existing project documents used several Phase 4 meanings:

```text
docs/roadmap/07-mvp-roadmap.md: Wallet Alpha + Copyability
docs/roadmap/08-execution-plan.md: complete scoring system
docs/learning/13-token-analysis-data-analyst-workflow.md: AI explanation layer
```

For this implementation cycle, Phase 4 was defined as:

```text
Phase 4A = complete scoring package + Copyability v0
```

This avoided jumping too early into AI reports or full Wallet Alpha.

## 3. Completed Capabilities

Before Phase 4A, the main scoring package included:

```text
Risk
Security
Entity Cluster
Opportunity
Grade / Action
```

After Phase 4A, the scoring package includes:

```text
Risk
Security
Entity Cluster
Opportunity
Copyability
Priority
Grade / Action
```

New output fields:

```text
copyability_score
copyability_evidence
priority_score
priority_evidence
```

These fields are now available in `AnalysisResult.to_mapping()` and therefore
in script JSON output.

## 4. Copyability v0 Design

Copyability v0 answers:

```text
If this token appears to have opportunity, is there still a practical
observation or follow window for a normal human user?
```

It does not claim:

```text
This wallet has proven alpha.
This token should be bought.
This token will go up.
```

Copyability v0 uses existing `TokenSnapshot` fields:

```text
market
flow_5m
early_buyers
funding
security
```

It does not call external API clients directly. This keeps the scoring module
stable and makes future data-source upgrades easier.

Main positive signals:

```text
usable or strong liquidity
usable or strong 24h volume
positive latest 5m net buy
buyers outnumber sellers
healthy early-buyer retention
```

Main negative signals:

```text
low liquidity
weak 24h volume
negative latest 5m net buy
sellers outnumber buyers
repeated negative net buy
early buyer exit ratio high
shared funder risk
high tax / honeypot / sellability risk
```

## 5. Priority Score Design

Priority Score combines:

```text
Opportunity
Copyability
Risk penalty
Entity Cluster penalty
Security penalty
```

Priority is used to rank candidates more smoothly than A/B/C/D alone.

Grade rules now consider:

```text
risk_score
opportunity_score
copyability_score
entity_cluster_score
security_score
```

Current high-level behavior:

```text
D: extreme risk or high security risk
C: high risk or strong entity-cluster concern
A: low risk + high opportunity + high copyability
B: moderate opportunity + moderate copyability + acceptable risk
C: default store-only result
```

The legacy `grade_from_scores(risk_score, opportunity_score)` call remains
compatible.

## 6. Files Added

Planning and reports:

```text
docs/progress/2026-06-05-phase4-plan.md
docs/progress/2026-06-05-phase4-check-report.md
docs/progress/2026-06-05-phase4-completion-report.md
```

Scoring:

```text
src/chainmind/scoring/copyability.py
```

Tests:

```text
tests/unit/test_copyability_scoring.py
tests/unit/test_priority_scoring.py
```

Calibration artifacts:

```text
experiments/phase4-calibration/labels.csv
experiments/phase4-calibration/batch-1-tokens.txt
experiments/phase4-calibration/batch-1-output.txt
experiments/phase4-calibration/batch-1-output.json
experiments/phase4-calibration/batch-1-results.md
experiments/phase4-calibration/batch-2-plan.md
experiments/phase4-calibration/batch-2-tokens.txt
experiments/phase4-calibration/batch-2-results.md
experiments/phase4-calibration/batch-2-controls-quick-output.md
experiments/phase4-calibration/snapshots/.gitkeep
```

## 7. Files Updated

Core result model:

```text
src/chainmind/domain/token_snapshot.py
```

Main orchestration:

```text
src/chainmind/orchestration/analyze_token.py
```

Scoring exports and priority logic:

```text
src/chainmind/scoring/__init__.py
src/chainmind/scoring/priority.py
```

CLI output:

```text
scripts/analyze_dune_token.py
scripts/batch_analyze_tokens.py
```

## 8. Validation

Test command:

```bash
python -m pytest
```

Latest result:

```text
75 passed
```

This confirms:

```text
Copyability v0 rules are tested.
Priority scoring is tested.
Existing analysis and batch workflows still pass.
Backward-compatible grade calls still work.
```

## 9. Real Sample Calibration: Batch 1

Batch 1 used cached BNB meme-token samples.

Command:

```bash
python scripts\batch_analyze_tokens.py --file experiments\phase4-calibration\batch-1-tokens.txt --output experiments\phase4-calibration\batch-1-output.txt
python scripts\batch_analyze_tokens.py --file experiments\phase4-calibration\batch-1-tokens.txt --json --output experiments\phase4-calibration\batch-1-output.json
```

Batch 1 result:

| Token | Symbol | Grade | Action | Risk | Security | Entity | Opportunity | Copyability | Priority |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| `0xf500d904b07ac6214be407b69fe817a82eac7777` | 世界杯纪念币 | D | filter | 100 | 0 | 50 | 20 | 0 | 9 |
| `0x90166915b98d24d284c56de3b9f4ed59338f7777` | 彩蝶 | D | filter | 85 | 0 | 50 | 50 | 20 | 33 |
| `0x3d96b30ba2c08724b70efff1ad16d005db1c7777` | 野马 | D | filter | 100 | 0 | 40 | 20 | 0 | 11 |
| `0x90507254e9c594e728172b9d217f4ab1a2ee7777` | 美蛙 | D | filter | 95 | 0 | 50 | 20 | 0 | 11 |
| `0xff6b0006d17af50a0c0082ca1beb03af3f284444` | 世界杯 | D | filter | 85 | 0 | 50 | 60 | 20 | 36 |
| `0x9ec5d5082895b8bf56523e02a831aa0dc8737777` | 矛 | C | store_only | 65 | 0 | 50 | 35 | 33 | 40 |

Batch 1 conclusion:

```text
Do not tune rules yet.
The batch is mostly risky/unknown meme samples.
Copyability is low but not flat.
Priority separates severity inside D-heavy samples.
```

## 10. Control Calibration: Batch 2

Batch 2 added mainstream/high-liquidity controls:

```text
USDT
WBNB
CAKE
USDC control address
```

The full Dune-backed Batch 2 command timed out at the shell level after 5
minutes, but it produced a complete table output:

```text
experiments/phase4-calibration/batch-2-output.txt
```

Deep Batch 2 result:

| Token | Symbol | Grade | Action | Risk | Security | Entity | Opportunity | Copyability | Priority |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| `0x55d398326f99059ff775485246999027b3197955` | USDT | B | watchlist | 45 | 40 | 0 | 60 | 80 | 73 |
| `0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c` | WBNB | D | filter | 100 | 0 | 30 | 30 | 0 | 16 |
| `0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82` | Cake | B | watchlist | 45 | 40 | 0 | 60 | 80 | 73 |
| `0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d` | UB | D | filter | 100 | 0 | 20 | 30 | 0 | 17 |
| `0xf500d904b07ac6214be407b69fe817a82eac7777` | 世界杯纪念币 | D | filter | 100 | 0 | 50 | 20 | 0 | 9 |
| `0x90166915b98d24d284c56de3b9f4ed59338f7777` | 彩蝶 | D | filter | 85 | 0 | 50 | 50 | 20 | 33 |
| `0x9ec5d5082895b8bf56523e02a831aa0dc8737777` | 矛 | C | store_only | 65 | 0 | 50 | 35 | 33 | 40 |

Interpretation of the timeout:

```text
The current Dune deep-analysis queries are designed for meme-token analysis and
can be slow for mainstream/high-volume controls. Even when output is produced,
the run should be treated as a heavier calibration path rather than the normal
low-latency control workflow.
```

A Quick Screen control check was run instead.

Summary:

| Token | Symbol | Quick Decision | Main Trigger | Notes |
|---|---:|---:|---|---|
| `0x55d398326f99059ff775485246999027b3197955` | USDT | BLOCK | mintable | Stablecoin / high-liquidity control; mintable is not equivalent to new meme-token mint risk. |
| `0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c` | WBNB | WATCH | owner not renounced / unknown | Wrapped native asset control. |
| `0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82` | CAKE | BLOCK | mintable | Mainstream ecosystem token; special contract permissions expected. |
| `0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d` | UB | WATCH | owner not renounced / unknown | Pair/symbol should be rechecked before using as canonical USDC. |

Batch 2 conclusion:

```text
Mainstream and infrastructure tokens need context.
Rules that are correct for new meme tokens can be too coarse for non-meme assets.
Do not tune Copyability v0 yet based on these controls.
```

Additional Batch 2 finding:

```text
USDT and CAKE can receive high Copyability scores because liquidity, volume, and
flow are strong, while still triggering security or context-specific rules such
as mintable / owner not renounced.
```

This confirms that Copyability v0 is not simply forcing high-liquidity tokens to
zero. The bigger issue is interpretation context: mainstream controls should
not be ranked as meme opportunities without a `token_profile` layer.

## 11. Important Boundary Learned

The most important finding from Batch 2:

```text
ChainMind needs a lightweight token_profile layer before using mainstream
tokens as scoring controls.
```

Suggested future values:

```text
meme_candidate
mainstream_control
infrastructure
```

This should initially be used for interpretation and rule boundaries, not as a
major refactor of the scoring core.

## 12. GitHub Upload

The Phase 4 work was committed and pushed to GitHub.

Branch:

```text
codex/chainmind-foundation
```

Remote:

```text
https://github.com/may-tonk/ai-web3-school-cohort-0.git
```

Pushed commits:

```text
51a8c71 feat: add phase 4a copyability scoring
02bdf71 docs: record phase 4 batch 2 control check
```

GitHub branch URL:

```text
https://github.com/may-tonk/ai-web3-school-cohort-0/tree/codex/chainmind-foundation
```

## 13. What Is Not Done Yet

Not done in Phase 4A:

```text
Full Wallet Alpha Score
GMGN signed request integration
Nansen-backed wallet alpha when credits are available
Dune wallet-history profile queries
AI report generation
Hermes push output
database-backed long-term wallet profiles
```

These remain future phases.

## 14. Recommended Next Step

Recommended next step:

```text
Phase 4A.2 = token_profile boundary layer
```

Goal:

```text
Separate meme-token candidate scoring from mainstream/infrastructure controls
without rewriting the scoring package.
```

Suggested implementation:

```text
Add token_profile metadata to snapshots or calibration labels.
Use token_profile for interpretation and future rule boundaries.
Keep Copyability v0 unchanged until more healthy meme samples are tested.
```

After that, move to:

```text
Phase 4B = wallet alpha snapshot design
```

Phase 4B should start with fields, not API calls:

```text
wallet_address
trade_count_30d
win_rate_30d
median_return_30d
buy_to_peak_15m
buy_to_peak_1h
same_block_entry_ratio
liquidity_after_entry_usd
copyability_penalty
```

## 15. Final Conclusion

Phase 4A is complete.

ChainMind now has a complete first-pass scoring package:

```text
Risk / Security / Entity / Opportunity / Copyability / Priority / Grade
```

The scoring framework is intentionally extensible. It supports future Wallet
Alpha upgrades without forcing a rewrite of the current pipeline.

The current system should now move from implementation to calibration and
context-boundary work before entering full Wallet Alpha.
