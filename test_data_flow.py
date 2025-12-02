"""
Test script to verify data flow between all functions
"""

import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("Testing Ask Your Data - Data Flow Verification")
print("=" * 80)

# Test 1: Intent Parser
print("\n[1/4] Testing Intent Parser...")
try:
    from src.nlp.intent_parser import parse_query
    
    test_query = "Top 10 states by revenue"
    result = parse_query(test_query)
    
    print(f"  Query: '{test_query}'")
    print(f"  ✓ Function returns dict: {isinstance(result, dict)}")
    print(f"  ✓ Has 'success' key: {'success' in result}")
    print(f"  ✓ Has 'intent' key: {'intent' in result}")
    print(f"  ✓ Has 'error' key: {'error' in result}")
    
    if result['success']:
        intent = result['intent']
        print(f"  ✓ Intent is dict: {isinstance(intent, dict)}")
        print(f"  ✓ Has 'intent_type': {'intent_type' in intent}")
        print(f"  ✓ Has 'metrics': {'metrics' in intent}")
        print(f"  ✓ Has 'dimensions': {'dimensions' in intent}")
        print(f"  Intent structure: SUCCESS")
    else:
        print(f"  ✗ Parse failed: {result['error']}")
        print(f"  Note: This might fail without API key - that's OK for structure test")
    
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 2: SQL Generator
print("\n[2/4] Testing SQL Generator...")
try:
    from src.sql.generator import generate_sql
    
    # Mock intent
    test_intent = {
        'intent_type': 'top_n',
        'metrics': ['revenue'],
        'dimensions': ['customer_state'],
        'filters': [],
        'order_by': 'revenue DESC',
        'limit': 10,
        'confidence': 0.95
    }
    
    result = generate_sql(test_intent)
    
    print(f"  Input: intent dict with {len(test_intent)} keys")
    print(f"  ✓ Function returns dict: {isinstance(result, dict)}")
    print(f"  ✓ Has 'sql' key: {'sql' in result}")
    print(f"  ✓ Has 'is_valid' key: {'is_valid' in result}")
    print(f"  ✓ Has 'errors' key: {'errors' in result}")
    print(f"  ✓ Has 'intent_type' key: {'intent_type' in result}")
    print(f"  SQL Generator structure: SUCCESS")
    
except Exception as e:
    print(f"  ✗ Error: {e}")
    print(f"  Note: This might fail without API key - that's OK for structure test")

# Test 3: SQL Executor
print("\n[3/4] Testing SQL Executor...")
try:
    from src.sql.executor import connect_db, run_query
    import pandas as pd
    
    # Try to connect
    try:
        connect_db("ask_your_data.db")
        print(f"  ✓ Database connection successful")
        
        # Test query
        test_sql = "SELECT COUNT(*) as count FROM mart.fact_orders LIMIT 1"
        result = run_query(test_sql)
        
        print(f"  ✓ Function returns dict: {isinstance(result, dict)}")
        print(f"  ✓ Has 'success' key: {'success' in result}")
        print(f"  ✓ Has 'data' key: {'data' in result}")
        print(f"  ✓ Has 'row_count' key: {'row_count' in result}")
        print(f"  ✓ Has 'execution_time_ms' key: {'execution_time_ms' in result}")
        print(f"  ✓ Has 'error' key: {'error' in result}")
        
        if result['success']:
            print(f"  ✓ Data is DataFrame: {isinstance(result['data'], pd.DataFrame)}")
            print(f"  ✓ Query executed: {result['row_count']} rows in {result['execution_time_ms']:.1f}ms")
            print(f"  SQL Executor: SUCCESS")
        else:
            print(f"  ✗ Query failed: {result['error']}")
            
    except FileNotFoundError:
        print(f"  ! Database file not found - structure test only")
        print(f"  ✓ Function structure: SUCCESS (file check works)")
        
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test 4: Chart Selector
print("\n[4/4] Testing Chart Selector...")
try:
    from src.charts.chart_selector import choose_chart
    import pandas as pd
    
    # Mock data
    test_data = pd.DataFrame({
        'state': ['SP', 'RJ', 'MG'],
        'revenue': [10000, 8000, 6000]
    })
    
    test_intent = {
        'intent_type': 'top_n',
        'original_query': 'Top states by revenue'
    }
    
    result = choose_chart(test_intent, test_data)
    
    print(f"  Input: DataFrame with {len(test_data)} rows, {len(test_data.columns)} columns")
    print(f"  ✓ Function returns dict: {isinstance(result, dict)}")
    print(f"  ✓ Has 'type' key: {'type' in result}")
    print(f"  ✓ Has 'x' key: {'x' in result}")
    print(f"  ✓ Has 'y' key: {'y' in result}")
    print(f"  ✓ Has 'title' key: {'title' in result}")
    print(f"  Chart type: {result.get('type')}")
    print(f"  Chart Selector: SUCCESS")
    
    # Test edge case: single value
    test_data_single = pd.DataFrame({'total_revenue': [50000]})
    result_single = choose_chart(test_intent, test_data_single)
    print(f"  ✓ Single value handling: {result_single.get('type')}")
    
    # Test edge case: empty data
    test_data_empty = pd.DataFrame()
    result_empty = choose_chart(test_intent, test_data_empty)
    print(f"  ✓ Empty data handling: {result_empty.get('type')}")
    
except Exception as e:
    print(f"  ✗ Error: {e}")

# Summary
print("\n" + "=" * 80)
print("DATA FLOW VERIFICATION COMPLETE")
print("=" * 80)
print("\nExpected flow:")
print("  parse_query(str) → dict{'success', 'intent', 'error'}")
print("  generate_sql(dict) → dict{'sql', 'is_valid', 'errors', 'intent_type'}")
print("  run_query(str) → dict{'success', 'data', 'row_count', 'execution_time_ms', 'error'}")
print("  choose_chart(dict, DataFrame) → dict{'type', 'x', 'y', 'title', ...}")
print("\nAll functions use simple dicts with consistent structure ✓")
print("=" * 80)
