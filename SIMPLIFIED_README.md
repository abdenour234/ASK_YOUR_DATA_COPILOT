# Ask Your Data - Simplified Version

## What Changed?

This is a **completely refactored, simplified version** of the Ask Your Data Copilot.

✅ **No OOP** - Pure functions, no classes  
✅ **No Pydantic** - Simple dicts with type hints  
✅ **76% less code** - 680 lines vs 2,844 lines  
✅ **Easy to read** - Clear, straightforward logic  
✅ **Minimal prints** - Only essential messages  

## Quick Start

### 1. Activate Environment
```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies (if needed)
```powershell
pip install streamlit pandas plotly duckdb requests python-dotenv faiss-cpu sentence-transformers
```

### 3. Set API Key
Create `.env` file:
```
OPENROUTER_API_KEY=your_key_here
```

### 4. Run App
```powershell
streamlit run src/ui/app.py
```

## Code Structure

```
src/
├── nlp/
│   ├── models.py          # Just type hints (5 lines)
│   └── intent_parser.py   # Simple functions (100 lines)
├── sql/
│   ├── generator.py       # Simple functions (100 lines)
│   ├── executor.py        # Simple functions (75 lines)
│   └── validator.py       # Simple function (30 lines)
├── api/
│   ├── rag.py            # Simple functions (80 lines)
│   └── main.py           # Simple FastAPI (40 lines)
├── charts/
│   └── chart_selector.py # Simple function (55 lines)
└── ui/
    └── app.py            # Simple Streamlit (200 lines)
```

**Total: 680 lines** (was 2,844 lines)

## How It Works

### Simple Flow

```
1. User enters natural language query
   ↓
2. parse_query(query) → returns intent dict
   ↓
3. generate_sql(intent) → returns SQL string
   ↓
4. run_query(sql) → returns DataFrame
   ↓
5. choose_chart(intent, data) → returns chart config
   ↓
6. render_chart(config, data) → displays result
```

### Example Usage

```python
# Parse query
from src.nlp.intent_parser import parse_query
result = parse_query("top 10 states by revenue")
intent = result['intent']

# Generate SQL
from src.sql.generator import generate_sql
sql_result = generate_sql(intent)
sql = sql_result['sql']

# Execute query
from src.sql.executor import run_query
exec_result = run_query(sql)
data = exec_result['data']

# Choose chart
from src.charts.chart_selector import choose_chart
chart_config = choose_chart(intent, data)
```

## Key Functions

### Intent Parser (`src/nlp/intent_parser.py`)
- `parse_query(query: str) -> dict`

### SQL Generator (`src/sql/generator.py`)
- `generate_sql(intent: dict) -> dict`

### SQL Executor (`src/sql/executor.py`)
- `connect_db(path: str)`
- `run_query(sql: str) -> dict`

### Chart Selector (`src/charts/chart_selector.py`)
- `choose_chart(intent: dict, data: DataFrame) -> dict`

### RAG (`src/api/rag.py`)
- `load_glossary()`
- `search_glossary(query: str, top_k: int) -> list`

## Example Queries

- "Top 10 states by revenue"
- "Total revenue by month"
- "Delivered orders in SP"
- "Top product categories"
- "Monthly sales for 2017"

## What Was Removed?

### Classes Removed (76% code reduction):
- ❌ `IntentParser` class
- ❌ `SQLGenerator` class
- ❌ `SQLExecutor` class
- ❌ `SQLValidator` class
- ❌ `GlossaryRetriever` class
- ❌ `ChartSelector` class
- ❌ `PlotlyRenderer` class

### Pydantic Models Removed:
- ❌ `Intent` model
- ❌ `Filter` model
- ❌ `DateRange` model
- ❌ `IntentParseResult` model
- ❌ `ExecutionResult` dataclass
- ❌ `RetrievalResult` model
- ❌ `ValidationResult` dataclass

### Other Removed:
- ❌ 100+ lines of CSS
- ❌ Complex caching
- ❌ Progress tracking
- ❌ Excessive logging

## Benefits

✅ **Easier to understand** - No OOP mental overhead  
✅ **Easier to debug** - Simple function calls  
✅ **Easier to modify** - Change one function at a time  
✅ **Easier to test** - Test individual functions  
✅ **Less code** - 76% reduction in lines  
✅ **Clearer flow** - Linear execution path  

## Notes

- All functions return simple dicts
- Type hints provided for clarity
- Global state used sparingly (DB connection, RAG index)
- Error handling with try/except
- Consistent dict structure: `{'success': bool, 'data': any, 'error': str}`
