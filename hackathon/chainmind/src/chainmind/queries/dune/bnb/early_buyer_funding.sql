-- ChainMind / BNB / Early-buyer funding sources
--
-- Purpose:
--   Inspect BNB inflows before each early buyer's first token buy, then surface
--   shared funding sources. This is the first low-cost same-funder signal.
--
-- Phase 2 fields supported:
--   - buyer_rank
--   - buyer
--   - first_buy_time
--   - tx_count_before_entry
--   - first_seen_time
--   - wallet_age_days_at_entry
--   - funder
--   - funded_selected_early_buyers
--   - total_funded_bnb
--
-- Important:
--   A shared funder is evidence, not proof. Routers, pools, CEX hot wallets,
--   and other infrastructure addresses must be labeled or filtered before this
--   becomes a formal same-entity rule.
--
-- Usage:
--   Create a Dune Text parameter named token_address.
--   Example token_address: 0x205f39c39f5fe15d4ef000aeb835de8deb264444
--
-- Performance note:
--   This query touches raw transaction/trace tables. Keep buyer_limit small
--   for first validation runs, then increase only after the query is stable.

WITH params AS (
    SELECT
        from_hex(substr('{{token_address}}', 3)) AS token,
        NOW() - INTERVAL '30' DAY AS start_time,
        NOW() AS end_time,
        20 AS buyer_limit,
        14 AS funding_lookback_days,
        60 AS history_lookback_days
),
known_infrastructure AS (
    SELECT *
    FROM (
        VALUES
            (0x10ed43c718714eb63d5aa57b78b54704e256024e, 'PancakeSwap V2 Router')
    ) AS t(address, label)
),
buyer_buys AS (
    SELECT
        tx_from AS buyer,
        MIN(block_time) AS first_buy_time,
        COUNT(*) AS buy_trades,
        SUM(amount_usd) AS buy_usd
    FROM dex.trades
    WHERE blockchain = 'bnb'
      AND block_time >= (SELECT start_time FROM params)
      AND token_bought_address = (SELECT token FROM params)
    GROUP BY 1
),
ranked_buyers AS (
    SELECT
        ROW_NUMBER() OVER (ORDER BY first_buy_time, buy_usd DESC) AS buyer_rank,
        buyer,
        first_buy_time,
        buy_trades,
        buy_usd
    FROM buyer_buys
),
selected_buyers AS (
    SELECT *
    FROM ranked_buyers
    WHERE buyer_rank <= (SELECT buyer_limit FROM params)
),
buyer_history AS (
    SELECT
        b.buyer,
        MIN(t.block_time) AS first_seen_time,
        COUNT(*) FILTER (
            WHERE t.block_time < b.first_buy_time
        ) AS tx_count_before_entry
    FROM selected_buyers b
    LEFT JOIN bnb.transactions t
        ON t."from" = b.buyer
       AND t.block_time >= (SELECT start_time FROM params) - INTERVAL '60' DAY
       AND t.block_time < (SELECT end_time FROM params)
    GROUP BY 1
),
pre_entry_funding AS (
    SELECT
        b.buyer_rank,
        b.buyer,
        b.first_buy_time,
        tr."from" AS funder,
        tr.block_time AS funding_time,
        tr.tx_hash AS funding_tx_hash,
        tr.value / 1e18 AS funded_bnb
    FROM selected_buyers b
    INNER JOIN bnb.traces tr
        ON tr."to" = b.buyer
       AND tr.block_time < b.first_buy_time
       AND tr.block_time >= b.first_buy_time - INTERVAL '14' DAY
       AND tr.block_time >= (SELECT start_time FROM params) - INTERVAL '14' DAY
       AND tr.block_time < (SELECT end_time FROM params)
       AND tr.value > 0
       AND tr.success = TRUE
       AND tr.type = 'call'
),
funder_summary AS (
    SELECT
        funder,
        COUNT(DISTINCT buyer) AS funded_selected_early_buyers,
        SUM(funded_bnb) AS total_funded_bnb,
        MIN(funding_time) AS first_funding_time,
        MAX(funding_time) AS last_funding_time
    FROM pre_entry_funding
    GROUP BY 1
)
SELECT
    f.buyer_rank,
    f.buyer,
    f.first_buy_time,
    h.first_seen_time,
    DATE_DIFF('day', h.first_seen_time, f.first_buy_time) AS wallet_age_days_at_entry,
    h.tx_count_before_entry,
    f.funder,
    i.label AS infrastructure_label,
    f.funding_time,
    f.funding_tx_hash,
    f.funded_bnb,
    s.funded_selected_early_buyers,
    s.total_funded_bnb,
    s.first_funding_time,
    s.last_funding_time
FROM pre_entry_funding f
LEFT JOIN funder_summary s
    ON f.funder = s.funder
LEFT JOIN buyer_history h
    ON f.buyer = h.buyer
LEFT JOIN known_infrastructure i
    ON f.funder = i.address
ORDER BY
    s.funded_selected_early_buyers DESC,
    s.total_funded_bnb DESC,
    f.buyer_rank,
    f.funding_time DESC;
