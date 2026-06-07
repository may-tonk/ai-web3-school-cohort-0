# 10. 项目目录简要说明

本文件简要说明 ChainMind 后续代码目录的用途，帮助开发时保持结构清晰。

## config/

存放项目配置，例如扫描频率、风险阈值、推送数量限制、AI prompt 配置等。后续调参优先改这里，不要把阈值写死在代码里。

## database/

项目级数据库工程目录。用于保存 MySQL 建表脚本、迁移脚本、初始化种子数据和规则版本数据；它描述“数据库长什么样”。

## docs/

项目文档目录。产品定位、系统架构、数据方法、评分模型、运营推送、路线图、风险和参考资料都归档在这里。

## src/chainmind/

正式 Python 包代码目录。后续所有可复用的核心逻辑都放在这里，避免把业务逻辑堆到 `scripts/` 或单个大文件里。

## src/chainmind/cli/

命令行入口，例如手动分析某个 token、启动 8 小时雷达扫描、执行每日复盘等。

## src/chainmind/api/

预留 HTTP API 服务入口。后续如果 Hermes、前端或其他服务要通过接口调用 ChainMind，可以放在这里。

## src/chainmind/core/

项目通用基础模块，例如配置加载、日志、错误类型、共享数据结构等。

## src/chainmind/orchestration/

流程编排层。负责把数据获取、清洗、评分、报告、推送串起来，但不直接写 SQL、不直接实现评分规则。

## src/chainmind/realtime/

实时发现与轻量筛选模块。负责新池扫描、重点钱包事件、市场异常事件、候选 token 排序等。

## src/chainmind/data/

外部数据源客户端。包括 Dune、DEX Screener、GoPlus、BscScan 等 API 的封装。

## src/chainmind/domain/

领域对象目录。后续可以放 Token、Wallet、Score、Alert、Review 等核心业务对象定义。

## src/chainmind/queries/

存放 Dune SQL 模板。一个 SQL 文件只解决一个问题，例如 5 分钟买卖盘、早期买家、资金来源、holder 集中度。

## src/chainmind/cleaning/

链上数据清洗层。负责地址标准化、交易方向统一、空值处理、浮点误差处理、时间窗口聚合等。

## src/chainmind/scoring/

评分模块。负责 Token Risk、Entity Cluster、Copyability、Opportunity、Priority 等分数计算。

## src/chainmind/learning/

复盘学习模块。负责分析历史推送表现、误报/漏报、规则命中率、钱包信号有效性，并生成规则调整建议；它不直接替代实时评分，而是反向优化评分规则。

## src/chainmind/alerts/

推送策略模块。负责判断是否推送、推送多少、是否进入冷却期、是否进入 8 小时摘要，以及 Hermes / Telegram 渠道适配。

## src/chainmind/reports/

报告生成模块。负责把结构化评分结果转成 Markdown 报告或 AI 解释报告。

## src/chainmind/storage/

数据库访问代码目录。它负责 Python 如何连接 MySQL、读写表、封装查询；具体建表 SQL 放在 `database/`。

## src/chainmind/services/

业务服务层。后续可以把跨模块的稳定业务能力放在这里，例如 token 分析服务、watchlist 服务、alert 服务。

## src/chainmind/utils/

通用小工具，例如地址处理、时间窗口处理、数字精度处理、JSON 读写等。不要把业务逻辑放进这里。

## scripts/

可执行脚本入口。后续 Hermes 或人工可以调用这里的脚本，例如 `analyze_token.py`、`radar_scan_8h.py`、`daily_review.py`。

## samples/

样本数据目录。用于保存测试 token、重点钱包列表、观察 token 列表和示例报告。

其中 `samples/feedback/` 可用于保存用户反馈、推送点击、人工标注结果，供学习复盘模块使用。

## experiments/

实验区。用于放临时分析、Dune 查询探索、回测结果和每周实验记录；稳定后再迁移到 `src/chainmind/`。

## runtime/

本地运行产生的数据目录。用于保存 SQLite 数据库、缓存、生成报告和导出文件，通常不提交到 Git。

其中 `runtime/learning/` 可用于保存每日复盘输出、规则建议草稿和临时回测结果。

## deployments/

部署配置目录。后续 Docker、systemd、cron 或服务器定时任务配置都放在这里。

## tests/

测试目录。优先测试评分规则、推送策略、数据清洗和候选排序，避免后续规则变化导致误判。

## 维护原则

- 数据源只负责取数。
- 清洗层只负责整理数据。
- 评分层只负责计算分数。
- 报告层只负责解释结果。
- 推送层只负责是否推、怎么推、推多少。
- 学习层只负责复盘、评估、提出规则调整建议。
- 编排层只负责串流程，不承载具体业务细节。

## 按阶段查找文件

正式代码目录仍然按工程职责组织，不建议把源码重命名为 `phase2_*`、`phase3_*` 或按阶段拆目录。

如果需要查看“某个阶段对应哪些代码、脚本、测试、实验和文档”，请读：

```text
docs/engineering/11-phase-file-map.md
```

后续每完成一个阶段，优先更新这份阶段文件地图，而不是改变正式代码命名。
