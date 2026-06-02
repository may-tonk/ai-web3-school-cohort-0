# Phase 3 Real Token Batch 1

Date: 2026-06-01

Purpose: record the first real BNB token batch after Phase 3 API integration, and use the results to calibrate risk rules.

## Current Pipeline

The real analysis flow now combines:

- Dune: trading activity, five-minute flow, early buyers, early buyer funding.
- DexScreener: market, liquidity, price, pair, and transaction windows.
- GoPlus: token security, owner, holder count, contract metadata.
- Honeypot.is: buy/sell simulation, honeypot status, buy tax, sell tax.
- Nansen: smart money holdings and token holder intelligence when credits are available.
- BNB RPC: direct chain reads such as owner and totalSupply.

Etherscan V2 is configured, but the free API plan does not support BNB Chain full coverage.

## Batch Results

| Token | Symbol | Grade | Action | Risk | Security | Entity | Liquidity USD | 24h Volume USD | 24h Change | Honeypot | Buy Tax | Sell Tax | Holders | Nansen Signal |
|---|---:|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `0xf500d904b07ac6214be407b69fe817a82eac7777` | 世界杯纪念币 | D | filter | 100 | 0 | 50 | 27,518.41 | 14,002.91 | 7.05% | false | 3.99% | 3.98% | 2,520 | false |
| `0x90166915b98d24d284c56de3b9f4ed59338f7777` | 꽈따 | C | store_only | 65 | 0 | 50 | 30,454.50 | 15,960.13 | -27.75% | false | 4.00% | 3.98% | 880 | unavailable |
| `0x3d96b30ba2c08724b70efff1ad16d005db1c7777` | 野马 | D | filter | 100 | 0 | 40 | 19,302.30 | 10,923.22 | -30.93% | false | 4.00% | 3.97% | 1,459 | false |
| `0x90507254e9c594e728172b9d217f4ab1a2ee7777` | 美蛙 | D | filter | 95 | 0 | 50 | 30,088.99 | 486.44 | -5.03% | false | 4.99% | 4.97% | 1,498 | unavailable |

## Token Notes

### 0xf500d904b07ac6214be407b69fe817a82eac7777

Symbol: 世界杯纪念币

Result: D / filter

Main risk rules:

- `negative_latest_net_buy`
- `sell_pressure_dominates`
- `repeated_negative_net_buy`
- `early_buyer_exit_ratio_high`
- `shared_funder_cluster`

Security layer:

- Honeypot: false
- Owner renounced: true
- Buy tax around 4%
- Sell tax around 4%
- Security score: 0

Observation: the token is filtered mainly because of trading behavior and early-buyer structure, not because of direct contract security flags.

### 0x90166915b98d24d284c56de3b9f4ed59338f7777

Symbol: 꽈따

Result: C / store_only

Main risk rules:

- `early_buyer_exit_ratio_high`
- `shared_funder_cluster`

Security layer:

- Honeypot: false
- Owner renounced: true
- Buy tax around 4%
- Sell tax around 4%
- Security score: 0

Observation: this token is the least severe in the batch. It still has early-buyer exit and shared-funder risk, so it is suitable for storage/monitoring rather than priority research.

### 0x3d96b30ba2c08724b70efff1ad16d005db1c7777

Symbol: 野马

Result: D / filter

Main risk rules:

- `low_liquidity`
- `negative_latest_net_buy`
- `sell_pressure_dominates`
- `repeated_negative_net_buy`
- `early_buyer_exit_ratio_high`
- `shared_funder_cluster`

Security layer:

- Honeypot: false
- Owner renounced: true
- Buy tax around 4%
- Sell tax around 4%
- Security score: 0

Observation: this token combines low liquidity, strong recent sell pressure, early-buyer exit, and shared-funder risk. It is a clear filter result under the current rules.

### 0x90507254e9c594e728172b9d217f4ab1a2ee7777

Symbol: 美蛙

Result: D / filter

Main risk rules:

- `negative_latest_net_buy`
- `sell_pressure_dominates`
- `early_buyer_exit_ratio_high`
- `shared_funder_cluster`

Security layer:

- Honeypot: false
- Owner renounced: true
- Buy tax around 5%
- Sell tax around 5%
- Security score: 0

Observation: liquidity is not the weakest in the batch, but 24h volume is low and the token still triggers sell-pressure, early-exit, and entity-cluster risks.

## Cross-Batch Observations

1. Contract security did not drive the filter decisions in this batch.

   All four tokens had `security_score = 0`, Honeypot.is returned `false`, and owner renounced was true.

2. Behavioral risk drove most decisions.

   The most common triggers were:

   - `early_buyer_exit_ratio_high`
   - `shared_funder_cluster`
   - `negative_latest_net_buy`
   - `sell_pressure_dominates`

3. Entity clustering is consistently active.

   Every token triggered shared-funder evidence. This may be a strong signal for BNB meme-token launches, but it needs calibration against more baseline samples.

4. Nansen credits are a current limitation.

   Nansen returned valid results in earlier smoke tests, but this batch hit insufficient credits for some calls. The pipeline handles this as an API warning and continues.

5. Etherscan V2 is not part of the active signal set.

   The key is configured, but free BNB Chain coverage is unavailable. This does not block the current workflow because BNB RPC, Dune, and GoPlus cover the core needs.

## Calibration Questions

- Is `early_buyer_exit_ratio_high` too strict for fast-moving BNB meme tokens?
- Should `shared_funder_cluster` be softened when cluster size is small but common in launch behavior?
- Should recent net-buy pressure be weighted by liquidity and 24h volume?
- Should tokens with clean contract security but bad behavior always receive D/filter?
- Do we need a separate `monitor_only` category between `store_only` and `filter`?

## Next Steps

1. Run a baseline batch with stable or mainstream BNB tokens.
2. Run another batch with fresh meme tokens from the same discovery source.
3. Compare false positives and rule sensitivity.
4. Decide whether to tune:
   - early-buyer exit threshold,
   - shared-funder cluster threshold,
   - low-liquidity threshold,
   - repeated negative net-buy threshold.
5. Add a short calibration summary after each batch.
