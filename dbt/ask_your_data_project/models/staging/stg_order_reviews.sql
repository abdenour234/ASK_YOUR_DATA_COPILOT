WITH source AS (
    SELECT * FROM raw.order_reviews
),

cleaned AS (
    SELECT
        review_id,
        order_id,
        CAST(review_score AS INTEGER) AS review_score,
        CAST(review_creation_date AS TIMESTAMP) AS review_created_ts,
        CAST(review_answer_timestamp AS TIMESTAMP) AS review_answer_ts,
        review_comment_title,
        review_comment_message
    FROM source
)

SELECT * FROM cleaned



