"""
Verification script for Ask Your Data Copilot dependencies
Sprint 1 - Ticket 1: Environment setup verification
"""

import sys

def verify_imports():
    """Test all required package imports and display versions."""
    
    packages = [
        ('duckdb', 'DuckDB'),
        ('dbt', 'dbt-core'),
        ('dbt.adapters.duckdb', 'dbt-duckdb'),
        ('streamlit', 'Streamlit'),
        ('plotly', 'Plotly'),
        ('faiss', 'FAISS'),
        ('pydantic', 'Pydantic'),
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
    ]
    
    print("=" * 60)
    print("Ask Your Data Copilot - Dependency Verification")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print("=" * 60)
    
    all_success = True
    
    for module_name, display_name in packages:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"✓ {display_name:20} {version:15} [OK]")
        except ImportError as e:
            print(f"✗ {display_name:20} {'N/A':15} [FAILED]")
            print(f"  Error: {e}")
            all_success = False
    
    print("=" * 60)
    
    if all_success:
        print("✓ All dependencies verified successfully!")
        print("=" * 60)
        return 0
    else:
        print("✗ Some dependencies failed to import.")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(verify_imports())
