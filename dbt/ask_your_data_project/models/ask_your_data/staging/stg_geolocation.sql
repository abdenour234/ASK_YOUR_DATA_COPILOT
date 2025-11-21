WITH source AS (
    SELECT * FROM {{ source('raw', 'geolocation') }}
),

cleaned AS (
    SELECT
        CAST(geolocation_zip_code_prefix AS INTEGER) AS zip_prefix,
        geolocation_lat AS lat,                    
        geolocation_lng AS lng,                    
        LOWER(TRIM(geolocation_city)) AS city,
        geolocation_state AS state
    FROM source
)

SELECT * FROM cleaned