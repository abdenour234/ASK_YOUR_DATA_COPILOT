WITH source AS (
    SELECT *
    FROM {{ source('raw', 'orders') }}
),
cleaned AS (
    SELECT
        order_id,
        customer_id,
        LOWER(TRIM(order_status)) AS order_status,
        CAST(order_purchase_timestamp AS TIMESTAMP) AS order_purchase_ts,
        CAST(order_approved_at AS TIMESTAMP) AS order_approved_ts,
        CAST(order_delivered_carrier_date AS TIMESTAMP) AS delivered_carrier_ts,
        CAST(order_delivered_customer_date AS TIMESTAMP) AS delivered_customer_ts,
        CAST(order_estimated_delivery_date AS TIMESTAMP) AS estimated_delivery_date
    FROM source
)
SELECT * FROM cleaned

