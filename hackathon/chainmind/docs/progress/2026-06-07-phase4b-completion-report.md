# ChainMind Phase 4B Completion Report

Date: 2026-06-07

## 1. Status

Current status:

```text
Phase 4A: completed
Phase 4A.1: calibration started
Phase 4B: completed as GMGN query-only Wallet Alpha v0
```

Phase 4B is complete for the current scope:

```text
GMGN query-only enrichment
GMGN smoke test
GMGN mapper
GMGN optional orchestration merge
real-token validation note
```

## 2. Scope Boundary

Phase 4B does not include trading.

Excluded:

```text
swap execution
auto buy
auto sell
copy trading execution
private-key loading
order routing
```

Future trading work is deferred to a later phase, currently documented as:

```text
Phase 6: Assisted Trading Execution
```

## 3. New Capabilities

New client:

```text
src/chainmind/data/gmgn_client.py
```

Supported query-only methods:

```text
get_token_info()
get_token_security()
get_token_holders()
get_token_traders()
get_token_intelligence()
get_trending_tokens()
get_wallet_holdings()
get_wallet_activity()
get_wallet_stats()
```

GMGN now enters the main snapshot as:

```text
snapshot.intelligence.gmgn
```

Mapped fields:

```text
source
top_holder_count
top_trader_count
smart_wallet_count
sniper_count
insider_count
bundled_wallet_count
has_wallet_signal
has_risk_wallet_signal
token_info_sample
token_security_sample
top_holders_sample
top_traders_sample
```

## 4. Nansen Replacement Status

GMGN is now the primary Phase 4B replacement candidate for Nansen's wallet
intelligence role.

Current source roles:

```text
GMGN   = wallet intelligence, top traders, top holders, trending, portfolio/activity
GoPlus = token/address/security risk
Dune   = deep validation, early buyers, funding, retention
Nansen = optional smart-money enrichment when credits are available
```

During validation, Nansen returned insufficient credits:

```text
HTTP 403
Insufficient credits remaining to call this endpoint.
```

This confirms that Nansen must not block Phase 4.

## 5. Validation

Smoke test:

```text
GMGN: PASS
query-only trending reachable; rows=3
```

Real token validation:

```text
Token: BNB USDT
Address: 0x55d398326f99059ff775485246999027b3197955
Snapshot: experiments/phase4-calibration/gmgn-batch-1-snapshot.json
Report: experiments/phase4-calibration/gmgn-batch-1-results.md
```

Real analysis result:

```text
Merged GMGN query-only intelligence data.
Nansen API failed because of insufficient credits.
```

## 6. Tests

Full test suite:

```text
python -m pytest
79 passed
```

Additional targeted validation:

```text
GMGN client unit tests
GMGN mapper unit tests
analyze_dune_token orchestration tests
smoke test with GMGN query-only CLI
real analyze_dune_token run with saved snapshot
```

## 7. Implementation Notes

Windows compatibility fixes were required:

```text
Resolve gmgn-cli / npx executable with shutil.which().
Decode gmgn-cli output as UTF-8 instead of the Windows default code page.
Map ChainMind chain name "bnb" to GMGN chain name "bsc".
```

Configuration now supports:

```text
GMGN_API_KEY
GMGN_CLI_COMMAND
GMGN_CHAIN
```

Phase 4B does not use:

```text
GMGN_PRIVATE_KEY
GMGN_PRIVATE_KEY_PATH
```

## 8. Remaining Work After Phase 4B

Recommended next work:

```text
1. Run GMGN validation on meme/new-pool tokens, not only USDT control.
2. Add GMGN-derived scoring evidence to priority/copyability carefully.
3. Add GoPlus address_security for early-buyer wallet risk.
4. Expand wallet activity enrichment once GMGN response shapes are stable.
5. Keep automated trading in a separate future phase.
```

## 9. Conclusion

Phase 4B is complete as a query-only Wallet Alpha v0.

ChainMind can now continue wallet-intelligence enrichment through GMGN even when
Nansen credits are unavailable. The framework remains analysis-only and leaves
enough space for future trading automation without pushing the current design
back to a rewrite.
