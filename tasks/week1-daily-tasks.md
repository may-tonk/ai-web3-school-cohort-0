# Week 1 每日任务清单

> 日期：2026-05-18 — 2026-05-24
> 主题：AI and Web3 foundations — 基础对齐 + 数据连接
> 目标：Agent 能查询链上数据并返回结果，有最小可用版本。

---

## 一周总观

| 天 | 日期 | 主题 | 产出物 | 时长 |
|---|---|---|---|---|
| D1 | 5/18 (今日) | 启动 + LLM Tool Use 基础 | `daily/2026-05-18.md` + Agent 骨架 | 6h |
| D2 | 5/19 | Agent 架构深入 | `chainmind/core/agent.py` 能跑通 | 6h |
| D3 | 5/20 | Dune API 接入 | `chainmind/core/data_source.py` | 6h |
| D4 | 5/21 | 自然语言 → SQL → 数据摘要 | experiments 脚本 | 6h |
| D5 | 5/22 | Web3 基础接入（钱包+测试网） | 测试网交易记录 | 6h |
| D6 | 5/23 | 合约调用基础 + 整合 | `experiments/week1-wallet/` | 6h |
| D7 | 5/24 (周日) | 周复盘 + 打卡 | `experiments/week1-dune-agent/` 完整版 | 4h |

---

## D1 | 5/18 (今日) — 启动 + LLM Tool Use 基础

### 上午 3h — 开发
- [ ] 创建 `chainmind/core/agent.py` 骨架（类级结构，支持接收指令、调用工具、返回结果）
- [ ] 实现最小可运行的 ReAct 循环（思考 → 行动 → 观察）
- [ ] git commit: `feat: init chainmind agent skeleton`

### 下午 2h — 学习
- [ ] 阅读 Handbook **LLM 章节** 和 **Tool Use 章节**
- [ ] 重点：Function Calling vs ReAct vs JSON Mode 的差异和适用场景
- [ ] 笔记写入 `daily/2026-05-18.md`

### 晚上 1h — 整理
- [ ] 梳理 Agent 架构图（用文本或简单图）
- [ ] 完成 `daily/2026-05-18.md` （包含学习心得 + 今日产出 + 明日计划）
- [ ] 如果有 Handbook 反馈 → `handbook-feedback/`
- [ ] git commit: `docs: day 1 learning notes`

---

## D2 | 5/19 — Agent 架构深入

### 上午 3h — 开发
- [ ] 实现多工具支持（Dune 查询、日历、计算等 mock 工具）
- [ ] 添加错误处理和重试机制
- [ ] git commit: `feat: multi-tool support with retry`

### 下午 2h — 学习
- [ ] 阅读 Handbook **Agent 架构** 相关章节
- [ ] 重点：Memory 设计、Planning 策略、错误恢复
- [ ] 笔记写入 `daily/2026-05-19.md`

### 晚上 1h — 整理
- [ ] 运行第一个端到端测试："查询最近一周 Uniswap 交易量"
- [ ] 记录测试结果和待解决问题
- [ ] git commit: `test: first end-to-end agent test`

---

## D3 | 5/20 — Dune API 接入

### 上午 3h — 开发
- [ ] 注册 Dune API Key（使用现有账户）
- [ ] 实现 `chainmind/core/data_source.py`，封装 Dune API 调用
- [ ] 支持两种模式：现成 Query ID 调用 + 新增 Query 提交
- [ ] git commit: `feat: dune api integration`

### 下午 2h — 学习
- [ ] 学习 Dune API 文档（重点是程序化调用）
- [ ] 回顾自己以前的 Dune 查询，选出 3 个最适合 Agent 的查询
- [ ] 笔记写入 `daily/2026-05-20.md`

### 晚上 1h — 整理
- [ ] 测试 Dune 连接稳定性（并发、超时、错误格式）
- [ ] 记录测试数据和发现
- [ ] git commit: `test: dune connection stress test`

---

## D4 | 5/21 — 自然语言 → SQL → 数据摘要

### 上午 3h — 开发
- [ ] 实现"自然语言 → SQL" 转换层（用 prompt 或简单模板）
- [ ] 实现数据摘要生成（用 LLM 把原始数据转为人话）
- [ ] git commit: `feat: nl-to-sql and data summarization`

### 下午 2h — 学习
- [ ] 阅读 Handbook **链上数据分析** 或 **Dune 高级查询**
- [ ] 重点：如何让 AI 理解"链上数据的脆弱性"
- [ ] 笔记写入 `daily/2026-05-21.md`

### 晚上 1h — 整理
- [ ] 完成第一个完整流程测试：用自然语言查询 → 获取数据 → 生成摘要
- [ ] 记录结果到 `experiments/week1-nl-to-sql/`
- [ ] git commit: `experiments: week1 nl-to-sql pipeline`

---

## D5 | 5/22 — Web3 基础接入（钱包+测试网）

### 上午 3h — 开发
- [ ] 准备测试钱包（MetaMask），记录地址
- [ ] 完成测试网（Sepolia / Holesky）第一笔交易
- [ ] 学习如何用 Etherscan API 获取交易详情
- [ ] git commit: `feat: testnet wallet setup`

### 下午 2h — 学习
- [ ] 阅读 Handbook **钱包、签名与交易**
- [ ] 重点：如何在 Agent 中安全地与钱包交互（不暴露私钥）
- [ ] 笔记写入 `daily/2026-05-22.md`

### 晚上 1h — 整理
- [ ] 整理测试网交易记录（地址、交易 hash、gas 花费）
- [ ] 封装一个简单的 RPC 调用工具（查余额、查交易）
- [ ] git commit: `feat: basic rpc tooling`

---

## D6 | 5/23 — 合约调用基础 + 整合

### 上午 3h — 开发
- [ ] 学习 web3.py / ethers.js 合约调用基础
- [ ] 实现一个简单的合约调用工具（例如查询 Uniswap Factory 中某个 token pair）
- [ ] 把合约调用整合到 Agent 工具集
- [ ] git commit: `feat: contract call tool integration`

### 下午 2h — 学习
- [ ] 阅读 Handbook **智能合约基础** 或 **权限与安全**
- [ ] 重点：Agent 的权限边界（什么可以自动执行，什么必须人工确认）
- [ ] 笔记写入 `daily/2026-05-23.md`

### 晚上 1h — 整理
- [ ] 运行综合测试：Agent 能同时查询 Dune 数据和链上状态
- [ ] 整理 `experiments/week1-wallet/`
- [ ] git commit: `test: week1 integration test`

---

## D7 | 5/24 (周日) — 周复盘 + 打卡

### 上午 2h — 开发
- [ ] 整合 Week 1 所有代码，确保 `experiments/week1-dune-agent/` 完整可运行
- [ ] 编写 Week 1 README（怎么跑、依赖、演示流程）
- [ ] git commit: `feat: week1 complete dune agent`

### 下午 1h — 学习
- [ ] 回顾本周 Handbook 笔记，补充遗漏
- [ ] 预览 Week 2 课程内容，做好心理准备
- [ ] 笔记写入 `daily/2026-05-24.md`

### 晚上 1h — 整理
- [ ] 撰写 Week 1 学习总结
- [ ] 生成本周打卡草稿（用 WCB API 提交证据）
- [ ] git commit: `docs: week1 summary and reflection`

---

## 周末产出物检查清单

- [ ] `chainmind/core/agent.py` — 能跑通的 Agent 主引擎
- [ ] `chainmind/core/data_source.py` — Dune API 调用封装
- [ ] `experiments/week1-dune-agent/` — 完整可运行的演示脚本
- [ ] `experiments/week1-wallet/` — 钱包+测试网记录
- [ ] `daily/` — 7 天学习笔记
- [ ] `至少 7 个 git commit`
- [ ] 本周打卡已提交（或草稿已准备）

---

## 紧急联系

- 如果任何一天落后 > 4h，立即通知 Agent 调整后续计划
- 如果遇到技术卡住 > 2h，先记录问题 → 跳过 → 晚上回头解决
- 每天晚上 23:00 前必须 git push
