-- ChainMind / BNB / Early buyers and remaining balance
--
-- Purpose:
--   Rank early buyers by first buy time and estimate whether they still hold
--   material token balance. This query supports the early-buyer exit risk.
--
-- Phase 2 fields supported:
--   - buyer_rank
--   - first_buy_time
--   - buy_trades
--   - tokens_bought
--   - buy_usd
--   - current_balance
--   - remaining_ratio
--   - early_buyer_exit_ratio, derived from remaining_ratio in Python
--
-- Usage:
--   Create a Dune Text parameter named token_address.
--   Example token_address: 0x205f39c39f5fe15d4ef000aeb835de8deb264444
--   If Dune token transfer schemas change, verify the tokens.transfers amount
--   column before using current_balance in formal scoring.

WITH params AS (
    SELECT
        from_hex(substr('{{token_address}}', 3)) AS token,
        NOW() - INTERVAL '30' DAY AS start_time,
        100 AS buyer_limit
),
buyer_buys AS (
    SELECT
        tx_from AS buyer,
        MIN(block_time) AS first_buy_time,
        COUNT(*) AS buy_trades,
        SUM(token_bought_amount) AS tokens_bought,
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
        tokens_bought,
        buy_usd
    FROM buyer_buys
),
selected_buyers AS (
    SELECT *
    FROM ranked_buyers
    WHERE buyer_rank <= (SELECT buyer_limit FROM params)
),
token_balances AS (
    SELECT
        wallet,
        SUM(balance_delta) AS current_balance
    FROM (
        SELECT
            "to" AS wallet,
            amount AS balance_delta
        FROM tokens.transfers
        WHERE blockchain = 'bnb'
          AND contract_address = (SELECT token FROM params)

        UNION ALL

        SELECT
            "from" AS wallet,
            -amount AS balance_delta
        FROM tokens.transfers
        WHERE blockchain = 'bnb'
          AND contract_address = (SELECT token FROM params)
    ) deltas
    GROUP BY 1
)
SELECT
    b.buyer_rank,
    b.buyer,
    b.first_buy_time,
    b.buy_trades,
    b.tokens_bought,
    b.buy_usd,
    COALESCE(t.current_balance, 0) AS current_balance,
    GREATEST(COALESCE(t.current_balance, 0), 0) / NULLIF(b.tokens_bought, 0) AS remaining_ratio
FROM selected_buyers b
LEFT JOIN token_balances t
    ON b.buyer = t.wallet
ORDER BY b.buyer_rank;
