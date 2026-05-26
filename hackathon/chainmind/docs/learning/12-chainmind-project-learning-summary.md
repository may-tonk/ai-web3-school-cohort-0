# 12. ChainMind 项目学习总结

更新时间：2026-05-24

本文用于总结近期围绕 ChainMind 项目学到的核心内容，包括项目定位、量化属性、相似 GitHub 项目对比、当前工程状态、已形成的判断框架，以及后续最值得继续推进的方向。

## 1. 我们对 ChainMind 的重新定位

ChainMind 不应该被定义为普通行情看板，也不应该被包装成 AI 自动交易机器人。

更准确的定位是：

```text
面向 BNB / EVM meme token 的链上行为风险过滤与可解释投研系统。
```

它的核心目标不是预测某个 token 一定会涨，而是回答：

```text
这个链上机会是否真实？
风险来自哪里？
早期资金是否已经撤退？
买盘是否真实扩散？
多个钱包买入是真共识还是假共识？
聪明钱信号是否可复制？
是否值得进入人工研究列表？
```

因此，ChainMind 第一阶段的正确方向是：

```text
先过滤坏机会
再识别可观察机会
最后由 AI 解释为什么
```

## 2. ChainMind 是否算量化

ChainMind 算量化，但不是传统意义上的自动交易量化。

它更接近：

```text
链上行为因子研究型量化
风险过滤型量化
半自动投研量化系统
事件驱动型链上分析系统
```

它不属于：

- 高频交易量化。
- 做市或套利机器人。
- 单纯 K 线技术指标策略。
- 自动下单系统。
- 黑箱式机器学习涨跌预测模型。

ChainMind 的量化特征主要来自三类因子：

### 2.1 Token Risk 因子

用于判断 token 是否存在明显风险。

典型指标包括：

- 流动性是否过低。
- 5m / 15m net_buy_usd 是否转负。
- trades / unique_traders 是否异常。
- 前 20 / 50 早期买家清仓比例。
- holder 集中度。
- 同 funder 早期买家数量。
- 新钱包比例。
- 合约权限和 LP 风险。

### 2.2 Wallet Alpha 因子

用于判断某个钱包是否真的有稳定 alpha。

典型指标包括：

- 历史胜率。
- realized PnL。
- median return。
- 最大回撤。
- rug exposure。
- 最近 7D / 30D / 90D 表现。
- 买入后 15m / 1h / 6h 表现。

### 2.3 Copyability 因子

用于判断普通用户是否还能复制这个钱包信号。

典型指标包括：

- 是否同区块买入。
- 是否开池几秒内买入。
- 是否依赖机器人速度或极高 gas。
- 买入时流动性是否过低。
- 买入后 5-15 分钟是否仍有成交量。
- 买入后是否仍有净买入和观察窗口。

核心认知是：

```text
高胜率钱包 ≠ 可复制钱包
聪明钱买入 ≠ 普通用户能跟
```

## 3. 与 GitHub 相似项目的对比

我们查看了 GitHub 上几类相似项目后发现，ChainMind 不是和某一个项目完全重合，而是处在多个方向的交叉点上。

## 3.1 传统 crypto 量化交易框架

代表项目：

- Freqtrade: https://github.com/freqtrade/freqtrade
- Hummingbot: https://github.com/hummingbot/hummingbot
- Jesse: https://github.com/jesse-ai/jesse

这些项目重点在：

- 策略回测。
- 参数优化。
- 交易所连接。
- 订单管理。
- 自动交易执行。
- 实盘风控。

ChainMind 与它们的区别：

| 对比维度 | 传统交易框架 | ChainMind |
| --- | --- | --- |
| 核心目标 | 自动交易与策略执行 | 风险过滤与投研解释 |
| 数据基础 | K 线、订单簿、交易所成交 | 链上交易、钱包、资金来源 |
| 输出结果 | 买卖信号或订单 | 风险等级、观察理由、研究报告 |
| 是否下单 | 通常会 | 第一阶段不做 |
| 适合场景 | 已知交易对策略 | 新 meme token 早期筛选 |

学习结论：

```text
ChainMind 不应该去卷成熟 trading bot，
而应该强调链上行为风控和可解释研究。
```

## 3.2 Rug / Honeypot / Token 安全检测工具

代表项目：

- RugWatch: https://github.com/machenxi/rugpull-scam-token-detection
- bsc-honeypot-detector: https://github.com/mraicodedev/bsc-honeypot-detector
- DumpDetective: https://github.com/JN-Bot666/dump-detective

这些项目重点在：

- 合约是否高危。
- 是否 honeypot。
- 是否能正常卖出。
- LP 是否有风险。
- owner / mint / blacklist / tax 权限。
- 项目方或创建者钱包是否异常。

ChainMind 与它们的区别：

| 对比维度 | Token 安全工具 | ChainMind |
| --- | --- | --- |
| 核心关注 | 合约和池子是否危险 | 资金行为是否真实、独立、可复制 |
| 判断对象 | token 合约 / LP / 权限 | token + 早期买家 + 钱包集群 |
| 优势 | 快速安全红旗 | 解释风险来源和观察条件 |
| 可借鉴点 | honeypot、LP、权限、税率检查 | 纳入 Risk Score 基础层 |

学习结论：

```text
ChainMind 不必重复造 Token Sniffer。
更好的做法是把 GoPlus / honeypot / LP 检查作为基础安全层，
然后继续做早期资金行为分析。
```

## 3.3 Smart Money / Wallet Tracker / Copy Trader 项目

代表项目：

- whale-wallet-mirror-copy-trader: https://github.com/Rezzecup/whale-wallet-mirror-copy-trader
- DeepLens: https://github.com/alanisme/deeplens

这类项目重点在：

- 监听重点钱包。
- 追踪 whale / smart money。
- 提醒钱包买入或卖出。
- 有些项目会直接做 mirror trading。

ChainMind 与它们的区别：

| 对比维度 | Wallet Tracker | ChainMind |
| --- | --- | --- |
| 常见逻辑 | 某钱包买了就提醒或复制 | 先判断这个信号是否可信、独立、可复制 |
| 主要风险 | 盲目追高或跟机器人 | 通过 Copyability 降噪 |
| 输出结果 | 钱包动作通知 | 钱包质量、同实体风险、可复制性 |
| 差异化 | 速度和钱包列表 | 判断质量和复盘闭环 |

学习结论：

```text
ChainMind 的差异化不是“更快提醒聪明钱”，
而是判断聪明钱信号是否真的值得普通用户观察。
```

## 3.4 链上数据基础设施项目

代表项目：

- Ethereum ETL: https://github.com/blockchain-etl/ethereum-etl
- BlockSci: https://github.com/citp/BlockSci
- Dune SQL 查询仓库: https://github.com/bitman09/Dune-Analytics

这些项目更像基础设施，重点在：

- 链上数据抽取。
- 数据清洗。
- 查询模板。
- 地址和交易分析。
- 研究型数据处理。

ChainMind 与它们的关系：

```text
Dune / ETL / RPC / API 是数据基础设施。
ChainMind 是基于这些数据的 meme token 风险研究应用。
```

学习结论：

```text
ChainMind 应该复用这些数据能力，
但产品价值要体现在评分、解释、分级和复盘上。
```

## 4. ChainMind 的核心差异化

综合对比后，ChainMind 最应该强调的差异化是：

1. 不只看合约安全，还看早期买家是否撤退。
2. 不只看聪明钱买入，还判断该信号是否可复制。
3. 不只看钱包数量，还判断是否存在同实体分仓和假共识。
4. 不直接输出交易指令，而是输出研究结论、风险来源和观察条件。
5. 不停留在一次性评分，而是通过每日复盘持续校正规则。

一句话表达：

```text
ChainMind 是 meme token 的链上风险研究 copilot，
不是自动炒币机器人。
```

## 5. 当前工程状态学习

当前项目已经从纯文档阶段进入基础工程阶段。

已经具备：

- Python 项目配置：`pyproject.toml`。
- 开发依赖：`requirements-dev.txt`。
- 样本 token JSON。
- 本地分析脚本：`scripts/analyze_token.py`。
- CLI 入口：`src/chainmind/cli/analyze_token.py`。
- 编排层：`src/chainmind/orchestration/analyze_token.py`。
- 领域对象：`src/chainmind/domain/token_snapshot.py`。
- 风险评分模块：`src/chainmind/scoring/token_risk.py`。
- 机会评分模块：`src/chainmind/scoring/opportunity.py`。
- 优先级分级模块：`src/chainmind/scoring/priority.py`。
- 基础自动测试：`tests/unit/test_analyze_token_cli_foundation.py`。

已验证的最小链路：

```text
样本 token JSON
-> TokenSnapshot
-> token risk / opportunity score
-> grade A/B/C/D
-> action
-> CLI 输出
```

这说明项目已经可以开始从“想法验证”进入“规则验证”。

## 6. 当前已经形成的判断框架

ChainMind 的综合判断可以分为 8 类：

1. 是否进入分析。
2. 合约安全判断。
3. 买卖盘健康判断。
4. 早期买家行为判断。
5. 同实体 / 假共识判断。
6. 钱包质量判断。
7. 可复制性判断。
8. 是否推送判断。

最终输出应包含：

```text
Risk Score
Entity Cluster Score
Wallet Alpha Score
Copyability Score
Opportunity Score
Priority Score
Grade A/B/C/D
```

可观察候选的大致逻辑是：

```text
风险不过高
+ 买盘相对健康
+ 早期买家未明显撤退
+ 没有强同实体嫌疑
+ 有高质量钱包参与
+ 这个钱包信号仍有可复制窗口
```

## 7. Dune 手动分析学习

Phase 1 的重点不是立即自动化，而是用 Dune 手动跑通分析路径。

已经理解的 Dune 分析模块包括：

- token 基础信息。
- 合约创建信息。
- DEX 交易与主要池子。
- 5 分钟买卖盘。
- 早期买家分析。
- holder 集中度。
- 早期买家资金来源。
- 同来源资金统计。

关键学习点：

```text
同 funder 是风险证据之一，
但不能直接等于同一个真实人。
```

需要进一步区分：

- 普通钱包地址。
- DEX Router。
- 池子合约。
- 协议基础设施地址。
- 交易所或常见资金分发地址。

否则 same-funder 规则容易误判。

## 8. AI 在项目中的正确位置

AI 不应该直接读取全量原始交易并预测涨跌。

AI 更适合在规则过滤之后工作：

```text
程序负责计算
规则负责过滤
AI 负责解释
复盘负责校正
```

AI 的输入应该是结构化摘要，例如：

```json
{
  "token": "XXX",
  "chain": "bnb",
  "risk_score": 68,
  "opportunity_score": 55,
  "early_buyer_exit_ratio": 0.42,
  "same_funder_cluster_count": 2,
  "copyability_score": 61
}
```

AI 的输出应该回答：

- 是否值得观察。
- 机会来自哪里。
- 风险来自哪里。
- 是否可复制。
- 后续观察条件是什么。
- 不确定性在哪里。

## 9. 最需要避免的表达

项目介绍中应避免：

```text
AI 自动发现暴涨币
智能炒币机器人
自动跟单系统
保证发现 alpha
高胜率买入信号
```

更推荐使用：

```text
链上行为风险过滤
meme token 投研辅助
可解释风险摘要
聪明钱可复制性判断
同实体与假共识识别
```

推荐一句话：

```text
ChainMind helps researchers filter risky meme tokens and explain on-chain signals before making manual decisions.
```

## 10. 后续最值得推进的方向

短期最重要的不是做大而全，而是补齐一个可验证闭环。

推荐优先级：

### P0：沉淀 Phase 1 Dune SQL

把已经跑通的手动查询整理为固定 SQL 模板：

- 基础交易。
- 5m 买卖盘。
- 早期买家。
- 资金来源。
- holder 集中度。

### P0：完善 Token Risk Score

把当前硬编码启发式规则逐步变成可配置权重：

- 低流动性。
- net_buy_usd 转负。
- trades / unique_traders 异常。
- 早期买家清仓比例。
- same-funder 风险。
- holder 集中度。
- 合约安全风险。

### P1：补充 Entity Cluster Score

先做低成本版本：

- 同 funder。
- 买入时间集中。
- 新钱包比例。
- 买入前交易次数。
- 基础设施地址过滤。

### P1：生成 AI 报告模板

让 AI 基于结构化 JSON 生成：

- A/B/C/D 等级解释。
- 机会来源。
- 风险来源。
- 可复制性说明。
- 后续观察条件。
- 不确定性。

### P2：建立复盘数据

每次分析或推送后记录：

- 15m / 1h / 6h / 24h 最大涨幅。
- 15m / 1h / 6h / 24h 最大回撤。
- 是否 rug。
- 是否存在普通用户可执行窗口。
- 当时风险分和机会分是否合理。

## 11. 最终学习结论

ChainMind 的方向是成立的，但不能用传统交易机器人的方式去做。

它最有价值的落地形态是：

```text
链上行为风控 + 聪明钱可复制性判断 + AI 投研解释 + 复盘校正
```

当前最关键的项目节奏是：

```text
不要急着自动交易
不要急着全市场扫描
不要急着黑箱 AI 预测

先把少量 token 分析清楚
先把风险规则跑通
先证明评分能过滤坏机会
先让报告解释得清楚、可复盘
```

一句话总结：

```text
ChainMind 不应该成为一个喊单机器人，
而应该成为 meme token 研究前的链上风险过滤器。
```
