# Phase 4A.1 Calibration Batch 1

## Run Info

Date: 2026-06-05

Command:

```bash
python scripts\batch_analyze_tokens.py --file experiments\phase4-calibration\batch-1-tokens.txt --output experiments\phase4-calibration\batch-1-output.txt
python scripts\batch_analyze_tokens.py --file experiments\phase4-calibration\batch-1-tokens.txt --json --output experiments\phase4-calibration\batch-1-output.json
```

Sample count: 6

Scope:

```text
cached BNB meme-token samples only
```

This batch is a regression and calibration batch, not a healthy-control batch.
Mainstream/stablecoin/high-liquidity controls are deferred to Batch 2 so this
run does not mix cached-regression behavior with fresh Dune query behavior.

## Summary Table

| Token | Symbol | Grade | Action | Risk | Security | Entity | Opportunity | Copyability | Priority |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|
| `0xf500d904b07ac6214be407b69fe817a82eac7777` | 世界杯纪念币 | D | filter | 100 | 0 | 50 | 20 | 0 | 9 |
| `0x90166915b98d24d284c56de3b9f4ed59338f7777` | 彩蝶 | D | filter | 85 | 0 | 50 | 50 | 20 | 33 |
| `0x3d96b30ba2c08724b70efff1ad16d005db1c7777` | 野马 | D | filter | 100 | 0 | 40 | 20 | 0 | 11 |
| `0x90507254e9c594e728172b9d217f4ab1a2ee7777` | 美蛙 | D | filter | 95 | 0 | 50 | 20 | 0 | 11 |
| `0xff6b0006d17af50a0c0082ca1beb03af3f284444` | 世界杯 | D | filter | 85 | 0 | 50 | 60 | 20 | 36 |
| `0x9ec5d5082895b8bf56523e02a831aa0dc8737777` | 矛 | C | store_only | 65 | 0 | 50 | 35 | 33 | 40 |

## Observations

### 1. Copyability Is Low But Not Flat

Copyability scores:

```text
0, 20, 0, 0, 20, 33
```

The score is not simply collapsing every token to zero. Tokens with usable
liquidity, usable volume, and positive latest flow can still keep non-zero
copyability even when early-buyer and shared-funder risks are active.

The lowest copyability scores are driven by overlapping risk:

```text
low or weak liquidity
weak 24h volume
negative latest net buy
sellers outnumbering buyers
repeated negative net buy
early buyer exit ratio high
shared funder risk
```

### 2. Priority Separates Severity Within Mostly Risky Samples

Priority scores:

```text
9, 33, 11, 11, 36, 40
```

The batch is mostly filtered, but priority still ranks relative severity. The
two samples with positive latest flow and usable volume keep higher priority
scores than the strongest filter cases.

### 3. Grade Distribution Is Still D-Heavy

Grade distribution:

```text
D: 5
C: 1
B: 0
A: 0
```

This is expected for this batch because the samples are mostly risky or unknown
meme-token candidates. It is not enough evidence that the new grade rules are
too strict. Batch 2 needs mainstream/high-liquidity controls and healthier meme
examples.

### 4. Current Grade Differences Make Sense

The only C/store-only sample is:

```text
0x9ec5d5082895b8bf56523e02a831aa0dc8737777
```

It has:

```text
risk_score = 65
copyability_score = 33
priority_score = 40
```

It still triggers early-buyer exit and shared-funder risk, but has usable
liquidity, usable volume, and positive latest net buy. C/store-only is
consistent with the current rules.

## Rule Tuning Candidates

Do not tune yet based on Batch 1 alone.

Potential rules to watch in Batch 2:

```text
copyability_liquidity_weak
copyability_volume_weak
copyability_early_buyer_exit_ratio_high
copyability_shared_funder_risk
shared_funder_cluster
early_buyer_exit_ratio_high
```

The main question for Batch 2:

```text
Do healthy/high-liquidity controls avoid being pushed to copyability 0?
```

If they do, the current Copyability v0 penalties are probably acceptable for a
first pass. If they do not, the likely first tuning candidates are:

```text
copyability_early_buyer_exit_ratio_high: -20 -> -15
copyability_shared_funder_risk: -25 -> -20
copyability_volume_weak: -10 -> -5
```

## Decision

Decision after Batch 1:

```text
Do not tune rules yet.
Run Batch 2 with mainstream/high-liquidity controls and healthier meme samples.
Keep Phase 4A scoring structure unchanged.
```

## Next Batch Proposal

Batch 2 should include:

```text
2-3 mainstream / stablecoin BNB tokens
2-3 high-liquidity meme or active tokens
3-5 fresh meme tokens
2-3 obvious low-quality tokens
```

Batch 2 may require fresh Dune query execution, so it should be treated as a
new-query calibration run rather than a pure cached regression run.
