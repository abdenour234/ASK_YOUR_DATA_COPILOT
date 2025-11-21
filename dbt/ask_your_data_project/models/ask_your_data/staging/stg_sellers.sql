WITH source AS (
    SELECT * FROM {{ source('raw', 'sellers') }}
),

cleaned AS (
    SELECT
        seller_id,
        CAST(seller_zip_code_prefix AS INTEGER) AS zip_prefix,
        LOWER(TRIM(seller_city)) AS seller_city,
        seller_state
    FROM source
)

SELECT * FROM cleaned