# Learner Profile

## ✅ 已确认画像

| 维度 | 确认内容 |
|------|---------|
| **AI 基础** | 有基础 |
| **Web3 基础** | 系统学习过，熟练 Solidity / Foundry / Hardhat / Remix / Dune |
| **编程能力** | 会基础脚本，可独立完成自动化任务 |
| **每日投入** | 6 小时 |
| **输出语言** | 中文 |
| **第一优先级** | **B — 产出可展示的个人项目，建立难以复制的个人品牌** |
| **核心竞争力** | **A — Dune 链上数据能力** |
| **执行风格** | **A — 每日明确任务清单，严格按计划执行** |

## 🎯 项目主线

**项目名称：ChainMind — DeFi 智能研究助手**

### 一句话定位
能查询链上数据、解读 DeFi 协议状态、生成可验证分析报告的 AI Agent。

### 为什么难以复制
- **数据壁垒**：大多数学员不懂 Dune，不懂链上数据的"脆弱性"
- **领域壁垒**：懂 AI 的人不懂 DeFi 机制，懂 DeFi 的人不会搭 Agent 框架
- **可验证壁垒**：大多数"DeFi Agent"是聊天机器人，你的是"数据驱动 + 可追溯报告"

### 核心能力
1. 自然语言查询链上数据（取代手写 SQL）
2. 实时监控并解读 DeFi 异常事件
3. 生成带数据来源引用的研究报告
4. 支持多协议横向对比分析

## ⚡ 每日节奏（6 小时精确分配）

| 时段 | 时长 | 内容 | 产出要求 |
|------|------|------|---------|
| 上午 | 2h | 学习 / 课程 / 架构理解 | 学习笔记 → daily/ |
| 下午 | 2.5h | 开发 / 代码 / 实验 | ≥1 个 git commit |
| 晚上 | 1.5h | 分析 / 整理 / 打卡 / 反馈 | 每天必须有一件"可被他人看到的产出物" |

## 📁 仓库产出结构

```
chainmind/                   # 项目主目录
  ├── core/
  │   ├── agent.py         # Agent 主引擎
  │   ├── data_source.py   # 数据接入层
  │   └── analyzer.py      # 分析模块
  ├── protocols/
  │   ├── uniswap_v3.py  # Uniswap V3 分析器
  │   ├── aave_v3.py     # Aave V3 分析器
  │   └── base.py          # 协议接口基类
  ├── reports/
  └── tests/
experiments/                 # 实验记录
submissions/                 # 最终交付物
```

## 🔧 技术栈

| 类别 | 工具 |
|------|------|
| AI 框架 | LangChain / LangGraph, OpenAI API / 本地 LLM |
| Web3 | Dune API, The Graph, Alchemy/Infura, Ethers.js/Viem |
| 合约 | Foundry (验证用), Solidity (阅读用) |
| 后端 | Python (async, 类型系统) |
| 前端 | Streamlit / Gradio (MVP 阶段) |
| 部署 | Vercel / Railway / 本地 Docker |

---
*Last updated: 2026-05-18*
