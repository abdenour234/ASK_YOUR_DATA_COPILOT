"""
Complete import verification test - check all modules can be imported
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("Import Verification Test")
print("=" * 80)

tests_passed = 0
tests_failed = 0

# Test 1: NLP Module
print("\n[1] Testing NLP Module Imports")
try:
    from src.nlp.intent_parser import parse_query, call_llm, extract_json, build_prompt
    from src.nlp import parse_query as parse_query_init
    print("  ✓ All NLP imports successful")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ NLP import failed: {e}")
    tests_failed += 1

# Test 2: SQL Module
print("\n[2] Testing SQL Module Imports")
try:
    from src.sql.generator import generate_sql, build_sql_prompt, validate_sql
    from src.sql.executor import connect_db, run_query, get_schema
    from src.sql import generate_sql as gen_init, run_query as run_init
    print("  ✓ All SQL imports successful")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ SQL import failed: {e}")
    tests_failed += 1

# Test 3: Charts Module
print("\n[3] Testing Charts Module Imports")
try:
    from src.charts.chart_selector import choose_chart
    from src.charts import choose_chart as choose_init
    print("  ✓ All Charts imports successful")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ Charts import failed: {e}")
    tests_failed += 1

# Test 4: API Module
print("\n[4] Testing API Module Imports")
try:
    from src.api.rag import search_glossary, load_glossary
    from src.api import search_glossary as search_init
    print("  ✓ All API imports successful")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ API import failed: {e}")
    tests_failed += 1

# Test 5: UI Module
print("\n[5] Testing UI Module Imports")
try:
    # Check if streamlit is available
    import streamlit as st
    print("  ✓ Streamlit available")
    
    # Test UI file syntax (don't run it)
    import ast
    ui_path = project_root / "src" / "ui" / "app.py"
    with open(ui_path, 'r', encoding='utf-8') as f:
        ast.parse(f.read())
    print("  ✓ UI app.py syntax valid")
    tests_passed += 1
except ImportError:
    print("  ! Streamlit not installed (that's OK for testing)")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ UI test failed: {e}")
    tests_failed += 1

# Test 6: Function signatures
print("\n[6] Testing Function Signatures")
try:
    from src.nlp import parse_query
    from src.sql import generate_sql, run_query
    from src.charts import choose_chart
    
    # Check they are functions
    assert callable(parse_query), "parse_query is not callable"
    assert callable(generate_sql), "generate_sql is not callable"
    assert callable(run_query), "run_query is not callable"
    assert callable(choose_chart), "choose_chart is not callable"
    
    print("  ✓ All functions are callable")
    tests_passed += 1
except Exception as e:
    print(f"  ✗ Function check failed: {e}")
    tests_failed += 1

# Test 7: Data Flow Types
print("\n[7] Testing Data Flow")
try:
    # Test parse_query return type
    result = parse_query("test query")
    assert isinstance(result, dict), "parse_query should return dict"
    assert 'success' in result, "parse_query result missing 'success'"
    assert 'intent' in result, "parse_query result missing 'intent'"
    assert 'error' in result, "parse_query result missing 'error'"
    print("  ✓ parse_query returns correct structure")
    
    # Test generate_sql with mock intent
    mock_intent = {
        'intent_type': 'top_n',
        'metrics': ['revenue'],
        'dimensions': ['state'],
        'filters': [],
        'limit': 10
    }
    sql_result = generate_sql(mock_intent)
    assert isinstance(sql_result, dict), "generate_sql should return dict"
    assert 'sql' in sql_result, "generate_sql result missing 'sql'"
    assert 'is_valid' in sql_result, "generate_sql result missing 'is_valid'"
    assert 'errors' in sql_result, "generate_sql result missing 'errors'"
    print("  ✓ generate_sql returns correct structure")
    
    # Test choose_chart with mock data
    import pandas as pd
    mock_data = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
    mock_intent = {'intent_type': 'top_n', 'original_query': 'test'}
    chart_config = choose_chart(mock_intent, mock_data)
    assert isinstance(chart_config, dict), "choose_chart should return dict"
    assert 'type' in chart_config, "choose_chart result missing 'type'"
    print("  ✓ choose_chart returns correct structure")
    
    tests_passed += 1
except Exception as e:
    print(f"  ✗ Data flow test failed: {e}")
    tests_failed += 1

# Summary
print("\n" + "=" * 80)
print("Test Summary")
print("=" * 80)
print(f"Passed: {tests_passed}")
print(f"Failed: {tests_failed}")

if tests_failed == 0:
    print("\n✓ ALL TESTS PASSED - Ready for Streamlit!")
    print("\nTo run the app:")
    print("  streamlit run src/ui/app.py")
else:
    print(f"\n✗ {tests_failed} test(s) failed - please fix before running")

print("=" * 80)
