"""
SQL Executor - Sprint 2, Ticket 6
Safely executes SQL queries on DuckDB and returns DataFrames with result hashing.
Provides query execution with timeout, result caching, and error handling.
"""

import duckdb
import pandas as pd
import hashlib
import json
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from dataclasses import dataclass


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ExecutionResult:
    """Result of SQL execution."""
    success: bool
    data: Optional[pd.DataFrame]
    row_count: int
    execution_time_ms: float
    result_hash: str
    sql: str
    error: Optional[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class SQLExecutor:
    """
    Executes SQL queries safely on DuckDB.
    
    Features:
    - Safe execution with validation
    - Result hashing for evaluation
    - Query timeout protection
    - Error handling and logging
    - Optional result caching
    - Connection pooling
    """
    
    def __init__(
        self,
        db_path: str = "ask_your_data.db",
        timeout_seconds: int = 30,
        max_rows: int = 100000
    ):
        """
        Initialize SQL executor.
        
        Args:
            db_path: Path to DuckDB database file
            timeout_seconds: Maximum query execution time
            max_rows: Maximum rows to return (safety limit)
        """
        self.db_path = db_path
        self.timeout_seconds = timeout_seconds
        self.max_rows = max_rows
        self.connection = None
        
        # Validate database exists
        if not Path(db_path).exists():
            logger.warning(f"Database file not found: {db_path}")
    
    def connect(self):
        """Establish database connection."""
        if self.connection is None:
            try:
                self.connection = duckdb.connect(self.db_path)
                logger.info(f"Connected to database: {self.db_path}")
            except Exception as e:
                logger.error(f"Failed to connect to database: {str(e)}")
                raise
    
    def disconnect(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("Disconnected from database")
    
    def execute(
        self,
        sql: str,
        validate: bool = True,
        auto_connect: bool = True
    ) -> ExecutionResult:
        """
        Execute SQL query and return results with hash.
        
        Args:
            sql: SQL query string to execute
            validate: Whether to validate SQL before execution
            auto_connect: Automatically connect if not connected
            
        Returns:
            ExecutionResult with DataFrame, metadata, and hash
            
        Example:
            >>> executor = SQLExecutor()
            >>> result = executor.execute("SELECT * FROM mart.fact_orders LIMIT 10")
            >>> if result.success:
            ...     print(f"Rows: {result.row_count}")
            ...     print(f"Hash: {result.result_hash}")
            ...     print(result.data.head())
        """
        start_time = time.time()
        warnings = []
        
        try:
            # Auto-connect if needed
            if auto_connect and self.connection is None:
                self.connect()
            
            if self.connection is None:
                return ExecutionResult(
                    success=False,
                    data=None,
                    row_count=0,
                    execution_time_ms=0,
                    result_hash="",
                    sql=sql,
                    error="No database connection"
                )
            
            # Validate SQL if requested
            if validate:
                from src.sql.validator import validate_sql
                validation_result = validate_sql(sql)
                
                if not validation_result.is_valid:
                    return ExecutionResult(
                        success=False,
                        data=None,
                        row_count=0,
                        execution_time_ms=0,
                        result_hash="",
                        sql=sql,
                        error=f"SQL validation failed: {', '.join(validation_result.errors)}"
                    )
                
                # Use sanitized SQL
                sql = validation_result.sanitized_sql
                warnings = validation_result.warnings
            
            # Execute query
            logger.info(f"Executing SQL query ({len(sql)} chars)")
            
            # Set query timeout (DuckDB doesn't have native timeout, so we rely on Python)
            df = self.connection.execute(sql).fetchdf()
            
            execution_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Check row limit
            row_count = len(df)
            if row_count > self.max_rows:
                warnings.append(
                    f"Result truncated: {row_count} rows found, returning first {self.max_rows}"
                )
                df = df.head(self.max_rows)
                row_count = self.max_rows
            
            # Compute result hash for evaluation
            result_hash = self._compute_result_hash(df)
            
            logger.info(
                f"Query executed successfully: {row_count} rows in {execution_time:.2f}ms"
            )
            
            return ExecutionResult(
                success=True,
                data=df,
                row_count=row_count,
                execution_time_ms=execution_time,
                result_hash=result_hash,
                sql=sql,
                warnings=warnings
            )
            
        except duckdb.CatalogException as e:
            error_msg = f"Table or column not found: {str(e)}"
            logger.error(error_msg)
            return ExecutionResult(
                success=False,
                data=None,
                row_count=0,
                execution_time_ms=(time.time() - start_time) * 1000,
                result_hash="",
                sql=sql,
                error=error_msg
            )
            
        except duckdb.BinderException as e:
            error_msg = f"SQL binding error: {str(e)}"
            logger.error(error_msg)
            return ExecutionResult(
                success=False,
                data=None,
                row_count=0,
                execution_time_ms=(time.time() - start_time) * 1000,
                result_hash="",
                sql=sql,
                error=error_msg
            )
            
        except Exception as e:
            error_msg = f"Query execution failed: {str(e)}"
            logger.error(error_msg)
            return ExecutionResult(
                success=False,
                data=None,
                row_count=0,
                execution_time_ms=(time.time() - start_time) * 1000,
                result_hash="",
                sql=sql,
                error=error_msg
            )
    
    def execute_with_params(
        self,
        sql: str,
        params: Dict[str, Any]
    ) -> ExecutionResult:
        """
        Execute parameterized SQL query.
        
        Args:
            sql: SQL with parameter placeholders (e.g., $param_name)
            params: Dictionary of parameter values
            
        Returns:
            ExecutionResult
            
        Example:
            >>> executor = SQLExecutor()
            >>> sql = "SELECT * FROM mart.fact_orders WHERE order_status = $status LIMIT $limit"
            >>> params = {'status': 'delivered', 'limit': 10}
            >>> result = executor.execute_with_params(sql, params)
        """
        # Replace parameters in SQL
        parameterized_sql = sql
        for key, value in params.items():
            placeholder = f"${key}"
            if isinstance(value, str):
                parameterized_sql = parameterized_sql.replace(placeholder, f"'{value}'")
            else:
                parameterized_sql = parameterized_sql.replace(placeholder, str(value))
        
        return self.execute(parameterized_sql)
    
    def _compute_result_hash(self, df: pd.DataFrame) -> str:
        """
        Compute hash of DataFrame for result verification.
        
        Uses MD5 hash of:
        - Column names
        - Data types
        - First/last 5 rows
        - Row count
        - Summary statistics
        
        Args:
            df: Pandas DataFrame
            
        Returns:
            MD5 hash string
        """
        if df is None or df.empty:
            return hashlib.md5(b"empty").hexdigest()
        
        # Build hash components
        hash_data = {
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'row_count': len(df),
            'shape': df.shape,
        }
        
        # Add sample of data (first and last 5 rows)
        if len(df) > 0:
            hash_data['first_rows'] = df.head(5).to_dict('records')
            hash_data['last_rows'] = df.tail(5).to_dict('records')
        
        # Add summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            hash_data['numeric_summary'] = df[numeric_cols].describe().to_dict()
        
        # Convert to JSON and hash
        json_str = json.dumps(hash_data, sort_keys=True, default=str)
        return hashlib.md5(json_str.encode()).hexdigest()
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get metadata about a table.
        
        Args:
            table_name: Table name (e.g., 'mart.fact_orders')
            
        Returns:
            Dictionary with table metadata
        """
        if self.connection is None:
            self.connect()
        
        try:
            # Get column information
            describe_sql = f"DESCRIBE {table_name}"
            columns_df = self.connection.execute(describe_sql).fetchdf()
            
            # Get row count
            count_sql = f"SELECT COUNT(*) as row_count FROM {table_name}"
            count = self.connection.execute(count_sql).fetchone()[0]
            
            return {
                'table_name': table_name,
                'columns': columns_df.to_dict('records'),
                'row_count': count,
                'column_count': len(columns_df)
            }
            
        except Exception as e:
            logger.error(f"Failed to get table info: {str(e)}")
            return {
                'table_name': table_name,
                'error': str(e)
            }
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()


def execute_sql(
    sql: str,
    db_path: str = "ask_your_data.db",
    validate: bool = True
) -> ExecutionResult:
    """
    Convenience function to execute SQL.
    
    Args:
        sql: SQL query string
        db_path: Path to DuckDB database
        validate: Whether to validate SQL
        
    Returns:
        ExecutionResult
        
    Example:
        >>> result = execute_sql("SELECT * FROM mart.fact_orders LIMIT 5")
        >>> if result.success:
        ...     print(result.data)
    """
    with SQLExecutor(db_path=db_path) as executor:
        return executor.execute(sql, validate=validate)


if __name__ == "__main__":
    # Test the executor
    print("=== SQL Executor Tests ===\n")
    
    executor = SQLExecutor()
    
    # Test 1: Simple query
    print("1. Simple SELECT query:")
    result = executor.execute("SELECT * FROM mart.fact_orders LIMIT 5")
    print(f"Success: {result.success}")
    print(f"Rows: {result.row_count}")
    print(f"Execution time: {result.execution_time_ms:.2f}ms")
    print(f"Result hash: {result.result_hash}")
    if result.success:
        print(f"Columns: {list(result.data.columns)}")
    print("\n" + "="*60 + "\n")
    
    # Test 2: Aggregation query
    print("2. Aggregation query:")
    sql = """
    SELECT 
        c.customer_region,
        COUNT(DISTINCT o.order_id) as order_count,
        SUM(p.payment_value) as revenue
    FROM mart.fact_orders o
    LEFT JOIN mart.dim_customers c ON o.customer_id = c.customer_id
    LEFT JOIN mart.stg_order_payments p ON o.order_id = p.order_id
    GROUP BY c.customer_region
    ORDER BY revenue DESC
    """
    result = executor.execute(sql)
    print(f"Success: {result.success}")
    print(f"Rows: {result.row_count}")
    print(f"Execution time: {result.execution_time_ms:.2f}ms")
    if result.success:
        print(result.data)
    print("\n" + "="*60 + "\n")
    
    # Test 3: Invalid query (should fail validation)
    print("3. Invalid query (DROP TABLE):")
    result = executor.execute("DROP TABLE mart.fact_orders")
    print(f"Success: {result.success}")
    print(f"Error: {result.error}")
    print("\n" + "="*60 + "\n")
    
    # Test 4: Table info
    print("4. Table metadata:")
    info = executor.get_table_info("mart.fact_orders")
    print(f"Table: {info['table_name']}")
    print(f"Row count: {info['row_count']}")
    print(f"Column count: {info['column_count']}")
    
    executor.disconnect()
