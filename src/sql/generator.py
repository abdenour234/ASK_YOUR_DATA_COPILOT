"""
Simple SQL generator - converts intent dict to SQL string with schema awareness
"""

import os
import json
import requests
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


def call_llm(prompt: str) -> str:
    """Call LLM for SQL generation."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not set")
    
    model = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
    
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
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']


def extract_sql(text: str) -> str:
    """Extract SQL from LLM response."""
    text = text.replace('```sql', '').replace('```', '')
    return text.strip()


def validate_sql(sql: str) -> bool:
    """Basic SQL safety check."""
    sql_upper = sql.upper()
    dangerous = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
    return not any(word in sql_upper for word in dangerous)


def get_schema_from_db() -> str:
    """Get database schema."""
    try:
        from src.sql.executor import get_schema
        return get_schema()
    except:
        # Fallback if executor not available
        return """
Table: mart.fact_orders
  - order_id, customer_id, payment_value, order_status, order_date

Table: mart.fact_order_items
  - order_id, product_id, price, freight_value

Table: mart.dim_customers
  - customer_id, customer_state, customer_city

Table: mart.dim_products
  - product_id, product_category, product_name

Table: mart.dim_sellers
  - seller_id, seller_state, seller_city
"""


def build_sql_prompt(intent: Dict) -> str:
    """Build prompt for SQL generation with schema."""
    schema = get_schema_from_db()
    
    prompt = f"""Generate DuckDB SQL query from this intent.

DATABASE SCHEMA:
{schema}

INTENT:
- Type: {intent.get('intent_type')}
- Metrics: {intent.get('metrics', [])}
- Dimensions: {intent.get('dimensions', [])}
- Filters: {intent.get('filters', [])}
- Order by: {intent.get('order_by')}
- Limit: {intent.get('limit')}

INSTRUCTIONS:
- Generate SELECT query only
- Use proper JOIN syntax when needed
- Use the exact table and column names from schema
- For revenue, use SUM(payment_value) from fact_orders
- For order count, use COUNT(*) or COUNT(order_id)
- Return ONLY the SQL query, no explanation or markdown

Generate the SQL query:"""
    
    return prompt


def generate_sql(intent: Dict) -> Dict:
    """
    Generate SQL from intent dict.
    
    Returns dict with:
    - sql: the SQL query string
    - is_valid: bool
    - errors: list of errors
    """
    try:
        prompt = build_sql_prompt(intent)
        response = call_llm(prompt)
        sql = extract_sql(response)
        
        is_valid = validate_sql(sql)
        errors = [] if is_valid else ["Unsafe SQL detected"]
        
        return {
            'sql': sql,
            'is_valid': is_valid,
            'errors': errors,
            'intent_type': intent.get('intent_type')
        }
    except Exception as e:
        return {
            'sql': '',
            'is_valid': False,
            'errors': [str(e)],
            'intent_type': intent.get('intent_type')
        }
