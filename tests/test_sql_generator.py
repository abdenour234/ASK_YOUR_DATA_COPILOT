"""
SQL Generator Test Suite - Sprint 2, Ticket 6
Tests for SQL generation from Intent objects to executable queries.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.nlp.models import Intent, Filter, DateRange
from src.sql.generator import SQLGenerator, generate_sql
from src.sql.executor import SQLExecutor
from src.sql.validator import SQLValidator


class TestSQLGeneration:
    """Test SQL generation for all intent types."""
    
    def __init__(self):
        self.generator = SQLGenerator()
        self.executor = SQLExecutor()
        self.validator = SQLValidator()
        self.passed = 0
        self.failed = 0
    
    def test_top_n_query(self):
        """Test TOP N query generation."""
        print("\n" + "="*70)
        print("TEST 1: Top N Query - Top 10 customer states by revenue")
        print("="*70)
        
        intent = Intent(
            intent_type='top_n',
            metrics=['revenue'],
            dimensions=['customer_state'],
            filters=[],
            limit=10,
            order_by='revenue DESC',
            confidence=0.95,
            original_query='What are the top 10 customer states by revenue?'
        )
        
        result = self.generator.generate(intent)
        
        print(f"\n✓ SQL Generated ({len(result['sql'])} chars)")
        print(f"✓ Valid: {result['is_valid']}")
        print(f"✓ Intent Type: {result['intent_type']}")
        print(f"✓ Metrics: {result['metrics']}")
        print(f"✓ Dimensions: {result['dimensions']}")
        
        if result['warnings']:
            print(f"⚠ Warnings: {result['warnings']}")
        
        print(f"\nGenerated SQL:\n{result['sql']}")
        
        # Execute the query
        exec_result = self.executor.execute(result['sql'])
        print(f"\n✓ Execution Success: {exec_result.success}")
        print(f"✓ Rows Returned: {exec_result.row_count}")
        print(f"✓ Execution Time: {exec_result.execution_time_ms:.2f}ms")
        print(f"✓ Result Hash: {exec_result.result_hash}")
        
        if exec_result.success and exec_result.data is not None:
            print(f"\nSample Results:")
            print(exec_result.data.head())
        
        if result['is_valid'] and exec_result.success:
            self.passed += 1
            print("\n✅ TEST PASSED")
        else:
            self.failed += 1
            print(f"\n❌ TEST FAILED: {exec_result.error}")
    
    def test_group_by_query(self):
        """Test GROUP BY query generation."""
        print("\n" + "="*70)
        print("TEST 2: Group By Query - Revenue and order count by region")
        print("="*70)
        
        intent = Intent(
            intent_type='group_by',
            metrics=['revenue', 'order_count'],
            dimensions=['customer_region'],
            filters=[],
            order_by='revenue DESC',
            confidence=0.92,
            original_query='Show me revenue and order count by customer region'
        )
        
        result = self.generator.generate(intent)
        
        print(f"\n✓ SQL Generated")
        print(f"✓ Valid: {result['is_valid']}")
        print(f"\nGenerated SQL:\n{result['sql']}")
        
        exec_result = self.executor.execute(result['sql'])
        print(f"\n✓ Execution Success: {exec_result.success}")
        print(f"✓ Rows: {exec_result.row_count}")
        print(f"✓ Time: {exec_result.execution_time_ms:.2f}ms")
        
        if exec_result.success and exec_result.data is not None:
            print(f"\nResults:")
            print(exec_result.data)
        
        if result['is_valid'] and exec_result.success:
            self.passed += 1
            print("\n✅ TEST PASSED")
        else:
            self.failed += 1
            print(f"\n❌ TEST FAILED: {exec_result.error}")
    
    def test_aggregation_query(self):
        """Test simple aggregation query."""
        print("\n" + "="*70)
        print("TEST 3: Aggregation Query - Total revenue")
        print("="*70)
        
        intent = Intent(
            intent_type='aggregation',
            metrics=['revenue'],
            dimensions=[],
            filters=[],
            confidence=0.98,
            original_query='What is the total revenue?'
        )
        
        result = self.generator.generate(intent)
        
        print(f"\n✓ SQL Generated")
        print(f"✓ Valid: {result['is_valid']}")
        print(f"\nGenerated SQL:\n{result['sql']}")
        
        exec_result = self.executor.execute(result['sql'])
        print(f"\n✓ Execution Success: {exec_result.success}")
        
        if exec_result.success and exec_result.data is not None:
            print(f"\nResult:")
            print(exec_result.data)
            total_revenue = exec_result.data['revenue'].values[0]
            print(f"\n💰 Total Revenue: R$ {total_revenue:,.2f}")
        
        if result['is_valid'] and exec_result.success:
            self.passed += 1
            print("\n✅ TEST PASSED")
        else:
            self.failed += 1
            print(f"\n❌ TEST FAILED: {exec_result.error}")
    
    def test_filter_query(self):
        """Test query with filters."""
        print("\n" + "="*70)
        print("TEST 4: Filter Query - Delivered orders in SP state")
        print("="*70)
        
        intent = Intent(
            intent_type='filter',
            metrics=['order_count'],
            dimensions=['customer_state'],
            filters=[
                Filter(dimension='order_status', operator='=', value='delivered'),
                Filter(dimension='customer_state', operator='=', value='SP')
            ],
            confidence=0.90,
            original_query='How many delivered orders in SP?'
        )
        
        result = self.generator.generate(intent)
        
        print(f"\n✓ SQL Generated")
        print(f"✓ Valid: {result['is_valid']}")
        print(f"✓ Filters Applied: {len(result['filters'])}")
        print(f"\nGenerated SQL:\n{result['sql']}")
        
        exec_result = self.executor.execute(result['sql'])
        print(f"\n✓ Execution Success: {exec_result.success}")
        
        if exec_result.success and exec_result.data is not None:
            print(f"\nResult:")
            print(exec_result.data)
        
        if result['is_valid'] and exec_result.success:
            self.passed += 1
            print("\n✅ TEST PASSED")
        else:
            self.failed += 1
            print(f"\n❌ TEST FAILED: {exec_result.error}")
    
    def test_time_series_query(self):
        """Test time series query."""
        print("\n" + "="*70)
        print("TEST 5: Time Series Query - Monthly revenue trend for 2017")
        print("="*70)
        
        intent = Intent(
            intent_type='time_series',
            metrics=['revenue'],
            dimensions=[],
            filters=[Filter(dimension='purchase_year', operator='=', value=2017)],
            time_grain='month',
            confidence=0.88,
            original_query='Show monthly revenue trend for 2017'
        )
        
        result = self.generator.generate(intent)
        
        print(f"\n✓ SQL Generated")
        print(f"✓ Valid: {result['is_valid']}")
        print(f"✓ Time Grain: month")
        print(f"\nGenerated SQL:\n{result['sql']}")
        
        exec_result = self.executor.execute(result['sql'])
        print(f"\n✓ Execution Success: {exec_result.success}")
        print(f"✓ Rows: {exec_result.row_count}")
        
        if exec_result.success and exec_result.data is not None:
            print(f"\nSample Results:")
            print(exec_result.data.head(6))
        
        if result['is_valid'] and exec_result.success:
            self.passed += 1
            print("\n✅ TEST PASSED")
        else:
            self.failed += 1
            print(f"\n❌ TEST FAILED: {exec_result.error}")
    
    def test_comparison_query(self):
        """Test comparison query."""
        print("\n" + "="*70)
        print("TEST 6: Comparison Query - Weekend vs Weekday orders")
        print("="*70)
        
        intent = Intent(
            intent_type='comparison',
            metrics=['revenue', 'order_count'],
            dimensions=['purchase_is_weekend'],
            comparison_dimension='purchase_is_weekend',
            filters=[],
            confidence=0.85,
            original_query='Compare weekend vs weekday orders'
        )
        
        result = self.generator.generate(intent)
        
        print(f"\n✓ SQL Generated")
        print(f"✓ Valid: {result['is_valid']}")
        print(f"\nGenerated SQL:\n{result['sql']}")
        
        exec_result = self.executor.execute(result['sql'])
        print(f"\n✓ Execution Success: {exec_result.success}")
        
        if exec_result.success and exec_result.data is not None:
            print(f"\nResults:")
            print(exec_result.data)
        
        if result['is_valid'] and exec_result.success:
            self.passed += 1
            print("\n✅ TEST PASSED")
        else:
            self.failed += 1
            print(f"\n❌ TEST FAILED: {exec_result.error}")
    
    def test_product_category_query(self):
        """Test query with product categories (English)."""
        print("\n" + "="*70)
        print("TEST 7: Top 10 product categories by revenue")
        print("="*70)
        
        intent = Intent(
            intent_type='top_n',
            metrics=['revenue'],
            dimensions=['product_category_name_english'],
            filters=[],
            limit=10,
            order_by='revenue DESC',
            confidence=0.93,
            original_query='Top 10 product categories by revenue'
        )
        
        result = self.generator.generate(intent)
        
        print(f"\n✓ SQL Generated")
        print(f"✓ Valid: {result['is_valid']}")
        print(f"\nGenerated SQL:\n{result['sql']}")
        
        exec_result = self.executor.execute(result['sql'])
        print(f"\n✓ Execution Success: {exec_result.success}")
        print(f"✓ Rows: {exec_result.row_count}")
        
        if exec_result.success and exec_result.data is not None:
            print(f"\nTop Product Categories:")
            print(exec_result.data)
        
        if result['is_valid'] and exec_result.success:
            self.passed += 1
            print("\n✅ TEST PASSED")
        else:
            self.failed += 1
            print(f"\n❌ TEST FAILED: {exec_result.error}")
    
    def test_validation_blocking(self):
        """Test that dangerous SQL is blocked."""
        print("\n" + "="*70)
        print("TEST 8: Validation - Blocking dangerous SQL")
        print("="*70)
        
        dangerous_queries = [
            "DROP TABLE mart.fact_orders",
            "DELETE FROM mart.fact_orders WHERE order_id = 1",
            "INSERT INTO mart.fact_orders VALUES (1, 2, 3)",
            "UPDATE mart.fact_orders SET order_status = 'canceled'",
        ]
        
        all_blocked = True
        for sql in dangerous_queries:
            validation = self.validator.validate(sql)
            print(f"\n✗ {sql[:50]}...")
            print(f"  Blocked: {not validation.is_valid}")
            if validation.errors:
                print(f"  Reason: {validation.errors[0]}")
            
            if validation.is_valid:
                all_blocked = False
        
        if all_blocked:
            self.passed += 1
            print("\n✅ TEST PASSED - All dangerous SQL blocked")
        else:
            self.failed += 1
            print("\n❌ TEST FAILED - Some dangerous SQL not blocked")
    
    def run_all_tests(self):
        """Run all tests and print summary."""
        print("\n" + "="*70)
        print("SQL GENERATION TEST SUITE - Sprint 2, Ticket 6")
        print("="*70)
        
        self.executor.connect()
        
        try:
            self.test_top_n_query()
            self.test_group_by_query()
            self.test_aggregation_query()
            self.test_filter_query()
            self.test_time_series_query()
            self.test_comparison_query()
            self.test_product_category_query()
            self.test_validation_blocking()
            
        finally:
            self.executor.disconnect()
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️  {self.failed} test(s) failed")
        
        return self.failed == 0


if __name__ == "__main__":
    tester = TestSQLGeneration()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
