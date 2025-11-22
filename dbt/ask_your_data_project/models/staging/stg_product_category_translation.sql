WITH source AS (
    SELECT * FROM {{ source('raw','product_category_translation') }}
),

cleaned AS (
    SELECT
        product_category_name,
        product_category_name_english
    FROM source
)

SELECT * FROM cleaned
