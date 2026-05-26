# Phase 2 Real Dune Validation - BNB Meme Tokens

Date: 2026-05-26

## Goal

Use real BNB Chain meme token addresses to validate whether the Phase 2 Dune API path can produce usable ChainMind token risk snapshots.

This validation focuses on the current Dune-only pipeline:

1. Run saved Dune queries with `token_address`.
2. Map query rows into `TokenSnapshot`.
3. Run ChainMind risk scoring.
4. Save real snapshots for later rule calibration.

## Inputs

| Candidate | Token Address |
| --- | --- |
| candidate_1 | `0xc911e8f97a02b7469294cb89440a6c616abd7777` |
| candidate_2 | `0xff6b0006d17af50a0c0082ca1beb03af3f284444` |
| candidate_3 | `0x9ec5d5082895b8bf56523e02a831aa0dc8737777` |

## Dune Queries Used

| Query | Purpose |
| --- | --- |
| `trading_activity` | 30d trading activity and DEX source summary |
| `five_minute_flow` | 5-minute buy/sell pressure |
| `early_buyers` | First 100 buyer behavior and remaining ratio |
| `early_buyer_funding` | Early buyer funder clustering |

## Results

| Candidate | First Trade Time | Volume USD | Traders | Trades | Grade | Action | Risk Score | Data Quality |
| --- | --- | ---: | ---: | ---: | --- | --- | ---: | --- |
| candidate_1 | 2026-05-26 09:23:34 UTC | 218,302 | 919 | 3,119 | D | filter | 95 | good |
| candidate_2 | 2026-05-22 14:30:50 UTC | 487,244 | 1,217 | 5,559 | C | store_only | 65 | good |
| candidate_3 | 2026-05-24 13:02:52 UTC | 698,556 | 2,272 | 9,184 | C | store_only | 65 | good |

## Risk Evidence

| Candidate | Triggered Evidence |
| --- | --- |
| candidate_1 | `negative_latest_net_buy`, `sell_pressure_dominates`, `early_buyer_exit_ratio_high`, `shared_funder_cluster` |
| candidate_2 | `early_buyer_exit_ratio_high`, `shared_funder_cluster` |
| candidate_3 | `early_buyer_exit_ratio_high`, `shared_funder_cluster` |

## Saved Snapshots

| Candidate | Snapshot |
| --- | --- |
| candidate_1 | `experiments/week2-token-risk-score/real-token-snapshots/candidate_1_snapshot.json` |
| candidate_2 | `experiments/week2-token-risk-score/real-token-snapshots/candidate_2_snapshot.json` |
| candidate_3 | `experiments/week2-token-risk-score/real-token-snapshots/candidate_3_snapshot.json` |

## Engineering Notes

The Dune API connection was unstable during validation. The project now supports per-query cache and execution recovery in `scripts/analyze_dune_token.py`.

This means:

- successful query rows are saved immediately;
- interrupted Dune executions can be resumed with their `execution_id`;
- reruns do not need to repeat already cached queries;
- this reduces wasted Dune credits and makes real-world validation more practical.

## Current Judgment

The Phase 2 pipeline is viable. We have moved from synthetic sample testing to real BNB meme token validation.

The current rules are useful as a first filter, especially for:

- early buyer exit behavior;
- shared funding source clusters;
- short-term sell pressure.

However, the rules still need calibration before they should be treated as production decisions. In this 3-token sample, all tokens triggered early buyer exit and shared funder evidence. That may be correct for risky meme tokens, but we need a larger comparison set to avoid over-filtering.

## Next Steps

1. Add at least 5-10 more real BNB meme token samples.
2. Include a few tokens that are known to be healthier or longer-lived.
3. Calibrate thresholds for:
   - `early_buyer_exit_ratio_high`;
   - `shared_funder_cluster`;
   - sell pressure rules.
4. Add external security/API fields:
   - honeypot status;
   - buy/sell tax;
   - contract ownership;
   - LP lock/burn status;
   - holder concentration from external APIs if available.
5. After calibration, move from "rule validation" to "AI explanation/report generation".

