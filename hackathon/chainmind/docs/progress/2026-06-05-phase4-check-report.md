# 2026-06-05 Phase 4A Check Report

## Summary

Phase 4A is implemented as:

```text
complete scoring package + Copyability v0
```

The implementation keeps Copyability independent from external API clients. It
uses existing `TokenSnapshot` fields and returns the shared `ScoreResult` shape,
so future wallet-level alpha data can be added without rewriting the scoring
pipeline.

## Completed Changes

New planning document:

```text
docs/progress/2026-06-05-phase4-plan.md
```

New scoring modules and tests:

```text
src/chainmind/scoring/copyability.py
tests/unit/test_copyability_scoring.py
tests/unit/test_priority_scoring.py
```

Updated core result fields:

```text
AnalysisResult.copyability_score
AnalysisResult.copyability_evidence
AnalysisResult.priority_score
AnalysisResult.priority_evidence
```

Updated orchestration:

```text
src/chainmind/orchestration/analyze_token.py
```

Updated scoring exports and priority logic:

```text
src/chainmind/scoring/__init__.py
src/chainmind/scoring/priority.py
```

Updated CLI output:

```text
scripts/analyze_dune_token.py
scripts/batch_analyze_tokens.py
```

## Copyability v0 Boundary

Copyability v0 estimates whether a token still has a practical observation or
follow window. It uses token-level evidence:

```text
liquidity
24h volume
latest 5m net buy
buyers vs sellers
repeated negative flow
early buyer exit ratio
shared funder cluster
tax / honeypot / sellability risk
```

It does not yet score wallet historical alpha. That is deferred until wallet
history sources are ready.

## Verification

Unit test result:

```text
75 passed
```

Single-token Dune analysis check:

```text
token: 0xf500d904b07ac6214be407b69fe817a82eac7777
grade: D
action: filter
risk_score: 100
security_score: 0
entity_cluster_score: 50
opportunity_score: 20
copyability_score: 0
priority_score: 9
data_quality: good/high
```

Batch regression with the first real token batch:

| Token | Grade | Action | Risk | Security | Entity | Opportunity | Copyability | Priority |
|---|---:|---|---:|---:|---:|---:|---:|---:|
| `0xf500d904b07ac6214be407b69fe817a82eac7777` | D | filter | 100 | 0 | 50 | 20 | 0 | 9 |
| `0x90166915b98d24d284c56de3b9f4ed59338f7777` | D | filter | 85 | 0 | 50 | 50 | 5 | 28 |
| `0x3d96b30ba2c08724b70efff1ad16d005db1c7777` | D | filter | 100 | 0 | 40 | 20 | 0 | 11 |
| `0x90507254e9c594e728172b9d217f4ab1a2ee7777` | D | filter | 95 | 0 | 50 | 20 | 0 | 11 |

The second sample moved from the previous C/store-only record to D/filter in
this run because the analysis merges current live market data with cached Dune
rows. This is expected and should be considered when comparing historical
reports.

## Known Limits

Nansen returned insufficient credits during live analysis. This is handled as a
warning and does not block the main pipeline.

GMGN signed request integration remains deferred. It is still a candidate data
source for Phase 4B wallet alpha.

Copyability v0 is token-level only. It should not be interpreted as a proven
wallet alpha score.

## Next Recommended Step

Recommended next step:

```text
Phase 4B preparation: decide the first wallet-history data source and define
wallet alpha snapshot fields without changing the existing scoring package.
```

Alternative next step:

```text
Run a broader calibration batch with healthy/high-liquidity BNB tokens and
fresh meme tokens to tune Copyability v0 thresholds.
```
