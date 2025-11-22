{{ config(materialized='table') }}

with products as (
    select
        product_id,
        product_category_name,
        name_length,
        description_length,
        photos_qty,
        weight_g,
        length_cm,
        width_cm,
        height_cm
    from {{ ref('stg_products') }}
),

translations as (
    select
        product_category_name,
        product_category_name_english
    from {{ ref('stg_product_category_translation') }}
)

select
    p.*,
    t.product_category_name_english
from products p
left join translations t
    on p.product_category_name = t.product_category_name
