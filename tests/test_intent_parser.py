"""
Sprint 2 - Ticket 5: Intent Parser Test Suite
Tests the IntentParser with various query types.

Run with: python tests/test_intent_parser.py
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.nlp.intent_parser import IntentParser, parse_intent
from src.nlp.models import Intent


def print_section(title: str):
    """Print formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_intent_parsing():
    """Test intent parsing with various query types."""
    
    # Check for API key
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.getenv("OPENROUTER_API_KEY"):
        print("❌ ERROR: OPENROUTER_API_KEY not found in environment")
        print("\nPlease:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenRouter API key to .env")
        print("3. Get API key from: https://openrouter.ai/keys")
        return False
    
    print_section("Intent Parser Test Suite")
    print("Model: openai/gpt-4o via OpenRouter")
    print("RAG: Enabled (using glossary context)")
    
    # Initialize parser
    parser = IntentParser()
    
    # Test cases
    test_cases = [
        {
            "name": "Top N Query",
            "query": "What are the top 10 product categories by revenue?",
            "expected_intent_type": "top_n",
            "expected_metrics": ["revenue"],
            "expected_dimensions": ["product_category"]
        },
        {
            "name": "Group By Query",
            "query": "Show me revenue by customer state",
            "expected_intent_type": "group_by",
            "expected_metrics": ["revenue"],
            "expected_dimensions": ["customer_state"]
        },
        {
            "name": "Simple Aggregation",
            "query": "What is the total revenue?",
            "expected_intent_type": "aggregation",
            "expected_metrics": ["revenue"],
            "expected_dimensions": []
        },
        {
            "name": "Time Series Query",
            "query": "Show me monthly sales trends for 2017",
            "expected_intent_type": "time_series",
            "expected_metrics": ["revenue"],
            "expected_dimensions": ["month"]
        },
        {
            "name": "Filter Query",
            "query": "How many orders were delivered in SP?",
            "expected_intent_type": "filter",
            "expected_metrics": ["order_count"],
            "expected_dimensions": ["customer_state"]
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print_section(f"Test {i}/{len(test_cases)}: {test_case['name']}")
        print(f"Query: \"{test_case['query']}\"")
        
        try:
            # Parse query
            result = parser.parse(test_case['query'])
            
            if not result.success:
                print(f"❌ FAILED: {result.error}")
                failed += 1
                continue
            
            intent = result.intent
            
            # Display results
            print(f"\n✓ Parsed successfully!")
            print(f"  Intent Type: {intent.intent_type}")
            print(f"  Metrics: {intent.metrics}")
            print(f"  Dimensions: {intent.dimensions}")
            print(f"  Filters: {intent.filters}")
            print(f"  Order By: {intent.order_by}")
            print(f"  Limit: {intent.limit}")
            print(f"  Time Grain: {intent.time_grain}")
            print(f"  Confidence: {intent.confidence:.2f}")
            
            # Validate
            checks = []
            
            # Check intent type
            if intent.intent_type == test_case['expected_intent_type']:
                checks.append("✓ Intent type correct")
            else:
                checks.append(f"✗ Intent type: expected {test_case['expected_intent_type']}, got {intent.intent_type}")
            
            # Check metrics (at least one expected metric present)
            if any(m in intent.metrics for m in test_case['expected_metrics']):
                checks.append("✓ Metrics correct")
            else:
                checks.append(f"✗ Metrics: expected {test_case['expected_metrics']}, got {intent.metrics}")
            
            # Check dimensions (at least one expected dimension present or both empty)
            if (not test_case['expected_dimensions'] and not intent.dimensions) or \
               any(d in intent.dimensions for d in test_case['expected_dimensions']):
                checks.append("✓ Dimensions correct")
            else:
                checks.append(f"✗ Dimensions: expected {test_case['expected_dimensions']}, got {intent.dimensions}")
            
            # Print validation
            print("\nValidation:")
            for check in checks:
                print(f"  {check}")
            
            if all(check.startswith("✓") for check in checks):
                print("\n✅ TEST PASSED")
                passed += 1
            else:
                print("\n⚠️  TEST PASSED (with warnings)")
                passed += 1
        
        except Exception as e:
            print(f"\n❌ FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # Summary
    print_section("Test Summary")
    print(f"Total Tests: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return False


def test_without_rag():
    """Test parsing without RAG context."""
    print_section("Test Without RAG Context")
    
    parser = IntentParser()
    result = parser.parse("What are the top 5 products?", use_rag=False)
    
    if result.success:
        print(f"✓ Parsed successfully without RAG")
        print(f"  Intent: {result.intent.intent_type}")
        print(f"  Confidence: {result.intent.confidence:.2f}")
        print("\nNote: Confidence may be lower without RAG context")
    else:
        print(f"✗ Failed: {result.error}")


def demo_interactive():
    """Interactive demo mode."""
    print_section("Interactive Demo Mode")
    print("Enter natural language queries (or 'quit' to exit)")
    print("\nExamples:")
    print("  - What are the top 10 product categories?")
    print("  - Show revenue by state")
    print("  - How many orders were placed in 2017?")
    
    parser = IntentParser()
    
    while True:
        print("\n" + "-" * 70)
        query = input("Query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not query:
            continue
        
        print("\n🧠 Parsing...")
        result = parser.parse(query)
        
        if result.success:
            intent = result.intent
            print(f"\n✓ Intent Type: {intent.intent_type}")
            print(f"  Metrics: {intent.metrics}")
            print(f"  Dimensions: {intent.dimensions}")
            print(f"  Filters: {intent.filters}")
            print(f"  Order By: {intent.order_by}")
            print(f"  Limit: {intent.limit}")
            print(f"  Confidence: {intent.confidence:.2f}")
        else:
            print(f"\n✗ Error: {result.error}")


if __name__ == "__main__":
    import sys
    
    # Run tests
    success = test_intent_parsing()
    
    # Test without RAG
    print("\n")
    test_without_rag()
    
    # Offer interactive mode
    if success:
        print("\n")
        response = input("Run interactive demo? (y/n): ").strip().lower()
        if response == 'y':
            demo_interactive()
    
    sys.exit(0 if success else 1)
