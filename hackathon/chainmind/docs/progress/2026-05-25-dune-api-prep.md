# 2026-05-25 Dune API 前置准备

本文记录接入 Dune API 前需要完成的配置和明日操作清单。

## 1. 今天已准备的内容

已新增本地环境变量文件：

```text
.env
```

已新增可提交的模板文件：

```text
.env.example
```

已更新 `.gitignore`，避免真实密钥进入 git：

```text
.env
.env.local
.env.*.local
```

已在 `config/app.yaml` 中预留 Dune 配置：

```yaml
integrations:
  dune:
    enabled: false
    api_key_env: DUNE_API_KEY
    query_ids:
      token_trading_activity_env: DUNE_QUERY_TOKEN_TRADING_ACTIVITY
      five_minute_flow_env: DUNE_QUERY_FIVE_MINUTE_FLOW
      early_buyers_env: DUNE_QUERY_EARLY_BUYERS
      early_buyer_funding_env: DUNE_QUERY_EARLY_BUYER_FUNDING
```

当前还没有接入 Dune API client，也没有执行远程查询。

## 2. 明天需要你准备的内容

### 2.1 获取 Dune API Key

拿到 Dune API Key 后，只写入本地 `.env`：

```text
DUNE_API_KEY=你的真实 key
```

不要把真实 key 发到聊天里，也不要写进 `.env.example` 或 `config/app.yaml`。

### 2.2 在 Dune 创建 4 个 Query

需要在 Dune 中分别创建并保存 4 个查询：

```text
token_trading_activity
five_minute_flow
early_buyers
early_buyer_funding
```

对应本地 SQL 文件：

```text
src/chainmind/queries/dune/bnb/token_trading_activity.sql
src/chainmind/queries/dune/bnb/five_minute_flow.sql
src/chainmind/queries/dune/bnb/early_buyers.sql
src/chainmind/queries/dune/bnb/early_buyer_funding.sql
```

保存后记录 Dune 的 query id。

### 2.3 把 query id 写入本地 `.env`

示例：

```text
DUNE_QUERY_TOKEN_TRADING_ACTIVITY=1234567
DUNE_QUERY_FIVE_MINUTE_FLOW=1234568
DUNE_QUERY_EARLY_BUYERS=1234569
DUNE_QUERY_EARLY_BUYER_FUNDING=1234570
```

## 3. Query 参数约定

后续自动化希望统一传入：

```text
token_address
```

因此明天在 Dune 创建 Query 时，需要把 SQL 中写死的 token 地址改成 Dune 参数。

当前本地 SQL 顶部类似：

```sql
WITH params AS (
    SELECT
        from_hex(substr('{{token_address}}', 3)) AS token
)
```

在 Dune 中将参数类型设置为 `Text`。目标是让 API 可以传入：

```json
{
  "token_address": "0x..."
}
```

如果 Dune 参数语法确认可用，可以统一使用类似：

```sql
WITH params AS (
    SELECT
        from_hex(substr('{{token_address}}', 3)) AS token
)
```

参数默认值填写带 `0x` 前缀的完整地址，例如：

```text
0xc911e8f97a02b7469294cb89440a6c616abd7777
```

SQL 中 `from_hex(substr('{{token_address}}', 3))` 会去掉 `0x` 并转换为 Dune 地址字段使用的 varbinary。第一次创建 Query 时优先确认 SQL 能在 Dune 页面跑通。

## 4. 明天验证顺序

建议顺序：

```text
1. 先创建 five_minute_flow query。
2. 用一个真实 BNB token 地址手动运行。
3. 确认 rows 能返回。
4. 再创建 early_buyers query。
5. 确认 remaining_ratio 字段可用。
6. 再创建 early_buyer_funding query。
7. 确认 funder / funded_selected_early_buyers 可用。
8. 最后创建 token_trading_activity query。
```

原因：

```text
five_minute_flow 是 Token Risk v0.1 最核心、最容易验证的行为数据。
early_buyers 和 funding 更容易遇到字段口径问题，放在后面逐步确认。
```

## 5. 明天给 Codex 的信息

明天你只需要提供：

```text
1. 3 个 BNB token 地址
2. 4 个 Dune query id
3. 是否已经把 DUNE_API_KEY 写入本地 .env
```

不需要把真实 API Key 发到聊天中。

## 6. 接下来要实现的代码

拿到 API Key 和 query id 后，下一步再实现：

```text
src/chainmind/data/dune_client.py
src/chainmind/data/dune_mappers.py
scripts/analyze_dune_token.py
```

目标：

```text
python scripts/analyze_dune_token.py 0xTOKEN --json
```

预期流程：

```text
Dune API 执行 query
-> 拉取 result rows
-> 映射为 TokenSnapshot
-> 执行 analyze_token
-> 输出 risk_score / risk_evidence / data_quality
```

Hermes 暂时不接入。先把本地自动化跑通，再让 Hermes 调用本地脚本或服务。
