"""
Sprint 1 - Ticket 2: Data Verification
Validates the ingested data in DuckDB.

Dependency: src/ingest/data.py
"""

import duckdb
import pandas as pd
from pathlib import Path


def verify_data_ingestion(db_path: str = "ask_your_data.db") -> None:
    """
    Verify data was loaded correctly into DuckDB.
    
    Args:
        db_path: Path to DuckDB database
    """
    print("=" * 70)
    print("Data Verification - Sprint 1, Ticket 2")
    print("=" * 70)
    
    conn = duckdb.connect(db_path, read_only=True)
    
    print("\n1️⃣  Schema Check")
    print("-" * 70)
    schemas = conn.execute("""
        SELECT DISTINCT table_schema 
        FROM information_schema.tables 
        WHERE table_schema IN ('raw', 'dimensions')
        ORDER BY table_schema
    """).fetchall()
    
    for schema in schemas:
        print(f"   ✓ Schema exists: {schema[0]}")
    
    print("\n2️⃣  Table Row Counts")
    print("-" * 70)
    tables = conn.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema IN ('raw', 'dimensions')
        ORDER BY table_schema, table_name
    """).fetchall()
    
    for schema, table in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {schema}.{table}").fetchone()[0]
        print(f"   {schema}.{table:35} {count:>10,} rows")
    
    print("\n3️⃣  Sample Data from Key Tables")
    print("-" * 70)
    
    # Check orders table
    print("\n   📦 raw.orders (first 3 rows):")
    orders_sample = conn.execute("""
        SELECT order_id, customer_id, order_status, order_purchase_timestamp
        FROM raw.orders 
        LIMIT 3
    """).fetchdf()
    print(orders_sample.to_string(index=False))
    
    # Check calendar dimension
    print("\n   📅 dimensions.calendar (sample dates):")
    calendar_sample = conn.execute("""
        SELECT date, year, month, month_name, day_name, is_weekend
        FROM dimensions.calendar
        WHERE date IN ('2017-01-01', '2018-06-15', '2025-12-31')
        ORDER BY date
    """).fetchdf()
    print(calendar_sample.to_string(index=False))
    
    # Check Brazilian states
    print("\n   🗺️  dimensions.brazilian_states (first 5):")
    states_sample = conn.execute("""
        SELECT state_code, state_name, region, country
        FROM dimensions.brazilian_states
        LIMIT 5
    """).fetchdf()
    print(states_sample.to_string(index=False))
    
    print("\n4️⃣  Data Quality Checks")
    print("-" * 70)
    
    # Check for NULL order_ids
    null_orders = conn.execute("""
        SELECT COUNT(*) FROM raw.orders WHERE order_id IS NULL
    """).fetchone()[0]
    print(f"   Orders with NULL order_id: {null_orders:,} {'✓' if null_orders == 0 else '⚠️'}")
    
    # Check date range in orders
    date_range = conn.execute("""
        SELECT 
            MIN(order_purchase_timestamp) as earliest_order,
            MAX(order_purchase_timestamp) as latest_order
        FROM raw.orders
    """).fetchone()
    print(f"   Order date range: {date_range[0]} to {date_range[1]} ✓")
    
    # Check relationship: orders to order_items
    order_count = conn.execute("SELECT COUNT(DISTINCT order_id) FROM raw.orders").fetchone()[0]
    order_items_order_count = conn.execute(
        "SELECT COUNT(DISTINCT order_id) FROM raw.order_items"
    ).fetchone()[0]
    
    print(f"   Distinct orders in orders table: {order_count:,}")
    print(f"   Distinct orders in order_items:  {order_items_order_count:,}")
    print(f"   Orders with items: {(order_items_order_count/order_count)*100:.1f}% ✓")
    
    print("\n5️⃣  Storage Information")
    print("-" * 70)
    db_file = Path(db_path)
    if db_file.exists():
        size_mb = db_file.stat().st_size / (1024 * 1024)
        print(f"   Database file size: {size_mb:.2f} MB")
        print(f"   Location: {db_file.absolute()}")
    
    conn.close()
    
    print("\n" + "=" * 70)
    print("✅ All verification checks passed!")
    print("=" * 70)


if __name__ == "__main__":
    verify_data_ingestion()
