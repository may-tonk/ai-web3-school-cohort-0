# 2026-05-25 Phase 2 Token Risk Score 执行计划

本文是 ChainMind 第二阶段的执行参考。后续推进 Phase 2 时，每完成一个步骤，都可以回到本文对照检查是否完成、是否需要调整，再进入下一步。

## 1. Phase 2 的目标

Phase 2 的核心目标是：

```text
把 Phase 1 手动分析中有效的风险判断，变成可运行、可测试、可解释、可复盘的 Token Risk Score v0.1。
```

也就是从当前的最小分析链路：

```text
样本 token JSON
-> TokenSnapshot
-> placeholder risk score
-> grade / action / reasons
```

升级为：

```text
结构化 token 数据
-> 数据质量检查
-> 多条风险规则评分
-> risk_score
-> risk_level
-> evidence / reasons
-> grade / action
```

Phase 2 完成后，ChainMind 应该能够回答：

```text
这个 token 为什么高风险？
风险主要来自低流动性、买卖盘恶化、刷量、早期买家撤退，还是同 funder / 新钱包线索？
哪些数据缺失，因此当前判断置信度不高？
这个结果是否能被测试和复盘？
```

## 2. Phase 2 不做什么

第二阶段先不做以下内容：

- 不做自动买卖。
- 不做 AI 自动预测涨跌。
- 不做全市场实时扫描。
- 不直接接 Hermes 自动化调度。
- 不做完整 Wallet Alpha Score。
- 不做完整 Copyability Score。
- 不把同 funder 直接判定为同一个真实人。

这些内容可以在后续阶段做。Phase 2 只聚焦：

```text
Token Risk Score v0.1
```

## 3. 当前已具备的基础

当前项目已经具备以下基础：

- Python 工程骨架。
- 本地 CLI 分析入口。
- `TokenSnapshot` 基础结构。
- `token_risk.py` 初始启发式规则。
- `opportunity.py` 初始机会评分。
- `priority.py` A/B/C/D 分级。
- healthy / risky 两个样本 JSON。
- 基础单元测试。
- Phase 1 首轮 Dune 检验报告。
- 4 个 BNB Dune SQL 模板：
  - `token_trading_activity.sql`
  - `five_minute_flow.sql`
  - `early_buyers.sql`
  - `early_buyer_funding.sql`

这说明 Phase 2 可以开始，但样本和真实 token 校验仍需要继续补。

## 4. Phase 2 总体流程

推荐执行流程：

```text
Step 1: 固定 Phase 2 输入字段
Step 2: 定义 Data Quality Layer
Step 3: 重构 Token Risk Score v0.1
Step 4: 调整 scoring 配置结构
Step 5: 扩展样本 JSON
Step 6: 增加规则单元测试
Step 7: 映射 Dune SQL 输出到样本结构
Step 8: 小规模真实 token 验证
Step 9: 写 Phase 2 检查报告
```

后续每一步完成后都应暂停确认，再进入下一步。

## 5. Step 1：固定 Phase 2 输入字段

### 5.1 要解决的问题

当前 `TokenSnapshot` 只有：

```text
token
market
flow_5m
early_buyers
```

这已经能跑最小评分，但不足以支持 Phase 2 的完整风险判断。

### 5.2 建议输入结构

Phase 2 建议将输入结构扩展为：

```json
{
  "token": {},
  "market": {},
  "flow_5m": [],
  "early_buyers": [],
  "funding": {},
  "security": {},
  "data_quality": {}
}
```

### 5.3 字段来源

| 字段 | 推荐来源 | 用途 |
| --- | --- | --- |
| `token` | API / 手动 | token 地址、symbol、chain、创建时间 |
| `market` | DEX Screener / Birdeye / GoPlus 等 API | 流动性、交易量、holder、基础市场状态 |
| `flow_5m` | Dune `five_minute_flow.sql` | 买卖盘、刷量、net buy |
| `early_buyers` | Dune `early_buyers.sql` | 早期买家是否撤退 |
| `funding` | Dune `early_buyer_funding.sql` | same-funder、新钱包、资金来源 |
| `security` | GoPlus / BscScan | honeypot、权限、LP、tax、blacklist |
| `data_quality` | ChainMind 自己计算 | 判断本次分析数据是否完整可信 |

### 5.4 本步产出

- 更新 `TokenSnapshot` 字段结构。
- 更新 healthy / risky 样本 JSON。
- 保持旧样本尽量兼容。

### 5.5 验收标准

- 现有 CLI 仍然能跑。
- 旧样本不会因为新增字段而失败。
- 新字段可以通过 `TokenSnapshot.from_mapping()` 读取。

## 6. Step 2：定义 Data Quality Layer

### 6.1 Data Quality 是什么

Data Quality 不是 token 的流动性，也不是 token 风险本身。

它判断的是：

```text
我们拿到的数据够不够完整、可信，能不能支撑后面的风险评分。
```

例如：

```text
liquidity_usd 很低
```

这是市场风险。

但：

```text
flow_5m 缺失
early_buyers 缺失
funding 缺失
amount_usd 大量为空
```

这是数据质量问题。

### 6.2 要检查的内容

第一版 Data Quality 建议检查：

| 检查项 | 含义 |
| --- | --- |
| 是否有 `market` | 没有则无法判断基础流动性和交易量 |
| 是否有 `flow_5m` | 没有则无法判断买卖盘和刷量 |
| 是否有 `early_buyers` | 没有则无法判断早期买家撤退 |
| 是否有 `funding` | 没有则无法判断 same-funder |
| `flow_5m` 中 `amount_usd` 是否缺失 | 缺失太多会影响 net buy |
| early buyer 数量是否太少 | 样本太少，不能强判断 |
| funder 是否可能是基础设施地址 | router / pool / CEX 不能直接当作同实体证据 |

### 6.3 建议输出

```json
{
  "level": "partial",
  "confidence": "medium",
  "missing_fields": ["funding"],
  "warnings": [
    "Missing funding data; same-funder risk cannot be evaluated."
  ]
}
```

### 6.4 本步产出

- 新增 `src/chainmind/scoring/data_quality.py`。
- 定义 `DataQualityResult`。
- 在分析结果中保留数据质量信息，或先在 reasons 中输出。

### 6.5 验收标准

- 完整样本输出 `good / high`。
- 缺少 `flow_5m` 的样本输出 `partial` 或 `poor`。
- 缺少 `funding` 不会导致评分失败，只会降低置信度。

## 7. Step 3：重构 Token Risk Score v0.1

### 7.1 当前状态

当前 `token_risk.py` 已经具备初始规则：

- 低流动性加分。
- 最新 5m `net_buy_usd < 0` 加分。
- `trades / unique_traders` 过高加分。
- 早期买家退出比例过高加分。

但当前仍是基础启发式，需要升级为更清晰的 v0.1。

### 7.2 建议规则模块

```text
calculate_token_risk
  -> score_liquidity_risk
  -> score_flow_risk
  -> score_wash_trading_risk
  -> score_early_buyer_exit_risk
  -> score_funding_cluster_risk
  -> score_security_risk
  -> apply_data_quality_adjustment
```

### 7.3 v0.1 风险规则

| 风险项 | 初始分数建议 | 说明 |
| --- | ---: | --- |
| 基础风险 | 20 | meme token 默认有基础风险 |
| 低流动性 | +20 | `liquidity_usd < 20000` |
| 最新 5m 净买入为负 | +15 | `net_buy_usd < 0` |
| 连续多个 5m 净买入为负 | +20 | 卖压持续增强 |
| trades / unique_traders 过高 | +20 | 疑似刷量或机器人 |
| sellers > buyers 且 sell volume 更大 | +15 | 买盘承接变弱 |
| 早期买家清仓比例 > 60% | +25 | 早期资金撤退 |
| 新钱包比例过高 | +15 | 疑似临时分仓或狙击 |
| 同 funder 覆盖多个早期买家 | +20 | 假共识或同实体风险 |
| GoPlus 高危 | +50 或直接 D | 合约风险优先级最高 |

### 7.4 本步产出

- 重构 `src/chainmind/scoring/token_risk.py`。
- 每条规则都输出可读 reason。
- 保持最终分数在 `0-100`。

### 7.5 验收标准

- healthy 样本仍应低风险。
- risky 样本仍应高风险或 D。
- 每个风险分变化都有 reason。
- 不因为缺少某个字段导致程序崩溃。

## 8. Step 4：调整 scoring 配置结构

### 8.1 要解决的问题

当前阈值基本写死在代码里，后续调参不方便。

Phase 2 可以先不做复杂配置加载，但应该先把配置结构设计出来。

### 8.2 建议配置结构

```yaml
token_risk:
  base_score: 20

  liquidity:
    low_usd: 20000
    score: 20

  flow:
    trades_per_unique_trader_high: 5
    negative_net_buy_score: 15
    consecutive_negative_buckets: 2
    consecutive_negative_score: 20
    weak_buy_side_score: 15

  early_buyers:
    exit_balance_ratio: 0.05
    high_exit_ratio: 0.6
    high_exit_score: 25
    new_wallet_age_days: 1
    new_wallet_ratio: 0.6
    new_wallet_score: 15

  funding:
    shared_funder_min_buyers: 2
    shared_funder_score: 20
```

### 8.3 本步产出

- 更新 `config/scoring.yaml`。
- 暂时可以先作为文档化配置，后续再接 loader。

### 8.4 验收标准

- 配置文件能清楚表达当前规则阈值。
- 代码中的阈值可以和配置对应。

## 9. Step 5：扩展样本 JSON

### 9.1 当前样本

当前已有：

- `example-healthy-token.json`
- `example-risky-token.json`

### 9.2 建议新增样本

建议新增：

```text
example-low-liquidity-token.json
example-wash-trading-token.json
example-early-exit-token.json
example-same-funder-token.json
example-incomplete-data-token.json
```

### 9.3 样本设计原则

每个样本只突出一种主要风险，方便判断规则是否生效。

例如：

```text
wash trading 样本：
trades 很高
unique_traders 很低
net_buy_usd 不一定很差
```

```text
same-funder 样本：
多个 early buyers 来自同一个非基础设施 funder
钱包年龄短
入场前交易次数少
```

### 9.4 本步产出

- 新增至少 3 个样本 JSON。
- 最终建议至少 5 个 Phase 2 风险场景样本。

### 9.5 验收标准

- 每个样本都可以通过 CLI 分析。
- 每个样本都触发预期风险 reason。

## 10. Step 6：增加规则单元测试

### 10.1 当前测试不足

当前测试主要验证最小链路能跑：

```text
TokenSnapshot
-> analyze_token
-> AnalysisResult
```

Phase 2 需要验证每条规则真的生效。

### 10.2 建议新增测试

新增：

```text
tests/unit/test_token_risk_scoring.py
tests/unit/test_data_quality.py
```

测试场景：

- 低流动性 token 风险分上升。
- `net_buy_usd < 0` 风险分上升。
- `trades / unique_traders` 过高风险分上升。
- 早期买家清仓比例高风险分上升。
- same-funder 风险分上升。
- 缺少 `flow_5m` 会降低数据质量。
- 缺少 `early_buyers` 不会崩溃。

### 10.3 本步产出

- 至少 5 个规则测试。
- `pytest` 全部通过。

### 10.4 验收标准

```text
pytest
```

输出通过。

## 11. Step 7：映射 Dune SQL 输出到样本结构

### 11.1 目标

明确 Dune 查询结果如何进入 ChainMind 的 JSON 输入。

### 11.2 映射关系

| SQL | 关键输出 | JSON 字段 |
| --- | --- | --- |
| `token_trading_activity.sql` | trades、unique_traders、volume_usd、main_pool_share | `market` 或 `trading` |
| `five_minute_flow.sql` | bucket、trades、unique_traders、buyers、sellers、net_buy_usd | `flow_5m` |
| `early_buyers.sql` | buyer、rank、buy_usd、remaining_ratio | `early_buyers` |
| `early_buyer_funding.sql` | funder、wallet_age、tx_count、funded_selected_early_buyers | `funding` / `early_buyers` |

### 11.3 本步产出

- 新增 `docs/data/06-dune-output-mapping.md`。
- 明确每个字段的口径。

### 11.4 验收标准

- 后续手动从 Dune 复制结果时，知道每列应该放到哪个 JSON 字段。
- 字段名和 Python 评分代码一致。

## 12. Step 8：小规模真实 token 验证

### 12.1 目标

用少量真实 token 验证规则是否合理，不急着追求 20-50 个。

### 12.2 建议样本分布

先选 5 个：

```text
1 个相对健康 token
1 个低流动性 token
1 个疑似刷量 token
1 个早期买家撤退 token
1 个 same-funder 明显 token
```

### 12.3 每个 token 记录内容

```text
token 地址
Dune 查询结果摘要
API 基础信息摘要
ChainMind risk_score
ChainMind grade / action
人工判断
是否一致
误判或不确定点
```

### 12.4 本步产出

- 新增 `experiments/week2-token-risk-score/`。
- 新增真实 token 验证记录。

### 12.5 验收标准

- 至少 3 个真实 token 完成手动验证。
- 记录至少 1 个需要调整的规则或字段口径。

## 13. Step 9：写 Phase 2 检查报告

### 13.1 目标

Phase 2 v0.1 完成后，要用报告固定阶段成果和问题。

### 13.2 建议报告位置

```text
experiments/week2-token-risk-score/phase2-check-report.md
```

### 13.3 报告内容

建议包含：

- 本阶段目标。
- 已实现规则。
- 输入字段结构。
- 测试样本。
- 真实 token 验证结果。
- 哪些规则有效。
- 哪些规则误判。
- 下一阶段需要调整的点。

### 13.4 验收标准

- 报告能说明 Phase 2 是否达到 v0.1。
- 后续 Phase 3 能基于报告继续做 Entity Cluster Score。

## 14. Phase 2 完成标准

Phase 2 不要求完美，但至少需要满足：

- `TokenSnapshot` 支持 Phase 2 输入字段。
- 有基础 Data Quality 判断。
- `Token Risk Score v0.1` 已实现。
- 至少 6 条风险规则可运行。
- 至少 5 个规则单元测试。
- 至少 5 个风险场景样本。
- 至少 3 个真实 token 小样本验证。
- 输出包含 `risk_score`、`grade`、`action` 和可读 reasons。
- 缺字段不会崩溃，只会降低置信度或跳过对应判断。

达到以上标准后，可以进入 Phase 3：

```text
Entity Cluster Score
```

## 15. 推荐执行节奏

后续实际执行时，建议按下面节奏推进：

```text
1. 扩展 TokenSnapshot
2. 加 Data Quality Layer
3. 重构 Token Risk Score
4. 更新 scoring.yaml
5. 新增样本 JSON
6. 新增规则测试
7. 跑 pytest
8. 手动验证真实 token
9. 写 Phase 2 check report
```

每完成一步都暂停检查：

```text
这一步是否达成目标？
输出是否能被后续步骤使用？
是否需要调整字段或规则？
测试是否通过？
```

## 16. 当前第一步建议

下一步建议从 Step 1 开始：

```text
扩展 TokenSnapshot 字段结构，但保持旧样本兼容。
```

先不要急着改评分规则。字段结构稳定后，再做 Data Quality 和 Token Risk v0.1，会更顺。
