# AI × Web3 School Learning Plan

> 基于学员画像定制：AI 有基础 / Web3 熟练开发者 / 开发+研究双轨 / 每日 6h
> 核心兴趣：链上数据分析、AI + DeFi、AI Agent 开发

## 🎯 学习策略

由于已具备扎实的 Web3 开发基础（Solidity / Foundry / Hardhat / Dune），本计划**不重复入门内容**，以下为核心策略：

1. **Bridge 优先**: 重点突破 AI 与 Web3 的交叉领域
2. **双轨并行**: 上午/下午开发，晚上研究分析，两条线同步推进
3. **以用驱学**: 每个概念都尽快落地为代码或分析报告
4. **开源沉淀**: 所有产出物默认入仓，作为 Proof-of-Work

---

## Phase 1: AI × Web3 核心对齐（第 1-2 周）

### 目标
建立 AI 与 Web3 交叉领域的完整知识框架，将已有技能链接到 AI Agent 和链上分析。

### 学习内容

#### 1.1 LLM 进阶（不是入门，是架构层）
- [ ] AI Agent 架构深度解析：ReAct、CoT、Tool Use、Planning
- [ ] 本地 LLM 部署与 API 管理（Ollama / vLLM）
- [ ] 上下文管理与长上下文方案（RAG、外部记忆）
- [ ] 多 Agent 协作架构（CrewAI / AutoGen 等）

#### 1.2 AI × Web3 Bridge
- [ ] 链上数据如何作为 LLM 的 Context：Dune API、The Graph、节点 RPC 数据拉取
- [ ] 智能合约作为 AI 的 Tool：读取、解析、执行合约交互
- [ ] 链上/链下事件如何触发 Agent 行为
- [ ] 链上证明（Proof of X）与 AI 结合场景

#### 1.3 链上数据 + AI 基础
- [ ] Dune API 进阶：从 SQL 查询到程序化拉取
- [ ] 链上数据的 NLP 处理：交易记录、日志解析
- [ ] 用 LLM 解读链上事件：交易模式识别、异常检测

### 交付物
- [ ] `experiments/phase1/agent-tool-use/` — 一个能查询链上数据的基础 Agent
- [ ] `experiments/phase1/chain-context/` — LLM 解读链上交易的实验
- [ ] `handbook-feedback/phase1.md` — 学习过程中的问题与反馈

---

## Phase 2: 双轨深度实践（第 3-5 周）

### 开发轨：AI + Web3 Agent 工程化

#### 2.1 Web3 Agent 核心开发
- [ ] 链上数据查询 Agent：钱包、交易、合约状态实时查询
- [ ] 分析 Agent：流动性分析、指标监控、异常预警
- [ ] 交易辅助 Agent：气费优化、滑点计算、路径分析
- [ ] 开发自己的 Agent 框架或工具链

#### 2.2 AI + DeFi 工程实践
- [ ] DeFi 协议接口与 AI 的对接（Aave、Uniswap、Compound）
- [ ] 用 LLM 解读 DeFi 策略并生成可执行建议
- [ ] 构建“DeFi 研究助手”Agent
- [ ] 实验 AI 驱动的合约逻辑原型

### 研究轨：深度分析与报告

#### 2.3 链上数据分析研究
- [ ] 主流公链数据样本分析（ETH、L2、其他 L1）
- [ ] 指定协议的深度数据挖掘（如 Uniswap V3 流动性分析）
- [ ] 用 AI 辅助生成数据可视化与洞察报告
- [ ] 建立可复用的分析模板和 SQL 库

#### 2.4 AI + DeFi 机制研究
- [ ] AI 在 DeFi 中的应用场景地图（预测、风控、自动化、治理）
- [ ] 代表性项目案例研究（Giza、Bittensor、？）
- [ ] 风险与挑战：读取性、欺骗性、中心化陷阱
- [ ] 产出研究报告 `submissions/ai-defi-research-report.md`

### 交付物
- [ ] `experiments/phase2/web3-agent/` — 完整 Agent 项目代码
- [ ] `submissions/on-chain-analysis-report-1.md` — 链上分析研究报告
- [ ] `submissions/ai-defi-research-report.md` — AI + DeFi 深度研究

---

## Phase 3: 整合交付与突破（第 6-8 周）

### 开发轨：完整项目

#### 3.1 终极项目选题（根据兴趣二选一或融合）
- **选项 A**: AI-powered 链上分析 Dashboard
  - 实时链上数据接入 + LLM 解读 + 可视化展示
  - 可监控多个协议，支持自然语言查询
- **选项 B**: DeFi 研究助手 Agent
  - 多协议数据聚合、策略分析、风险预警
  - 支持用自然语言生成研究报告

#### 3.2 项目工程化
- [ ] 前后端架构设计
- [ ] 测试覆盖与文档
- [ ] 开源发布准备（README、License、Demo）
- [ ] 部署上线或 Demo 视频

### 研究轨：深度输出

#### 3.3 研究成果巩固
- [ ] 基于 Phase 2 报告，产出更完整的系列分析
- [ ] 尝试向 Handbook 提交修改建议或新增章节
- [ ] 撰写技术博客或 Twitter 线程分享

#### 3.4 Hackathon / Bootcamp 结业
- [ ] 组队或个人参赛
- [ ] 完成项目提交与演示
- [ ] 学习总结与复盘

### 交付物
- [ ] `hackathon/` — Hackathon 项目材料
- [ ] `submissions/final-project/` — 终极项目
- [ ] `submissions/learning-summary.md` — 完整学习复盘

---

## 📅 Daily Rhythm（6 小时版）

| 时段 | 内容 | 时长 | 产出物 | 轨道 |
|------|------|------|---------|------|
| 上午 | 课程学习 / 新概念消化 | 2h | 学习笔记、理论总结 | 开发+研究 |
| 下午 | 开发实践 / 代码 / Agent 调试 | 2.5h | Git commit、实验记录 | 🛠️ 开发轨 |
| 晚上 | 链上数据分析 / 笔记整理 / 打卡 | 1.5h | 分析报告、daily note、feedback | 📊 研究轨 |

### 每周节奏
- **周一**: 宊整复盘上周，调整本周任务
- **周五**: 开发轨 Milestone 验证（Agent 能力检查）
- **周日**: 研究轨深度输出（报告 / 分析）

---

## 📋 核心原则

1. **Proof of Work**: 每天产出可公开的笔记、代码或分析
2. **双轨并行**: 不要等开发完成才做研究，同时推进
3. **Feedback Loop**: 遇到问题立即记录到 `handbook-feedback/`
4. **Consistency**: 6 小时是优势，保持节奏比突击更重要
5. **开源心态**: 所有学习过程默认可被他人查看和引用
6. **用于实战**: 每个理论概念都要在 48h 内落地为代码或分析

---

## 🔧 工具链（预设）

| 类别 | 工具 |
|------|------|
| 开发 | Python, TypeScript, Solidity |
| AI 框架 | LangChain / LangGraph, CrewAI, 自定义 Agent |
| Web3 | Foundry, Hardhat, Ethers.js/Viem, Alchemy/Infura |
| 数据 | Dune API, The Graph, 自定义 Subgraph |
| 部署 | Vercel, Railway, AWS / 本地 Docker |
| 协作 | GitHub, WCB Learning, Telegram |

---

## 📊 进度跟踪

| Phase | 状态 | 开始日期 | 结束日期 | 关键交付物 |
|-------|------|---------|---------|------------|
| Phase 1 | 🔴 待开始 | - | - | Agent 原型 + 链上数据实验 |
| Phase 2 | ⚪ 待开始 | - | - | 完整 Agent + 研究报告 |
| Phase 3 | ⚪ 待开始 | - | - | 终极项目 + 学习复盘 |

---
*Last updated: 2026-05-18*
*Next review: 每周一更新进度*
