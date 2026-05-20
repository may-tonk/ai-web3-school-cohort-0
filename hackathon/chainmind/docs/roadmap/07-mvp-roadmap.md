# 07. MVP Roadmap

## MVP 总目标

第一版 ChainMind 不追求完整自动化，也不追求预测上涨，而是做成：

> BNB meme token 风险过滤 + 可复制聪明钱观察 + AI 风险摘要。

## Phase 1：Dune 手动分析模板

目标：

```text
用 Dune SQL 手动分析 20-50 个 token
覆盖成功案例、失败案例、疑似刷量案例、出货案例
形成固定分析模板
```

要做：

```text
DEX 交易分析
5 分钟买卖盘分析
早期买家分析
当前 holder 集中度
早期买家资金来源分析
简单钱包行为分析
```

产出：

```text
experiments/week1-risk-filter/
submissions/research/report-1.md
```

## Phase 2：Token Risk Score

目标：

```text
把手动分析中有效的规则变成评分系统
```

第一版规则：

```text
前 20 买家清仓比例
同 funder 早期买家数量
新钱包比例
trades / unique_traders
net_buy_usd 是否转负
sell_volume 是否由少数钱包贡献
holder 集中度
```

产出：

```text
chainmind/scoring/token_risk.py
```

## Phase 3：Entity Cluster Score

目标：

```text
识别早期买家是否可能来自同一实体
```

第一版证据：

```text
同 funder
买入时间集中
新钱包比例
gas 来源相似
历史交互合约重叠
```

产出：

```text
chainmind/scoring/entity_cluster.py
```

## Phase 4：Wallet Alpha + Copyability

目标：

```text
区分赚钱钱包和可复制钱包
```

第一版先做轻量指标：

```text
最近 30 天表现
交易次数
胜率
买入后 15m / 1h 表现
同区块买入比例
买入后是否仍有流动性
```

产出：

```text
chainmind/scoring/copyability.py
```

## Phase 5：AI Report + Hermes 推送

目标：

```text
将评分结果变成可读报告和分级推送
```

输出：

```text
A/B/C/D 等级
机会来源
风险来源
是否可复制
是否疑似同实体
后续观察条件
不确定性
```

产出：

```text
chainmind/reports/template.md
Hermes 推送任务
```

## Phase 6：每日复盘系统

目标：

```text
记录每次推送后的表现，用事实校正规则
```

复盘字段：

```text
推送时间
token 地址
当时价格 / 市值 / 流动性
risk_score
opportunity_score
AI 结论等级
15m / 1h / 6h / 24h 最大涨幅
15m / 1h / 6h / 24h 最大回撤
是否 rug
是否出现可执行入场窗口
```

## 短期优先级

```text
P0：BNB token Dune 手动分析模板
P0：Token Risk Score 规则草案
P1：Entity Cluster Score 低成本版本
P1：AI 报告模板
P2：Wallet Alpha Score
P2：Copyability Score
P3：自动化 API 管道
P3：Hermes 实时推送
```

