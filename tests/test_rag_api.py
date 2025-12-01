"""
Sprint 1 - Ticket 4: RAG API Test Suite
Tests the FastAPI /retrieve endpoint with various queries.

Run this after starting the server with:
    python -m uvicorn src.api.main:app --reload --port 8000
"""

import requests
import json
from typing import Dict, Any


BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_health():
    """Test health check endpoint."""
    print_section("1. Health Check")
    
    response = requests.get(f"{BASE_URL}/")
    data = response.json()
    
    print(f"Status: {data['status']}")
    print(f"Version: {data['version']}")
    print(f"Index Loaded: {data['index_loaded']}")
    print(f"Total Entries: {data['total_entries']}")
    
    assert data['status'] == 'healthy', "Server not healthy"
    assert data['index_loaded'] == True, "Index not loaded"
    print("✓ Health check passed")


def test_retrieve_revenue():
    """Test retrieval for revenue query."""
    print_section("2. Retrieve: Total Revenue Query")
    
    response = requests.get(f"{BASE_URL}/retrieve", params={
        "query": "What is the total revenue?",
        "top_k": 3
    })
    data = response.json()
    
    print(f"Query: {data['query']}")
    print(f"Results: {len(data['results'])}")
    
    for i, result in enumerate(data['results'], 1):
        print(f"\n  {i}. {result['type']}: {result['name']}")
        print(f"     Description: {result['description']}")
        print(f"     Score: {result['score']:.4f}")
        if 'sql_column' in result['metadata']:
            print(f"     SQL: {result['metadata']['sql_column']} ({result['metadata']['table']})")
    
    # Assertions
    assert len(data['results']) > 0, "No results returned"
    assert data['results'][0]['type'] in ['metric', 'business_term'], "Top result should be metric or business term"
    print("\n✓ Revenue query passed")


def test_retrieve_by_state():
    """Test retrieval for state dimension query."""
    print_section("3. Retrieve: Sales by State Query")
    
    response = requests.get(f"{BASE_URL}/retrieve", params={
        "query": "Show me sales by state",
        "top_k": 5
    })
    data = response.json()
    
    print(f"Query: {data['query']}")
    print(f"Results: {len(data['results'])}")
    
    for i, result in enumerate(data['results'], 1):
        print(f"\n  {i}. {result['type']}: {result['name']} (score: {result['score']:.4f})")
    
    # Check for state dimension
    has_state = any('state' in r['name'] for r in data['results'])
    assert has_state, "Should find state-related dimension"
    print("\n✓ State query passed")


def test_sql_context():
    """Test SQL context generation."""
    print_section("4. SQL Context: Revenue by Category")
    
    response = requests.get(f"{BASE_URL}/context/show revenue by product category")
    data = response.json()
    
    print(f"Query: {data['query']}")
    print(f"\nMetrics ({len(data['metrics'])}):")
    for m in data['metrics']:
        print(f"  - {m['name']}: {m['sql_column']} (table: {m['table']})")
    
    print(f"\nDimensions ({len(data['dimensions'])}):")
    for d in data['dimensions']:
        print(f"  - {d['name']}: {d['sql_column']} (table: {d['table']})")
    
    print(f"\nBusiness Terms ({len(data['business_terms'])}):")
    for bt in data['business_terms']:
        print(f"  - {bt['name']}: {bt['description']}")
    
    print(f"\nCommon Patterns ({len(data['common_patterns'])}):")
    for cp in data['common_patterns']:
        print(f"  - {cp['query']}")
        print(f"    Pattern: {cp['sql_pattern'][:80]}...")
    
    # Assertions
    assert len(data['metrics']) > 0, "Should find metrics"
    assert len(data['dimensions']) > 0, "Should find dimensions"
    assert any('revenue' in m['name'] for m in data['metrics']), "Should find revenue metric"
    assert any('category' in d['name'] for d in data['dimensions']), "Should find category dimension"
    print("\n✓ SQL context passed")


def test_list_metrics():
    """Test metrics listing."""
    print_section("5. List All Metrics")
    
    response = requests.get(f"{BASE_URL}/metrics")
    data = response.json()
    
    print(f"Total Metrics: {data['count']}")
    print("\nAvailable Metrics:")
    for m in data['metrics']:
        print(f"  - {m['name']}: {m['description']}")
        print(f"    SQL: {m['aggregation']}({m['sql_column']}) from {m['table']}")
    
    assert data['count'] >= 5, "Should have at least 5 metrics"
    print(f"\n✓ Found {data['count']} metrics")


def test_search_dimensions():
    """Test dimension search."""
    print_section("6. Search Dimensions: Location")
    
    response = requests.get(f"{BASE_URL}/dimensions", params={"query": "location"})
    data = response.json()
    
    print(f"Search Query: {data['query']}")
    print(f"Results: {data['count']}")
    
    for d in data['dimensions']:
        print(f"  - {d['name']}: {d['description']} (score: {d['score']:.4f})")
    
    assert data['count'] > 0, "Should find location-related dimensions"
    print(f"\n✓ Found {data['count']} location dimensions")


def test_filter_by_type():
    """Test filtering by type."""
    print_section("7. Filter by Type: Metrics Only")
    
    response = requests.get(f"{BASE_URL}/retrieve", params={
        "query": "sales revenue orders",
        "top_k": 10,
        "filter_type": "metric"
    })
    data = response.json()
    
    print(f"Query: {data['query']}")
    print(f"Filter: metric")
    print(f"Results: {len(data['results'])}")
    
    for r in data['results']:
        print(f"  - {r['name']} (type: {r['type']})")
    
    # All results should be metrics
    assert all(r['type'] == 'metric' for r in data['results']), "All results should be metrics"
    print("\n✓ Type filtering works")


def run_all_tests():
    """Run all test cases."""
    print("\n" + "=" * 70)
    print("  ASK YOUR DATA - RAG API TEST SUITE")
    print("=" * 70)
    print("\nTesting FastAPI endpoints at:", BASE_URL)
    
    tests = [
        test_health,
        test_retrieve_revenue,
        test_retrieve_by_state,
        test_sql_context,
        test_list_metrics,
        test_search_dimensions,
        test_filter_by_type
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ Test failed: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    print("  TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    return failed == 0


if __name__ == "__main__":
    import sys
    
    print("\nℹ️  Make sure the server is running:")
    print("   python -m uvicorn src.api.main:app --reload --port 8000")
    print("\nPress Enter to start tests or Ctrl+C to cancel...")
    input()
    
    success = run_all_tests()
    sys.exit(0 if success else 1)
