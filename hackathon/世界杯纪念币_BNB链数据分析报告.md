# 世界杯纪念币 BNB 链数据分析报告

> 分析对象：`0xf500d904b07ac6214be407b69fe817a82eac7777`  
> 链：BNB Smart Chain  
> 生成时间：2026-05-31  
> 说明：本文基于公开链上数据、BscScan、DexScreener 以及只读 RPC 调用整理，不构成投资建议。

## 1. 背景

本次分析对象是 BNB 链上的 BEP-20 代币：

```text
0xf500d904b07ac6214be407b69fe817a82eac7777
```

BscScan 显示该代币名称为：

```text
世界杯纪念币
```

该项目同时关联了一个 NFT / Vault / 分红玩法，前一次检查中定位到相关合约：

```text
0x1122fe4854C7847925F33Cf91bD1081F203e59B5
```

本报告先重点分析代币本身，包括交易池、持有人分布、合约结构、税费状态和主要风险。

## 2. 分析问题

本次主要回答以下问题：

1. 这个代币当前的基础链上状态是什么？
2. 市场交易是否活跃？
3. 流动性是否充足？
4. 持仓是否集中？
5. 合约权限和税费机制是否存在风险？
6. 如果要参与这个项目，应该重点注意什么？

## 3. 数据来源

本次使用的数据来源包括：

- BscScan Token 页面
- BscScan 合约源码页面
- BscScan Token Holders 页面
- BscScan Token Transfers 页面
- DexScreener 公开 API
- BNB Chain 公开 RPC 只读调用

主要链接：

- BscScan Token：https://bscscan.com/token/0xf500d904b07ac6214be407b69fe817a82eac7777
- BscScan 合约：https://bscscan.com/address/0xf500d904b07ac6214be407b69fe817a82eac7777
- DexScreener 交易池：https://dexscreener.com/bsc/0xebb457931162c638170a44fd5bb4f24a457e2f13

## 4. 基础信息

| 项目 | 数据 |
| --- | --- |
| Token 名称 | 世界杯纪念币 |
| Token 符号 | 世界杯纪念币 |
| 合约地址 | `0xf500d904b07ac6214be407b69fe817a82eac7777` |
| 链 | BNB Smart Chain |
| 标准 | BEP-20 |
| 小数位 | 18 |
| 最大供应量 | 1,000,000,000 |
| 当前总供应量 | 1,000,000,000 |
| BscScan Reputation | Unknown |
| 源码状态 | Source Code Verified, Minimal Proxy |
| 实现合约 | `0x024f18294970b5c76c0691b87f138a0317156422` |
| 合约名称 | `FlapTaxTokenV3` |

### 初步判断

这是一个已验证源码的代理代币合约，但不是普通 ERC-20。它使用 `FlapTaxTokenV3`，包含买卖税、池子状态、税费处理器、分红合约等机制。

源码验证只能说明链上字节码和提交源码匹配，不代表合约安全。

## 5. 市场交易数据

DexScreener 当前识别到主要交易池：

```text
0xebb457931162c638170a44fd5bb4f24a457e2f13
```

交易对：

```text
世界杯纪念币 / WBNB
```

DEX：

```text
PancakeSwap V2
```

### 交易池指标

| 指标 | 数据 |
| --- | --- |
| 当前价格 | 约 0.00008490 美元 |
| WBNB 计价 | 0.0000001165 WBNB |
| 流动性 | 约 28,431 美元 |
| 池中代币数量 | 约 167,425,340 枚 |
| 池中 WBNB 数量 | 约 19.5153 WBNB |
| FDV | 约 82,897 美元 |
| Market Cap | 约 82,897 美元 |
| 池子创建时间 | 2026-05-29 12:57:54 UTC |

### 交易活跃度

| 周期 | 买入笔数 | 卖出笔数 | 成交量 | 价格变化 |
| --- | ---: | ---: | ---: | ---: |
| 5 分钟 | 0 | 1 | 约 1.22 美元 | -0.99% |
| 1 小时 | 15 | 8 | 约 458.50 美元 | -3.62% |
| 6 小时 | 117 | 57 | 约 8,279.31 美元 | +19.67% |
| 24 小时 | 589 | 225 | 约 38,214.63 美元 | +2.58% |

### 市场解读

从 24 小时数据看，交易还算活跃，买入笔数明显多于卖出笔数。但从流动性看，池子只有约 2.8 万美元，仍属于小池子。

这意味着：

- 稍大金额买卖就可能产生明显滑点。
- 少数大户卖出可能明显影响价格。
- FDV 和流动性规模都偏小，价格稳定性较弱。

## 6. 持有人分析

BscScan Token 页面显示：

```text
Holders: 2,523
```

Token Transfers 页面显示：

```text
累计转账记录约 2,746 笔
```

### 持仓集中度

BscScan 持有人页显示：

| 指标 | 数据 |
| --- | --- |
| Top 5 持仓占比 | 33.84% |
| Top 10 持仓占比 | 39.24% |
| 至少持有 1% 总供应的地址数 | 9 个 |
| 持有超过 100,000 枚的地址占持有人比例 | 10.78% |
| 这些大额地址持有供应量 | 99.57% |
| 持有不超过 10 枚的地址占比 | 77.45% |

### Top 持仓地址

| 排名 | 地址 / 标签 | 数量 | 占比 |
| --- | --- | ---: | ---: |
| 1 | PancakeSwap V2 池子 `0xebb457...2F13` | 167,425,340.5137 | 16.7425% |
| 2 | `0x780269...F00C` | 119,000,000 | 11.9000% |
| 3 | 销毁地址 `0x000...dEaD` | 23,674,408.6769 | 2.3674% |
| 4 | `0x88cA1974...f643` | 14,749,590.7519 | 1.4750% |
| 5 | `0xa9B3c651...34DC` | 13,603,717.2130 | 1.3604% |

### 持仓结构解读

这个持仓结构有几个明显特征：

1. 流动性池是第一大持有人，占约 16.74%。
2. 第二大地址单独持有 11.9%，这是一个需要重点观察的地址。
3. 销毁地址只占约 2.37%，销毁比例不算特别高。
4. Top 10 占比约 39.24%，集中度偏高。
5. 大量地址余额极小，77.45% 的地址持有不超过 10 枚，可能包含空投、灰尘地址、测试地址或分散地址。

## 7. 合约结构分析

该 Token 合约不是普通 ERC-20，而是 `FlapTaxTokenV3`。

从 ABI 和源码可以看到，它包含以下关键函数或字段：

- `owner()`
- `buyTaxRate()`
- `sellTaxRate()`
- `getPoolStateData()`
- `mainPool()`
- `taxProcessor()`
- `dividendContract()`
- `startMigration()`
- `finalizeMigration()`
- `permit()`
- `transferOwnership()`
- `renounceOwnership()`

### 当前只读状态

通过 BNB Chain 公开 RPC 读取到：

| 字段 | 当前值 |
| --- | --- |
| owner | `0x0000000000000000000000000000000000000000` |
| mainPool | `0xebb457931162c638170a44fd5bb4f24a457e2f13` |
| dividendContract | `0x7041c1c2f6a579313c926336f9a4f3a713e33e61` |
| taxProcessor | `0xb8170a51c0a539c36aa6d90c264999f292ba3409` |
| quoteToken | `0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c` |
| buyTaxRate | 400 |
| sellTaxRate | 400 |
| state | 2 |

`buyTaxRate` 和 `sellTaxRate` 使用 basis points，也就是万分比：

```text
400 / 10000 = 4%
```

也就是说，当前买卖税率约为：

```text
买入税：4%
卖出税：4%
```

`quoteToken` 是 WBNB：

```text
0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c
```

### 池子状态数据

`getPoolStateData()` 返回：

| 字段 | 当前值 |
| --- | --- |
| currentState | 2 |
| currentBuyTaxRate | 400 |
| currentSellTaxRate | 400 |
| currentLiquidationThreshold | 400,000 枚 Token |
| currentTaxExpirationTime | 2126-05-05 12:57:54 UTC |
| currentAntiFarmerExpirationTime | 2026-06-01 12:57:54 UTC |

### 合约解读

积极因素：

- owner 已经是零地址，说明常规 `onlyOwner` 权限大概率已经放弃。
- 主交易池和 DexScreener 识别到的 PancakeSwap V2 池一致。
- 当前税率可以读到，是 4% / 4%，不是隐藏税率。

风险因素：

- 这是复杂税费型代币，不是简单 ERC-20。
- 税费处理依赖 `taxProcessor`。
- 分红记录依赖 `dividendContract`。
- `taxExpirationTime` 显示到 2126 年，意味着税费机制可能长期存在，而不是短期启动税。
- 合约使用代理结构，普通用户理解成本更高。

## 8. NFT / 分红玩法风险

前一次检查中，相关 NFT / Vault 合约为：

```text
0x1122fe4854C7847925F33Cf91bD1081F203e59B5
```

该玩法更像：

```text
用 Token 铸造 NFT
Token 被转入合约后销毁
NFT 持有人领取 BNB 分红
NFT 可以尝试卖回 Vault
```

需要重点注意：

- 这不是传统意义上的“质押后随时取回本金”。
- 如果 Token 被销毁换成 NFT，你持有的是 NFT 权益，而不是原 Token 本金。
- NFT 卖回依赖 Vault 地板池是否有足够 BNB。
- 如果相关 Vault 被暂停，领取或卖回可能受影响。
- 如果你授权 NFT `setApprovalForAll`，要在操作后及时撤销。

## 9. 风险评估

### 1. 市场风险：高

池子流动性约 2.8 万美元，FDV 约 8.3 万美元，属于小盘新币。价格容易被单笔交易影响。

### 2. 持仓风险：中高

Top 10 地址持有约 39.24%，第二大地址单独持有 11.9%。如果大地址卖出，会对价格造成较大压力。

### 3. 合约风险：中

owner 已归零是积极信号，但合约本身是复杂税费型结构，包含 `taxProcessor`、`dividendContract`、长期税费状态等，不能按普通 ERC-20 判断。

### 4. 玩法风险：高

NFT / Vault 玩法涉及 Token 销毁、NFT 权益、BNB 分红和地板池卖回。它不是低风险 staking，本质更像“用 Token 换一个可分红 / 可卖回的 NFT 权益凭证”。

### 5. 信息风险：高

BscScan Reputation 仍为 Unknown，Token 信息未完善。项目公开信息、审计信息、团队信息仍需要进一步确认。

## 10. 关键发现

1. 该代币是真实存在的 BNB 链 BEP-20，源码已验证，但使用 Minimal Proxy。
2. 主要交易池是 PancakeSwap V2，池子地址为 `0xebb457...2F13`。
3. 当前流动性约 28,431 美元，不算深。
4. 24 小时成交量约 38,214 美元，短期交易活跃。
5. 持有人约 2,523，累计转账约 2,746 笔。
6. Top 10 持仓约 39.24%，集中度偏高。
7. 当前买卖税均为 4%。
8. owner 为零地址，常规 owner 权限已放弃。
9. 税费机制显示可能长期存在，taxExpirationTime 到 2126 年。
10. NFT / Vault 玩法不应简单理解成“安全质押”，需要单独做交互风险控制。

## 11. 建议

如果只是做数据分析：

- 继续追踪 24 小时买卖笔数变化。
- 重点观察第二大地址 `0x780269ec703937b6ae8aa3b1d102697f8b30f00c` 是否转出或卖出。
- 观察 PancakeSwap 池子 WBNB 数量是否持续增加或减少。
- 观察销毁地址占比是否持续上升。
- 观察 NFT / Vault 合约 BNB 余额是否足以支撑卖回。

如果准备参与：

- 不建议使用主钱包。
- 不建议大额参与。
- 不要无限授权。
- 不要长期保留 `setApprovalForAll`。
- 操作后使用 BscScan Token Approval Checker 或 Revoke.cash 撤销授权。
- 把 NFT / Vault 当作高风险玩法，而不是稳定收益产品。

## 12. 后续可以继续做的分析

下一步可以继续做三类更深入分析：

1. 大户行为追踪
   - 追踪 Top 20 地址近期是否买入、卖出、分散或归集。

2. 交易行为分析
   - 统计买卖频率、平均买入金额、平均卖出金额、短线地址比例。

3. NFT / Vault 专项分析
   - 统计 NFT 铸造数量、卖回数量、分红池余额、地板池余额、用户领取情况。

## 13. 总结

这个代币目前具备一定交易热度和社区参与痕迹，但它仍是一个新小盘、高波动、高信息不确定性的项目。

从正面看：

- 源码已验证。
- owner 已归零。
- 当前税率可读。
- 交易池和转账数据真实存在。

从风险看：

- 流动性不深。
- Top 持仓集中。
- 合约机制复杂。
- 税费长期存在。
- NFT / Vault 玩法存在资金池和授权风险。

综合判断：

```text
适合观察和小额测试，不适合主钱包和大额重仓。
```

