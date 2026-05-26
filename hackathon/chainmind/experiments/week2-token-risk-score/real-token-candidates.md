# Phase 2 Real Token Candidates

Collected date: 2026-05-26

These are real BNB Chain meme token candidates for Phase 2 validation. They are not yet analyzed or scored. The next step is to create Dune saved queries, fill query ids in `.env`, then run Dune API automation.

## Candidate Addresses

| Label | Chain | Token address | Notes |
| --- | --- | --- | --- |
| candidate_1 | bnb | `0xc911e8f97a02b7469294cb89440a6c616abd7777` | New meme token provided for Phase 2 validation |
| candidate_2 | bnb | `0xff6b0006d17af50a0c0082ca1beb03af3f284444` | New meme token provided for Phase 2 validation |
| candidate_3 | bnb | `0x9ec5d5082895b8bf56523e02a831aa0dc8737777` | New meme token provided for Phase 2 validation |

## Next Validation Steps

1. Create saved Dune queries from the four parameterized SQL files.
2. Ensure each Dune query has a Text parameter named `token_address`.
3. Put query ids into local `.env`.
4. Build and run the Dune API client.
5. Generate real snapshot JSON files under:

```text
experiments/week2-token-risk-score/real-token-snapshots/
```

6. Run ChainMind scoring and record `risk_score`, `risk_evidence`, and `data_quality`.
