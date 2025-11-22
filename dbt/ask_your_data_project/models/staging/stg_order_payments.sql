WITH source AS (
    SELECT * FROM raw.order_payments
),

cleaned AS (
    SELECT
        order_id,
        CAST(payment_sequential AS INTEGER) AS payment_sequential,
        LOWER(TRIM(payment_type)) AS payment_type,
        CAST(payment_installments AS INTEGER) AS installments,
        CAST(payment_value AS DOUBLE) AS payment_value
    FROM source
)

SELECT * FROM cleaned