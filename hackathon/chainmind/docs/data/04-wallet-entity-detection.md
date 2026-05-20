# 04. 钱包分析与同实体识别

## 为什么钱包分析是核心

普通 token 表面数据在很多工具里都能看到。真正有壁垒的是地址行为分析：

- 哪些钱包真的有 alpha。
- 哪些钱包只是曾经赚过钱。
- 哪些钱包不可复制。
- 哪些钱包是机器人、项目方、狙击地址或同一实体分仓。
- 多个钱包同时买入是真共识还是假共识。

## 钱包分层

不要把所有高收益钱包混在一起，建议至少分为：

```text
短线 meme 钱包
早期发现型钱包
可复制型高胜率钱包
狙击型钱包
LP / 做市型钱包
项目方关联钱包
疑似机器人钱包
长期配置钱包
```

meme 场景最值得跟踪的是：

```text
短线 meme 钱包
早期发现型钱包
可复制型高胜率钱包
非项目方关联钱包
非机器人钱包
```

## 同实体识别的核心思想

钱包数量不等于真实人数。一个实体可能控制多个钱包分仓买入，制造“多人共识”的假象。

例如：

```text
13 个钱包同时买入一个 token
```

可能是：

```text
13 个独立交易者形成真实共识
1 个实体控制 13 个钱包批量买入
```

这两种情况对风险判断完全不同。

## Entity Cluster Score

目标不是证明 100% 是同一个人，而是给出概率和证据。

建议公式：

```text
entity_cluster_score =
    temporal_score * 0.25
  + funding_source_score * 0.30
  + nonce_similarity_score * 0.15
  + gas_station_score * 0.15
  + contract_overlap_score * 0.15
```

分级：

```text
0.00 - 0.30：大概率独立
0.30 - 0.60：存在关联，需要观察
0.60 - 0.80：高度疑似同一实体
0.80 - 1.00：强关联实体集群
```

## 五类证据

### Temporal Fingerprinting

判断多个钱包是否在极短时间内执行相似交易。

可计算字段：

```text
wallet_a_buy_time
wallet_b_buy_time
time_diff_seconds
same_block_flag
same_minute_flag
burst_cluster_id
```

风险信号：

```text
多个早期买家在 30 秒内连续买入
多个钱包总是在固定间隔交易
多个钱包在多个 token 上保持类似时间关系
```

### Funding Source Analysis

判断多个钱包是否来自同一个资金来源。

可计算字段：

```text
first_native_token_funder
funding_time
funding_amount
funded_wallet_count
```

风险信号：

```text
同一个 funder 资助多个早期买家
同一个 funder 资助的钱包集中买入同一个 token
这些钱包后续集中卖出或转走
```

### Nonce / Wallet Age

Dune 上不一定方便直接取 nonce，可以先用历史交易数近似。

可计算字段：

```text
buyer_nonce_at_entry
wallet_age_days
tx_count_before_entry
contract_count_before_entry
```

风险信号：

```text
多个早期买家都是新钱包
买入前几乎没有历史交易
新钱包在同一时间段买入
```

### Gas Station Detection

判断多个钱包是否从同一个 gas 资金站获得 gas。

可计算字段：

```text
gas_funder
gas_funding_time
gas_funding_amount
funded_wallet_count
```

风险信号：

```text
同一 gas_funder 在短时间内给多个新钱包转入小额 BNB/ETH
这些钱包随后买入同一个 token
```

### Contract Overlap

判断多个钱包历史交互路径是否高度相似。

可计算字段：

```text
common_contract_count
contract_overlap_ratio
shared_token_count
shared_router_count
```

风险信号：

```text
多个钱包只交互同一批 router、launchpad、meme token 或同一 deployer 创建的 token
```

## 报告表达原则

不要写：

```text
这些钱包一定是同一个人。
```

应该写：

```text
这些早期买家存在较强关联迹象，主要证据是同 funder、买入时间集中、新钱包比例高。
```

