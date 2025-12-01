"""
End-to-End Integration Example - Ticket 5 + Ticket 6
Shows complete flow: NL Query → Intent Parsing → SQL Generation → Execution
"""

import sys
from pathlib import Path
import os

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.nlp.intent_parser import IntentParser
from src.sql.generator import SQLGenerator
from src.sql.executor import SQLExecutor


def demo_end_to_end_flow():
    """
    Demonstrates the complete pipeline from natural language to results.
    
    Flow:
    1. Natural Language Query (user input)
    2. Intent Parsing (Ticket 5) - OpenRouter API
    3. SQL Generation (Ticket 6) - Template-based
    4. SQL Execution (Ticket 6) - DuckDB query
    5. Results Display
    """
    
    print("=" * 80)
    print("ASK YOUR DATA COPILOT - END-TO-END INTEGRATION DEMO")
    print("=" * 80)
    
    # Initialize components
    print("\n📦 Initializing components...")
    parser = IntentParser()
    generator = SQLGenerator()
    executor = SQLExecutor()
    executor.connect()
    
    # Test queries covering different intent types
    test_queries = [
        "What are the top 10 customer states by revenue?",
        "Show me total revenue by region",
        "What is the total revenue?",
        "How many delivered orders in SP?",
        "Show monthly revenue trend for 2017",
    ]
    
    print(f"✓ IntentParser initialized")
    print(f"✓ SQLGenerator initialized")
    print(f"✓ SQLExecutor connected to database")
    
    try:
        for i, query in enumerate(test_queries, 1):
            print("\n" + "=" * 80)
            print(f"QUERY {i}/{len(test_queries)}")
            print("=" * 80)
            
            # Step 1: Natural Language Input
            print(f"\n💬 User Query: \"{query}\"")
            
            # Step 2: Intent Parsing (Ticket 5)
            print(f"\n🔍 Step 1: Parsing intent using OpenRouter API...")
            intent_result = parser.parse(query)
            
            if not intent_result.success:
                print(f"❌ Intent parsing failed: {intent_result.error}")
                continue
            
            intent = intent_result.intent
            print(f"✓ Intent Type: {intent.intent_type}")
            print(f"✓ Confidence: {intent.confidence:.2%}")
            print(f"✓ Metrics: {intent.metrics}")
            print(f"✓ Dimensions: {intent.dimensions}")
            if intent.filters:
                print(f"✓ Filters: {len(intent.filters)}")
            
            # Step 3: SQL Generation (Ticket 6)
            print(f"\n🔧 Step 2: Generating SQL from intent...")
            sql_result = generator.generate(intent)
            
            if not sql_result['is_valid']:
                print(f"❌ SQL generation failed: {sql_result['errors']}")
                continue
            
            sql = sql_result['sql']
            print(f"✓ SQL Generated ({len(sql)} chars)")
            print(f"\nGenerated SQL:\n{sql}")
            
            # Step 4: SQL Execution (Ticket 6)
            print(f"\n⚡ Step 3: Executing SQL on DuckDB...")
            exec_result = executor.execute(sql)
            
            if not exec_result.success:
                print(f"❌ Execution failed: {exec_result.error}")
                continue
            
            print(f"✓ Execution Success")
            print(f"✓ Rows Returned: {exec_result.row_count}")
            print(f"✓ Execution Time: {exec_result.execution_time_ms:.2f}ms")
            print(f"✓ Result Hash: {exec_result.result_hash[:16]}...")
            
            # Step 5: Results Display
            print(f"\n📊 Results:")
            if exec_result.data is not None:
                if exec_result.row_count <= 10:
                    print(exec_result.data.to_string(index=False))
                else:
                    print(exec_result.data.head(10).to_string(index=False))
                    print(f"... ({exec_result.row_count - 10} more rows)")
            
            print(f"\n✅ Query completed successfully!")
            
    finally:
        executor.disconnect()
        print("\n" + "=" * 80)
        print("Demo completed")
        print("=" * 80)


if __name__ == "__main__":
    # Check for API key
    if not os.getenv('OPENROUTER_API_KEY'):
        print("⚠️  Warning: OPENROUTER_API_KEY not found in environment")
        print("Please set it in .env file or environment variables")
        print("\nRunning with limited intent parsing capabilities...")
        print("\nYou can still test SQL generation and execution directly:")
        print("  python src/sql/generator.py")
        print("  python tests/test_sql_generator.py")
    else:
        demo_end_to_end_flow()
