"""
SQL Validator - Sprint 2, Ticket 6
Validates SQL queries for safety, preventing DDL/DML operations.
Ensures only SELECT statements are executed.
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of SQL validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    sanitized_sql: str = ""


class SQLValidator:
    """
    Validates SQL queries for safety and correctness.
    
    Prevents:
    - DDL operations (CREATE, DROP, ALTER, TRUNCATE)
    - DML operations (INSERT, UPDATE, DELETE, MERGE)
    - System commands (GRANT, REVOKE, EXECUTE)
    - SQL injection patterns
    
    Allows:
    - SELECT statements only
    - Common functions (SUM, COUNT, AVG, etc.)
    - JOINs, WHERE, GROUP BY, ORDER BY, LIMIT
    """
    
    # Dangerous SQL keywords that should be blocked
    BLOCKED_KEYWORDS = [
        # DDL (Data Definition Language)
        'CREATE', 'DROP', 'ALTER', 'TRUNCATE', 'RENAME',
        
        # DML (Data Modification Language) - except SELECT
        'INSERT', 'UPDATE', 'DELETE', 'MERGE', 'REPLACE',
        
        # DCL (Data Control Language)
        'GRANT', 'REVOKE',
        
        # TCL (Transaction Control Language)
        'COMMIT', 'ROLLBACK', 'SAVEPOINT',
        
        # System/Admin commands
        'EXECUTE', 'EXEC', 'CALL', 'ATTACH', 'DETACH',
        'PRAGMA', 'VACUUM', 'ANALYZE',
        
        # File operations
        'COPY', 'EXPORT', 'IMPORT', 'LOAD',
    ]
    
    # Allowed SQL keywords
    ALLOWED_KEYWORDS = [
        'SELECT', 'FROM', 'WHERE', 'GROUP BY', 'HAVING', 'ORDER BY',
        'LIMIT', 'OFFSET', 'AS', 'JOIN', 'INNER', 'LEFT', 'RIGHT',
        'OUTER', 'ON', 'AND', 'OR', 'NOT', 'IN', 'BETWEEN', 'LIKE',
        'DISTINCT', 'UNION', 'INTERSECT', 'EXCEPT', 'WITH', 'CASE',
        'WHEN', 'THEN', 'ELSE', 'END', 'CAST', 'COALESCE', 'NULLIF',
    ]
    
    # Common aggregate and scalar functions
    ALLOWED_FUNCTIONS = [
        'SUM', 'COUNT', 'AVG', 'MIN', 'MAX', 'STDDEV', 'VARIANCE',
        'ROUND', 'FLOOR', 'CEIL', 'ABS', 'SQRT', 'POWER',
        'UPPER', 'LOWER', 'TRIM', 'LENGTH', 'SUBSTRING', 'CONCAT',
        'DATE', 'YEAR', 'MONTH', 'DAY', 'EXTRACT', 'DATE_DIFF',
        'DATEDIFF', 'CURRENT_DATE', 'CURRENT_TIMESTAMP',
    ]
    
    # SQL injection patterns to detect
    INJECTION_PATTERNS = [
        r';\s*DROP\s+TABLE',
        r';\s*DELETE\s+FROM',
        r';\s*UPDATE\s+.*SET',
        r'--\s*$',  # SQL comment at end
        r'/\*.*\*/',  # Multi-line comment
        r"'\s*OR\s+'1'\s*=\s*'1",  # Classic injection
        r'UNION\s+SELECT.*FROM\s+information_schema',
    ]
    
    def __init__(self):
        """Initialize SQL validator."""
        self.blocked_pattern = re.compile(
            r'\b(' + '|'.join(self.BLOCKED_KEYWORDS) + r')\b',
            re.IGNORECASE
        )
        
        self.injection_patterns = [
            re.compile(pattern, re.IGNORECASE | re.DOTALL)
            for pattern in self.INJECTION_PATTERNS
        ]
    
    def validate(self, sql: str) -> ValidationResult:
        """
        Validate SQL query for safety.
        
        Args:
            sql: SQL query string to validate
            
        Returns:
            ValidationResult with validation status and messages
            
        Example:
            >>> validator = SQLValidator()
            >>> result = validator.validate("SELECT * FROM orders")
            >>> assert result.is_valid == True
            >>> result = validator.validate("DROP TABLE orders")
            >>> assert result.is_valid == False
        """
        errors = []
        warnings = []
        
        if not sql or not sql.strip():
            errors.append("SQL query is empty")
            return ValidationResult(False, errors, warnings)
        
        sql = sql.strip()
        
        # Check for blocked keywords (DDL/DML)
        blocked_matches = self.blocked_pattern.findall(sql)
        if blocked_matches:
            errors.append(
                f"Blocked SQL keywords detected: {', '.join(set(blocked_matches))}. "
                "Only SELECT queries are allowed."
            )
        
        # Check for SQL injection patterns
        for pattern in self.injection_patterns:
            if pattern.search(sql):
                errors.append(
                    f"Potential SQL injection pattern detected: {pattern.pattern}"
                )
        
        # Check if query starts with SELECT
        sql_upper = sql.upper().strip()
        if not sql_upper.startswith('SELECT') and not sql_upper.startswith('WITH'):
            errors.append(
                "Query must start with SELECT or WITH (for CTEs). "
                f"Found: {sql.split()[0] if sql.split() else 'unknown'}"
            )
        
        # Check for multiple statements (semicolon-separated)
        # Allow semicolon only at the end
        semicolon_count = sql.count(';')
        if semicolon_count > 1:
            errors.append(
                "Multiple SQL statements detected. Only single SELECT queries allowed."
            )
        elif semicolon_count == 1 and not sql.rstrip().endswith(';'):
            errors.append(
                "Semicolon detected in middle of query. Potential SQL injection."
            )
        
        # Sanitize SQL (remove trailing semicolon if present)
        sanitized_sql = sql.rstrip(';').strip()
        
        # Warnings for potentially problematic patterns
        if re.search(r'SELECT\s+\*', sql, re.IGNORECASE):
            warnings.append(
                "Using SELECT * may return excessive data. Consider specifying columns."
            )
        
        if not re.search(r'\bLIMIT\b', sql, re.IGNORECASE):
            warnings.append(
                "No LIMIT clause detected. Query may return large result set."
            )
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            sanitized_sql=sanitized_sql if is_valid else ""
        )
    
    def sanitize_identifier(self, identifier: str) -> str:
        """
        Sanitize table/column identifier to prevent injection.
        
        Args:
            identifier: Table or column name
            
        Returns:
            Sanitized identifier
            
        Example:
            >>> validator = SQLValidator()
            >>> validator.sanitize_identifier("users; DROP TABLE--")
            'users_DROP_TABLE'
        """
        # Remove non-alphanumeric characters except underscore and dot
        sanitized = re.sub(r'[^a-zA-Z0-9_.]', '_', identifier)
        
        # Remove leading/trailing underscores
        sanitized = sanitized.strip('_')
        
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = 'col_' + sanitized
        
        return sanitized
    
    def validate_table_name(self, table_name: str, allowed_schemas: List[str] = None) -> Tuple[bool, str]:
        """
        Validate table name against allowed schemas.
        
        Args:
            table_name: Table name (may include schema like 'mart.fact_orders')
            allowed_schemas: List of allowed schema names (default: ['mart', 'raw', 'dimensions'])
            
        Returns:
            Tuple of (is_valid, error_message)
            
        Example:
            >>> validator = SQLValidator()
            >>> is_valid, msg = validator.validate_table_name("mart.fact_orders")
            >>> assert is_valid == True
            >>> is_valid, msg = validator.validate_table_name("information_schema.tables")
            >>> assert is_valid == False
        """
        if allowed_schemas is None:
            allowed_schemas = ['mart', 'raw', 'dimensions']
        
        # Check for schema.table format
        if '.' in table_name:
            parts = table_name.split('.')
            if len(parts) != 2:
                return False, f"Invalid table name format: {table_name}"
            
            schema, table = parts
            if schema not in allowed_schemas:
                return False, f"Schema '{schema}' not in allowed list: {allowed_schemas}"
        
        # Check for SQL injection in table name
        if re.search(r'[;\'"\\]', table_name):
            return False, f"Invalid characters in table name: {table_name}"
        
        return True, ""
    
    def validate_column_name(self, column_name: str) -> Tuple[bool, str]:
        """
        Validate column name for safety.
        
        Args:
            column_name: Column name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Allow alphanumeric, underscore, and dot (for table.column)
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', column_name):
            return False, f"Invalid column name format: {column_name}"
        
        return True, ""


def validate_sql(sql: str) -> ValidationResult:
    """
    Convenience function to validate SQL.
    
    Args:
        sql: SQL query string
        
    Returns:
        ValidationResult
        
    Example:
        >>> result = validate_sql("SELECT * FROM mart.fact_orders LIMIT 10")
        >>> print(result.is_valid)
        True
    """
    validator = SQLValidator()
    return validator.validate(sql)


if __name__ == "__main__":
    # Test the validator
    validator = SQLValidator()
    
    print("=== SQL Validator Tests ===\n")
    
    # Valid queries
    valid_queries = [
        "SELECT * FROM mart.fact_orders LIMIT 10",
        "SELECT customer_state, SUM(payment_value) FROM mart.fact_orders GROUP BY customer_state",
        "WITH cte AS (SELECT * FROM mart.dim_customers) SELECT * FROM cte",
    ]
    
    print("Valid queries:")
    for sql in valid_queries:
        result = validator.validate(sql)
        print(f"✓ {sql[:50]}... → Valid: {result.is_valid}")
        if result.warnings:
            print(f"  Warnings: {result.warnings}")
    
    print("\n" + "="*60 + "\n")
    
    # Invalid queries
    invalid_queries = [
        "DROP TABLE mart.fact_orders",
        "DELETE FROM mart.fact_orders WHERE order_id = 1",
        "SELECT * FROM mart.fact_orders; DROP TABLE users--",
        "INSERT INTO mart.fact_orders VALUES (1, 2, 3)",
        "UPDATE mart.fact_orders SET order_status = 'canceled'",
    ]
    
    print("Invalid queries (should be blocked):")
    for sql in invalid_queries:
        result = validator.validate(sql)
        print(f"✗ {sql[:50]}... → Valid: {result.is_valid}")
        if result.errors:
            print(f"  Errors: {result.errors[0]}")
