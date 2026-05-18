# AI × Web3 School Learning Plan

> 学员画像：Web3 开发熟练工程师 / Dune 高级用户 / 6h 每天
> 核心目标：**B — 产出可展示的个人项目，建立难以复制的个人品牌**
> 核心竞争力：**A — Dune 链上数据能力**
> 执行风格：**A — 每日明确任务清单，严格按计划执行**
> 项目主线：**构建能理解链上数据的 DeFi 研究 Agent**

---

## 🎯 项目定义：ChainMind — DeFi 智能研究助手

### 一句话描述
一个能查询链上数据、解读 DeFi 协议状态、生成可验证分析报告的 AI Agent。

### 为什么难以复制
- **数据壁垒**：大多数学员不懂 Dune，不懂链上数据的"脆弱性"（滚回、滞后、粒度问题）
- **领域壁垒**：懂 AI 的人不懂 DeFi 机制，懂 DeFi 的人不会搭 Agent 框架
- **可验证壁垒**：大多数"DeFi Agent" 是聊天机器人，你的是"数据驱动 + 可追溯报告"

### 核心能力
1. 自然语言查询链上数据（取代手写 SQL）
2. 实时监控并解读 DeFi 异常事件
3. 生成带数据来源引用的研究报告
4. 支持多协议横向对比分析

---

## 📁 仓库产出结构

以下是 8 周后你的 repo 应该包含的内容，也是每天的指北：

```
ai-web3-school-cohort-0/
├── README.md                    # 项目介绍 + Demo 链接
├── profile.md                   # 学员画像
├── learning-plan.md             # 本文件
├── chainmind/                   # 项目主目录
│   ├── README.md                # 项目设计文档
│   ├── core/
│   │   ├── agent.py           # Agent 主引擎
│   │   ├── data_source.py     # 数据接入层
│   │   └── analyzer.py        # 分析模块
│   ├── protocols/
│   │   ├── uniswap_v3.py    # 协议特定分析器
│   │   ├── aave_v3.py
│   │   └── base.py            # 协议接口基类
│   ├── reports/
│   │   └── template.md        # 报告生成模板
│   └── tests/
│       └── test_core.py       # 测试
├── experiments/                 # 实验记录
├── submissions/
│   ├── research/
│   └── demo-video.md
├── daily/                       # 每日学习笔记
├── handbook-feedback/           # 手册反馈
└── templates/
    ├── daily-note.md
    └── task-note.md
```

---

## 📅 时间线：8 周精确路径

### Phase 1：基础对齐 — 第 1-2 周
>目标：Agent 能查询链上数据并返回结果，有最小可用版本。

**Week 1: 连接数据**
- 学习 LLM 的 Tool Use 架构
- 搭建 Dune API 调用层
- 实现：自然语言 → SQL → 数据 → 文本摘要
- 交付：`experiments/week1-dune-agent/` 能跑通的脚本

**Week 2: 解读数据**
- 学习 AI Agent 的 ReAct / Planning 架构
- 让 Agent 不仅仅"查到数据"，还能"解释数据意义"
- 交付：`chainmind/core/` 基础架构 + 第一个分析模块

### Phase 2: 双轨深度 — 第 3-5 周
>目标：多协议支持 + AI+DeFi 研究深度报告。

**Week 3: 多协议支持**
- 实现 Uniswap V3 分析器（流动性、价格区间、手续费）
- 实现 Aave V3 分析器（清算、借贷率、风险参数）
- 交付：`chainmind/protocols/` 协议模块

**Week 4: 研究输出**
- 用自己的 Agent 生成第一份 DeFi 协议分析报告
- 产出研究文章 / Twitter 线程
- 交付：`submissions/research/report-1.md`

**Week 5: 产品化**
- 添加实时监控能力（定时任务 / 事件触发）
- 添加报告生成模板（Markdown / PDF 输出）
- 交付：可定时运行的完整 Agent

### Phase 3: 整合交付 — 第 6-8 周
>目标：完整项目 + 开源发布准备。

**Week 6: 工程化**
- 前端界面（Streamlit / Gradio 快速搭建）
- 错误处理、重试机制、日志
- 交付：可交互的 Web 界面

**Week 7: 研究深度**
- 选择一个 DeFi 细分方向做深度研究（AI 清算预测 / MEV 分析 / 治理建议）
- 用 Agent 辅助生成研究报告
- 交付：深度研究报告

**Week 8: 发布与复盘**
- 开源发布准备（README、License、Demo 视频）
- 撰写项目介绍博客 / Twitter 线程
- 学习总结与复盘
- 交付：完整项目 + 可展示的作品集

---

## ⚡ 每日节奏模板（6 小时）

### 上午 2h — 学习 & 结构
```
任务类型：读 Handbook / 看课程 / 学新架构
产出要求：学习笔记写入 daily/YYYY-MM-DD.md
关键原则：不只是"看完"，要写出"如何应用到 ChainMind 项目中"
```

### 下午 2.5h — 开发 & 实践
```
任务类型：写代码 / 调试 Agent / 测试 Dune 查询
产出要求：至少 1 个 git commit
关键原则：代码可以是粗糙的，但必须能跑通或有明确的待解决问题
```

### 晚上 1.5h — 分析 & 整理
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
2. **48h 落地**：每个新概念学完 48h 内必须有代码 commit
3. **每日交付**：每天结束时 repo 必须比昨天早上更丰富
4. **数据为核**：每个决策、每份报告都必须有链上数据支撑
5. **可复现**：所有分析结果必须注明数据来源和查询时间
6. **安全红线**：私钥不上链、交易不自动执行、测试网优先

---

## 📊 进度跟踪模板

| 周次 | 里程碑 | 状态 | 备注 |
|------|--------|------|------|
| W1 | Dune 查询 Agent 原型 | ⬜ | |
| W2 | 数据解读 + 分析模块 | ⬜ | |
| W3 | 多协议支持 | ⬜ | |
| W4 | 第一份研究报告 | ⬜ | |
| W5 | 实时监控 + 报告生成 | ⬜ | |
| W6 | Web 界面 + 工程化 | ⬜ | |
| W7 | 深度研究 | ⬜ | |
| W8 | 开源发布 + 复盘 | ⬜ | |

---

## 📝 更新日志

| 日期 | 变更 |
|------|------|
| 2026-05-18 | 初始版学习计划 |
| 2026-05-18 | 重写为项目驱动版，明确主线为 ChainMind Agent |

---
*Next review: 每周一更新进度*
