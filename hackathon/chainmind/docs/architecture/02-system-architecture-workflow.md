# 02. 系统架构与 Workflow

## 总体 Workflow

```text
链上 API / Dune / DEX 数据源
        ↓
数据清洗与结构化
        ↓
Token Risk Filter
        ↓
Entity Detection Layer
        ↓
Wallet Quality / Copyability Layer
        ↓
规则过滤 95%-99% 噪音
        ↓
AI Explanation Layer
        ↓
Hermes 推送到 Telegram / 文档 / 群组
        ↓
每日复盘与评分校正
```

## 各组件分工

### Dune

适合做：

- 历史分析。
- 回测。
- 地址研究。
- token 早期交易行为聚合。
- 形成固定 SQL 模板。

不适合承担高频实时监听。

### 链上 API

适合做：

- 新 token / 新 pool 实时发现。
- 重点钱包买入监听。
- 较低延迟的交易、余额、合约状态查询。

候选数据源：

- BscScan / Etherscan API
- Alchemy
- Helius
- DEX Screener API
- Birdeye API
- GoPlus API

### 规则引擎

负责：

- 计算风险指标。
- 过滤明显垃圾 token。
- 生成评分。
- 输出结构化摘要给 AI。

### AI

负责：

- 把复杂指标解释成人话。
- 总结机会和风险。
- 生成 Telegram 推送文案。
- 生成每日复盘报告。
- 比较多个候选 token 的优先级。

不负责：

- 直接处理全量原始交易。
- 直接预测涨跌。
- 替代链上计算。
- 替代规则引擎。

### Hermes

适合作为：

- 定时调度层。
- 触发器层。
- Telegram / 群组 / 文档推送层。
- 每日复盘任务调度层。

## 建议系统分层

```text
第一层：Token Risk Filter
判断 token 是否存在明显风险。

第二层：Entity Detection Layer
判断早期买家是否可能来自同一实体、机器人或项目方。

第三层：Wallet Quality Layer
判断参与钱包是否真的有稳定 alpha。

第四层：Copyability Layer
判断普通用户是否还有跟随空间。

第五层：AI Explanation Layer
将前面结果整理为可读报告。

第六层：Daily Review Loop
记录推送后的结果，用复盘反向校正评分。
```

## 核心数据表

### wallet_profile

```text
wallet_address
chain
first_seen_time
last_active_time
trade_count
realized_pnl_usd
win_rate
median_return
avg_hold_duration
max_drawdown
risk_score
wallet_style
alpha_score
copyability_score
```

### wallet_token_trades

```text
wallet_address
token_address
chain
first_buy_time
first_sell_time
buy_usd
sell_usd
realized_pnl_usd
holding_duration
max_price_after_buy_15m
max_price_after_buy_1h
max_price_after_buy_6h
drawdown_after_buy_1h
```

### wallet_relationships

```text
wallet_a
wallet_b
chain
temporal_score
funding_score
nonce_score
gas_station_score
contract_overlap_score
entity_cluster_score
relationship_reason
```

### token_signal_summary

```text
token_address
chain
detected_time
alpha_wallet_count
copyable_alpha_wallet_count
entity_adjusted_wallet_count
early_buyer_concentration
early_buyer_exit_ratio
same_funder_cluster_count
net_buy_usd_5m
net_buy_usd_15m
risk_score
opportunity_score
ai_summary
```

