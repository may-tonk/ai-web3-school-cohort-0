# ChainMind Phase 3 Handoff

Date: 2026-06-01

Purpose: provide a compact project handoff for a new Codex account, new thread, or lost conversation memory.

## How To Resume

If a new assistant starts from scratch, ask it to read these files first:

1. `README.md`
2. `docs/roadmap/07-mvp-roadmap.md`
3. `docs/roadmap/08-execution-plan.md`
4. `docs/progress/2026-05-31-phase3-plan.md`
5. `docs/progress/2026-05-31-phase3-api-requirements.md`
6. `docs/progress/2026-06-01-phase3-real-token-batch-1.md`
7. `docs/progress/2026-06-01-phase3-handoff.md`

Then run:

```bash
python -m pytest
python scripts\smoke_test_apis.py
```

Expected latest test status:

```text
64 passed
```

## Current Phase Status

Phase 3 v1 is complete.

Current definition:

```text
Phase 3 = realtime quick screen + Dune deep analysis + security API integration + entity cluster v0.1 + real sample calibration.
```

The project now has two analysis modes:

1. Quick Screen: low-latency first filter, no Dune dependency.
2. Dune Deep Analysis: slower but deeper wallet, flow, and funding analysis.

## Main Commands

### API Smoke Test

```bash
python scripts\smoke_test_apis.py
```

Purpose:

- Verify configured APIs without printing secrets.
- Checks Dune, DexScreener, GoPlus, Honeypot.is, BNB RPC, Etherscan V2, Nansen, GMGN config status.

Known behavior:

- Etherscan V2 returns WARN because free API access does not support BNB Chain full coverage.
- GMGN returns SKIP because signed request integration is not implemented yet.
- Nansen may fail or warn if credits are exhausted.

### Realtime Quick Screen

```bash
python scripts\quick_screen_token.py <bnb_token_address>
```

Purpose:

- Run low-latency screening without Dune.
- Uses DexScreener, GoPlus, Honeypot.is, and BNB RPC.
- Outputs `PASS`, `WATCH`, or `BLOCK`.

Example:

```bash
python scripts\quick_screen_token.py 0xf500d904b07ac6214be407b69fe817a82eac7777
```

### Dune Deep Analysis

```bash
python scripts\analyze_dune_token.py <bnb_token_address>
```

Purpose:

- Full deep analysis.
- Uses cached Dune rows by default.
- Enriches with DexScreener, GoPlus, Honeypot.is, Nansen, and BNB RPC.

Refresh Dune cache:

```bash
python scripts\analyze_dune_token.py <bnb_token_address> --refresh-cache
```

JSON output:

```bash
python scripts\analyze_dune_token.py <bnb_token_address> --json
```

### Batch Analysis

```bash
python scripts\batch_analyze_tokens.py <token_a> <token_b> <token_c>
```

File input:

```bash
python scripts\batch_analyze_tokens.py --file tokens.txt
```

JSON output:

```bash
python scripts\batch_analyze_tokens.py --file tokens.txt --json
```

## Environment Variables

Configuration lives in `.env`.

Do not print real secrets in assistant responses.

Important variables:

```env
DUNE_API_KEY=
DUNE_QUERY_TOKEN_TRADING_ACTIVITY=
DUNE_QUERY_FIVE_MINUTE_FLOW=
DUNE_QUERY_EARLY_BUYERS=
DUNE_QUERY_EARLY_BUYER_FUNDING=

DEXSCREENER_BASE_URL=https://api.dexscreener.com

GOPLUS_BASE_URL=https://api.gopluslabs.io
GOPLUS_ACCESS_TOKEN=

HONEYPOT_BASE_URL=https://api.honeypot.is

BNB_RPC_URL=

ETHERSCAN_BASE_URL=https://api.etherscan.io/v2/api
ETHERSCAN_API_KEY=
ETHERSCAN_CHAIN_ID=56

NANSEN_BASE_URL=https://api.nansen.ai/api/v1
NANSEN_API_KEY=
NANSEN_CHAIN=bnb

GMGN_API_KEY=
GMGN_PRIVATE_KEY_PATH=runtime/keys/gmgn_ed25519_private.pem
GMGN_CHAIN=bsc
```

Notes:

- `BNB_RPC_URL` must point to BNB Chain. `eth_chainId` should return `0x38`.
- `GOPLUS_ACCESS_TOKEN` can be empty if the public GoPlus endpoint works.
- Etherscan V2 free tier does not currently support full BNB Chain access.
- Nansen credits may run out; the pipeline should degrade gracefully.
- GMGN key is configured, but signed request logic is not implemented.

## APIs Integrated Into Main Flow

### Quick Screen

Integrated:

- DexScreener
- GoPlus
- Honeypot.is
- BNB RPC

Not used:

- Dune
- Nansen
- Etherscan
- GMGN

### Dune Deep Analysis

Integrated:

- Dune
- DexScreener
- GoPlus
- Honeypot.is
- Nansen
- BNB RPC

Optional / limited:

- Etherscan V2 is configured but not useful on free BNB Chain plan.
- GMGN is configured but not implemented.

## Important Files Added Or Updated In Phase 3

Scripts:

- `scripts/smoke_test_apis.py`
- `scripts/quick_screen_token.py`
- `scripts/analyze_dune_token.py`
- `scripts/batch_analyze_tokens.py`

Data clients:

- `src/chainmind/data/http_json.py`
- `src/chainmind/data/dexscreener_client.py`
- `src/chainmind/data/goplus_client.py`
- `src/chainmind/data/honeypot_client.py`
- `src/chainmind/data/nansen_client.py`
- `src/chainmind/data/bnb_rpc_client.py`
- `src/chainmind/data/query_cache.py`
- `src/chainmind/data/api_mappers.py`
- `src/chainmind/data/chain_ids.py`

Orchestration:

- `src/chainmind/orchestration/analyze_dune_token.py`
- `src/chainmind/orchestration/quick_screen_token.py`

Scoring:

- `src/chainmind/scoring/security.py`
- `src/chainmind/scoring/entity_cluster.py`
- `src/chainmind/scoring/quick_screen.py`

Progress docs:

- `docs/progress/2026-05-31-phase3-plan.md`
- `docs/progress/2026-05-31-phase3-api-requirements.md`
- `docs/progress/2026-06-01-phase3-real-token-batch-1.md`
- `docs/progress/2026-06-01-phase3-handoff.md`

## Real Sample Batch 1

Documented in:

```text
docs/progress/2026-06-01-phase3-real-token-batch-1.md
```

Tokens analyzed:

```text
0xf500d904b07ac6214be407b69fe817a82eac7777
0x90166915b98d24d284c56de3b9f4ed59338f7777
0x3d96b30ba2c08724b70efff1ad16d005db1c7777
0x90507254e9c594e728172b9d217f4ab1a2ee7777
```

Batch observation:

- Contract security was mostly clean.
- Honeypot.is returned false for these samples.
- Owner renounced was true.
- Most filter decisions came from behavior and entity signals:
  - early buyer exit,
  - recent sell pressure,
  - shared funder cluster,
  - low liquidity or low volume.

## Known Limitations

1. Dune has delay and can be slow.

   Dune is now treated as deep confirmation, not realtime screening.

2. Nansen credits can run out.

   Nansen should be optional. Missing Nansen data should not block analysis.

3. Etherscan V2 free plan does not support BNB Chain full coverage.

   Keep it configured, but do not depend on it for Phase 3.

4. GMGN signed request flow is not implemented.

   GMGN remains a future realtime intelligence source.

5. Quick Screen can pass tokens that deep Dune analysis later filters.

   This is expected. Quick Screen sees realtime market/security signals, not early-buyer funding structure.

## Next Recommended Work

### Option A: Phase 3 Check Report

Write a formal Phase 3 completion report.

Suggested path:

```text
docs/progress/2026-06-01-phase3-check-report.md
```

Include:

- What Phase 3 completed.
- API status.
- Scripts and commands.
- Real samples.
- Known limitations.
- Next stage recommendation.

### Option B: Phase 3 Calibration

Run more baseline samples:

- mainstream BNB tokens,
- high-liquidity tokens,
- fresh meme tokens,
- obvious low-quality tokens.

Goal:

- Check if rules are too strict.
- Calibrate early-buyer exit threshold.
- Calibrate shared-funder cluster threshold.
- Tune quick-screen WATCH/BLOCK thresholds.

### Option C: GMGN Integration

Implement GMGN signed requests.

Goal:

- Replace part of Nansen's smart-money role.
- Add realtime hot token / smart wallet / market signal data.

### Option D: Phase 4

Based on existing docs, Phase 4 can move toward:

- Wallet Alpha + Copyability, or
- Full scoring system, or
- AI explanation/report layer.

Before starting Phase 4, decide which roadmap naming convention to follow:

- `docs/roadmap/07-mvp-roadmap.md`: Phase 4 = Wallet Alpha + Copyability.
- `docs/roadmap/08-execution-plan.md`: Stage 4 = complete scoring system.
- `docs/learning/13-token-analysis-data-analyst-workflow.md`: Phase 4 = AI explanation layer.

Recommended next practical step:

```text
Write Phase 3 check report, then start calibration before adding more product features.
```

## Resume Prompt For New Account

Use this prompt in a new account/thread:

```text
请先阅读 ChainMind 项目的 README.md，以及 docs/progress/2026-06-01-phase3-handoff.md。
然后检查当前代码和测试状态，继续 Phase 3 后的校准/报告工作。
注意不要打印 .env 中的真实 API key。
```
