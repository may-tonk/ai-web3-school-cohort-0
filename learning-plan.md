# AI × Web3 School Learning Plan

> 学员：web3小虾米（Justin Li）
> 画像：Web3 开发熟练 / Dune 高级用户 / Python+AI 基础 / 每日 6h
> 核心目标：**B — 产出可展示的个人项目，建立难以复制的个人品牌**
> 核心竞争力：**A — Dune 链上数据能力**
> 执行风格：**A — 每日明确任务清单，严格按计划执行**
> 项目主线：**ChainMind — 链上行为风险过滤与可复制聪明钱研究系统**
> 课程周期：**4 周（2026-05-18 → 2026-06-14）**

---

## 🎯 项目定义：ChainMind — 链上行为风险过滤系统

### 一句话描述
一个基于 Dune/API/Hermes/AI 的链上行为雷达：先过滤 meme token 的骗局、刷量、内盘和出货风险，再识别少数值得人工继续研究的可复制聪明钱信号。

### 为什么难以复制
- **数据壁垒**：大多数学员不懂 Dune，不懂链上数据的脆弱性（滞后、精度误差、路由污染、价格缺失）
- **行为壁垒**：普通工具展示 token 表面数据，本项目分析早期买家、同 funder、刷量、出货和同实体分仓
- **可复制壁垒**：不是只找赚钱钱包，而是识别普通用户仍有机会跟随的钱包行为
- **复盘壁垒**：每次推送都记录 15m / 1h / 6h / 24h 表现，用结果反向校准评分

### 核心能力
1. Token Risk Filter：过滤疑似刷量、内盘、早期出货、同实体分仓的 meme token
2. Entity Detection Layer：用同 funder、时间指纹、新钱包比例、gas 来源和合约重叠识别地址集群
3. Wallet Quality / Copyability Layer：区分高胜率钱包和可复制钱包
4. AI Explanation Layer：基于结构化指标生成 A/B/C/D 分级、风险来源和后续观察条件
5. Daily Review Loop：复盘推送后表现，持续校正规则

### 第一阶段边界

第一阶段不做自动交易、不做泛化行情看板、不追求 AI 直接预测涨跌。优先把项目做成一个可靠的风险过滤器：

```text
先排除坏机会
再筛选可观察机会
最后让 AI 解释为什么
```

---

## 📁 仓库产出结构

```
ai-web3-school-cohort-0/
├── README.md                    # 项目介绍 + Demo 链接
├── profile.md                   # 学员画像
├── learning-plan.md             # 本文件
├── chainmind/                   # 项目主目录
│   ├── README.md                # 项目设计文档
│   ├── core/
│   │   ├── agent.py           # Agent 主引擎
│   │   ├── data_source.py     # 数据接入层（Dune / RPC）
│   │   └── analyzer.py        # 分析模块
│   ├── protocols/
│   │   ├── uniswap_v3.py    # 协议特定分析器
│   │   ├── aave_v3.py
│   │   └── base.py            # 协议接口基类
│   ├── scoring/
│   │   ├── token_risk.py      # Token Risk Score
│   │   ├── entity_cluster.py  # 同实体风险评分
│   │   └── copyability.py     # 可复制性评分
│   ├── reports/
│   │   └── template.md        # 风险报告生成模板
│   └── tests/
│       └── test_core.py       # 测试
├── experiments/                 # 实验记录（每周一个子目录）
├── submissions/
│   ├── research/                # 研究报告
│   └── demo-video.md            # Demo 说明
├── daily/                       # 每日学习笔记
├── handbook-feedback/           # 手册反馈
└── templates/
    ├── daily-note.md
    └── task-note.md
```

---

## 📅 时间线：4 周精确路径

> 课程官方结构：
> - Week 1 | Bootcamp: AI and Web3 foundations
> - Week 2 | Bootcamp: AI × Web3 intersection areas
> - Week 3 | Practice deepening and Hackathon kickoff
> - Week 4 | Hackathon sprint and Demo showcase

### Week 1：基础对齐 + 数据连接（5/18-5/24）
> 目标：Agent 能查询链上数据并返回结果，有最小可用版本。
> 课程对应：AI and Web3 foundations

**Day 1-2: LLM Tool Use + Agent 架构**
- 学习 Handbook LLM / Tool Use 章节
- 理解 ReAct / Function Calling 架构
- 搭建最小 Agent 框架（能接收指令、调用工具、返回结果）
- 交付：`chainmind/core/agent.py` 骨架

**Day 3-4: Dune 数据接入 + 风险指标模板**
- 学习 Dune API（你已有基础，聚焦程序化调用）
- 实现固定 SQL 模板 → Dune Query → 风险指标摘要
- 优先覆盖 BNB meme token 的早期买家、5 分钟买卖盘、同 funder、新钱包比例
- 交付：`chainmind/core/data_source.py` + `experiments/week1-risk-filter/`

**Day 5-6: Web3 基础接入**
- 准备测试钱包，完成测试网交易
- 学习合约调用基础（ethers.js / web3.py）
- 交付：测试网交易记录 + `experiments/week1-wallet/`

**Day 7: 周复盘**
- 整合 Week 1 代码，确保 Agent 能"查数据 + 输出风险摘要"
- 产出 Week 1 学习总结
- 交付：`experiments/week1-risk-filter/` 完整可运行

---

### Week 2：交叉领域 + 方向选择（5/25-5/31）
> 目标：多协议支持 + 明确黑客松方向。
> 课程对应：AI × Web3 intersection areas

**Day 8-9: Token Risk Score**
- 让 Agent 不仅仅"查到数据"，还能把数据转成风险判断
- 实现早期买家清仓、trades/unique_traders、net_buy_usd、同 funder、新钱包比例等规则
- 交付：`chainmind/scoring/token_risk.py` 基础版

**Day 10-11: Entity Detection + Copyability**
- 实现同实体风险评分：同 funder、时间集中、新钱包比例、gas 来源、合约交互重叠
- 实现可复制性评分：同区块买入、开池后秒级买入、买入后 5-15 分钟是否仍有流动性
- 交付：`chainmind/scoring/entity_cluster.py` + `chainmind/scoring/copyability.py`

**Day 12-13: 方向锁定**
- 结合课程 track（Agentic Commerce / Dev Tooling / AI Security / Governance）
- 选定黑客松方向：**Dev Tooling / AI Security — ChainMind 作为链上风险研究基础设施**
- 产出项目提案文档
- 交付：`submissions/hackathon-proposal.md`

- 用 Agent 生成第一份 BNB meme token 风险过滤报告
- 整理 Week 2 笔记
- 交付：`submissions/research/report-1.md`

---

### Week 3：深化实践 + 黑客松启动（6/1-6/7）
> 目标：核心功能完成，项目可演示。
> 课程对应：Practice deepening and Hackathon kickoff

**Day 15-16: 实时监控**
- 添加定时任务 / 事件触发能力
- 实现报告生成模板（Markdown 输出）
- 交付：可定时运行的风险扫描 Agent

**Day 17-18: 报告引擎**
- 实现带数据来源引用的报告生成
- 支持 A/B/C/D 分级、机会来源、风险来源、后续观察条件
- 交付：`chainmind/reports/` 报告模块

**Day 19-20: 工程化**
- 错误处理、重试机制、日志
- 前端界面（Streamlit / Gradio 快速搭建）
- 交付：可交互的 Web 界面

**Day 21: 周复盘 + 团队对齐**
- 整合所有模块，确保端到端可运行
- 准备黑客松 Demo 脚本
- 交付：`submissions/demo-script.md`

---

### Week 4：黑客松冲刺 + Demo 展示（6/8-6/14）
> 目标：完整项目 + 开源发布准备。
> 课程对应：Hackathon sprint and Demo showcase

**Day 22-23: 核心完善**
- 修复 bug，优化查询速度
- 增加更多协议支持（可选：Curve, Compound）
- 交付：稳定的 v0.1 版本

**Day 24-25: Demo 准备**
- 录制 Demo 视频（3-5 分钟）
- 完善 README（项目介绍、运行方式、截图）
- 交付：`submissions/demo-video.md` + 视频文件

**Day 26-27: 发布与展示**
- 开源发布准备（README、License、贡献指南）
- 撰写项目介绍 Twitter 线程 / 博客
- 提交黑客松作品
- 交付：完整开源项目 + 社媒内容

**Day 28: 结业复盘**
- 学习总结与复盘
- 整理项目后续 Roadmap
- 交付：`submissions/final-reflection.md`

---

## ⚡ 每日节奏模板（6 小时）

### 上午 3h — 开发 & 实践
```
任务类型：写代码 / 调试 Agent / 测试 Dune 查询
产出要求：至少 1 个 git commit
关键原则：代码可以是粗糙的，但必须能跑通或有明确的待解决问题
```

### 下午 2h — 学习 & 结构
```
任务类型：读 Handbook / 看课程 / 学新架构
产出要求：学习笔记写入 daily/YYYY-MM-DD.md
关键原则：不只是"看完"，要写出"如何应用到 ChainMind 项目中"
```

### 晚上 1h — 分析 & 整理
```
任务类型：链上数据分析 / 笔记整理 / 打卡 / 反馈
产出要求：
  - daily note 完整
  - 如果有数据分析结果→写入 experiments/
  - 如果有 Handbook 问题→写入 handbook-feedback/
  - 生成打卡草稿
关键原则：每天必须有一件"可被他人看到的产出物"
```

---

## 📋 核心原则

1. **项目驱动**：所有学习都应该回答"这对 ChainMind 有什么帮助"
2. **24h 落地**：每个新概念学完 24h 内必须有代码 commit（4 周节奏更快）
3. **每日交付**：每天结束时 repo 必须比昨天早上更丰富
4. **数据为核**：每个决策、每份报告都必须有链上数据支撑
5. **可复现**：所有分析结果必须注明数据来源和查询时间
6. **安全红线**：私钥不上链、交易不自动执行、测试网优先

---

## 📊 进度跟踪模板

| 周次 | 里程碑 | 状态 | 备注 |
|------|--------|------|------|
| W1 | BNB meme 风险过滤原型 | ⬜ | Dune + 固定指标模板 |
| W2 | Token Risk + Entity + Copyability | ⬜ | 方向锁定 |
| W3 | 报告引擎 + Web 界面 | ⬜ | 深化实践 |
| W4 | 开源发布 + Demo | ⬜ | 黑客松冲刺 |

---

## 📝 更新日志

| 日期 | 变更 |
|------|------|
| 2026-05-18 | 初始版 8 周计划 |
| 2026-05-18 | 按实际课程时长压缩为 4 周，与官方 Bootcamp 结构对齐 |

---
*Next review: 每周日复盘*
