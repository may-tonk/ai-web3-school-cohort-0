-- ChainMind / BNB / Five-minute buy-sell flow
--
-- Purpose:
--   Aggregate token trading behavior into five-minute buckets. This is the
--   main query for spotting real buyer expansion, sell pressure, and possible
--   wash trading.
--
-- Phase 2 fields supported:
--   - trades
--   - unique_traders
--   - trades_per_unique_trader
--   - buyers
--   - sellers
--   - buy_volume_usd
--   - sell_volume_usd
--   - net_buy_usd
--
-- Usage:
--   Create a Dune Text parameter named token_address.
--   Example token_address: 0x205f39c39f5fe15d4ef000aeb835de8deb264444

WITH params AS (
    SELECT
        from_hex(substr('{{token_address}}', 3)) AS token,
        NOW() - INTERVAL '24' HOUR AS start_time
),
token_trades AS (
    SELECT
        date_add(
            'minute',
            - (minute(block_time) % 5),
            date_trunc('minute', block_time)
        ) AS bucket_5m,
        tx_hash,
        tx_from,
        amount_usd,
        CASE
            WHEN token_bought_address = (SELECT token FROM params) THEN 'buy'
            WHEN token_sold_address = (SELECT token FROM params) THEN 'sell'
            ELSE 'other'
        END AS side
    FROM dex.trades
    WHERE blockchain = 'bnb'
      AND block_time >= (SELECT start_time FROM params)
      AND (
          token_bought_address = (SELECT token FROM params)
          OR token_sold_address = (SELECT token FROM params)
      )
)
SELECT
    bucket_5m,
    COUNT(*) AS trades,
    COUNT(DISTINCT tx_from) AS unique_traders,
    CAST(COUNT(*) AS DOUBLE) / NULLIF(COUNT(DISTINCT tx_from), 0) AS trades_per_unique_trader,
    SUM(CASE WHEN side = 'buy' THEN 1 ELSE 0 END) AS buy_trades,
    SUM(CASE WHEN side = 'sell' THEN 1 ELSE 0 END) AS sell_trades,
    COUNT(DISTINCT CASE WHEN side = 'buy' THEN tx_from END) AS buyers,
    COUNT(DISTINCT CASE WHEN side = 'sell' THEN tx_from END) AS sellers,
    SUM(CASE WHEN side = 'buy' THEN amount_usd ELSE 0 END) AS buy_volume_usd,
    SUM(CASE WHEN side = 'sell' THEN amount_usd ELSE 0 END) AS sell_volume_usd,
    SUM(CASE WHEN side = 'buy' THEN amount_usd ELSE -amount_usd END) AS net_buy_usd
FROM token_trades
GROUP BY 1
ORDER BY bucket_5m;
