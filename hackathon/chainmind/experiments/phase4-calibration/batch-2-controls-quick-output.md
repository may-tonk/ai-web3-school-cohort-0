# Batch 2 Controls Quick Screen Output

Date: 2026-06-05

Purpose: run mainstream/high-liquidity controls through the low-latency quick
screen after the full Dune-backed Batch 2 run timed out.

## USDT

Token:

```text
0x55d398326f99059ff775485246999027b3197955
```

Result:

```text
Decision: BLOCK
Symbol: USDT
Liquidity USD: 41,192,685.27
24h Volume USD: 13,827,948.43
Honeypot: False
Buy Tax: 0.00%
Sell Tax: 0.00%
Owner Renounced: False
Mintable: True
Holder Count: 0
Reason: quick_mintable_block
```

Interpretation: USDT is a high-liquidity stablecoin control, not a meme
opportunity. The mintable flag is expected for some mainstream/infrastructure
contracts and should not be interpreted the same way as a new meme-token
mintable flag.

## WBNB

Token:

```text
0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c
```

Result:

```text
Decision: WATCH
Symbol: WBNB
Liquidity USD: 35,185,475.58
24h Volume USD: 12,062,003.42
Honeypot: False
Buy Tax: 0.00%
Sell Tax: 0.00%
Owner Renounced: N/A
Mintable: False
Holder Count: 6,251,456
Reason: quick_owner_not_renounced_watch
```

Interpretation: WBNB behaves like a high-liquidity control. Owner-renounced
metadata is not enough to evaluate wrapped native asset contracts.

## CAKE

Token:

```text
0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82
```

Result:

```text
Decision: BLOCK
Symbol: Cake
Liquidity USD: 12,739,291.18
24h Volume USD: 323,585.81
Honeypot: False
Buy Tax: 0.00%
Sell Tax: 0.00%
Owner Renounced: False
Mintable: True
Holder Count: 1,904,787
Reason: quick_mintable_block
```

Interpretation: CAKE is a mainstream ecosystem token. Like USDT, the mintable
flag should be interpreted differently from a new meme token.

## USDC Control Address

Token:

```text
0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d
```

Result:

```text
Decision: WATCH
Symbol: UB
Liquidity USD: 3,449,862.84
24h Volume USD: 12,212,819.92
Honeypot: False
Buy Tax: 0.00%
Sell Tax: 0.00%
Owner Renounced: N/A
Mintable: N/A
Holder Count: 3,742,335
Reason: quick_owner_not_renounced_watch
```

Interpretation: DexScreener returned symbol `UB` for the selected pair, so this
control should be rechecked before using it as a canonical USDC sample.

## Takeaway

Quick Screen controls show that mainstream/infrastructure tokens can trigger
rules that are correct for new meme tokens but too coarse for non-meme assets.

This supports adding a future context flag such as:

```text
token_profile = meme_candidate | mainstream_control | infrastructure
```

The current Phase 4A scoring package should remain focused on BNB meme-token
risk filtering until that context layer exists.
