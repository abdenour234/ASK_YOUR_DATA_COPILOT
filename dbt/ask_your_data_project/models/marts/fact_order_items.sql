{{ config(materialized='table') }}

WITH items AS (
    SELECT
        order_id,
        order_item_id,
        product_id,
        seller_id,
        shipping_limit_ts,
        price,
        freight_value
    FROM {{ ref('stg_order_items') }}
),

calendar AS (
    SELECT
        date,
        date_key
    FROM {{ source('dimensions', 'calendar') }}
)

SELECT
    i.*,
    cal.date_key AS shipping_limit_date_key
FROM items i
LEFT JOIN calendar cal ON i.shipping_limit_ts = cal.date
