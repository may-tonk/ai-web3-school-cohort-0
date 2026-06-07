# GMGN Batch 1 Validation Results

Date: 2026-06-07

## Purpose

Validate Phase 4B GMGN query-only integration on a real BNB Chain token and
confirm that ChainMind can continue analysis when Nansen credits are exhausted.

## Environment

```text
GMGN_API_KEY: configured
GMGN_CLI_COMMAND: npx gmgn-cli
GMGN_CHAIN: bsc
Private key: not used
Trading / swap: not used
```

The local machine did not have a global `gmgn-cli` executable. Validation used
`npx gmgn-cli` through `GMGN_CLI_COMMAND`.

## Smoke Test

Command:

```bash
python scripts\smoke_test_apis.py --token-address 0x55d398326f99059ff775485246999027b3197955 --timeout 60 --json
```

Important result:

```text
GMGN: PASS, query-only trending reachable; rows=3
Nansen: FAIL, request failed
Etherscan V2: WARN, free API access is not supported for BNB Chain
```

Interpretation:

```text
GMGN query-only access is available.
Nansen is not reliable for Phase 4 because the account can hit insufficient credits.
Etherscan remains non-blocking for BNB Chain free-tier coverage.
```

## Real Token Analysis

Token:

```text
USDT on BNB Chain
0x55d398326f99059ff775485246999027b3197955
```

Command:

```bash
python scripts\analyze_dune_token.py 0x55d398326f99059ff775485246999027b3197955 --save-snapshot experiments\phase4-calibration\gmgn-batch-1-snapshot.json
```

Saved snapshot:

```text
experiments/phase4-calibration/gmgn-batch-1-snapshot.json
```

Important result:

```text
Merged GMGN query-only intelligence data.
Nansen API failed: insufficient credits.
```

Snapshot GMGN fields:

```text
snapshot.intelligence.gmgn.source = gmgn
snapshot.intelligence.gmgn.top_holder_count = 0
snapshot.intelligence.gmgn.top_trader_count = 0
snapshot.intelligence.gmgn.smart_wallet_count = 0
snapshot.intelligence.gmgn.sniper_count = 0
snapshot.intelligence.gmgn.insider_count = 0
snapshot.intelligence.gmgn.bundled_wallet_count = 0
snapshot.intelligence.gmgn.has_wallet_signal = false
```

Interpretation:

```text
GMGN successfully entered the ChainMind snapshot.
USDT is a mainstream control token, so a lack of meme-style top trader or sniper
signals is acceptable for this validation sample.
The important validation point is not alpha discovery on USDT; it is successful
query, mapping, orchestration merge, and non-blocking Nansen failure handling.
```

## Issues Found And Fixed

Two implementation issues were found during validation:

```text
1. Windows subprocess could not find npx/gmgn-cli unless the executable was resolved.
2. Windows GBK decoding failed on gmgn-cli UTF-8 output.
```

Fixes:

```text
GmgnClient now resolves CLI executables with shutil.which().
GmgnClient now decodes subprocess output as UTF-8 with replacement for invalid bytes.
GmgnClient maps ChainMind chain "bnb" to GMGN chain "bsc".
```

## Conclusion

GMGN query-only integration is validated at the infrastructure level.

Phase 4B can treat GMGN as the primary Nansen replacement candidate for:

```text
query-only wallet intelligence
top holder / top trader evidence
trending token checks
future wallet activity enrichment
```

Nansen should remain optional because the current account can return insufficient
credits.
