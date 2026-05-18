# Week 1 每日任务清单：连接数据

> 目标：Dune 查询 Agent 原型 — 能用自然语言查询链上数据并返回结果

---

## Day 1 — 启动日（今天）

### 上午 2h
- [ ] 阅读 Handbook “AI 基础 → LLM ” 相关章节
- [ ] 学习 LLM 的 Tool Use 架构（Function Calling / Tools）
- [ ] 学习笔记写入 `daily/2026-05-18.md`

### 下午 2.5h
- [ ] 创建项目目录 `chainmind/` 结构
- [ ] 创建 `chainmind/core/data_source.py` 基础框架
- [ ] 实现第一个函数：调用 Dune API 获取指定 query 结果
- [ ] git commit

### 晚上 1.5h
- [ ] 完成 `daily/2026-05-18.md` 笔记整理
- [ ] 检查 WCB 打卡入口，生成打卡草稿
- [ ] 如果有 Handbook 问题 → 写入 `handbook-feedback/`
- [ ] 推送代码到 GitHub

### 交付物
- `chainmind/core/data_source.py` 能调通 Dune API 的脚本

---

## Day 2 — 自然语言 → SQL

### 上午 2h
- [ ] 学习 Prompt Engineering 中的 "Text-to-SQL" 技术
- [ ] 研究如何让 LLM 生成 Dune SQL 查询
- [ ] 学习笔记写入 daily/

### 下午 2.5h
- [ ] 创建 `chainmind/core/query_builder.py`
- [ ] 实现：LLM 接收自然语言 → 生成 SQL 查询
- [ ] 测试 3 个不同的查询意图（如 TVL、交易量、流动性）
- [ ] git commit

### 晚上 1.5h
- [ ] 整理测试结果，记录成功和失败的查询
- [ ] 完成 daily 笔记
- [ ] 打卡 + 推送

### 交付物
- `chainmind/core/query_builder.py` 能将自然语言转换为 SQL 的模块

---

## Day 3 — 数据解读

### 上午 2h
- [ ] 学习如何让 LLM 解读 Dune 返回的结果
- [ ] 了解"结果摘要" vs "详细解读"的不同策略
- [ ] 学习笔记

### 下午 2.5h
- [ ] 创建 `chainmind/core/analyzer.py`
- [ ] 实现：接收 Dune 数据 → LLM 生成中文分析摘要
- [ ] 测试：用实际的 Uniswap 流动性数据做实验
- [ ] git commit

### 晚上 1.5h
- [ ] 整理分析结果，记录有趣的洞察
- [ ] 完成 daily 笔记
- [ ] 打卡 + 推送

### 交付物
- `chainmind/core/analyzer.py` 能解读数据并生成摘要的模块

---

## Day 4 — 组装 Agent

### 上午 2h
- [ ] 学习 ReAct 架构（Reasoning + Acting）
- [ ] 理解 Agent 如何"思考" → "执行工具" → "观察结果"
- [ ] 学习笔记

### 下午 2.5h
- [ ] 创建 `chainmind/core/agent.py`
- [ ] 将 data_source + query_builder + analyzer 组装成一个 Agent
- [ ] 实现：用户输入 → Agent 查询 → 返回分析 → 记录交互
- [ ] git commit

### 晚上 1.5h
- [ ] 测试完整流程，记录 bug 和待优化点
- [ ] 完成 daily 笔记
- [ ] 打卡 + 推送

### 交付物
- `chainmind/core/agent.py` 完整的 Agent 主引擎

---

## Day 5 — 优化与边界情况

### 上午 2h
- [ ] 学习错误处理：API 限流、查询失败、数据格式变化
- [ ] 学习笔记

### 下午 2.5h
- [ ] 实现错误处理机制（重试、降级、用户提示）
- [ ] 测试各种边界情况（空数据、超时、无效查询）
- [ ] git commit

### 晚上 1.5h
- [ ] 写 Week 1 复盘笔记
- [ ] 完成 daily 笔记
- [ ] 打卡 + 推送

### 交付物
- 稳健的 Agent 原型，能处理常见错误

---

## Day 6 — 测试与文档

### 上午 2h
- [ ] 学习 Python 测试基础（pytest）
- [ ] 学习笔记

### 下午 2.5h
- [ ] 编写 `chainmind/tests/test_core.py`
- [ ] 测试各个模块的核心功能
- [ ] 撰写 `chainmind/README.md` 设计文档
- [ ] git commit

### 晚上 1.5h
- [ ] 运行测试，修复发现的问题
- [ ] 完成 daily 笔记
- [ ] 打卡 + 推送

### 交付物
- 完整的测试 + 项目设计文档

---

## Day 7 — 周复盘

### 上午 2h
- [ ] 复盘本周学习内容，整理知识点
- [ ] 更新 `learning-plan.md` 进度

### 下午 2.5h
- [ ] 给 Agent 添加一个"小惊喜"功能（例如：支持更多协议、图表生成、多轮对话）
- [ ] git commit

### 晚上 1.5h
- [ ] 撰写 Week 1 学习总结
- [ ] 检查所有交付物是否完整
- [ ] 完成 daily 笔记
- [ ] 打卡 + 推送

### 交付物
- Week 1 复盘报告
- 更新后的仓库

---

## ⚠️ 安全红线

- **私钥不上链**：不要在代码中 hardcode 任何密钥、API key、钱包私钥
- **交易不自动执行**：Agent 仅限于查询和分析，不要添加自动交易功能
- **测试网优先**：所有涉及真实链的测试都在测试网进行

---
*Created: 2026-05-18*
