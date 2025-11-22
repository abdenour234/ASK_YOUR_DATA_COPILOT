import duckdb
con = duckdb.connect("ask_your_data.db")
print(con.execute("SELECT * FROM fact_orders LIMIT 5").fetchdf())
print(con.execute("SELECT * FROM fact_order_items LIMIT 5").fetchdf())
print(con.execute("SELECT * FROM dim_customers LIMIT 5").fetchdf())
print(con.execute("SELECT * FROM dim_products LIMIT 5").fetchdf())
print(con.execute("SELECT * FROM dim_sellers LIMIT 5").fetchdf())
con.close()