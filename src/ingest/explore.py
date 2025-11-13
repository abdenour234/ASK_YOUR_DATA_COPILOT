"""
Sprint 1 - Ticket 2: Interactive DuckDB Explorer
Quick utility to explore the Olist dataset.

Usage:
    python src/ingest/explore.py
"""

import duckdb
import pandas as pd


def explore_database(db_path: str = "ask_your_data.db") -> None:
    """Interactive exploration of the DuckDB database."""
    
    conn = duckdb.connect(db_path, read_only=True)
    
    print("=" * 70)
    print("DuckDB Database Explorer")
    print("=" * 70)
    
    # Common queries menu
    queries = {
        "1": ("List all tables", """
            SELECT table_schema, table_name, 
                   (SELECT COUNT(*) FROM information_schema.columns c 
                    WHERE c.table_schema = t.table_schema 
                    AND c.table_name = t.table_name) as columns
            FROM information_schema.tables t
            WHERE table_schema IN ('raw', 'dimensions')
            ORDER BY table_schema, table_name
        """),
        "2": ("Order status summary", """
            SELECT order_status, 
                   COUNT(*) as count,
                   ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
            FROM raw.orders
            GROUP BY order_status
            ORDER BY count DESC
        """),
        "3": ("Top 10 states by customers", """
            SELECT customer_state, COUNT(*) as customer_count
            FROM raw.customers
            GROUP BY customer_state
            ORDER BY customer_count DESC
            LIMIT 10
        """),
        "4": ("Monthly order trends", """
            SELECT 
                c.year,
                c.month,
                c.month_name,
                COUNT(DISTINCT o.order_id) as orders,
                COUNT(DISTINCT o.customer_id) as customers
            FROM raw.orders o
            JOIN dimensions.calendar c ON DATE(o.order_purchase_timestamp) = c.date
            GROUP BY c.year, c.month, c.month_name
            ORDER BY c.year, c.month
        """),
        "5": ("Product categories (top 10)", """
            SELECT 
                COALESCE(t.product_category_name_english, p.product_category_name) as category,
                COUNT(*) as product_count
            FROM raw.products p
            LEFT JOIN raw.product_category_translation t 
                ON p.product_category_name = t.product_category_name
            GROUP BY category
            ORDER BY product_count DESC
            LIMIT 10
        """),
        "6": ("Payment type distribution", """
            SELECT payment_type, 
                   COUNT(*) as payment_count,
                   ROUND(SUM(payment_value), 2) as total_value
            FROM raw.order_payments
            GROUP BY payment_type
            ORDER BY total_value DESC
        """),
        "7": ("Review score distribution", """
            SELECT review_score,
                   COUNT(*) as review_count,
                   ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
            FROM raw.order_reviews
            GROUP BY review_score
            ORDER BY review_score DESC
        """),
        "8": ("Orders by region", """
            SELECT 
                s.region,
                COUNT(DISTINCT o.order_id) as order_count,
                COUNT(DISTINCT c.customer_id) as customer_count
            FROM raw.orders o
            JOIN raw.customers c ON o.customer_id = c.customer_id
            JOIN dimensions.brazilian_states s ON c.customer_state = s.state_code
            GROUP BY s.region
            ORDER BY order_count DESC
        """),
        "9": ("Calendar dimension sample", """
            SELECT date, year, quarter, month, month_name, day_name, is_weekend
            FROM dimensions.calendar
            WHERE year = 2017 AND month = 1
            LIMIT 10
        """),
    }
    
    while True:
        print("\n📊 Quick Queries:")
        print("-" * 70)
        for key, (desc, _) in queries.items():
            print(f"   {key}. {desc}")
        print("   0. Exit")
        print("-" * 70)
        
        choice = input("\nSelect query (0-9): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye!")
            break
        
        if choice not in queries:
            print("❌ Invalid choice. Please select 0-9.")
            continue
        
        desc, query = queries[choice]
        print(f"\n📈 {desc}")
        print("-" * 70)
        
        try:
            result = conn.execute(query).fetchdf()
            print(result.to_string(index=False))
        except Exception as e:
            print(f"❌ Error: {e}")
    
    conn.close()


if __name__ == "__main__":
    explore_database()
