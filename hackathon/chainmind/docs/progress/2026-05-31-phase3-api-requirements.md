# 2026-05-31 Phase 3 API 需求清单

本文记录 ChainMind Phase 3 直接接入真实 API 所需的服务、用途和建议环境变量。

## 1. 必需 API

### Dune API

用途：

```text
行为型链上数据：
- 交易活跃度
- 5 分钟买卖盘
- 早期买家
- 早期买家资金来源
```

需要准备：

```text
DUNE_API_KEY
DUNE_QUERY_TOKEN_TRADING_ACTIVITY
DUNE_QUERY_FIVE_MINUTE_FLOW
DUNE_QUERY_EARLY_BUYERS
DUNE_QUERY_EARLY_BUYER_FUNDING
```

当前项目已经支持这些环境变量。

### DexScreener API

用途：

```text
市场快照：
- 主交易池
- 流动性
- 价格
- FDV / market cap
- 5m / 1h / 6h / 24h 交易量
- 买卖笔数
- pairCreatedAt
```

官方文档显示 token pairs / token 查询接口可按 token address 获取池子数据，并有公开 rate limit。  
参考：https://docs.dexscreener.com/api/reference

需要准备：

```text
不需要 API key
```

建议环境变量：

```text
DEXSCREENER_BASE_URL=https://api.dexscreener.com
```

### GoPlus Token Security API

用途：

```text
安全字段：
- honeypot / 是否可卖
- buy tax / sell tax
- owner 权限
- mint / blacklist / proxy 等风险
- holder / LP 相关风险字段
```

官方 Token Security endpoint：

```text
GET https://api.gopluslabs.io/api/v1/token_security/{chain_id}
```

BNB Chain 使用：

```text
chain_id=56
```

参考：https://docs.gopluslabs.io/reference/tokensecurityusingget_1

需要准备：

```text
GoPlus API access token / API key（如果账号或额度要求）
```

建议环境变量：

```text
GOPLUS_BASE_URL=https://api.gopluslabs.io
GOPLUS_API_KEY=
```

如果 GoPlus 当前账号允许无 key 调用，可以先留空测试；但正式使用建议准备 key 或 access token，避免额度和限流不稳定。

### BNB RPC

用途：

```text
只读合约状态补充：
- owner()
- balanceOf()
- totalSupply()
- getPoolStateData()
- buyTaxRate()
- sellTaxRate()
- proxy / implementation 检查辅助
```

需要准备：

```text
一个稳定的 BNB Chain RPC URL
```

建议来源：

```text
ZAN / Ankr / QuickNode / Alchemy / 自有节点 / 其他稳定 RPC 服务
```

建议环境变量：

```text
BNB_RPC_URL=
```

## 2. 可选但推荐 API

### Honeypot.is API

用途：

```text
交叉验证：
- honeypotResult.isHoneypot
- honeypotReason
- simulationSuccess
- buy / sell simulation
```

官方文档显示支持 Ethereum、BNB Smart Chain、Base，并提供：

```text
GET /v2/IsHoneypot
```

参考：https://docs.honeypot.is/ishoneypot

需要准备：

```text
通常不需要 API key
```

建议环境变量：

```text
HONEYPOT_BASE_URL=https://api.honeypot.is
```

### BscScan / Etherscan V2 API

用途：

```text
合约和 holder 补充：
- contract source / ABI
- token holder count
- top holders / holder list
- contract metadata
```

Etherscan V2 文档中 token holder list 使用：

```text
https://api.etherscan.io/v2/api
chainid=56
module=token
action=tokenholderlist
```

注意：官方文档标注 token holder list 是 PRO endpoint，需要 Standard Plan 或以上。  
参考：https://docs.etherscan.io/api-reference/endpoint/tokenholderlist

需要准备：

```text
ETHERSCAN_API_KEY 或 BSCSAN_API_KEY
```

建议环境变量：

```text
ETHERSCAN_API_KEY=
ETHERSCAN_BASE_URL=https://api.etherscan.io/v2/api
ETHERSCAN_CHAIN_ID=56
```

如果暂时没有付费计划，holder 集中度可以先用 GoPlus / DexScreener / Dune / RPC fallback。

## 3. 最小可用组合

如果要最快开始接真实 API，建议先准备：

```text
DUNE_API_KEY
DUNE_QUERY_TOKEN_TRADING_ACTIVITY
DUNE_QUERY_FIVE_MINUTE_FLOW
DUNE_QUERY_EARLY_BUYERS
DUNE_QUERY_EARLY_BUYER_FUNDING
BNB_RPC_URL
GOPLUS_API_KEY（如果需要）
```

DexScreener 和 Honeypot.is 可以先不准备 key。

## 4. 建议 .env 结构

```text
DUNE_API_KEY=
DUNE_QUERY_TOKEN_TRADING_ACTIVITY=
DUNE_QUERY_FIVE_MINUTE_FLOW=
DUNE_QUERY_EARLY_BUYERS=
DUNE_QUERY_EARLY_BUYER_FUNDING=

DEXSCREENER_BASE_URL=https://api.dexscreener.com

GOPLUS_BASE_URL=https://api.gopluslabs.io
GOPLUS_API_KEY=

HONEYPOT_BASE_URL=https://api.honeypot.is

BNB_RPC_URL=

ETHERSCAN_API_KEY=
ETHERSCAN_BASE_URL=https://api.etherscan.io/v2/api
ETHERSCAN_CHAIN_ID=56
```

## 5. 接入优先级

建议实现顺序：

```text
1. DexScreener market client
2. GoPlus token security client
3. BNB RPC readonly client
4. Honeypot.is cross-check client
5. Etherscan / BscScan holder and contract metadata client
```

第一版先保证 market + security 可以进入 `TokenSnapshot`，再考虑 holder 集中度和合约源码细节。
