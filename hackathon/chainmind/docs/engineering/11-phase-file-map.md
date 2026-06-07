# 11. Phase File Map

This document maps project phases to the files they introduced, changed, or
currently depend on. It is an orientation index, not a replacement for the
engineering directory structure.

## Why This Exists

ChainMind source code is organized by responsibility:

```text
data
cleaning
domain
scoring
orchestration
scripts
tests
```

That structure should remain stable. Files should not be renamed to
`phase2_*`, `phase3_*`, or `phase4_*` because the same module can keep evolving
across later phases.

This map answers a different question:

```text
If I want to inspect or modify a specific project phase, which files should I
read first?
```

## Maintenance Rule

Whenever a phase is completed or materially changed, update this document with:

```text
phase status
main docs
main code files
main scripts
main tests
main experiments or samples
known follow-up work
```

## Phase 1: Risk Filter / Manual Dune Exploration

### Status

```text
Historical / completed as project foundation
```

### Main Purpose

Create the initial BNB meme-token risk-filtering direction and organize early
Dune/manual analysis work.

### Main Docs

```text
docs/progress/2026-05-21-progress.md
docs/research/2026-05-26-bnb-meme-token-real-research-report.md
experiments/week1-risk-filter/phase1-check-report.md
```

### Main Experiments

```text
experiments/week1-risk-filter/
```

### Notes

Phase 1 is mostly research and workflow formation. It did not introduce the
current formal Python scoring package as a stable API.

## Phase 2: Token Risk Score

### Status

```text
Implemented and still maintained
```

### Main Purpose

Turn manual Dune observations into executable token-risk rules and
`TokenSnapshot`-based scoring.

### Main Docs

```text
docs/progress/2026-05-25-phase2-token-risk-plan.md
docs/progress/2026-05-25-dune-api-prep.md
docs/progress/2026-05-26-phase2-real-dune-validation.md
docs/scoring/03-scoring-models.md
docs/scoring/04-judgement-framework.md
```

### Main Code

```text
src/chainmind/domain/token_snapshot.py
src/chainmind/scoring/token_risk.py
src/chainmind/scoring/opportunity.py
src/chainmind/scoring/priority.py
src/chainmind/scoring/score_result.py
src/chainmind/orchestration/analyze_token.py
src/chainmind/data/dune_client.py
src/chainmind/data/dune_mappers.py
src/chainmind/queries/dune/bnb/token_trading_activity.sql
src/chainmind/queries/dune/bnb/five_minute_flow.sql
src/chainmind/queries/dune/bnb/early_buyers.sql
src/chainmind/queries/dune/bnb/early_buyer_funding.sql
```

### Main Scripts

```text
scripts/analyze_token.py
scripts/analyze_dune_token.py
```

### Main Tests

```text
tests/unit/test_token_risk_scoring.py
tests/unit/test_analyze_token_cli_foundation.py
tests/unit/test_sample_snapshots.py
tests/unit/test_dune_mappers.py
```

### Main Experiments / Samples

```text
experiments/week2-token-risk-score/
samples/tokens/
```

### Notes

`priority.py` was introduced early, but Phase 4A later upgraded its scoring
inputs and output evidence.

## Phase 3: Dune Deep Analysis + API Enrichment + Entity Cluster

### Status

```text
Implemented and validated as Phase 3 v1
```

### Main Purpose

Productize Dune-backed deep token analysis, add API/RPC enrichment, and expose
Entity Cluster v0.1.

### Main Docs

```text
docs/progress/2026-05-31-phase3-plan.md
docs/progress/2026-05-31-phase3-api-requirements.md
docs/progress/2026-06-01-phase3-real-token-batch-1.md
docs/progress/2026-06-01-phase3-handoff.md
docs/progress/2026-06-01-phase3-handoff-zh.md
docs/data/04-wallet-entity-detection.md
docs/data/05-dune-analysis-playbook.md
docs/data/06-dune-api-output-mapping.md
```

### Main Code

```text
src/chainmind/orchestration/analyze_dune_token.py
src/chainmind/orchestration/quick_screen_token.py
src/chainmind/data/query_cache.py
src/chainmind/data/http_json.py
src/chainmind/data/dexscreener_client.py
src/chainmind/data/goplus_client.py
src/chainmind/data/honeypot_client.py
src/chainmind/data/nansen_client.py
src/chainmind/data/bnb_rpc_client.py
src/chainmind/data/api_mappers.py
src/chainmind/data/chain_ids.py
src/chainmind/cleaning/dune_cleaners.py
src/chainmind/scoring/security.py
src/chainmind/scoring/entity_cluster.py
src/chainmind/scoring/quick_screen.py
src/chainmind/scoring/data_quality.py
```

### Main Scripts

```text
scripts/smoke_test_apis.py
scripts/quick_screen_token.py
scripts/analyze_dune_token.py
scripts/batch_analyze_tokens.py
```

### Main Tests

```text
tests/unit/test_api_clients.py
tests/unit/test_api_mappers.py
tests/unit/test_bnb_rpc_client.py
tests/unit/test_query_cache.py
tests/unit/test_dune_cleaners.py
tests/unit/test_data_quality.py
tests/unit/test_security_scoring.py
tests/unit/test_entity_cluster_scoring.py
tests/unit/test_quick_screen.py
tests/unit/test_analyze_dune_token_orchestration.py
tests/unit/test_batch_analyze_tokens.py
```

### Main Experiments / Runtime Artifacts

```text
experiments/week2-token-risk-score/dune-query-cache/
experiments/week2-token-risk-score/real-token-snapshots/
```

### Known Limits

```text
Nansen can fail when credits are exhausted.
GMGN is configured but signed requests are not implemented.
Dune is a deep confirmation layer, not a low-latency scanner.
```

## Phase 4A: Complete Scoring Package + Copyability v0

### Status

```text
Implemented and committed
```

### Main Purpose

Upgrade the analysis output from:

```text
Risk / Security / Entity / Opportunity / Grade
```

to:

```text
Risk / Security / Entity / Opportunity / Copyability / Priority / Grade
```

### Main Docs

```text
docs/progress/2026-06-05-phase4-plan.md
docs/progress/2026-06-05-phase4-check-report.md
docs/progress/2026-06-05-phase4-completion-report.md
docs/roadmap/08-execution-plan.md
```

### Main Code

```text
src/chainmind/scoring/copyability.py
src/chainmind/scoring/priority.py
src/chainmind/scoring/__init__.py
src/chainmind/domain/token_snapshot.py
src/chainmind/orchestration/analyze_token.py
```

### Main Scripts

```text
scripts/analyze_dune_token.py
scripts/batch_analyze_tokens.py
```

### Main Tests

```text
tests/unit/test_copyability_scoring.py
tests/unit/test_priority_scoring.py
tests/unit/test_batch_analyze_tokens.py
tests/unit/test_analyze_dune_token_orchestration.py
```

### Main Experiments

```text
experiments/phase4-calibration/
```

### Main Output Fields

```text
copyability_score
copyability_evidence
priority_score
priority_evidence
```

### Known Limits

```text
Copyability v0 is token-level only.
Full Wallet Alpha is not implemented.
Mainstream / infrastructure tokens need token_profile context before final
interpretation.
```

## Phase 4A.1: Copyability / Priority Calibration

### Status

```text
Started
Batch 1 completed
Batch 2 control check completed
```

### Main Purpose

Check whether Copyability v0 and Priority Score behave sensibly on real cached
samples and control samples before tuning rules.

### Main Docs / Artifacts

```text
experiments/phase4-calibration/labels.csv
experiments/phase4-calibration/batch-1-tokens.txt
experiments/phase4-calibration/batch-1-output.txt
experiments/phase4-calibration/batch-1-output.json
experiments/phase4-calibration/batch-1-results.md
experiments/phase4-calibration/batch-2-plan.md
experiments/phase4-calibration/batch-2-tokens.txt
experiments/phase4-calibration/batch-2-output.txt
experiments/phase4-calibration/batch-2-results.md
experiments/phase4-calibration/batch-2-controls-quick-output.md
```

### Current Decision

```text
Do not tune Copyability v0 yet.
Add token_profile context before interpreting mainstream controls as meme
opportunities.
```

## Phase 4A.2: Token Profile Boundary Layer

### Status

```text
Recommended next step
Not implemented
```

### Main Purpose

Distinguish different token interpretation contexts without rewriting the
scoring package.

### Proposed Profiles

```text
meme_candidate
mainstream_control
infrastructure
```

### Likely Files

```text
src/chainmind/domain/token_snapshot.py
src/chainmind/orchestration/analyze_token.py
src/chainmind/scoring/quick_screen.py
src/chainmind/scoring/priority.py
experiments/phase4-calibration/labels.csv
```

### Notes

The first implementation should be light. Use `token_profile` for explanation
and rule boundaries before making it a major scoring refactor.

## Phase 4B: GMGN Query-Only Wallet Alpha v0

### Status

```text
Implemented
Validated on one BNB control token
```

### Purpose

Add a query-only wallet intelligence layer so ChainMind can keep analyzing
wallet and trader signals when Nansen credits are unavailable.

Phase 4B does not include trading, swap execution, private-key loading, auto
buy, auto sell, or copy-trading execution.

### Main Docs / Artifacts

```text
docs/progress/2026-06-07-phase4b-gmgn-wallet-alpha-plan.md
docs/progress/2026-06-07-phase4b-completion-report.md
experiments/phase4-calibration/gmgn-batch-1-results.md
experiments/phase4-calibration/gmgn-batch-1-snapshot.json
```

### Main Code

```text
src/chainmind/data/gmgn_client.py
src/chainmind/data/api_mappers.py
src/chainmind/orchestration/analyze_dune_token.py
src/chainmind/data/__init__.py
```

### Main Scripts

```text
scripts/smoke_test_apis.py
scripts/analyze_dune_token.py
```

### Main Tests

```text
tests/unit/test_api_clients.py
tests/unit/test_api_mappers.py
tests/unit/test_analyze_dune_token_orchestration.py
```

### Main Output Fields

```text
snapshot.intelligence.gmgn.source
snapshot.intelligence.gmgn.top_holder_count
snapshot.intelligence.gmgn.top_trader_count
snapshot.intelligence.gmgn.smart_wallet_count
snapshot.intelligence.gmgn.sniper_count
snapshot.intelligence.gmgn.insider_count
snapshot.intelligence.gmgn.bundled_wallet_count
snapshot.intelligence.gmgn.has_wallet_signal
snapshot.intelligence.gmgn.has_risk_wallet_signal
snapshot.intelligence.gmgn.token_info_sample
snapshot.intelligence.gmgn.token_security_sample
snapshot.intelligence.gmgn.top_holders_sample
snapshot.intelligence.gmgn.top_traders_sample
```

### Validated Behavior

```text
GMGN query-only trending smoke test passes.
GMGN token intelligence can merge into analyze_dune_token output.
Nansen insufficient credits are recorded as warnings and do not block analysis.
ChainMind chain "bnb" maps to GMGN chain "bsc".
Windows can run gmgn-cli through GMGN_CLI_COMMAND=npx gmgn-cli.
```

### Data Source Roles

```text
GMGN   = wallet intelligence, top traders, top holders, trending, portfolio/activity
GoPlus = token/address/security risk
Dune   = deep validation, early buyers, funding, retention
Nansen = optional smart-money enrichment when credits are available
```

### Future Wallet Alpha Fields

These remain future fields. Phase 4B created the data-source foundation but did
not complete full wallet alpha scoring.

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

### Candidate Data Sources

```text
GMGN query-only CLI
Nansen smart money when credits are available
Dune wallet-history queries
local labeled sample dataset
```

### Next Recommendations

```text
Run GMGN validation on meme/new-pool tokens.
Add small GMGN-derived priority/copyability evidence.
Add GoPlus address_security for early-buyer wallet risk.
Keep automated trading in a separate future phase.
```

## Phase 4B.1: GMGN Evidence Scoring

### Status

```text
Implemented
Validated on one risky/meme cached token
```

### Purpose

Let GMGN wallet/trader signals appear in scoring evidence without allowing them
to override risk, security, entity, or Dune validation evidence.

### Main Docs / Artifacts

```text
docs/progress/2026-06-07-phase4b1-gmgn-scoring-report.md
experiments/phase4-calibration/gmgn-scoring-sample-snapshot.json
```

### Main Code

```text
src/chainmind/scoring/copyability.py
src/chainmind/scoring/priority.py
src/chainmind/orchestration/analyze_token.py
```

### Main Tests

```text
tests/unit/test_copyability_scoring.py
tests/unit/test_priority_scoring.py
```

### Main Output Fields

```text
copyability_evidence[].rule_id = copyability_gmgn_smart_wallet_signal
copyability_evidence[].rule_id = copyability_gmgn_top_trader_signal
copyability_evidence[].rule_id = copyability_gmgn_risky_wallet_signal
priority_evidence[].rule_id = priority_gmgn_smart_wallet_signal
priority_evidence[].rule_id = priority_gmgn_top_trader_signal
priority_evidence[].rule_id = priority_gmgn_risky_wallet_penalty
priority_evidence[].rule_id = priority_gmgn_positive_signal_blocked_by_risk
```

### Guardrail

```text
If risk_score >= 70 or security_score >= 70, GMGN positive priority bonuses are
blocked and recorded as neutral evidence.
```

## Phase 5: Report Generation

### Status

```text
Not started
```

### Planned Files

```text
src/chainmind/reports/
config/prompts.yaml
runtime/reports/
```

### Related Docs

```text
docs/operations/06-ai-hermes-reporting.md
```

## Phase 6: Hermes Push Interface

### Status

```text
Not started
```

### Planned Files

```text
src/chainmind/alerts/alert_policy.py
src/chainmind/alerts/cooldown.py
src/chainmind/alerts/digest_builder.py
src/chainmind/alerts/channels/hermes.py
```

## Phase 7+: Radar, Watchlist, Review, Learning

### Status

```text
Not started
```

### Planned Areas

```text
src/chainmind/realtime/
src/chainmind/orchestration/radar_scan.py
src/chainmind/orchestration/watch_token.py
src/chainmind/orchestration/watch_wallet.py
src/chainmind/orchestration/daily_review.py
src/chainmind/learning/
src/chainmind/reports/review_report.py
```

## Quick Lookup: Code By Capability

| Capability | Main Files | Main Phase |
|---|---|---|
| Token risk scoring | `src/chainmind/scoring/token_risk.py` | Phase 2 |
| Opportunity scoring | `src/chainmind/scoring/opportunity.py` | Phase 2 |
| Priority grading | `src/chainmind/scoring/priority.py` | Phase 2, upgraded in Phase 4A |
| Dune deep analysis | `src/chainmind/orchestration/analyze_dune_token.py` | Phase 3 |
| Query cache | `src/chainmind/data/query_cache.py` | Phase 3 |
| API enrichment | `src/chainmind/data/*_client.py`, `src/chainmind/data/api_mappers.py` | Phase 3 |
| Quick screen | `src/chainmind/orchestration/quick_screen_token.py`, `src/chainmind/scoring/quick_screen.py` | Phase 3 |
| Security scoring | `src/chainmind/scoring/security.py` | Phase 3 |
| Entity clustering | `src/chainmind/scoring/entity_cluster.py` | Phase 3 |
| Data quality | `src/chainmind/scoring/data_quality.py` | Phase 3 |
| Copyability v0 | `src/chainmind/scoring/copyability.py` | Phase 4A |
| Full analysis result | `src/chainmind/domain/token_snapshot.py` | Phase 2, expanded in Phase 3/4A |
| Main token analysis flow | `src/chainmind/orchestration/analyze_token.py` | Phase 2, expanded in Phase 3/4A |

## Quick Lookup: Scripts By Capability

| Script | Purpose | Main Phase |
|---|---|---|
| `scripts/analyze_token.py` | Basic token analysis entry | Phase 2 |
| `scripts/analyze_dune_token.py` | Dune-backed deep analysis | Phase 3, upgraded in Phase 4A |
| `scripts/quick_screen_token.py` | Low-latency API/RPC quick screen | Phase 3 |
| `scripts/batch_analyze_tokens.py` | Batch Dune-backed analysis | Phase 3, upgraded in Phase 4A |
| `scripts/smoke_test_apis.py` | API health check | Phase 3 |

## Quick Lookup: Current Validation Command

```bash
python -m pytest
```

Latest known result after Phase 4A:

```text
75 passed
```
