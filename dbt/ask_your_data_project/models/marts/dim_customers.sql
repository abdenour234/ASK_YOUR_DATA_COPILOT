WITH customers AS (
    SELECT
        customer_id,
        customer_unique_id,
        zip_prefix,
        customer_city,
        customer_state
    FROM {{ ref('stg_customers') }}
),
states AS (
    SELECT
        state_code,
        region
    FROM {{ source('dimensions', 'brazilian_states') }}
)

SELECT
    c.*,
    s.region AS customer_region
FROM customers c
LEFT JOIN states s ON c.customer_state = s.state_code
