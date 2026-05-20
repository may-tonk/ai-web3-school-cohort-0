# 06. AI 解释与 Hermes 推送

## AI 的位置

AI 应该在规则过滤之后工作。

正确分工：

```text
程序负责计算
规则负责过滤
AI 负责解释
```

AI 不应该直接做：

```text
读取所有原始交易
直接预测涨跌
直接给买入卖出指令
替代规则引擎
替代链上计算
```

AI 更适合做：

```text
把复杂指标解释成人话
总结机会和风险
对候选 token 分层
生成 Telegram 推送内容
生成每日复盘报告
比较多个候选的优先级
```

## AI 输入格式

AI 输入应该是结构化摘要，例如：

```json
{
  "token": "XXX",
  "chain": "bnb",
  "detected_time": "2026-05-20T12:00:00Z",
  "signal": {
    "alpha_wallet_count": 3,
    "copyable_alpha_wallet_count": 2,
    "net_buy_usd_5m": 12000,
    "buyer_growth": "positive"
  },
  "risk": {
    "risk_score": 68,
    "early_buyer_exit_ratio": 0.42,
    "same_funder_cluster_count": 2,
    "wash_trading_suspected": true
  },
  "copyability": {
    "score": 61,
    "reason": "买入后 5-15 分钟仍有成交量，但开池初期拉升较快"
  }
}
```

## AI 输出模板

建议固定输出：

```text
结论等级：B
处理建议：进入观察列表，不建议追高

机会来源：
- 2 个可复制型高胜率地址在 15 分钟内买入
- 当前 buyers 增长快于 sellers
- 5 分钟 net_buy_usd 仍为正

主要风险：
- 早期买家清仓比例偏高
- 有 2 个早期买家来自相同 funder
- sell_volume_usd 正在上升

可复制性：
- 部分信号可复制，但开池早期涨幅过快

后续观察条件：
- 继续监控 buyers、unique_traders、sell_volume_usd、early buyer outflow
- 如果未来 15 分钟 net_buy_usd 转负，降级为 C

不确定性：
- holder 集中度和 LP 风险仍需补充验证
```

## Hermes 推送节奏

建议任务：

```text
每 5 分钟：
扫描新 token / 新交易池 / 异常放量 token

每 15 分钟：
检查重点高胜率地址是否买入新 token

每小时：
汇总候选 token，输出 Top 10 机会和风险

每天：
复盘昨日推送 token 的 15m / 1h / 6h / 24h 表现
```

## 推送分级

```text
A 级：高优先级，需要人工立即查看
B 级：进入观察列表
C 级：风险偏高，仅记录
D 级：疑似内盘 / 刷量 / 出货，默认忽略
```

## Telegram 短消息模板

```text
[B] XXX / BNB
结论：进入观察列表，不建议追高。

机会：2 个可复制高胜率钱包买入，5m 净买入为正。
风险：早期买家清仓 42%，2 个买家疑似同 funder。
观察：若 15m net_buy_usd 转负，降级为 C。
```

