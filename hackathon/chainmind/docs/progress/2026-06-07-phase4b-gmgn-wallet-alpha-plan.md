# ChainMind Phase 4B GMGN Wallet Alpha Plan

Date: 2026-06-07

## 1. Purpose

Phase 4B will add query-only wallet alpha enrichment through GMGN.

The goal is to make ChainMind less dependent on Nansen credits while keeping
the project focused on analysis, not execution.

Phase 4B should answer:

```text
Does this token have meaningful smart-wallet or top-trader participation?
Are the participating wallets active, profitable, or suspicious?
Is the wallet signal still observable or copyable for a normal user?
Can GMGN provide useful wallet and market evidence when Nansen is unavailable?
```

## 2. Scope

In scope:

```text
GMGN query-only client
GMGN API smoke test
Token profile enrichment
Top holders / top traders enrichment
Wallet portfolio / wallet activity enrichment
GMGN mapping into ChainMind snapshot evidence
Optional orchestration integration
Unit tests
Real-token validation notes
```

Out of scope:

```text
Swap execution
Auto buy
Auto sell
Copy trading execution
Private key loading
Trading wallet management
Order routing
```

Phase 4B must not require a private key.

## 3. Data Source Roles

GMGN will become the primary Phase 4B replacement candidate for the Nansen smart
money layer.

```text
GMGN   = smart-wallet, top-trader, trending, portfolio, wallet activity signals
GoPlus = address, contract, approval, phishing, and transaction security signals
Dune   = deep validation, early buyers, same-funder, wallet age, retention
Nansen = optional smart-money enrichment when credits are available
```

This means GMGN replaces part of Nansen's role, not every external data source.

## 4. Authentication Rule

Phase 4B only uses GMGN query capability.

```text
Required:
GMGN_API_KEY
GMGN_CHAIN

Not used in Phase 4B:
GMGN_PRIVATE_KEY
GMGN_PRIVATE_KEY_PATH
```

Trading features require private-key or hosted-wallet permissions and belong to
a later phase.

## 5. Proposed Implementation Steps

### Step 1: Documentation Boundary

Create this plan and document that auto trading is deferred to a future phase.

### Step 2: GMGN Query Client

Add:

```text
src/chainmind/data/gmgn_client.py
```

Initial methods should be query-only:

```text
get_token_profile(token_address)
get_token_top_traders(token_address)
get_token_top_holders(token_address)
get_wallet_profile(wallet_address)
get_wallet_activity(wallet_address)
get_trending_tokens()
```

The first implementation can start with the smallest stable subset if the GMGN
API surface requires incremental confirmation.

### Step 3: Smoke Test

Update:

```text
scripts/smoke_test_apis.py
```

Expected behavior:

```text
GMGN_API_KEY empty -> SKIP
GMGN query succeeds -> PASS
GMGN query fails -> FAIL
```

The smoke test should not perform any trade, swap, signature, or private-key
operation.

### Step 4: Mapping Layer

Add mapper functions in:

```text
src/chainmind/data/api_mappers.py
```

Candidate output fields:

```text
intelligence.gmgn
wallet_alpha
trader_signals
top_trader_count
top_holder_count
smart_wallet_count
sniper_count
insider_count
bundled_wallet_count
wallet_pnl_sample
wallet_recent_activity_sample
wallet_signal_confidence
```

GMGN evidence should be explainable. Raw API payloads should not leak into the
final snapshot unless intentionally sampled.

### Step 5: Orchestration

Update:

```text
src/chainmind/orchestration/analyze_dune_token.py
```

GMGN should be optional, like Nansen.

```text
GMGN failure -> append warning, continue analysis
Nansen failure -> append warning, continue analysis
GoPlus / Honeypot / Dune risk evidence remains authoritative
```

GMGN positive signals should increase observation priority, but they must not
cancel hard security risks.

### Step 6: Scoring Integration

First version:

```text
Add GMGN evidence to priority_evidence and copyability_evidence.
Use small score adjustments only.
Do not lower risk because of GMGN smart-wallet participation.
```

Suggested initial scoring direction:

```text
Top traders / smart-wallet participation -> small priority boost
Healthy wallet activity / PnL evidence -> small copyability boost
Sniper / insider / bundled-wallet concentration -> risk or copyability penalty
```

### Step 7: Tests

Add or update:

```text
tests/unit/test_api_clients.py
tests/unit/test_api_mappers.py
tests/unit/test_analyze_dune_token_orchestration.py
tests/unit/test_priority_scoring.py
tests/unit/test_copyability_scoring.py
```

Required test behavior:

```text
GMGN client reads only query credentials.
GMGN client does not read private keys.
GMGN mapper produces stable snapshot fields.
GMGN failures do not stop token analysis.
GMGN evidence appears in final output.
```

### Step 8: Real-Token Validation

Create validation notes under:

```text
experiments/phase4-calibration/
```

Suggested files:

```text
gmgn-batch-1-output.txt
gmgn-batch-1-results.md
```

Validation sample types:

```text
new meme token
active real trading token
mainstream or infrastructure control token
```

## 6. Completion Criteria

Phase 4B is complete when:

```text
GMGN query-only client exists.
GMGN smoke test no longer returns "configured but not implemented".
GMGN query evidence can enter analysis output.
Nansen is no longer a Phase 4 blocker.
Private-key and swap features remain out of Phase 4.
Unit tests pass.
At least one GMGN validation note is recorded.
```

## 7. Future Phase: Assisted Trading / Automation

Auto trading is intentionally deferred.

Future trading work should have its own phase and risk controls:

```text
manual confirmation before execution
dry-run mode
per-trade limits
daily loss limits
allowlist / blocklist
slippage caps
simulation before submission
private-key isolation
audit logs
kill switch
no autonomous trading without explicit user approval
```

Candidate future name:

```text
Phase 6: Assisted Trading Execution
```

This future phase can evaluate GMGN swap / trading capabilities, but Phase 4B
must remain query-only.
