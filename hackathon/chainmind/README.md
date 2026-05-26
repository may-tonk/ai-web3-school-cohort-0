# ChainMind 项目索引

本目录由 `daily/2026-05-19/AI_DeFi_Meme_Workflow_学习总结.md` 拆分整理而来，用于 ChainMind 的项目设计、开发、复盘和黑客松材料准备。

原始学习总结保留在 `daily/2026-05-19/AI_DeFi_Meme_Workflow_学习总结.md`，这里整理为更接近正式项目的工程结构。

## 项目定位

ChainMind 暂不定位为 AI 自动投资机器人，也不做普通行情看板，而是：

> 链上行为风险过滤 + 可复制聪明钱观察 + AI 研究解释系统。

第一阶段目标是先排除明显高风险 token，再把少数值得人工研究的候选解释清楚。

## 顶层结构

| 目录 | 用途 |
|------|------|
| `docs/` | 项目定位、架构、数据、评分、运营、路线图等设计文档 |
| `config/` | 扫描频率、评分阈值、推送限制、prompt 等配置 |
| `database/` | MySQL schema、migration、seed、规则版本等数据库工程文件 |
| `src/chainmind/` | 正式 Python 包代码 |
| `scripts/` | 人工或 Hermes 调用的薄脚本入口 |
| `samples/` | 样本 token、重点钱包、示例报告 |
| `experiments/` | 临时实验、回测、Dune 查询探索 |
| `runtime/` | 本地运行产生的缓存、日志、报告、导出文件 |
| `tests/` | 单元测试、集成测试和测试样本 |
| `deployments/` | Docker、systemd、cron 等部署配置 |

## 文档结构

| 文件 | 用途 |
|------|------|
| `docs/product/01-positioning-and-boundaries.md` | 项目定位、边界、不做什么、核心差异化 |
| `docs/architecture/02-system-architecture-workflow.md` | 系统分层、数据流、Dune/API/Hermes/AI 分工 |
| `docs/scoring/03-scoring-models.md` | Token Risk、Opportunity、Wallet Alpha、Copyability 评分设计 |
| `docs/scoring/04-judgement-framework.md` | ChainMind 8 类核心判断框架 |
| `docs/data/04-wallet-entity-detection.md` | 钱包分析、聪明钱、同实体识别、Sybil/集群判断 |
| `docs/data/05-dune-analysis-playbook.md` | Dune 手动分析模板、BNB token 分析步骤、核心 SQL 方向 |
| `docs/operations/06-ai-hermes-reporting.md` | AI 报告模板、Hermes 推送节奏、分级提醒格式 |
| `docs/roadmap/07-mvp-roadmap.md` | 阶段拆解、交付物、优先级和短期任务 |
| `docs/roadmap/08-execution-plan.md` | 从建库到 Hermes、复盘学习的实际完成步骤 |
| `docs/risks/08-risks-and-mitigations.md` | 可能遇到的困难、误判风险、对应解决方法 |
| `docs/references/09-references.md` | 参考资料、API、论文和产品方法论链接 |
| `docs/engineering/10-directory-guide.md` | 工程目录职责说明 |
| `docs/learning/` | 复盘学习、规则校正、Hermes 学习边界相关文档 |

## 推荐阅读顺序

1. 先读 `docs/product/01-positioning-and-boundaries.md`，明确项目不走偏。
2. 再读 `docs/architecture/02-system-architecture-workflow.md`，理解整体数据流。
3. 开发评分系统时读 `docs/scoring/03-scoring-models.md`、`docs/scoring/04-judgement-framework.md` 和 `docs/data/04-wallet-entity-detection.md`。
4. 写 Dune 查询时读 `docs/data/05-dune-analysis-playbook.md`。
5. 接 Hermes 和 AI 报告时读 `docs/operations/06-ai-hermes-reporting.md`。
6. 做计划和复盘时读 `docs/roadmap/07-mvp-roadmap.md`、`docs/roadmap/08-execution-plan.md`、`docs/risks/08-risks-and-mitigations.md` 与 `docs/learning/`。
