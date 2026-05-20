# 03. 评分体系设计

评分系统第一版应该尽量清晰、可解释、可复盘。不要一开始追求复杂模型，先让每个分数都能追溯到具体证据。

## Token Risk Score

用于判断某个 token 是否存在明显风险。

核心风险维度：

```text
top10 / top20 holder 占比
早期买家集中度
早期买家清仓比例
同 funder 地址数量
新钱包比例
deployer 关联地址
合约权限风险
LP 风险
卖压变化
刷量迹象
```

第一版建议规则：

```text
前 20 早期买家清仓比例 > 60% → 高风险
同一 funder 覆盖多个早期买家 → 提高风险
trades 高但 unique_traders 低 → 刷量嫌疑
net_buy_usd 连续转负 → 出货压力增强
sell_volume_usd 由少数钱包贡献 → 大户出货嫌疑
新钱包比例过高 → 临时分仓/狙击风险
```

输出分级：

```text
0-30：低风险，允许进入下一层分析
30-60：中风险，需要观察
60-80：高风险，谨慎处理
80-100：极高风险，默认过滤
```

## Token Opportunity Score

用于衡量某个 token 是否值得进入观察列表。

核心机会维度：

```text
高胜率地址参与数量
可复制高胜率地址数量
真实买家增长
成交量增长质量
买入后是否仍有可跟随空间
市场环境是否 risk-on
```

注意：Opportunity Score 必须和 Risk Score 一起看。高机会不代表低风险。

## Wallet Alpha Score

用于判断某个钱包是否有稳定预测价值。

基础字段：

```text
wallet_address
chain
total_realized_pnl_usd
win_rate
trade_count
median_return
average_return
max_drawdown
avg_hold_duration
median_hold_duration
profitable_token_count
loss_token_count
rug_exposure_count
last_active_time
```

meme 场景更重要的字段：

```text
buy_to_peak_15m
buy_to_peak_1h
buy_to_peak_6h
buy_to_peak_24h
buy_to_drawdown_1h
entry_marketcap_median
entry_liquidity_median
early_entry_ratio
sell_before_crash_ratio
```

关键判断：

```text
不要只看总 PnL。
要看中位数收益、样本数量、最近表现、回撤和 rug 暴露。
要按 7D / 30D / 90D / All-time 拆分，避免历史强钱包当前失效。
```

## Copyability Score

用于判断某个钱包信号普通用户是否还能跟。

核心字段：

```text
copyability_score
entry_after_pool_created_seconds
same_block_entry_flag
avg_entry_slippage_estimate
liquidity_after_entry_usd
marketcap_after_entry_usd
priority_fee_level
gas_pattern_score
post_entry_available_volume
entry_tx_count_before_wallet
```

降分条件：

```text
同区块买入
开池后几秒内买入
买入时流动性极低
买入后价格瞬间拉升
依赖极高 gas / priority fee
疑似机器人速度
与项目方或同实体集群相关
```

加分条件：

```text
买入后 5-15 分钟仍有二次入场窗口
买入后仍有足够交易量和流动性
买入后净买入仍为正
钱包历史行为不是秒级狙击
```

## 推荐综合判断

最终优先级不应该只看一个分数：

```text
可观察候选 =
    Risk Score 不高
  + Opportunity Score 适中或较高
  + 有 Copyable Alpha Wallet
  + Entity Cluster 风险可接受
  + 仍有后续观察窗口
```

