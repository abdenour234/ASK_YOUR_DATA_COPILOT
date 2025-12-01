import duckdb

conn = duckdb.connect('ask_your_data.db')

print('=== TABLE ROW COUNTS ===')
print(conn.execute("""
SELECT 'fact_orders' as table_name, COUNT(*) as row_count FROM mart.fact_orders
UNION ALL SELECT 'fact_order_items', COUNT(*) FROM mart.fact_order_items
UNION ALL SELECT 'dim_customers', COUNT(*) FROM mart.dim_customers
UNION ALL SELECT 'dim_products', COUNT(*) FROM mart.dim_products
UNION ALL SELECT 'dim_sellers', COUNT(*) FROM mart.dim_sellers
""").fetchdf())

print('\n=== ENRICHED DATA EXAMPLES ===')

print('\n1. Customer Regions:')
print(conn.execute("""
SELECT customer_region, COUNT(*) as customer_count 
FROM mart.dim_customers 
GROUP BY customer_region 
ORDER BY customer_count DESC
""").fetchdf())

print('\n2. Product Categories (English):')
print(conn.execute("""
SELECT product_category_name_english, COUNT(*) as product_count 
FROM mart.dim_products 
WHERE product_category_name_english IS NOT NULL 
GROUP BY product_category_name_english 
ORDER BY product_count DESC 
LIMIT 5
""").fetchdf())

print('\n3. Orders by Year:')
print(conn.execute("""
SELECT purchase_year, COUNT(*) as order_count 
FROM mart.fact_orders 
WHERE purchase_year IS NOT NULL 
GROUP BY purchase_year 
ORDER BY purchase_year
""").fetchdf())

print('\n4. Weekend vs Weekday Orders:')
print(conn.execute("""
SELECT 
    CASE WHEN purchase_is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END as day_type,
    COUNT(*) as order_count
FROM mart.fact_orders
GROUP BY purchase_is_weekend
ORDER BY purchase_is_weekend
""").fetchdf())

conn.close()
