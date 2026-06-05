# Phase 4A.1 Calibration Batch 2 Plan

## Purpose

Batch 1 used cached risky/unknown meme-token samples. It showed that
Copyability v0 can separate severity inside mostly risky samples, but it cannot
prove whether the rules are too strict.

Batch 2 adds control samples.

Main question:

```text
Do mainstream / high-liquidity / healthier tokens avoid being pushed to
copyability 0?
```

## Scope

Batch 2 should include:

```text
mainstream BNB tokens
stablecoin / infrastructure controls
high-liquidity active tokens
healthier meme-token candidates
fresh meme-token candidates
known weak / risky tokens
```

The first Batch 2 token list only seeds mainstream controls and existing known
samples. Fresh meme-token addresses should be added after manual discovery.

## Important Interpretation Rule

Mainstream controls are not expected to become A-grade opportunities.

They are used to check whether the scoring framework handles:

```text
high liquidity
high volume
special contract permissions
large holder counts
non-meme token behavior
```

For example, a stablecoin can be a poor meme opportunity while still showing
that Copyability v0 should not collapse solely because of liquidity or volume.

## Candidate Controls

Known BNB Chain controls:

| Symbol | Address | Sample Type | Purpose |
|---|---|---|---|
| USDT | `0x55d398326f99059ff775485246999027b3197955` | mainstream | stablecoin / high-liquidity control |
| WBNB | `0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c` | mainstream | wrapped native asset control |
| CAKE | `0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82` | mainstream | active BNB ecosystem token control |
| USDC | `0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d` | mainstream | stablecoin / high-liquidity control |

These addresses are long-lived BNB Chain token contracts. They should still be
checked with live APIs before final interpretation.

## Run Policy

Batch 2 may require fresh Dune execution. Run it separately from Batch 1.

Suggested first run:

```bash
python scripts\batch_analyze_tokens.py --file experiments\phase4-calibration\batch-2-tokens.txt --output experiments\phase4-calibration\batch-2-output.txt
```

JSON output:

```bash
python scripts\batch_analyze_tokens.py --file experiments\phase4-calibration\batch-2-tokens.txt --json --output experiments\phase4-calibration\batch-2-output.json
```

If Dune is slow or expensive, split the file into:

```text
batch-2-controls.txt
batch-2-meme-candidates.txt
```

## What To Check

For each sample, inspect:

```text
grade
action
risk
security
entity
opportunity
copyability
priority
risk_rules
copyability_rules
```

Key checks:

```text
1. Do high-liquidity controls avoid copyability 0?
2. Do special contracts trigger security/risk in expected ways?
3. Do meme candidates still separate into C/D/B instead of all D?
4. Does shared_funder_cluster over-penalize normal launch behavior?
5. Does early_buyer_exit_ratio_high over-penalize active-but-risky tokens?
```

## Tuning Gates

Do not tune rules unless Batch 2 shows one of these problems:

```text
healthy/high-liquidity controls all collapse to copyability 0
every meme candidate becomes D even with positive flow and usable liquidity
priority scores do not separate obvious weak samples from better samples
one rule dominates every result regardless of sample type
```

Likely first tuning candidates:

```text
copyability_volume_weak: -10 -> -5
copyability_shared_funder_risk: -25 -> -20
copyability_early_buyer_exit_ratio_high: -20 -> -15
```

## Completion Criteria

Batch 2 is complete when:

```text
batch-2-output.txt exists
batch-2-output.json exists
batch-2-results.md records observations
at least 4 controls and 4 meme/risky samples are included
python -m pytest passes
rule-tuning decision is recorded
```
