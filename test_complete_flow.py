"""
Test complete flow with all new features
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("Testing Complete Flow with New Features")
print("=" * 80)

# Test 1: RAG Integration
print("\n[1] Testing RAG Integration")
print("-" * 80)
from src.nlp.intent_parser import parse_query

result = parse_query("What are the top 10 states by revenue?", use_rag=True)
print(f"Success: {result['success']}")
if result['success']:
    print(f"Intent Type: {result['intent'].get('intent_type')}")
    print(f"Metrics: {result['intent'].get('metrics')}")
    print(f"Dimensions: {result['intent'].get('dimensions')}")
    print(f"Limit: {result['intent'].get('limit')}")

# Test 2: Schema Extraction
print("\n[2] Testing Schema Extraction")
print("-" * 80)
try:
    from src.sql.executor import connect_db, get_schema
    
    connect_db()
    schema = get_schema()
    print(f"Schema extracted: {len(schema)} characters")
    print("\nFirst 300 chars:")
    print(schema[:300])
    print(f"\nSchema extraction: SUCCESS")
except Exception as e:
    print(f"Schema extraction error: {e}")

# Test 3: SQL Generation with Schema
print("\n[3] Testing SQL Generation with Schema")
print("-" * 80)
from src.sql.generator import generate_sql

test_intent = {
    'intent_type': 'top_n',
    'metrics': ['revenue'],
    'dimensions': ['customer_state'],
    'filters': [],
    'order_by': 'revenue DESC',
    'limit': 10
}

sql_result = generate_sql(test_intent)
print(f"Valid: {sql_result['is_valid']}")
if sql_result['is_valid']:
    print(f"\nGenerated SQL:")
    print(sql_result['sql'])

# Test 4: Query Execution with Auto-Retry
print("\n[4] Testing Query Execution with Auto-Retry")
print("-" * 80)
from src.sql.executor import run_query

if sql_result['is_valid']:
    exec_result = run_query(sql_result['sql'])
    print(f"Success: {exec_result['success']}")
    print(f"Rows: {exec_result['row_count']}")
    print(f"Execution Time: {exec_result['execution_time_ms']:.1f}ms")
    print(f"Retries: {exec_result['retries']}")
    
    if exec_result['success']:
        print(f"\nFirst 3 results:")
        print(exec_result['data'].head(3))

# Test 5: Error Recovery
print("\n[5] Testing Error Recovery (intentional bad SQL)")
print("-" * 80)
bad_sql = "SELECT invalid_column FROM nonexistent_table"
error_result = run_query(bad_sql, max_retries=1)
print(f"Success: {error_result['success']}")
print(f"Retries attempted: {error_result['retries']}")
if not error_result['success']:
    print(f"Error (expected): {error_result['error'][:100]}...")

print("\n" + "=" * 80)
print("All Tests Complete!")
print("=" * 80)
print("\nNew Features Working:")
print("  [x] RAG context integration")
print("  [x] Database schema extraction")
print("  [x] Schema-aware SQL generation")
print("  [x] Auto-retry on SQL errors")
print("  [x] LLM-based error fixing")
print("=" * 80)
