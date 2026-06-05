# Phase 4A.1 Calibration Batch 2

## Status

Partially run.

The full Dune-backed Batch 2 command timed out after 5 minutes. No
`batch-2-output.txt` or `batch-2-output.json` was produced.

Follow-up action:

```text
Run mainstream/high-liquidity controls through Quick Screen first, then design
lighter Dune control queries if deep analysis is still needed.
```

## Purpose

Batch 2 adds mainstream and high-liquidity controls to check whether
Copyability v0 is over-penalizing tokens outside the risky cached meme samples.

## Planned Command

```bash
python scripts\batch_analyze_tokens.py --file experiments\phase4-calibration\batch-2-tokens.txt --output experiments\phase4-calibration\batch-2-output.txt
python scripts\batch_analyze_tokens.py --file experiments\phase4-calibration\batch-2-tokens.txt --json --output experiments\phase4-calibration\batch-2-output.json
```

## Attempted Dune Run

Command:

```bash
python scripts\batch_analyze_tokens.py --file experiments\phase4-calibration\batch-2-tokens.txt --output experiments\phase4-calibration\batch-2-output.txt
```

Result:

```text
Timed out after 5 minutes.
```

Interpretation:

```text
Existing deep Dune queries are designed around meme-token analysis and can be
too heavy for mainstream/high-volume controls.
```

## Control Quick Screen Results

Recorded in:

```text
experiments/phase4-calibration/batch-2-controls-quick-output.md
```

Summary:

| Token | Symbol | Quick Decision | Main Trigger | Notes |
|---|---:|---:|---|---|
| `0x55d398326f99059ff775485246999027b3197955` | USDT | BLOCK | mintable | High-liquidity stablecoin; mintable is not equivalent to new meme-token mint risk. |
| `0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c` | WBNB | WATCH | owner not renounced / unknown | Wrapped native asset control. |
| `0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82` | CAKE | BLOCK | mintable | Mainstream ecosystem token; special contract permissions expected. |
| `0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d` | UB | WATCH | owner not renounced / unknown | Address/pair symbol should be rechecked before using as canonical USDC. |

## Summary Table

Pending.

## Observations

Mainstream controls confirm an important boundary:

```text
Rules that are correct for new meme tokens can be too coarse for mainstream or
infrastructure assets.
```

This does not invalidate Copyability v0. It means Batch 2 should not compare
mainstream controls and meme candidates as if they share the same product
context.

Future scoring should add a lightweight context field:

```text
token_profile = meme_candidate | mainstream_control | infrastructure
```

Until then, mainstream controls should be used to inspect individual rule
behavior, not to assign final A/B/C/D opportunity grades.

## Rule Tuning Decision

Do not tune Copyability v0 yet.

Decision:

```text
Keep Phase 4A rules unchanged.
Create a lighter Batch 2B path for controls instead of forcing the existing
Dune deep-analysis queries onto mainstream/high-volume tokens.
```
