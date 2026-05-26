-- ChainMind / BNB / Token trading activity
--
-- Purpose:
--   Find the main DEX pools, trading volume, trader count, and first/last
--   trade times for one token.
--
-- Phase 2 fields supported:
--   - trades
--   - unique_traders
--   - volume_usd
--   - first_trade_time
--   - project / version level market activity
--
-- Usage:
--   Create a Dune Text parameter named token_address.
--   Example token_address: 0x205f39c39f5fe15d4ef000aeb835de8deb264444

WITH params AS (
    SELECT
        from_hex(substr('{{token_address}}', 3)) AS token,
        NOW() - INTERVAL '30' DAY AS start_time
),
token_trades AS (
    SELECT
        project,
        version,
        block_time,
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
),
pool_summary AS (
    SELECT
        project,
        version,
        COUNT(*) AS trades,
        COUNT(DISTINCT tx_from) AS unique_traders,
        SUM(amount_usd) AS volume_usd,
        SUM(CASE WHEN side = 'buy' THEN amount_usd ELSE 0 END) AS buy_volume_usd,
        SUM(CASE WHEN side = 'sell' THEN amount_usd ELSE 0 END) AS sell_volume_usd,
        MIN(block_time) AS first_trade_time,
        MAX(block_time) AS last_trade_time
    FROM token_trades
    GROUP BY 1, 2
),
total_summary AS (
    SELECT
        SUM(volume_usd) AS total_volume_usd
    FROM pool_summary
)
SELECT
    p.project,
    p.version,
    p.trades,
    p.unique_traders,
    p.volume_usd,
    p.buy_volume_usd,
    p.sell_volume_usd,
    p.volume_usd / NULLIF(t.total_volume_usd, 0) AS project_volume_share,
    p.first_trade_time,
    p.last_trade_time
FROM pool_summary p
CROSS JOIN total_summary t
ORDER BY p.volume_usd DESC NULLS LAST;
