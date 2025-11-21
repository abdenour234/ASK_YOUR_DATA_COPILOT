WITH source AS (
    SELECT * FROM {{ source('raw', 'customers') }}
),

cleaned AS (
    SELECT
        customer_id,
        customer_unique_id,
        CAST(customer_zip_code_prefix AS INTEGER) AS zip_prefix,
        LOWER(TRIM(customer_city)) AS customer_city,
        customer_state
    FROM source
)

SELECT * FROM cleaned
