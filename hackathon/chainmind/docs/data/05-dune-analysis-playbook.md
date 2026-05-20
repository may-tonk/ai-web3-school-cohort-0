# 05. Dune 分析 Playbook

第一阶段建议先在 BNB 链上做手动分析，因为已有 BNB token 样本和 Dune 查询方向。

## 分析目标

对一个新 token，优先回答：

```text
谁在买？
谁在卖？
早期买家是否已经撤退？
买盘是否真实扩散？
交易活跃度是否可能是刷量？
早期买家是否来自同一 funder？
是否值得进入人工观察列表？
```

## 常用 Dune 表

BNB 链通常使用：

```sql
blockchain = 'bnb'
```

常用表：

```text
tokens.erc20
tokens.transfers
dex.trades
bnb.creation_traces
prices.hour
prices.minute
```

## Step 1：代币基础信息

目标：

```text
确认 token symbol
确认 decimals
确认合约地址是否被 Dune 收录
```

示例：

```sql
WITH params AS (
    SELECT 0x205f39c39f5fe15d4ef000aeb835de8deb264444 AS token
)

SELECT *
FROM tokens.erc20
WHERE blockchain = 'bnb'
  AND contract_address = (SELECT token FROM params);
```

## Step 2：合约创建信息

目标：

```text
创建时间
deployer 地址
创建交易
是否由 factory 创建
deployer 是否还和其他 token 有关联
```

示例：

```sql
WITH params AS (
    SELECT 0x205f39c39f5fe15d4ef000aeb835de8deb264444 AS token
)

SELECT *
FROM bnb.creation_traces
WHERE address = (SELECT token FROM params)
LIMIT 10;
```

## Step 3：DEX 交易与主要池子

目标：

```text
主要 pool_address
首笔交易时间
交易量
交易者数量
是否集中在单一池子
```

示例：

```sql
WITH params AS (
    SELECT 0x205f39c39f5fe15d4ef000aeb835de8deb264444 AS token
)

SELECT
    project,
    version,
    pool_address,
    COUNT(*) AS trades,
    COUNT(DISTINCT tx_from) AS traders,
    SUM(amount_usd) AS volume_usd,
    MIN(block_time) AS first_trade_time,
    MAX(block_time) AS last_trade_time
FROM dex.trades
WHERE blockchain = 'bnb'
  AND block_time > now() - INTERVAL '30' day
  AND (
      token_bought_address = (SELECT token FROM params)
      OR token_sold_address = (SELECT token FROM params)
  )
GROUP BY 1, 2, 3
ORDER BY volume_usd DESC NULLS LAST;
```

## Step 4：5 分钟买卖盘分析

核心字段：

```text
bucket_5m
trades
unique_traders
buy_trades
sell_trades
buyers
sellers
buy_volume_usd
sell_volume_usd
net_buy_usd
```

判断方式：

```text
unique_traders 增长 + buyers 增长 + net_buy_usd 为正
    → 买盘真实扩散

trades 高但 unique_traders 低
    → 可能刷量或机器人

buyers 很多但 sell_volume_usd 更大
    → 散户可能在接大户卖盘

net_buy_usd 从正转负
    → 卖压开始增强
```

## Step 5：早期买家分析

核心字段：

```text
buyer_rank
buyer
first_buy_time
buy_trades
tokens_bought
buy_usd
current_balance
remaining_ratio
```

判断方式：

```text
早期买家 remaining_ratio 接近 0
    → 可能已经卖出或转走

早期大买家 buy_usd 高但 current_balance 为 0
    → 重点风险信号

前 20 / 50 / 100 买家大量清仓
    → 早期资金可能已经撤退

早期买家仍持有
    → 继续观察是否锁仓、分仓或等待出货
```

注意：

```text
current_balance = -1.4901161193847656e-8
remaining_ratio = -1.49e-16
```

这通常是浮点精度误差，应该当作 0 处理。

## Step 6：资金来源与同实体风险

建议先做低成本版本：

```text
早期买家的第一笔 BNB 来源
买入前 1 天 / 7 天 / 14 天内的资金来源
多个早期买家是否来自同一个 funder
买入前交易次数
买入前钱包首次出现时间
```

风险信号：

```text
同一个 funder 资助多个早期买家
多个新钱包集中买入
早期买家后续集中卖出或转走
```

