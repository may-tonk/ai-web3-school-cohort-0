# 06. Dune / API 输出到 ChainMind Snapshot 的字段映射

本文定义真实 token 数据如何整理成 ChainMind 的 `TokenSnapshot` JSON。它用于 Phase 2 的真实 token 小样本验证，也为后续 Hermes / API 自动化接入做字段约定。

## 1. 总体原则

ChainMind 不应该用 Dune 重复计算所有基础指标。推荐分工是：

```text
API：获取快照型基础数据和安全数据
Dune：获取行为型、关系型、时间序列型数据
ChainMind：负责数据质量检查、风险评分、证据输出
AI：负责基于结构化证据生成人类可读解释
```

第一版真实样本可以手动整理为 JSON。等字段稳定后，再考虑自动化采集和数据库存储。

## 2. Snapshot 顶层结构

真实 token snapshot 建议使用以下结构：

```json
{
  "sample_meta": {},
  "token": {},
  "market": {},
  "flow_5m": [],
  "early_buyers": [],
  "funding": {},
  "security": {},
  "data_quality": {}
}
```

其中：

- `sample_meta` 记录样本来源，不参与评分。
- `token` 记录 token 基础身份。
- `market` 记录 API 或 Dune 汇总得到的基础市场快照。
- `flow_5m` 记录 Dune 五分钟买卖盘。
- `early_buyers` 记录 Dune 早期买家和余额。
- `funding` 记录 Dune 早期买家资金来源聚合。
- `security` 记录 GoPlus / BscScan 等安全结果。
- `data_quality` 通常留空，由 ChainMind 运行时计算。

## 3. sample_meta

真实样本建议写：

```json
{
  "sample_meta": {
    "sample_type": "real",
    "purpose": "phase2_validation",
    "is_real_onchain_data": true,
    "sources": ["dune", "dexscreener", "goplus"],
    "collected_at": "2026-05-25T00:00:00Z",
    "notes": "Manual snapshot assembled for Phase 2 validation."
  }
}
```

synthetic 样本必须写：

```json
{
  "sample_type": "synthetic",
  "is_real_onchain_data": false
}
```

避免后续把手写测试数据误当真实链上案例。

## 4. API 到 JSON 的映射

### 4.1 token

| JSON 字段 | 推荐来源 | 说明 |
| --- | --- | --- |
| `token.address` | 用户输入 / API | token 合约地址 |
| `token.symbol` | DEX Screener / token metadata API | symbol 缺失时可用 `UNKNOWN` |
| `token.chain` | 固定为 `bnb` | Phase 2 先聚焦 BNB |
| `token.created_at` | Dune `bnb.creation_traces` / BscScan | 如果没有可省略 |

示例：

```json
{
  "token": {
    "address": "0x...",
    "symbol": "XXX",
    "chain": "bnb",
    "created_at": "2026-05-25T00:00:00Z"
  }
}
```

### 4.2 market

| JSON 字段 | 推荐来源 | 说明 |
| --- | --- | --- |
| `market.liquidity_usd` | DEX Screener / Birdeye | Token Risk v0.1 已使用 |
| `market.volume_5m_usd` | DEX Screener / Birdeye | Opportunity Score 已使用 |
| `market.volume_1h_usd` | DEX Screener / Birdeye | 后续可用于趋势判断 |
| `market.holder_count` | GoPlus / BscScan / 其他 API | 当前不作为核心规则 |
| `market.pair_address` | DEX Screener | 可用于定位主池 |
| `market.market_cap_usd` | DEX Screener / Birdeye | 后续可用于入场阶段判断 |

注意：

```text
holder 集中度、流动性、价格、成交量等基础指标优先走 API。
Dune 主要承担行为分析，不需要重复做所有静态指标。
```

## 5. Dune SQL 到 JSON 的映射

## 5.1 token_trading_activity.sql

文件：

```text
src/chainmind/queries/dune/bnb/token_trading_activity.sql
```

用途：

```text
确认主要交易池、交易量、交易人数、首笔交易时间和主池占比。
```

推荐映射：

| SQL 输出字段 | JSON 目标字段 | 说明 |
| --- | --- | --- |
| `pool_address` | `market.pair_address` | 取 volume 最大的一行作为主池 |
| `volume_usd` | `market.volume_source_dune_usd` | 可作为 API volume 交叉验证 |
| `unique_traders` | `market.unique_traders_30d` | 可用于判断样本规模 |
| `first_trade_time` | `token.first_trade_time` | 可辅助判断开池时间 |
| `main_pool_share` | `market.main_pool_share` | 多池分散时降低置信度 |

如果 API 已经提供更稳定的流动性和成交量，Dune 的结果主要作为交叉验证，不必强行覆盖 API 字段。

## 5.2 five_minute_flow.sql

文件：

```text
src/chainmind/queries/dune/bnb/five_minute_flow.sql
```

用途：

```text
判断买卖盘质量、刷量嫌疑和卖压变化。
```

推荐映射到 `flow_5m`：

| SQL 输出字段 | JSON 字段 | Token Risk 是否使用 |
| --- | --- | --- |
| `bucket_5m` | `flow_5m[].bucket` | 否，辅助展示 |
| `trades` | `flow_5m[].trades` | 是 |
| `unique_traders` | `flow_5m[].unique_traders` | 是 |
| `buy_trades` | `flow_5m[].buy_trades` | 暂未使用 |
| `sell_trades` | `flow_5m[].sell_trades` | 暂未使用 |
| `buyers` | `flow_5m[].buyers` | 是 |
| `sellers` | `flow_5m[].sellers` | 是 |
| `buy_volume_usd` | `flow_5m[].buy_volume_usd` | 是 |
| `sell_volume_usd` | `flow_5m[].sell_volume_usd` | 是 |
| `net_buy_usd` | `flow_5m[].net_buy_usd` | 是 |

示例：

```json
{
  "flow_5m": [
    {
      "bucket": "2026-05-25T12:00:00Z",
      "trades": 120,
      "unique_traders": 40,
      "buyers": 25,
      "sellers": 18,
      "buy_volume_usd": 18000,
      "sell_volume_usd": 9000,
      "net_buy_usd": 9000
    }
  ]
}
```

缺失处理：

- 如果 `amount_usd` 大量为空，保留行，但 Data Quality 应提示 USD volume 可信度较低。
- 如果完全没有 `flow_5m`，不要编造，留空数组。
- 留空会导致 Data Quality 降级。

## 5.3 early_buyers.sql

文件：

```text
src/chainmind/queries/dune/bnb/early_buyers.sql
```

用途：

```text
判断早期买家是否已经撤退，尤其是前 20 / 50 / 100 买家 remaining_ratio。
```

推荐映射到 `early_buyers`：

| SQL 输出字段 | JSON 字段 | Token Risk 是否使用 |
| --- | --- | --- |
| `buyer_rank` | `early_buyers[].rank` | 否，辅助排序 |
| `buyer` | `early_buyers[].wallet` | 否，作为证据上下文 |
| `first_buy_time` | `early_buyers[].first_buy_time` | 后续可用 |
| `buy_trades` | `early_buyers[].buy_trades` | 暂未使用 |
| `tokens_bought` | `early_buyers[].tokens_bought` | 暂未使用 |
| `buy_usd` | `early_buyers[].buy_usd` | 后续可用于大买家风险 |
| `current_balance` | `early_buyers[].current_balance` | 暂未直接使用 |
| `remaining_ratio` | `early_buyers[].remaining_ratio` | 是 |

当前代码同时兼容：

```text
current_balance_ratio
remaining_ratio
```

真实 Dune 数据建议使用：

```json
{
  "remaining_ratio": 0.42
}
```

缺失处理：

- 如果 `remaining_ratio` 因 token transfer 字段不准而异常，需要在样本 notes 中标明。
- 如果只拿到早期买家列表，拿不到余额，不要手填比例。
- 留空时 Data Quality 可能仍认为有 early buyer 数据，但早期退出规则不会有效触发。

## 5.4 early_buyer_funding.sql

文件：

```text
src/chainmind/queries/dune/bnb/early_buyer_funding.sql
```

用途：

```text
判断早期买家是否存在同 funder、新钱包、低历史交易数等同实体或假共识线索。
```

推荐映射有两部分。

### early_buyers 补充字段

| SQL 输出字段 | JSON 字段 | 说明 |
| --- | --- | --- |
| `wallet_age_days_at_entry` | `early_buyers[].wallet_age_days` | 可用于计算新钱包比例 |
| `tx_count_before_entry` | `early_buyers[].tx_count_before_entry` | 可用于判断新钱包 |
| `funder` | `early_buyers[].first_funder` | 可作为上下文 |

### funding 聚合字段

| SQL 输出字段 | JSON 字段 | Token Risk 是否使用 |
| --- | --- | --- |
| `funder` | `funding.shared_funders[].funder` | 是，作为上下文 |
| `funded_selected_early_buyers` | `funding.shared_funders[].funded_early_buyers` | 是 |
| `infrastructure_label` | `funding.shared_funders[].is_infrastructure` | 是，需人工转换 |
| `total_funded_bnb` | `funding.shared_funders[].total_funded_bnb` | 暂未使用 |
| derived | `funding.new_wallet_ratio` | 是 |

示例：

```json
{
  "funding": {
    "shared_funders": [
      {
        "funder": "0x...",
        "funded_early_buyers": 4,
        "is_infrastructure": false,
        "total_funded_bnb": 2.4
      }
    ],
    "new_wallet_ratio": 0.8
  }
}
```

`is_infrastructure` 判断建议：

```text
如果 Dune 的 infrastructure_label 非空，则填 true。
如果 funder 是 router、pool、CEX 热钱包、常见 gas 分发地址，也应填 true。
无法确认时先填 false，但在 notes 中标记不确定。
```

缺失处理：

- 如果 funding 数据没有跑，`funding` 留空对象或省略。
- Data Quality 会标记缺少 funding。
- 不要因为缺少 funding 就假设没有 same-funder 风险。

## 6. security 字段

第一版建议来自 GoPlus / BscScan / 其他安全 API。

推荐结构：

```json
{
  "security": {
    "source": "goplus",
    "high_risk": false,
    "warnings": [],
    "is_honeypot": false,
    "buy_tax": 0,
    "sell_tax": 0,
    "can_take_back_ownership": false,
    "is_blacklisted": false,
    "is_mintable": false
  }
}
```

当前 Token Risk v0.1 只使用：

```text
security.high_risk
```

后续可以逐步把 honeypot、tax、mint、blacklist、LP 风险拆成独立证据。

## 7. 数据缺失处理规则

不要为了让评分完整而伪造字段。

建议：

| 缺失内容 | 处理方式 |
| --- | --- |
| 没有 `market` | 留空，Data Quality 降级 |
| 没有 `flow_5m` | 留空数组，不能判断买卖盘 |
| 没有 `early_buyers` | 留空数组，不能判断早期撤退 |
| 没有 `funding` | 留空对象，不能判断 same-funder |
| 没有 `security` | 留空对象，不能判断合约安全 |
| `amount_usd` 缺失 | 保留原始行，但记录 warning |
| `remaining_ratio` 不可信 | 不要强行使用，写入 notes |

核心原则：

```text
缺失字段应该降低置信度，而不是被填成看起来正常的数据。
```

## 8. Phase 2 真实样本最小要求

每个真实 token snapshot 至少建议具备：

```text
token.address
token.symbol
token.chain
market.liquidity_usd
market.volume_5m_usd
flow_5m 至少 1 条
early_buyers 至少 5 条
security.high_risk
```

如果要验证 same-funder 规则，还需要：

```text
funding.shared_funders
funding.new_wallet_ratio
```

如果这些字段不足，仍然可以跑 ChainMind，但输出只能作为低置信度分析。

## 9. 手动整理真实样本的建议流程

```text
1. 选定 token 地址。
2. 用 API 获取 token / market / security 基础字段。
3. 在 Dune 运行 token_trading_activity.sql。
4. 在 Dune 运行 five_minute_flow.sql。
5. 在 Dune 运行 early_buyers.sql。
6. 如需 same-funder，运行 early_buyer_funding.sql。
7. 按本文映射整理成 JSON。
8. 运行 chainmind-analyze-token 或 scripts/analyze_token.py。
9. 记录 risk_score、risk_evidence、data_quality。
10. 人工判断结果是否合理。
```

## 10. 后续自动化方向

等真实样本验证通过后，可以再考虑自动化：

```text
API client 拉 market/security
Dune API 拉查询结果
ChainMind 自动合并为 TokenSnapshot
Hermes 负责调度和推送
```

在字段和规则稳定之前，不建议过早把 Hermes 接入全自动流程。
