# AI + DeFi 链上数据分析 Workflow 学习总结

日期：2026-05-19  
主题：通过链上数据、地址跟踪、高胜率钱包分析、Dune/API/Hermes 工作流，辅助 meme 代币研究与投资决策。

---

## 1. 今天讨论的核心方向

我们最初讨论的是用 Dune、链上 API、Hermes 和 AI 结合，做一个和 DeFi / meme 代币相关的分析系统。

经过讨论后，方向逐渐明确：

我们不是要做一个完整的 autonomous agent，也不是让 AI 直接自动买卖代币，而是要做一个：

> 链上数据分析 + 高胜率地址跟踪 + 风险过滤 + AI 解释报告 + Hermes 推送 的工作流系统。

这个系统的核心不是展示行情数据，因为很多软件已经可以做到，例如 GMGN、DEX Screener、Birdeye、Ave、Arkham、Nansen 等。

真正有价值的地方在于：

- 哪些地址值得跟踪？
- 哪些高胜率地址是可复制的？
- 哪些地址其实是项目方、机器人、内盘或同一实体分仓？
- 哪些 meme 代币只是表面热度高，实际已经进入出货阶段？
- 当前市场环境是否适合追 meme？
- 某个新代币是早期机会，还是已经是接盘区？
- AI 如何把复杂链上数据解释成人能读懂的研究结论？

所以我们的目标不是“做一个行情看板”，而是做一个：

> 高胜率地址可复制性分析系统 + meme 风险过滤系统 + AI 研究报告生成器。

---

## 2. 推荐的整体 Workflow

整体工作流可以设计成：

```text
链上 API / Dune / DEX 数据源
        ↓
数据清洗与结构化
        ↓
地址行为分析
        ↓
钱包评分与可复制性评分
        ↓
代币风险评分
        ↓
市场环境判断
        ↓
规则过滤 95%-99% 噪音
        ↓
AI 生成解释、排序、报告
        ↓
Hermes 推送到 Telegram / 文档 / 群组
        ↓
每日复盘与评分校正
```

其中：

- Dune 适合历史分析、回测、地址研究、交易行为聚合。
- 链上 API 适合实时监听，比如 Helius、Alchemy、Etherscan、BscScan。
- DEX Screener、Birdeye 适合补充市场数据。
- GoPlus 适合合约和 token 安全检测。
- Hermes 适合定时任务、触发器和推送。
- AI 适合做解释、总结、风险描述和报告生成，不适合直接处理海量原始交易数据。

---

## 3. 为什么不要把所有数据都交给 AI

如果把每个 token、每个钱包、每笔交易都交给 AI 分析，token 消耗会非常大，而且效果不稳定。

更合理的方式是：

```text
程序负责计算
规则负责过滤
AI 负责解释
```

也就是说：

- 钱包胜率、PnL、持仓时间、买卖行为，由程序计算。
- 风险规则、过滤条件、评分系统，由代码完成。
- AI 只处理最后筛选出来的少数高价值候选。
- AI 的输入应该是结构化摘要，而不是原始交易日志。

例如，不应该给 AI 输入几千行交易记录，而应该输入：

```json
{
  "token": "XXX",
  "chain": "bnb",
  "signal": {
    "alpha_wallets": 3,
    "median_1h_return": "1.8x",
    "copyability_score": 72,
    "market_regime": "risk_on"
  },
  "risk": {
    "top20_holding": "41%",
    "early_buyers_exited": true,
    "same_funder_cluster": true,
    "lp_risk": "medium"
  }
}
```

AI 根据这些摘要输出：

- 是否值得观察
- 主要机会在哪里
- 主要风险在哪里
- 后续确认条件是什么
- 是否适合进入二次观察列表

---

## 4. 核心不是 Token 分析，而是地址分析

普通 token 信息，比如价格、流动性、持有人、成交量、Top holder，在很多软件上都能看到。

真正有壁垒的是地址行为分析。

我们需要建立一个 wallet scoring 系统，分析每个地址是否真的有 alpha。

### 4.1 Wallet Alpha Score

用于判断某个地址是否有预测价值。

可参考指标：

```text
历史胜率
平均收益
中位数收益
最大亏损
最大回撤
平均持仓时间
买入后 5m / 15m / 1h / 6h / 24h 表现
是否经常买在启动前
是否经常卖在高点前
是否经常参与 rug
是否买入后能吸引跟随资金
```

重点不是“这个地址赚了多少钱”，而是：

> 这个地址买入后，是否对未来价格有稳定的正向预测价值。

### 4.2 Copyability Score

很多高胜率地址不可复制。

不可复制的原因包括：

```text
同区块买入
开盘前买入
极高 gas / priority fee 抢跑
机器人速度极快
依赖私有信息
与项目方有关联
买入时市值极小，普通人跟不上
买入后流动性不足
买入后立刻分仓或转移
```

所以我们真正要找的是：

```text
高胜率 + 非内盘 + 非机器人 + 买入后仍有流动性 + 普通用户可以跟进
```

这类地址才值得进入重点跟踪列表。

---

## 5. 钱包 / 聪明钱 / 地址集群方法论学习与项目连接

这一部分是我们项目最核心的能力来源之一。

普通 meme 工具已经可以展示价格、成交量、流动性、holder、Top holder 等信息。我们真正要做出差异化，不能停留在 token 表面数据，而要深入到：

- 哪些钱包真的有 alpha？
- 哪些钱包只是曾经赚过钱，但不可复制？
- 哪些高胜率钱包其实是项目方、机器人、狙击地址或同一实体分仓？
- 多个钱包同时买入，到底是市场共识，还是一个实体在拆分操作？
- Smart Money 买入后，普通用户是否还有可跟随空间？

因此，我们需要把“聪明钱跟踪”拆成三个层级：

```text
钱包盈利能力分析
        ↓
钱包可复制性分析
        ↓
地址集群 / Sybil / 同实体识别
```

### 5.1 Nansen Smart Money 方法论：不要只看赚钱

参考资料：

- [Nansen Smart Money 101](https://academy.nansen.ai/en/articles/2132837-smart-money-101)
- [Nansen API Overview](https://docs.nansen.ai/api/overview)
- [Nansen Smart Money: How It Works](https://eco.com/support/en/articles/14800361-nansen-smart-money-how-it-works)

Nansen 的 Smart Money 思路不是简单地说“这个地址赚过钱，所以它聪明”。它更强调标签体系和不同时间窗口下的钱包表现。

Nansen 的方法论中，Smart Money 可以根据不同时间段和行为类型进行划分，例如：

```text
30D Smart Trader
90D Smart Trader
180D Smart Trader
All-Time Smart Trader
```

它关注的核心指标包括：

```text
PnL
Win Rate
ROI
Realized Profit
交易多样性
盈利 token 数量
资产多样性
持仓周期
短线 / 长线风格
```

这对我们的启发是：

> 高胜率地址不能混在一起看，必须按时间窗口和交易风格拆分。

例如一个地址：

```text
30 天表现很好
90 天表现一般
180 天表现很差
```

它可能只是最近踩中了一个热点，而不是长期有 alpha。

另一个地址：

```text
All-Time PnL 很高
但最近 30 天胜率下降
```

它可能曾经厉害，但当前不适合跟踪。

所以我们项目里不能只做一个简单的“聪明钱列表”，而应该做分层：

```text
短线 meme 钱包
中周期趋势钱包
长期配置钱包
狙击型钱包
LP / 做市型钱包
项目方关联钱包
疑似机器人钱包
```

对于 meme 项目，我们最需要的是：

```text
短线 meme 钱包
早期发现型钱包
可复制型高胜率钱包
非项目方关联钱包
非机器人钱包
```

### 5.2 从 Nansen 学到的项目设计

Nansen 的 Token God Mode 和 Wallet Profiler 对我们很有参考价值。

Nansen API 里有几类能力值得借鉴：

```text
address/current-balance
address/historical-balances
address/transactions
address/related-wallets
address/pnl-summary
address/pnl
address/counterparties
tgm/flows
tgm/who-bought-sold
tgm/pnl-leaderboard
tgm/indicators
```

我们不一定使用 Nansen API，但可以学习它的产品结构。

我们的项目可以拆成类似模块：

```text
Wallet Profiler
分析某个钱包的历史交易、PnL、持仓、风格、胜率、回撤。

Token God Mode Lite
分析某个 token 中，谁在买、谁在卖、早期地址是否出货、聪明钱是否进入。

Related Wallets
分析一个钱包是否和其他钱包存在资金、交易、时间上的关联。

Smart Flow
分析高胜率钱包对某个 token 是净买入还是净卖出。
```

对我们当前 Dune / API 工作流来说，可以先实现一个轻量版。

### 5.3 Thrive Smart Money：适合直接落地的钱包评分模型

参考资料：

- [Thrive Smart Money Tracking Docs](https://docs.thrive.fi/docs/smart-money)
- [Thrive On-Chain Widgets](https://docs.thrive.fi/docs/market-intel-on-chain)

Thrive 的 Smart Money Tracking 很接近我们要做的 Wallet Alpha Score。

它提到的钱包 leaderboard 字段包括：

```text
Realized PnL
Win Rate
Trade Count
Average Hold Duration
Top Tokens
Risk Score
```

这些字段非常适合直接变成我们的第一版钱包评分表。

### 5.4 我们可以建立的 Wallet Alpha Score

我们的 Wallet Alpha Score 不应该只看 PnL，而应该看“稳定性 + 可复现性 + meme 适配度”。

建议字段：

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
best_token
worst_token
last_active_time
```

更适合 meme 的字段：

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

其中最重要的是：

```text
买入后 15 分钟 / 1 小时 / 6 小时表现
```

因为 meme 的机会窗口很短。一个地址长期 PnL 很高，但如果它买入后 10 秒就拉升，普通用户根本跟不上，那它对我们的系统价值有限。

### 5.5 Copyability Score：项目和普通 Smart Money 工具的关键区别

普通工具告诉你：

```text
某个聪明钱地址买入了某个 token
```

但它没有回答：

```text
现在还能不能跟？
这个地址的行为普通用户能不能复制？
它是不是同区块狙击？
它是不是项目方或机器人？
买入后还有没有足够流动性？
```

所以我们需要单独设计一个 Copyability Score。

建议字段：

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

判断逻辑：

```text
同区块买入 = 降低可复制性
开池后几秒内买入 = 降低可复制性
买入时流动性极低 = 降低可复制性
买入后价格瞬间拉升 = 降低可复制性
买入后仍有足够交易量和流动性 = 提高可复制性
买入后 5-15 分钟仍有二次入场机会 = 提高可复制性
```

最终我们要找的不是“最赚钱钱包”，而是：

```text
高胜率 + 可复制 + 非内盘 + 非机器人 + 买入后仍有空间
```

### 5.6 Thrive 方法论对我们项目的直接连接

Thrive 强调：

```text
Realized PnL
Win Rate
Trade Count
Average Hold Duration
Risk Score
```

我们可以直接对应成：

```text
Realized PnL → 钱包真实已实现收益
Win Rate → 钱包历史胜率
Trade Count → 样本数量，避免一两次运气好
Average Hold Duration → 钱包交易风格
Risk Score → 钱包收益波动和回撤风险
```

项目中可以这样使用：

```text
如果一个钱包 PnL 很高，但 trade_count 很低：
    可能只是运气好，不进入核心跟踪列表。

如果一个钱包 win_rate 高，但平均收益低：
    可能适合短线套利，但不一定适合 meme 爆发机会。

如果一个钱包 PnL 高但 risk_score 高：
    可能收益大、回撤也大，只能作为高风险信号。

如果一个钱包 PnL 中等、win_rate 稳定、trade_count 足够、hold_duration 符合 meme 节奏：
    更适合进入可跟踪钱包池。
```

### 5.7 Ramaris Sybil Detection：识别假共识的关键

参考资料：

- [Ramaris Sybil Detection / Coordinated Wallet Activity](https://www.ramaris.app/blog/sybil-detection/)

Ramaris 的核心观点非常重要：

> 原始钱包数量可能是假的，一个实体可以控制很多钱包。

它举的逻辑是：

```text
13 个钱包同时买入一个资产
```

这可能代表两种完全不同的情况：

```text
情况 1：13 个独立交易者形成真实共识
情况 2：1 个实体控制 13 个钱包分仓买入
```

对 meme 来说，这个区别非常关键。

如果是情况 1，说明市场自然扩散，信号更健康。  
如果是情况 2，说明可能是项目方、机器人、庄家或内部地址在制造热度。

Ramaris 提到的 5 个信号包括：

```text
Temporal Fingerprinting
Funding Source Analysis
Nonce Correlation
Gas Station Detection
Contract Overlap
```

它还提到可以用 composite score 判断钱包对之间是否属于同一实体，并用 Union-Find 把钱包聚类。

### 5.8 Ramaris 的 5 个信号如何迁移到我们的项目

#### Temporal Fingerprinting：时间指纹

含义：

```text
多个钱包是否在极短时间内执行相似交易？
是否总是在同一区块、连续区块、固定间隔内买入？
是否存在批量爆发式交易？
```

我们可以在 Dune / API 里计算：

```text
wallet_a_buy_time
wallet_b_buy_time
time_diff_seconds
same_block_flag
same_minute_flag
burst_cluster_id
```

风险信号：

```text
多个早期买家在 30 秒内连续买入
多个钱包总是在固定间隔交易
多个钱包在多个 token 上都保持类似时间关系
```

项目解释：

```text
这可能不是自然买盘，而是同一脚本或同一操作者批量执行。
```

#### Funding Source Analysis：资金来源分析

含义：

```text
多个钱包是否由同一个地址资助？
```

这是我们在 Dune 里已经开始做的方向。

在 BNB 链上，可以查：

```text
早期买家的第一笔 BNB 来源
买入前 1 天 / 7 天 / 14 天内的资金来源
多个早期买家是否来自同一个 funder
```

风险信号：

```text
同一个 funder 资助多个早期买家
同一个 funder 资助的钱包集中买入同一个 token
这些钱包后续集中卖出或转走
```

项目解释：

```text
这说明这些钱包可能不是独立买家，而是同一实体分仓。
```

#### Nonce Correlation：Nonce 相关性

含义：

```text
EVM 钱包的 nonce 反映交易次数和钱包使用历史。
```

新钱包如果 nonce 很低，并且同时参与同一个 token，风险更高。

我们可以计算：

```text
buyer_nonce_at_entry
wallet_age_days
tx_count_before_entry
```

风险信号：

```text
多个早期买家都是新钱包
nonce 很低
买入前几乎没有历史交易
这些新钱包在同一时间段买入
```

项目解释：

```text
这类地址可能是临时创建的狙击、刷量或分仓钱包。
```

Dune 上如果直接取 nonce 不方便，可以先用历史交易数近似：

```text
买入前该钱包交易次数
买入前该钱包首次出现时间
买入前该钱包交互过的合约数量
```

#### Gas Station Detection：Gas 资金站识别

含义：

```text
多个钱包是否从同一个 gas station 地址拿到 gas？
```

在 EVM 链上，很多批量钱包会先收到少量 BNB/ETH 作为 gas，然后参与交易。

可计算字段：

```text
gas_funder
gas_funding_time
gas_funding_amount
funded_wallet_count
```

风险信号：

```text
同一 gas_funder 在短时间内给多个新钱包转入小额 BNB
这些钱包随后买入同一个 token
```

项目解释：

```text
这可能是批量控制钱包，不是自然买家。
```

#### Contract Overlap：合约交互重叠

含义：

```text
多个钱包是否经常和同一批合约交互？
```

比如多个钱包都只交互：

```text
同一个 router
同一个 launchpad
同一批 meme token
同一个 deployer 创建的 token
```

这说明它们可能属于同一交易系统或同一团队。

可计算字段：

```text
common_contract_count
contract_overlap_ratio
shared_token_count
shared_router_count
```

项目解释：

```text
如果多个钱包历史交互路径高度相似，它们的独立性要打折。
```

### 5.9 我们项目里的 Entity Cluster Score

结合 Ramaris，我们应该建立一个 Entity Cluster Score。

目标不是证明 100% 是同一个人，而是给出概率和风险提示。

建议评分：

```text
entity_cluster_score =
    temporal_score * 0.25
  + funding_source_score * 0.30
  + nonce_similarity_score * 0.15
  + gas_station_score * 0.15
  + contract_overlap_score * 0.15
```

可以先简单分级：

```text
0.00 - 0.30：大概率独立
0.30 - 0.60：存在关联，需要观察
0.60 - 0.80：高度疑似同一实体
0.80 - 1.00：强关联实体集群
```

当多个早期买家聚类后，我们不能再用：

```text
100 个 holder
```

而应该用：

```text
约 35 个独立实体
```

这会让 token 风险判断更真实。

### 5.10 把三套方法论合并成实际工作流

综合 Nansen、Thrive、Ramaris，我们的系统应该这样做：

```text
第一层：Wallet Performance
这个钱包历史是否赚钱？

第二层：Wallet Consistency
这个钱包是否稳定，而不是偶然赚过？

第三层：Wallet Style
它是短线 meme 钱包、长期钱包、机器人、LP，还是项目方？

第四层：Copyability
它的买入行为普通用户是否能跟？

第五层：Entity Detection
它是否和其他钱包属于同一实体？

第六层：Token Context
它当前买入的 token 是否存在早期集中、出货、刷量、LP 或合约风险？

第七层：AI Explanation
AI 把以上结果整理成人类可读的报告。
```

最终输出不应该是：

```text
某聪明钱买入 XXX
```

而应该是：

```text
3 个高胜率钱包买入 XXX，其中 2 个具备较高可复制性；
但这 3 个钱包中有 2 个来自相同 funder，疑似关联；
早期买家中 40% 已经清仓；
当前买盘仍为正，但 sell_volume 正在上升；
综合判断：进入观察列表，不建议追高。
```

### 5.11 建议保存的核心数据库表

#### wallet_profile

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

#### wallet_token_trades

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

#### wallet_relationships

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

#### token_signal_summary

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

### 5.12 这一部分对项目的最终价值

这三套资料给我们的最终启发是：

```text
Nansen 告诉我们：
聪明钱需要标签化、分时间窗口、分交易风格。

Thrive 告诉我们：
钱包评分要看 realized PnL、win rate、trade count、hold duration、risk score。

Ramaris 告诉我们：
钱包数量不等于真实人数，必须做地址聚类和同实体识别。
```

所以我们项目的核心不应该是：

```text
发现有多少钱包买入某个 token
```

而应该是：

```text
发现有多少“真正独立且可复制的高质量钱包”买入某个 token。
```

这是我们和普通 meme 工具最大的区别。

---

## 6. 从 MemeTrans 学到的核心思想

我们参考了论文：

- [MemeTrans: Detecting High-Risk Memecoin Launches on Solana](https://arxiv.org/abs/2602.13480)
- [PDF 直链](https://arxiv.org/pdf/2602.13480)
- [GitHub 仓库](https://github.com/git-disl/MemeTrans)
- [Raw README](https://raw.githubusercontent.com/git-disl/MemeTrans/main/README.md)

它的核心启发是：

> meme 风险往往在 DEX 上交易之前，或者早期交易阶段就已经形成。

它研究的是 Solana 上 Pump.fun 到 Raydium 迁移的 memecoin，但思想可以迁移到 BNB、Base、ETH。

最值得借鉴的点：

```text
早期买家集中度
dev 持仓
sniper 持仓
top10 / top20 holder 集中度
bundle / 同实体账户识别
迁移前交易行为
早期价格和成交量轨迹
普通买家是否在迁移后亏损
```

对我们来说，最重要的是：

```text
不要只看表面 holder 分布
要做实体级别的持仓集中度分析
要看早期买家是否已经出货
要看买盘是否真实扩散
要看价格上涨是否伴随真实买家增长
```

---

## 7. Dune 上分析一个新代币时的步骤

我们用 BNB 链 token：

```text
0x205f39c39f5fe15d4ef000aeb835de8deb264444
```

模拟了 Dune 分析流程。

BNB 链在 Dune 中通常使用：

```sql
blockchain = 'bnb'
```

常用表包括：

```text
tokens.erc20
tokens.transfers
dex.trades
bnb.creation_traces
prices.hour / prices.minute
```

### 7.1 第一步：查代币基础信息

目标：

```text
确认 token symbol
decimals
合约地址是否被 Dune 收录
```

示例 SQL：

```sql
WITH params AS (
    SELECT 0x205f39c39f5fe15d4ef000aeb835de8deb264444 AS token
)

SELECT *
FROM tokens.erc20
WHERE blockchain = 'bnb'
  AND contract_address = (SELECT token FROM params);
```

### 7.2 第二步：查合约创建信息

目标：

```text
创建时间
deployer 地址
创建交易
是否由 factory 创建
deployer 是否还和其他 token 有关联
```

示例 SQL：

```sql
WITH params AS (
    SELECT 0x205f39c39f5fe15d4ef000aeb835de8deb264444 AS token
)

SELECT *
FROM bnb.creation_traces
WHERE address = (SELECT token FROM params)
LIMIT 10;
```

### 7.3 第三步：查 DEX 交易和主要交易池

目标：

```text
主要 pool_address
首笔交易时间
交易量
交易者数量
是否集中在单一池子
```

示例 SQL：

```sql
WITH params AS (
    SELECT 0x205f39c39f5fe15d4ef000aeb835de8deb264444 AS token
)

SELECT
    project,
    version,
    pool_address,
    COUNT(*) AS trades,
    COUNT(DISTINCT tx_from) AS traders,
    SUM(amount_usd) AS volume_usd,
    MIN(block_time) AS first_trade_time,
    MAX(block_time) AS last_trade_time
FROM dex.trades
WHERE blockchain = 'bnb'
  AND block_time > now() - INTERVAL '30' day
  AND (
      token_bought_address = (SELECT token FROM params)
      OR token_sold_address = (SELECT token FROM params)
  )
GROUP BY 1, 2, 3
ORDER BY volume_usd DESC NULLS LAST;
```

### 7.4 第四步：做 5 分钟买卖盘分析

字段包括：

```text
bucket_5m
trades
unique_traders
buy_trades
sell_trades
buyers
sellers
buy_volume_usd
sell_volume_usd
net_buy_usd
```

含义如下：

- `bucket_5m`：每 5 分钟一个时间窗口。
- `trades`：该时间段总交易笔数。
- `unique_traders`：该时间段不同交易钱包数量。
- `buy_trades`：买入交易笔数。
- `sell_trades`：卖出交易笔数。
- `buyers`：不同买家数量。
- `sellers`：不同卖家数量。
- `buy_volume_usd`：买入金额。
- `sell_volume_usd`：卖出金额。
- `net_buy_usd`：净买入金额，等于买入金额减卖出金额。

核心判断方式：

```text
trades 高但 unique_traders 低 = 可能刷量或机器人
buyers 增长 + buy_volume 增长 = 买盘扩散
buyers 很多但 sell_volume 更大 = 散户接大户卖盘
net_buy_usd 从正转负 = 卖压开始增强
unique_traders 不增长但交易变多 = 活跃度可能是假的
```

### 7.5 第五步：早期买家分析

字段包括：

```text
buyer_rank
buyer
first_buy_time
buy_trades
tokens_bought
buy_usd
current_balance
remaining_ratio
```

含义如下：

- `buyer_rank`：按照首次买入时间排序的买家排名。
- `buyer`：买家钱包地址。
- `first_buy_time`：首次买入时间。
- `buy_trades`：该地址买入次数。
- `tokens_bought`：累计买入 token 数量。
- `buy_usd`：累计买入金额。
- `current_balance`：当前 token 持仓。
- `remaining_ratio`：当前持仓 / 累计买入数量。

核心判断：

```text
早期买家 remaining_ratio 接近 0 = 可能已经卖出或转走
早期大买家 buy_usd 很高但 current_balance 为 0 = 重点风险信号
前 20 / 50 / 100 买家大量清仓 = 早期资金已经撤退
早期买家仍持有 = 需要继续观察是否锁仓、分仓或等待出货
```

如果 Dune 里出现：

```text
current_balance = -1.4901161193847656e-8
remaining_ratio = -1.49e-16
```

这通常不是负持仓，而是浮点精度误差，应该当作 0 处理。

---

## 8. 怎么把数据转换成信息

数据本身没有意义，必须变成判断。

### 8.1 买盘健康

健康情况：

```text
unique_traders 增长
buyers 增长
buy_volume_usd > sell_volume_usd
net_buy_usd 连续为正
```

解释：

```text
买盘真实扩散，参与地址增加，资金持续流入。
```

### 8.2 出货风险

风险情况：

```text
buyers 很多
buy_volume_usd 增长变慢
sell_volume_usd 快速增长
net_buy_usd 转负
早期买家 remaining_ratio 接近 0
```

解释：

```text
市场还有热度，但早期地址可能正在把筹码卖给新买家。
```

### 8.3 刷量或机器人

风险情况：

```text
trades 很高
unique_traders 很低
trades_per_wallet 很高
buy_trades / buyers 很高
sell_trades / sellers 很高
```

解释：

```text
交易活跃度可能由少数钱包反复制造，不是真实扩散。
```

### 8.4 地址集群风险

风险情况：

```text
多个早期买家来自同一个 funder
多个早期买家买入时间接近
多个早期买家后续同时卖出
多个地址持仓数量接近
```

解释：

```text
这些地址可能不是独立买家，而是同一实体拆分地址。
```

---

## 9. 推荐建立的评分体系

### 9.1 Token Opportunity Score

衡量机会：

```text
高胜率地址参与数量
高胜率地址历史表现
买入后是否仍有可跟随空间
真实买家增长
成交量增长质量
市场环境是否 risk-on
```

### 9.2 Token Risk Score

衡量风险：

```text
top10 / top20 holder 占比
早期买家集中度
早期买家清仓比例
同 funder 地址数量
deployer 关联地址
合约权限风险
LP 风险
卖压变化
刷量迹象
```

### 9.3 Wallet Alpha Score

衡量地址是否有 alpha：

```text
历史胜率
中位数收益
买入后 15m / 1h / 6h 表现
最大回撤
参与 rug 比例
是否经常领先市场
```

### 9.4 Copyability Score

衡量地址能否被跟随：

```text
买入是否太早
买入是否同区块
买入时流动性是否足够
买入后是否还有入场空间
是否依赖机器人速度
是否频繁分仓
是否疑似内盘
```

---

## 10. AI 应该放在哪里

AI 不应该直接做这些事情：

```text
读取所有原始交易
直接预测涨跌
直接给买入卖出指令
替代规则引擎
替代链上计算
```

AI 更适合做：

```text
把复杂指标解释成人话
总结机会和风险
对候选 token 分层
生成 Telegram 推送内容
生成每日复盘报告
比较多个候选的优先级
```

理想输出类似：

```text
结论：B+，进入观察列表，不建议追高。

原因：
3 个可复制型高胜率地址在 15 分钟内买入；
这些地址过去 30 天 meme 交易中位收益为 1.8x；
当前买家增长快于卖家增长；
但早期第 2 买家买入金额较大，目前已经基本清仓。

主要风险：
Top holder 集中度需要继续检查；
早期买家是否来自同一 funder 需要验证；
如果未来 15 分钟 net_buy_usd 转负，可能进入出货阶段。

后续观察条件：
继续监控 buyers、unique_traders、sell_volume_usd、early buyer outflow。
```

---

## 11. Hermes 可以承担的角色

Hermes 可以作为调度和推送层。

推荐任务：

```text
每 5 分钟：
扫描新 token / 新交易池 / 异常放量 token

每 15 分钟：
检查重点高胜率地址是否买入新 token

每小时：
汇总候选 token，输出 Top 10 机会和风险

每天：
复盘昨日推送 token 的 15m / 1h / 6h / 24h 表现
```

Hermes 推送内容不应该太长，最好分层：

```text
A级：高优先级，需要人工立即查看
B级：进入观察列表
C级：风险过高，忽略
D级：疑似内盘 / 刷量 / 出货
```

---

## 12. 第一阶段 MVP 工作内容

建议第一版不要做太大。

### 阶段 1：Dune 手动分析

目标：

```text
先用 Dune SQL 手动分析 20-50 个 token
总结哪些指标最有效
形成固定分析模板
```

要做：

```text
DEX 交易分析
5 分钟买卖盘分析
早期买家分析
当前 holder 集中度
早期买家资金来源分析
简单钱包 PnL 分析
```

### 阶段 2：建立地址库

目标：

```text
收集 500-2000 个 meme 活跃钱包
计算 Wallet Alpha Score
筛选可复制地址
剔除机器人、项目方、疑似内盘地址
```

### 阶段 3：自动化数据管道

目标：

```text
通过 API 自动获取交易、持仓、DEX 数据
定时计算指标
存储到数据库
```

可用数据源：

```text
Dune API
BscScan / Etherscan API
Alchemy
Helius
DEX Screener API
Birdeye API
GoPlus API
```

### 阶段 4：Hermes 推送

目标：

```text
把规则过滤后的候选 token 推送出来
AI 只负责解释和总结
```

### 阶段 5：复盘系统

目标：

```text
每天复盘昨日推送
记录推送后 15m / 1h / 6h / 24h 表现
计算最大涨幅、最大回撤、是否 rug
反向优化评分系统
```

---

## 13. 接下来建议立刻做的事情

第一步：

```text
选定一条链：BNB 或 Solana 或 Base
```

建议先选 BNB，因为现在已经开始用 BNB token 做 Dune 分析。

第二步：

```text
整理 10-20 个历史 meme token
包括成功案例和失败案例
```

第三步：

```text
用同一套 Dune SQL 分析这些 token
比较它们的早期买家、买卖盘、holder、资金来源
```

第四步：

```text
总结风险规则
比如：
- 前 20 买家清仓比例 > 60%
- 同一 funder 资助多个早期买家
- trades 高但 unique_traders 低
- net_buy_usd 连续转负
- sell_volume_usd 由少数钱包贡献
```

第五步：

```text
把这些规则变成 Token Risk Score
```

第六步：

```text
再引入 AI 生成解释报告
```

---

## 14. 参考链接

### 链上分析与 meme 风险

- [MemeTrans arXiv](https://arxiv.org/abs/2602.13480)
- [MemeTrans PDF](https://arxiv.org/pdf/2602.13480)
- [MemeTrans GitHub](https://github.com/git-disl/MemeTrans)
- [MemeTrans Raw README](https://raw.githubusercontent.com/git-disl/MemeTrans/main/README.md)

### 钱包 / 聪明钱 / 地址集群

- [Nansen Smart Money 101](https://academy.nansen.ai/en/articles/2132837-smart-money-101)
- [Nansen API Overview](https://docs.nansen.ai/api/overview)
- [Nansen Smart Money: How It Works](https://eco.com/support/en/articles/14800361-nansen-smart-money-how-it-works)
- [Thrive Smart Money Tracking Docs](https://docs.thrive.fi/docs/smart-money)
- [Thrive On-Chain Widgets](https://docs.thrive.fi/docs/market-intel-on-chain)
- [Ramaris Sybil Detection](https://www.ramaris.app/blog/sybil-detection/)

### API / 数据源

- [Dune API Overview](https://docs.dune.com/api-reference/api-overview)
- [Dune BNB dex.trades](https://docs.dune.com/data-catalog/evm/bnb/curated-data/dex/dex-trades)
- [Dune Token Transfers](https://docs.dune.com/data-catalog/curated/token-transfers/evm/token-transfers)
- [DEX Screener API](https://docs.dexscreener.com/api/reference)
- [GoPlus Token Security API](https://docs.gopluslabs.io/reference/token-security-api)
- [Helius Webhooks](https://www.helius.dev/docs/webhooks)
- [Alchemy Webhooks](https://www.alchemy.com/docs/reference/webhooks-overview)

---

## 15. 最重要的结论

今天最重要的学习结论是：

> 这个系统的价值不在于展示 token 数据，而在于识别数据背后的行为结构。

我们真正要分析的是：

```text
谁在买？
谁在卖？
早期买家有没有撤退？
高胜率地址是否真的可复制？
多个地址是否属于同一实体？
买盘是真实扩散还是刷量？
当前市场环境是否支持 meme 投机？
风险是否已经大于机会？
```

最终目标不是让 AI 预测涨跌，而是让系统做到：

```text
早发现机会
早排除骗局
早识别出货
早判断是否值得人工进一步研究
```

一句话总结：

> 我们要做的是一个基于链上行为的 meme 机会与风险过滤系统，而不是普通行情工具，也不是 AI 自动投资机器人。

