"""
Simple test to verify model debugging works
"""

import sys
from pathlib import Path
import os

# Add project root
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

print("=" * 80)
print("Testing Model Debugging")
print("=" * 80)

# Show env configuration
from dotenv import load_dotenv
load_dotenv()

print(f"\nEnvironment Configuration:")
print(f"  OPENROUTER_MODEL: {os.getenv('OPENROUTER_MODEL', 'not set')}")
print(f"  API Key: {os.getenv('OPENROUTER_API_KEY', 'not set')[:15]}...")

# Test Intent Parser
print("\n" + "=" * 80)
print("Test 1: Intent Parser with Debugging")
print("=" * 80)

from src.nlp.intent_parser import parse_query

result = parse_query("Top 10 states by revenue")

print(f"\nResult:")
print(f"  Success: {result['success']}")
if result['success']:
    intent = result['intent']
    print(f"  Intent Type: {intent.get('intent_type')}")
    print(f"  Metrics: {intent.get('metrics')}")
    print(f"  Dimensions: {intent.get('dimensions')}")
    print(f"  Limit: {intent.get('limit')}")
else:
    print(f"  Error: {result['error']}")

# Test SQL Generator
print("\n" + "=" * 80)
print("Test 2: SQL Generator with Debugging")
print("=" * 80)

from src.sql.generator import generate_sql

test_intent = {
    'intent_type': 'top_n',
    'metrics': ['revenue'],
    'dimensions': ['customer_state'],
    'filters': [],
    'order_by': 'revenue DESC',
    'limit': 10
}

result = generate_sql(test_intent)

print(f"\nResult:")
print(f"  Valid: {result['is_valid']}")
if result['is_valid']:
    print(f"  SQL (first 100 chars): {result['sql'][:100]}...")
else:
    print(f"  Errors: {result['errors']}")

print("\n" + "=" * 80)
print("Debugging Complete!")
print("=" * 80)
print("\nYou should see [DEBUG] output above showing:")
print("  - Which model is being used")
print("  - API key (masked)")
print("  - Response status")
print("  - Model that actually responded")
print("=" * 80)
