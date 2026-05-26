# 08. ChainMind 项目完成步骤

本文件用于指导 ChainMind 从项目设计进入可执行系统。  
`07-mvp-roadmap.md` 更偏阶段路线，本文件更偏实际开发顺序。

## 当前状态

目前项目已经具备：

- 项目定位和边界。
- 正式目录结构。
- 判断框架。
- 基础评分方向。
- Dune / API / Hermes / AI 的职责分工。
- learning 复盘学习闭环设计。
- 部分代码基础和测试入口。

但项目还没有形成完整自动化闭环。下一步应该优先跑通一条主链路：

```text
输入 token
→ 获取数据
→ 简单评分
→ 输出结果
→ 后续再接 Dune、AI、Hermes、复盘学习
```

## 阶段 0：项目基础整理

目标：让项目具备正式开发基础。

要做：

- 确认 Python 环境和依赖。
- 确认配置文件结构。
- 确认 MySQL 数据库方案。
- 准备 `.env.example`。
- 准备基础测试命令。

产出：

```text
pyproject.toml
requirements-dev.txt
config/app.yaml
config/scoring.yaml
.env.example
```

完成标志：

```text
项目可以安装依赖
测试命令可以运行
配置文件可以被 Python 读取
```

## 阶段 1：MySQL 数据库基础

目标：建立 ChainMind 的项目记忆层。

要做：

- 创建 MySQL 数据库 `chainmind`。
- 编写核心建表 SQL。
- 设计基础表结构。
- 实现 Python 数据库连接。
- 实现基础读写封装。

建议表：

```text
watchlist_tokens
watchlist_wallets
candidate_tokens
token_snapshots
analysis_runs
token_scores
alerts
review_results
query_cache
rule_versions
rule_suggestions
```

产出：

```text
database/schema/001_core_tables.sql
database/schema/002_analysis_tables.sql
database/schema/003_alert_review_tables.sql
database/rules/001_rule_version_tables.sql
src/chainmind/storage/
```

完成标志：

```text
MySQL 中能看到 chainmind 数据库和核心表
Python 可以写入一条 analysis_run
Python 可以读取 token_scores
```

## 阶段 2：单 token 实时分析

目标：先让指定 token 可以被分析，不依赖全自动扫描。

要做：

- 实现 DEX Screener 数据接入。
- 实现 GoPlus 安全检查。
- 将实时数据整理成 TokenSnapshot。
- 实现简单 Token Risk Score。
- 实现 `analyze_token` 编排流程。
- 实现命令行脚本入口。

第一版只判断：

```text
流动性是否足够
成交量是否足够
交易数是否足够
GoPlus 是否高危
价格是否短时暴拉
```

产出：

```text
src/chainmind/data/
src/chainmind/domain/token_snapshot.py
src/chainmind/scoring/token_risk.py
src/chainmind/orchestration/analyze_token.py
scripts/analyze_token.py
```

完成标志：

```bash
python scripts/analyze_token.py --chain bnb --token 0x...
```

能够输出：

```text
risk_score
grade
reasons
evidence
```

并写入 MySQL。

## 阶段 3：Dune 深度分析

目标：对通过初筛的 token 做深度链上结构分析。

要做：

- 实现 Dune API client。
- 整理 BNB Dune SQL 模板。
- 实现 Dune 查询参数传入。
- 实现查询结果缓存。
- 实现 Dune 结果清洗。

核心 SQL：

```text
token_trading_activity.sql
five_minute_flow.sql
early_buyers.sql
early_buyer_funding.sql
holder_snapshot.sql
```

重点输出：

```text
5m / 15m / 1h 买卖盘
buyers / sellers
net_buy_usd
早期买家列表
早期买家 remaining_ratio
同 funder 风险
holder 集中度
```

完成标志：

```text
输入 token
→ 自动跑 Dune 查询
→ 获取结构化结果
→ 清洗后传给 scoring
```

## 阶段 4：完整评分体系

目标：把判断框架落成可执行评分。

要做：

- 完善 Token Risk Score。
- 实现 Entity Cluster Score。
- 实现 Copyability Score。
- 实现 Opportunity Score。
- 实现 Priority Score。
- 实现 A/B/C/D 分级规则。

每个评分模块统一输出：

```json
{
  "score": 72,
  "level": "high",
  "reasons": [],
  "evidence": {}
}
```

产出：

```text
src/chainmind/scoring/token_risk.py
src/chainmind/scoring/entity_cluster.py
src/chainmind/scoring/copyability.py
src/chainmind/scoring/opportunity.py
src/chainmind/scoring/priority.py
```

完成标志：

```text
同一个 token 可以输出完整评分包：
Risk / Entity / Copyability / Opportunity / Priority / Grade
```

## 阶段 5：报告生成

目标：把结构化评分结果转成可读研究报告。

要做：

- 实现 Markdown 报告模板。
- 实现 AI 报告生成。
- 固定报告字段。
- 明确不输出买入、卖出、仓位、止盈止损。

报告结构：

```text
结论等级
处理建议
机会来源
主要风险
可复制性
后续观察条件
不确定性
```

产出：

```text
src/chainmind/reports/
config/prompts.yaml
runtime/reports/
```

完成标志：

```text
每次 analyze_token 都能生成 Markdown 报告
```

## 阶段 6：推送策略与 Hermes 接口

目标：让 ChainMind 能被 Hermes 自动触发和推送。

要做：

- 实现 alert_policy。
- 实现 cooldown。
- 实现 digest_builder。
- 实现 Hermes 输出格式。
- 让脚本输出 Hermes 可读取的 JSON / Markdown。

推送规则：

```text
A：即时推送
B：进入 8 小时摘要
C：只入库
D：过滤
```

产出：

```text
src/chainmind/alerts/alert_policy.py
src/chainmind/alerts/cooldown.py
src/chainmind/alerts/digest_builder.py
src/chainmind/alerts/channels/hermes.py
```

完成标志：

```text
Hermes 调用脚本后，可以拿到 should_send、grade、summary、report_markdown
```

## 阶段 7：8 小时雷达扫描

目标：系统能主动发现候选 token，但不做高频全市场轰炸。

要做：

- 实现 new_pair_scanner。
- 实现 realtime_filter。
- 实现 candidate_ranker。
- 每 8 小时轻扫 BNB meme 新池 / 活跃池。
- Top 30 进入候选池。
- Top 10-15 跑 Dune 深度分析。
- A/B 进入推送或摘要。

产出：

```text
src/chainmind/realtime/new_pair_scanner.py
src/chainmind/realtime/realtime_filter.py
src/chainmind/realtime/candidate_ranker.py
src/chainmind/orchestration/radar_scan.py
scripts/radar_scan_8h.py
```

完成标志：

```bash
python scripts/radar_scan_8h.py
```

能够输出：

```text
候选列表
深度分析列表
A/B/C/D 结果
推送摘要
```

## 阶段 8：watchlist 监控

目标：支持指定 token / wallet 的事件触发。

要做：

- 实现 watchlist_tokens。
- 实现 watchlist_wallets。
- 检测重点钱包买入新 token。
- 检测观察 token 的风险变化。
- 支持 B 升 A 或重大风险事件触发提醒。

产出：

```text
src/chainmind/realtime/wallet_event_detector.py
src/chainmind/realtime/market_event_detector.py
src/chainmind/orchestration/watch_token.py
src/chainmind/orchestration/watch_wallet.py
scripts/monitor_watchlist.py
```

完成标志：

```text
用户指定 token 或 wallet 后，系统能根据事件触发分析
```

## 阶段 9：每日复盘

目标：让系统知道自己判断得好不好。

要做：

- 读取昨日 alerts。
- 查询推送后 15m / 1h / 6h / 24h 表现。
- 计算最大涨幅。
- 计算最大回撤。
- 判断是否 rug。
- 判断是否有可执行观察窗口。
- 写入 review_results。
- 生成每日复盘报告。

产出：

```text
src/chainmind/orchestration/daily_review.py
src/chainmind/reports/review_report.py
scripts/daily_review.py
```

完成标志：

```bash
python scripts/daily_review.py
```

能够生成：

```text
昨日 A/B/C/D 表现
误报样本
漏报样本
规则改进方向
```

## 阶段 10：学习复盘闭环

目标：让系统不只是固定规则，而是可以持续优化。

要做：

- 统计规则命中率。
- 分析误报。
- 分析漏报。
- 评估钱包信号有效性。
- 生成规则权重调整建议。
- 管理规则版本。

产出：

```text
src/chainmind/learning/evaluators/
src/chainmind/learning/backtesting/
src/chainmind/learning/advisors/
database/rules/
```

完成标志：

```text
系统能输出规则调整建议：
哪个规则过严
哪个规则过松
哪个钱包失效
哪个指标应该加权
```

## 阶段 11：项目级完善

目标：让项目可以展示、维护和部署。

要做：

- 补充单元测试。
- 补充集成测试。
- 补充 README 运行说明。
- 补充日志。
- 补充异常处理。
- 补充 Docker / cron / systemd 部署配置。
- 准备样本数据。
- 准备 Demo 脚本。

产出：

```text
tests/unit/
tests/integration/
deployments/
samples/
docs/
```

完成标志：

```text
别人按 README 能配置环境并跑通 analyze_token
```

## 推荐优先级

当前最重要的 3 个阶段：

```text
1. MySQL + 项目基础整理
2. analyze_token 单 token 实时分析
3. Dune 深度分析
```

先不要急着做：

```text
多链支持
复杂前端
自动交易
复杂自由 Agent
全市场高频扫描
```

## 最短可执行路线

如果要最快让项目跑起来，按这个顺序：

```text
建库
→ DEX Screener
→ GoPlus
→ 简单评分
→ MySQL 入库
→ Markdown 报告
→ Dune 深度分析
→ A/B/C/D 分级
→ Hermes 输出
```

跑通这条后，ChainMind 就从项目设计进入可执行产品。
