# ChainMind 阶段三交接文档（中文版）

日期：2026-06-01

用途：当切换到新的 Codex 账号、新线程，或者当前对话记忆丢失时，用这份文档快速恢复项目上下文。

## 如何恢复上下文

如果新的助手从零开始接手，请先让它阅读这些文件：

1. `README.md`
2. `docs/roadmap/07-mvp-roadmap.md`
3. `docs/roadmap/08-execution-plan.md`
4. `docs/progress/2026-05-31-phase3-plan.md`
5. `docs/progress/2026-05-31-phase3-api-requirements.md`
6. `docs/progress/2026-06-01-phase3-real-token-batch-1.md`
7. `docs/progress/2026-06-01-phase3-handoff.md`
8. `docs/progress/2026-06-01-phase3-handoff-zh.md`

然后运行：

```bash
python -m pytest
python scripts\smoke_test_apis.py
```

目前最新测试状态预期为：

```text
64 passed
```

## 当前阶段状态

阶段三 v1 已完成。

当前阶段三的定义：

```text
阶段三 = 实时 Quick Screen + Dune 深度分析 + 安全 API 接入 + 实体聚类 v0.1 + 真实样本校准
```

项目现在有两种分析模式：

1. `Quick Screen`：低延迟初筛，不依赖 Dune。
2. `Dune Deep Analysis`：速度更慢，但能分析钱包、资金流、早期买家和资金来源。

## 主要命令

### API 冒烟测试

```bash
python scripts\smoke_test_apis.py
```

用途：

- 检查已配置 API 是否可用。
- 不打印真实密钥。
- 检查 Dune、DexScreener、GoPlus、Honeypot.is、BNB RPC、Etherscan V2、Nansen、GMGN 的配置状态。

已知行为：

- Etherscan V2 免费套餐不支持 BNB Chain full coverage，所以会返回 `WARN`。
- GMGN 已配置 key，但签名请求逻辑还没有正式实现，所以会返回 `SKIP`。
- Nansen 如果积分耗尽，可能失败或返回警告。

### 实时 Quick Screen

```bash
python scripts\quick_screen_token.py <bnb_token_address>
```

用途：

- 不依赖 Dune，快速筛查 BNB 链代币。
- 使用 DexScreener、GoPlus、Honeypot.is、BNB RPC。
- 输出 `PASS`、`WATCH` 或 `BLOCK`。

示例：

```bash
python scripts\quick_screen_token.py 0xf500d904b07ac6214be407b69fe817a82eac7777
```

### Dune 深度分析

```bash
python scripts\analyze_dune_token.py <bnb_token_address>
```

用途：

- 完整深度分析。
- 默认使用本地 Dune 缓存。
- 会融合 DexScreener、GoPlus、Honeypot.is、Nansen、BNB RPC 数据。

刷新 Dune 缓存：

```bash
python scripts\analyze_dune_token.py <bnb_token_address> --refresh-cache
```

输出 JSON：

```bash
python scripts\analyze_dune_token.py <bnb_token_address> --json
```

### 批量分析

```bash
python scripts\batch_analyze_tokens.py <token_a> <token_b> <token_c>
```

从文件读取地址：

```bash
python scripts\batch_analyze_tokens.py --file tokens.txt
```

输出 JSON：

```bash
python scripts\batch_analyze_tokens.py --file tokens.txt --json
```

## 环境变量

配置位于 `.env`。

重要提醒：不要在对话、日志、报告里打印真实 API key 或私钥。

主要变量：

```env
DUNE_API_KEY=
DUNE_QUERY_TOKEN_TRADING_ACTIVITY=
DUNE_QUERY_FIVE_MINUTE_FLOW=
DUNE_QUERY_EARLY_BUYERS=
DUNE_QUERY_EARLY_BUYER_FUNDING=

DEXSCREENER_BASE_URL=https://api.dexscreener.com

GOPLUS_BASE_URL=https://api.gopluslabs.io
GOPLUS_ACCESS_TOKEN=

HONEYPOT_BASE_URL=https://api.honeypot.is

BNB_RPC_URL=

ETHERSCAN_BASE_URL=https://api.etherscan.io/v2/api
ETHERSCAN_API_KEY=
ETHERSCAN_CHAIN_ID=56

NANSEN_BASE_URL=https://api.nansen.ai/api/v1
NANSEN_API_KEY=
NANSEN_CHAIN=bnb

GMGN_API_KEY=
GMGN_PRIVATE_KEY_PATH=runtime/keys/gmgn_ed25519_private.pem
GMGN_CHAIN=bsc
```

说明：

- `BNB_RPC_URL` 必须指向 BNB Chain，`eth_chainId` 应返回 `0x38`。
- `GOPLUS_ACCESS_TOKEN` 可以为空，只要 GoPlus 公共接口可用即可。
- Etherscan V2 免费套餐目前不支持 BNB Chain 完整访问能力。
- Nansen 积分可能耗尽，因此 Nansen 数据必须作为可选增强项，不能阻塞主流程。
- GMGN key 已配置，但签名请求逻辑还未实现。

## 已接入主流程的 API

### Quick Screen

已接入：

- DexScreener
- GoPlus
- Honeypot.is
- BNB RPC

未使用：

- Dune
- Nansen
- Etherscan
- GMGN

### Dune Deep Analysis

已接入：

- Dune
- DexScreener
- GoPlus
- Honeypot.is
- Nansen
- BNB RPC

可选或受限：

- Etherscan V2 已配置，但免费套餐对 BNB Chain 用处有限。
- GMGN 已配置，但签名请求逻辑还没有实现。

## 阶段三新增或更新的重要文件

脚本：

- `scripts/smoke_test_apis.py`
- `scripts/quick_screen_token.py`
- `scripts/analyze_dune_token.py`
- `scripts/batch_analyze_tokens.py`

数据客户端：

- `src/chainmind/data/http_json.py`
- `src/chainmind/data/dexscreener_client.py`
- `src/chainmind/data/goplus_client.py`
- `src/chainmind/data/honeypot_client.py`
- `src/chainmind/data/nansen_client.py`
- `src/chainmind/data/bnb_rpc_client.py`
- `src/chainmind/data/query_cache.py`
- `src/chainmind/data/api_mappers.py`
- `src/chainmind/data/chain_ids.py`

编排层：

- `src/chainmind/orchestration/analyze_dune_token.py`
- `src/chainmind/orchestration/quick_screen_token.py`

评分层：

- `src/chainmind/scoring/security.py`
- `src/chainmind/scoring/entity_cluster.py`
- `src/chainmind/scoring/quick_screen.py`

进度文档：

- `docs/progress/2026-05-31-phase3-plan.md`
- `docs/progress/2026-05-31-phase3-api-requirements.md`
- `docs/progress/2026-06-01-phase3-real-token-batch-1.md`
- `docs/progress/2026-06-01-phase3-handoff.md`
- `docs/progress/2026-06-01-phase3-handoff-zh.md`

## 真实样本批次 1

记录文件：

```text
docs/progress/2026-06-01-phase3-real-token-batch-1.md
```

已分析代币：

```text
0xf500d904b07ac6214be407b69fe817a82eac7777
0x90166915b98d24d284c56de3b9f4ed59338f7777
0x3d96b30ba2c08724b70efff1ad16d005db1c7777
0x90507254e9c594e728172b9d217f4ab1a2ee7777
```

样本观察：

- 合约安全层面大多较干净。
- Honeypot.is 对这些样本返回 `false`。
- GoPlus 显示 owner renounced 多数为 true。
- 主要筛选依据来自行为和实体信号：
  - 早期买家退出；
  - 近期卖压；
  - 共同资金来源；
  - 低流动性或低成交量。

## 已知限制

1. Dune 有延迟，而且有时较慢。

   当前把 Dune 当作深度确认层，不把它作为实时筛查层。

2. Nansen 积分可能用完。

   Nansen 应作为可选增强数据源，缺失时不能阻塞分析流程。

3. Etherscan V2 免费套餐不支持 BNB Chain 完整覆盖。

   可以继续保留配置，但阶段三不依赖它。

4. GMGN 签名请求还没有实现。

   GMGN 未来可以作为实时市场、聪明钱、热门币数据源。

5. Quick Screen 可能放过一些 Dune 深度分析会过滤的代币。

   这是预期现象。Quick Screen 主要看实时市场和安全信号，不看早期资金结构。

## 下一步推荐工作

### 选项 A：阶段三检查报告

写一份正式阶段三完成报告。

建议路径：

```text
docs/progress/2026-06-01-phase3-check-report.md
```

建议包含：

- 阶段三完成了什么；
- API 当前状态；
- 脚本和命令；
- 真实样本；
- 已知限制；
- 下一阶段建议。

### 选项 B：阶段三规则校准

继续跑更多基准样本：

- BNB 链主流代币；
- 高流动性代币；
- 新发 meme 代币；
- 明显低质量代币。

目标：

- 检查规则是否过严；
- 校准早期买家退出阈值；
- 校准共同资金来源阈值；
- 调整 Quick Screen 的 `WATCH` / `BLOCK` 阈值。

### 选项 C：GMGN 接入

实现 GMGN 签名请求。

目标：

- 替代一部分 Nansen 的聪明钱角色；
- 增加实时热门代币、聪明钱包、市场信号数据。

### 选项 D：阶段四

根据现有文档，阶段四可以向这些方向推进：

- 钱包 Alpha 与可复制性；
- 完整评分系统；
- AI 解释与报告层。

开始阶段四之前，需要统一路线图命名：

- `docs/roadmap/07-mvp-roadmap.md`：Phase 4 = Wallet Alpha + Copyability。
- `docs/roadmap/08-execution-plan.md`：Stage 4 = 完整评分系统。
- `docs/learning/13-token-analysis-data-analyst-workflow.md`：Phase 4 = AI 解释层。

推荐的实际下一步：

```text
先写阶段三检查报告，然后开始校准，再添加更多产品功能。
```

## 新账号 / 新线程恢复提示词

可以把下面这段直接发给新的 Codex 账号或新对话：

```text
请先阅读 ChainMind 项目的 README.md，以及 docs/progress/2026-06-01-phase3-handoff-zh.md。
然后检查当前代码、测试和 API 配置状态，继续阶段三之后的校准、报告或阶段四准备工作。
注意：不要打印 .env 中的真实 API key、私钥或其他敏感信息。
当前项目目录是 D:\ai-web3-school-cohort-0\hackathon\chainmind。
```
