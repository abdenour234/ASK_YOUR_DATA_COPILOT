"""
Simple SQL executor - runs queries with schema extraction and auto-retry on errors
"""

import duckdb
import pandas as pd
import time
from typing import Dict, Optional, List
from pathlib import Path


# Global connection
_connection = None
_schema_cache = None


def connect_db(db_path: str = "ask_your_data.db") -> None:
    """Connect to DuckDB database."""
    global _connection
    if _connection is None:
        if not Path(db_path).exists():
            raise FileNotFoundError(f"Database not found: {db_path}")
        _connection = duckdb.connect(db_path)


def disconnect_db() -> None:
    """Close database connection."""
    global _connection
    if _connection:
        _connection.close()
        _connection = None


def get_schema() -> str:
    """Extract database schema as formatted string."""
    global _schema_cache, _connection
    
    if _schema_cache:
        return _schema_cache
    
    if _connection is None:
        connect_db()
    
    schema_parts = []
    
    try:
        # Get all tables in mart schema
        tables_query = """
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'mart'
            ORDER BY table_name
        """
        tables_df = _connection.execute(tables_query).df()
        
        for _, row in tables_df.iterrows():
            schema_name = row['table_schema']
            table_name = row['table_name']
            full_table = f"{schema_name}.{table_name}"
            
            # Get columns for this table
            columns_query = f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_schema = '{schema_name}' AND table_name = '{table_name}'
                ORDER BY ordinal_position
            """
            columns_df = _connection.execute(columns_query).df()
            
            # Format table info
            schema_parts.append(f"\nTable: {full_table}")
            for _, col in columns_df.iterrows():
                schema_parts.append(f"  - {col['column_name']} ({col['data_type']})")
        
        _schema_cache = "\n".join(schema_parts)
        return _schema_cache
        
    except Exception as e:
        # Fallback to basic schema if query fails
        return """
Table: mart.fact_orders
  - order_id (VARCHAR)
  - customer_id (VARCHAR)
  - payment_value (DOUBLE)
  - order_status (VARCHAR)
  - order_date (DATE)

Table: mart.fact_order_items
  - order_id (VARCHAR)
  - product_id (VARCHAR)
  - price (DOUBLE)
  - freight_value (DOUBLE)

Table: mart.dim_customers
  - customer_id (VARCHAR)
  - customer_state (VARCHAR)
  - customer_city (VARCHAR)

Table: mart.dim_products
  - product_id (VARCHAR)
  - product_category (VARCHAR)
  - product_name (VARCHAR)

Table: mart.dim_sellers
  - seller_id (VARCHAR)
  - seller_state (VARCHAR)
  - seller_city (VARCHAR)
"""


def fix_sql_with_llm(sql: str, error: str) -> str:
    """Use LLM to fix SQL based on error message."""
    import os
    import requests
    from dotenv import load_dotenv
    
    load_dotenv()
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        return sql  # Return original if no API key
    
    model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
    
    schema = get_schema()
    
    prompt = f"""Fix this SQL query that failed with an error.

DATABASE SCHEMA:
{schema}

FAILED SQL:
{sql}

ERROR:
{error}

Return ONLY the corrected SQL query, no explanation or markdown."""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost:8501"),
        "X-Title": os.getenv("OPENROUTER_SITE_NAME", "Ask Your Data")
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        response.raise_for_status()
        fixed_sql = response.json()['choices'][0]['message']['content']
        
        # Clean up SQL
        fixed_sql = fixed_sql.replace('```sql', '').replace('```', '').strip()
        return fixed_sql
    except:
        return sql  # Return original if fix fails


def run_query(sql: str, timeout: int = 30, max_retries: int = 2) -> Dict:
    """
    Execute SQL query and return results with auto-retry on errors.
    
    Returns dict with:
    - success: bool
    - data: DataFrame if success
    - row_count: int
    - execution_time_ms: float
    - error: str if failed
    - retries: int number of retry attempts
    """
    if _connection is None:
        connect_db()
    
    retries = 0
    original_sql = sql
    
    for attempt in range(max_retries + 1):
        start_time = time.time()
        
        try:
            result_df = _connection.execute(sql).df()
            execution_time = (time.time() - start_time) * 1000
            
            return {
                'success': True,
                'data': result_df,
                'row_count': len(result_df),
                'execution_time_ms': execution_time,
                'sql': sql,
                'error': None,
                'retries': retries
            }
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            error_msg = str(e)
            
            # If not last attempt, try to fix SQL
            if attempt < max_retries:
                retries += 1
                fixed_sql = fix_sql_with_llm(sql, error_msg)
                if fixed_sql != sql:
                    sql = fixed_sql
                    continue
            
            # Return error if all retries failed
            return {
                'success': False,
                'data': None,
                'row_count': 0,
                'execution_time_ms': execution_time,
                'sql': original_sql,
                'error': error_msg,
                'retries': retries
            }
