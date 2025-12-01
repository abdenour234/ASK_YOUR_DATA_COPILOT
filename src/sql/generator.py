"""
SQL Generator - Sprint 2, Ticket 6 (Refactored)
Uses AI model to generate SQL queries from Intent objects.
Integrates with RAG for context and validates for safety.

Changes:
- AI generates SQL directly (no more template-based approach)
- Keeps safety validation to block unsafe queries
- Uses OpenRouter API to generate SQL from structured Intent + RAG context
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
import logging
from dotenv import load_dotenv

from src.nlp.models import Intent, Filter, DateRange
from src.sql.validator import SQLValidator, ValidationResult

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SQLGenerator:
    """
    Generates safe SQL queries from Intent objects using AI.
    
    Workflow:
    1. Receive Intent object from intent parser
    2. Build prompt with Intent details + RAG context + database schema
    3. Call AI model (via OpenRouter) to generate SQL
    4. Validate SQL with SQLValidator (safety checks)
    5. Return safe, executable SQL
    
    The AI model has full context about:
    - Available tables and columns (from RAG)
    - User's intent (metrics, dimensions, filters)
    - Database schema structure
    """
    
    def __init__(
        self,
        rag_context: Optional[Dict[str, Any]] = None,
        api_key: Optional[str] = None,
        model: str = "openrouter/auto"
    ):
        """
        Initialize SQL generator.
        
        Args:
            rag_context: Optional RAG context with glossary info
            api_key: OpenRouter API key (defaults to OPENROUTER_API_KEY env var)
            model: Model to use for SQL generation (default: openrouter/auto - picks free model)
        """
        self.validator = SQLValidator()
        self.rag_context = rag_context or {}
        
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not found. Set OPENROUTER_API_KEY environment variable."
            )
        
        self.model = model or os.getenv("OPENROUTER_MODEL", "openrouter/auto")
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def generate(
        self,
        intent: Intent,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Generate SQL from Intent object using AI.
        
        Args:
            intent: Parsed Intent object from NL query
            validate: Whether to validate generated SQL (default True)
            
        Returns:
            Dictionary with:
            - sql: Generated SQL query string
            - is_valid: Validation result
            - errors: List of validation errors (if any)
            - warnings: List of validation warnings
            - intent_type: Original intent type
            - metrics: Metrics used
            - dimensions: Dimensions used
            
        Example:
            >>> from src.nlp.models import Intent
            >>> generator = SQLGenerator()
            >>> intent = Intent(
            ...     intent_type='top_n',
            ...     metrics=['revenue'],
            ...     dimensions=['customer_state'],
            ...     limit=10,
            ...     order_by='revenue DESC',
            ...     confidence=0.95,
            ...     original_query='top 10 states by revenue'
            ... )
            >>> result = generator.generate(intent)
            >>> print(result['sql'])
        """
        logger.info(f"Generating SQL using AI for query: {intent.original_query}")
        
        try:
            # Build prompt for AI
            prompt = self._build_sql_prompt(intent)
            
            # Call AI to generate SQL
            sql = self._call_ai_for_sql(prompt)
            
            if not sql:
                raise ValueError("AI failed to generate SQL")
            
            logger.info(f"AI generated SQL ({len(sql)} characters)")
            
            # Validate SQL if requested
            validation_result = None
            if validate:
                validation_result = self.validator.validate(sql)
                
                if not validation_result.is_valid:
                    logger.error(f"SQL validation failed: {validation_result.errors}")
                    return {
                        'sql': sql,
                        'is_valid': False,
                        'errors': validation_result.errors,
                        'warnings': validation_result.warnings,
                        'intent_type': intent.intent_type,
                        'metrics': intent.metrics,
                        'dimensions': intent.dimensions
                    }
                
                # Use sanitized SQL
                sql = validation_result.sanitized_sql
            
            logger.info(f"Successfully generated and validated SQL")
            
            return {
                'sql': sql,
                'is_valid': True,
                'errors': [],
                'warnings': validation_result.warnings if validation_result else [],
                'intent_type': intent.intent_type,
                'metrics': intent.metrics,
                'dimensions': intent.dimensions,
                'filters': [self._filter_to_dict(f) for f in intent.filters] if intent.filters else []
            }
            
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            return {
                'sql': '',
                'is_valid': False,
                'errors': [str(e)],
                'warnings': [],
                'intent_type': intent.intent_type,
                'metrics': intent.metrics,
                'dimensions': intent.dimensions
            }
    
    def _build_sql_prompt(self, intent: Intent) -> str:
        """
        Build prompt for AI to generate SQL.
        
        Args:
            intent: Parsed Intent object
            
        Returns:
            Formatted prompt string with all necessary context
        """
        # Prepare intent details
        intent_json = {
            "query": intent.original_query,
            "intent_type": intent.intent_type,
            "metrics": intent.metrics,
            "dimensions": intent.dimensions,
            "filters": [self._filter_to_dict(f) for f in intent.filters] if intent.filters else [],
            "limit": intent.limit,
            "order_by": intent.order_by,
            "time_grain": intent.time_grain,
            "comparison_dimension": intent.comparison_dimension
        }
        
        # Database schema information - EXACT column names from dbt models
        schema_info = """
DATABASE SCHEMA (EXACT COLUMN NAMES):

Available Tables and Their Columns:

1. mart.fact_orders - Main fact table with order transactions
   Columns:
   - order_id (VARCHAR)
   - customer_id (VARCHAR)
   - order_status (VARCHAR)
   - order_purchase_ts (TIMESTAMP) -- IMPORTANT: Use this, NOT order_purchase_date
   - order_approved_ts (TIMESTAMP)
   - delivered_carrier_ts (TIMESTAMP)
   - delivered_customer_ts (TIMESTAMP)
   - estimated_delivery_date (DATE)
   - purchase_date_key (INTEGER)
   - purchase_year (INTEGER) -- Extracted from order_purchase_ts
   - purchase_month (INTEGER) -- Extracted from order_purchase_ts
   - purchase_day_name (VARCHAR) -- Extracted from order_purchase_ts
   - purchase_is_weekend (BOOLEAN) -- Extracted from order_purchase_ts

2. mart.dim_customers - Customer dimension
   Columns:
   - customer_id (VARCHAR)
   - customer_unique_id (VARCHAR)
   - zip_prefix (VARCHAR)
   - customer_city (VARCHAR)
   - customer_state (VARCHAR) -- Two-letter state code (e.g., 'SP', 'RJ')
   - customer_region (VARCHAR) -- Geographic region

3. mart.dim_products - Product dimension  
   Columns:
   - product_id (VARCHAR)
   - product_category_name (VARCHAR) -- Portuguese name
   - name_length (INTEGER)
   - description_length (INTEGER)
   - photos_qty (INTEGER)
   - weight_g (INTEGER)
   - length_cm (INTEGER)
   - width_cm (INTEGER)
   - height_cm (INTEGER)
   - product_category_name_english (VARCHAR) -- English name

4. mart.dim_sellers - Seller dimension
   Columns:
   - seller_id (VARCHAR)
   - zip_prefix (VARCHAR)
   - seller_city (VARCHAR)
   - seller_state (VARCHAR)
   - seller_region (VARCHAR)

5. mart.fact_order_items - Order line items
   Columns:
   - order_id (VARCHAR)
   - order_item_id (INTEGER)
   - product_id (VARCHAR)
   - seller_id (VARCHAR)
   - shipping_limit_ts (TIMESTAMP)
   - price (DOUBLE)
   - freight_value (DOUBLE)
   - shipping_limit_date_key (INTEGER)

6. mart.stg_order_payments - Payment staging table
   Columns:
   - order_id (VARCHAR)
   - payment_sequential (INTEGER)
   - payment_type (VARCHAR) -- 'credit_card', 'boleto', 'voucher', 'debit_card'
   - installments (INTEGER)
   - payment_value (DOUBLE) -- IMPORTANT: Use this for revenue calculations

Common Metrics (How to Calculate):
- revenue: SUM(p.payment_value) FROM mart.stg_order_payments p
- order_count: COUNT(DISTINCT o.order_id) FROM mart.fact_orders o
- customer_count: COUNT(DISTINCT c.customer_id) FROM mart.dim_customers c
- avg_order_value: AVG(p.payment_value) FROM mart.stg_order_payments p
- avg_freight: AVG(i.freight_value) FROM mart.fact_order_items i

Common Join Patterns:
- Orders to Customers: fact_orders.customer_id = dim_customers.customer_id
- Orders to Payments: fact_orders.order_id = stg_order_payments.order_id
- Orders to Items: fact_orders.order_id = fact_order_items.order_id
- Items to Products: fact_order_items.product_id = dim_products.product_id
- Items to Sellers: fact_order_items.seller_id = dim_sellers.seller_id

DUCKDB SQL SYNTAX (IMPORTANT):
- Date arithmetic: Use INTERVAL like: order_purchase_ts >= CURRENT_DATE - INTERVAL '6 months'
- NOT date_sub() or date_add() functions
- Extract date parts: EXTRACT(YEAR FROM order_purchase_ts) or use purchase_year column
- String comparison: Use single quotes 'value' not double quotes
- Date literals: DATE '2016-01-01' or CAST('2016-01-01' AS DATE)
- Current date: CURRENT_DATE (no parentheses)
- Date filtering: For years, use purchase_year = 2016 (integer comparison, NOT date ranges)
"""
        
        # RAG context if available
        rag_context_str = ""
        if self.rag_context:
            rag_context_str = f"\n\nADDITIONAL CONTEXT FROM GLOSSARY:\n{json.dumps(self.rag_context, indent=2)}"
        
        prompt = f"""
You are an expert SQL generator for DuckDB. Generate a safe, efficient SELECT query based on the user's intent.

{schema_info}

USER INTENT:
{json.dumps(intent_json, indent=2)}{rag_context_str}

CRITICAL RULES (MUST FOLLOW):
1. Generate ONLY a SELECT statement (no DDL/DML commands)
2. Use EXACT column names from the schema above - DO NOT guess or assume column names
3. For dates, use order_purchase_ts (TIMESTAMP) NOT order_purchase_date
4. For revenue, use payment_value from stg_order_payments
5. Always include schema prefix: mart.fact_orders, mart.dim_customers, etc.
6. Use proper JOINs when accessing multiple tables (see Common Join Patterns above)
7. Use appropriate WHERE clauses for filters
8. USE DUCKDB SYNTAX ONLY:
9. Use GROUP BY for aggregations with dimensions
10. Include ORDER BY and LIMIT as specified in intent
11. Use clear table aliases (e.g., o for orders, c for customers, p for payments)
12. Return ONLY the SQL query, no explanations or markdown code blocks

Generate the SQL query now:
"""
        return prompt
    
    def _call_ai_for_sql(self, prompt: str) -> str:
        """
        Call OpenRouter API to generate SQL.
        
        Args:
            prompt: Formatted prompt with intent and schema context
            
        Returns:
            Generated SQL query string
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert SQL query generator. Generate only valid DuckDB SELECT statements. Return ONLY the SQL query without any markdown formatting or explanations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.1,  # Low temperature for consistent SQL generation
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            sql = result['choices'][0]['message']['content'].strip()
            
            # Clean up any markdown code blocks
            sql = sql.replace('```sql', '').replace('```', '').strip()
            
            return sql
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise ValueError(f"Failed to generate SQL via AI: {str(e)}")
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected API response format: {str(e)}")
            raise ValueError(f"Invalid API response: {str(e)}")
    
    def _filter_to_dict(self, filter_obj: Filter) -> Dict[str, Any]:
        """
        Convert Filter object to dictionary.
        
        Args:
            filter_obj: Filter Pydantic model
            
        Returns:
            Dictionary with dimension, operator, value
        """
        return {
            'dimension': filter_obj.dimension,
            'operator': filter_obj.operator,
            'value': filter_obj.value
        }


def generate_sql(intent: Intent, rag_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to generate SQL from Intent using AI.
    
    Args:
        intent: Parsed Intent object
        rag_context: Optional RAG context
        
    Returns:
        Dictionary with SQL and metadata
        
    Example:
        >>> from src.nlp.models import Intent
        >>> intent = Intent(
        ...     intent_type='aggregation',
        ...     metrics=['revenue'],
        ...     dimensions=[],
        ...     filters=[],
        ...     confidence=0.98,
        ...     original_query='what is total revenue'
        ... )
        >>> result = generate_sql(intent)
        >>> print(result['sql'])
    """
    generator = SQLGenerator(rag_context=rag_context)
    return generator.generate(intent)


if __name__ == "__main__":
    # Test the AI-based SQL generator
    from src.nlp.models import Intent, Filter
    
    print("=== AI-Based SQL Generator Tests ===\n")
    print("Note: Requires OPENROUTER_API_KEY environment variable\\n")
    
    try:
        generator = SQLGenerator()
        
        # Test 1: Top N query
        print("1. Top 5 customer states by revenue:")
        intent = Intent(
            intent_type='top_n',
            metrics=['revenue'],
            dimensions=['customer_state'],
            filters=[],
            limit=5,
            order_by='revenue DESC',
            confidence=0.95,
            original_query='top 5 states by revenue'
        )
        result = generator.generate(intent)
        print(f"Valid: {result['is_valid']}")
        if result['is_valid']:
            print(f"SQL:\\n{result['sql']}\\n")
        else:
            print(f"Errors: {result['errors']}\\n")
        print("="*60 + "\\n")
        
        # Test 2: Simple aggregation
        print("2. Total revenue:")
        intent = Intent(
            intent_type='aggregation',
            metrics=['revenue'],
            dimensions=[],
            filters=[],
            confidence=0.98,
            original_query='what is total revenue'
        )
        result = generator.generate(intent)
        print(f"Valid: {result['is_valid']}")
        if result['is_valid']:
            print(f"SQL:\\n{result['sql']}\\n")
        else:
            print(f"Errors: {result['errors']}\\n")
        print("="*60 + "\\n")
        
        print("✅ AI-based SQL generation tests completed!")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Make sure OPENROUTER_API_KEY is set in your .env file")
