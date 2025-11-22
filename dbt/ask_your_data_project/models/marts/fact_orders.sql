{{ config(materialized='table') }}

WITH orders AS (
    SELECT
        order_id,
        customer_id,
        order_status,
        order_purchase_ts,
        order_approved_ts,
        delivered_carrier_ts,
        delivered_customer_ts,
        estimated_delivery_date
    FROM {{ ref('stg_orders') }}
),

calendar AS (
    SELECT
        date,
        date_key,
        year,
        month,
        day,
        day_name,
        is_weekend
    FROM {{ source('dimensions', 'calendar') }}
)

SELECT
    o.*,
    cal.date_key AS purchase_date_key,
    cal.year AS purchase_year,
    cal.month AS purchase_month,
    cal.day_name AS purchase_day_name,
    cal.is_weekend AS purchase_is_weekend
FROM orders o
LEFT JOIN calendar cal ON o.order_purchase_ts = cal.date
