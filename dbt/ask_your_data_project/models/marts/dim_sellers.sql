{{ config(materialized='table') }}

WITH sellers AS (
    SELECT
        seller_id,
        zip_prefix,
        seller_city,
        seller_state
    FROM {{ ref('stg_sellers') }}
),

states AS (
    SELECT
        state_code,
        region
    FROM {{ source('dimensions', 'brazilian_states') }}
)

SELECT
    s.*,
    st.region AS seller_region
FROM sellers s
LEFT JOIN states st ON s.seller_state = st.state_code
