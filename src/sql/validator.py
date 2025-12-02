"""
Simple SQL validator - basic safety checks
"""


def validate_sql(sql: str) -> dict:
    """
    Validate SQL for safety.
    
    Returns dict with:
    - is_valid: bool
    - errors: list of error strings
    """
    sql_upper = sql.upper()
    
    # Block dangerous operations
    dangerous = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE', 'TRUNCATE']
    
    errors = []
    for word in dangerous:
        if word in sql_upper:
            errors.append(f"Blocked keyword: {word}")
    
    # Must contain SELECT
    if 'SELECT' not in sql_upper:
        errors.append("Query must contain SELECT")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors
    }
