WITH source AS (
    SELECT * FROM raw.products
),

cleaned AS (
    SELECT
        product_id,
        CASE 
            WHEN NULLIF(TRIM(product_category_name), '') IS NULL THEN NULL
            ELSE LOWER(TRIM(product_category_name))
        END AS product_category_name,
        CAST(product_name_lenght AS INTEGER) AS name_length,
        CAST(product_description_lenght AS INTEGER) AS description_length,
        CAST(product_photos_qty AS INTEGER) AS photos_qty,
        CAST(product_weight_g AS INTEGER) AS weight_g,
        CAST(product_length_cm AS INTEGER) AS length_cm,
        CAST(product_width_cm AS INTEGER) AS width_cm,
        CAST(product_height_cm AS INTEGER) AS height_cm
    FROM source
)
SELECT * FROM cleaned
