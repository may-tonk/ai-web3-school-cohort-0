# Phase 1 Check Report

## Scope

This report records the first check of the Phase 1 Dune manual-analysis flow.
The goal of this check is to confirm that the main Phase 1 query path can run
end to end on one BSC token before the project moves into later stages.

This report is not a multi-token research conclusion.

## Target Token

| Field | Value |
| --- | --- |
| Chain | BSC / BNB Chain |
| Token | `14` |
| Token address | `0x205f39c39f5fe15d4ef000aeb835de8deb264444` |
| Check date | 2026-05-21 |

## Checked Modules

The following Phase 1 modules were exercised in Dune:

1. DEX trading activity and per-window trader activity.
2. Five-minute buy/sell and net-buy observation.
3. Ranked buyer analysis.
4. Holder summary and holder concentration fields.
5. Contract creation lookup through `bnb.creation_traces`.
6. Early-buyer pre-entry BNB funding lookup.
7. Same-source funding aggregation for selected early buyers.

## Contract Creation Check

The contract creation lookup returned a creation record for the target token.

| Field | Observed value |
| --- | --- |
| Creation time | `2026-05-17 16:12:21` |
| Block number | `98843750` |
| Creation tx | `0xe9f50e4d32b55431717ee394d54f1615961b3f293dbdeb5d15a4bc8478b80d01` |
| Created contract | `0x205f39c39f5fe15d4ef000aeb835de8deb264444` |
| Creation-side address observed | `0x757eba15a64468e6535532fcf093cef90e226f85` |

Result:

- The contract-creation query path is usable for this token.
- Bytecode was returned, but bytecode review is outside this Phase 1 flow check.

## Trading And Holder Check

The Dune dashboard returned:

- trader activity over time;
- net-buy observations;
- buy/sell trade split observations;
- ranked buyer rows;
- per-trader buy, sell, realized-net, and net-token fields;
- holder summary fields including holder count and top-holder concentration.

The observed holder summary included:

| Field | Observed value |
| --- | --- |
| Holder count | `1985` |
| Buy volume USD | `2188487.9` |
| Sell volume USD | `2169786.4` |
| Net buy USD | `18701.5` |
| Top 10 supply pct | `0.2` |
| Top 20 supply pct | `0.3` |

Result:

- The trading and holder views provide the fields required for the first
  Phase 1 pass.
- Percentage display units should be confirmed before using concentration
  fields in a formal rule.

## Early Buyer Check

The ranked buyer query returned early buyers with:

- buyer rank;
- buyer address;
- first buy time;
- buy trade count;
- tokens bought;
- buy amount in USD;
- current balance fields.

The first five early buyers used in the funding check were:

| Rank | Buyer |
| --- | --- |
| 1 | `0x0f80aa9dd2aff0d79455a1f7843c6e39e5a27985` |
| 2 | `0xa9b0295aa2d8486735d3fb3e92ab77e678ae3f9a` |
| 3 | `0x79e337339346c9f5786a746916a0600d3f9eda65` |
| 4 | `0x175c6e02f549d9ae58205693854b2f8f8621022a` |
| 5 | `0x4dc0c365578ed0b5161ce97551c613354df3e400` |

Observation:

- The early-buyer view exposed current-balance information for front-ranked
  buyers, so early exit signals can be checked in this workflow.

## Funding Source Check

The pre-entry funding lookup returned BNB inflows for selected early buyers.
For buyer rank 1, multiple BNB inflows before first buy were observed from:

```text
0x62ccef0b4545166f721caa9fee13c1d3767e27dc
```

The same-source aggregation over the selected early buyers returned:

| Source address | Funded selected early buyers | Notes |
| --- | --- | --- |
| `0x10ed43c718714eb63d5aa57b78b54704e256024e` | `2` | Infrastructure-like address; should not be treated as a human funder without labeling. |
| `0x62ccef0b4545166f721caa9fee13c1d3767e27dc` | `2` | Shared source signal among selected early buyers. |
| `0x5b17dda2510d2d7dfe2cc4a03e4fe597afb65751` | `1` | Single selected early buyer in this check. |

Result:

- The funding lookup can recover pre-entry BNB inflows for early buyers.
- The same-source aggregation can surface shared inbound funding addresses.
- Same-source detection needs address labeling or filtering for routers, pools,
  and other protocol infrastructure before it is promoted into a formal risk rule.

## Check Conclusion

The first Phase 1 Dune manual-analysis flow check is complete for token `14`.
The main analysis path can be executed with the current query approach:

```text
trading activity
-> five-minute flow
-> ranked buyers
-> holder summary
-> contract creation
-> early-buyer funding
-> same-source aggregation
```

The check also identified one important rule-design caution:

```text
Shared inbound addresses are useful evidence, but not every shared source is a
shared human funder.
```

## Follow-Up

The next project step can use this checked flow as input for rule
formalization and later sample expansion. Before automating same-funder risk,
the workflow should separate ordinary wallets from common protocol
infrastructure addresses.
