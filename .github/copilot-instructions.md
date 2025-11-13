# Ask Your Data — Intelligent BI Copilot

## Project Overview

**Goal**: Build an intelligent NL-to-SQL copilot that interprets natural language queries, generates SQL dynamically, executes on DuckDB, and produces interactive charts with narrative insights.

**Tech Stack**: DuckDB (analytics), dbt-core (transformations), FAISS (RAG), Llama 3.1/Ollama (NLP), Streamlit (UI), FastAPI (API)

**Dataset**: Olist Brazilian E-commerce (Kaggle) — `ask_your_data.db` with raw tables transformed via dbt

---

## Architecture & Data Flow

```
User Query (NL) → Intent Parser (Llama 3.1) → RAG Glossary Lookup (FAISS)
                ↓
            SQL Generator → Safety Validator → DuckDB Executor
                ↓
            DataFrame → Chart Recommender + LLM Narrative
                ↓
            Streamlit UI (Interactive Visualization)
```

### Key Components

- **`src/ingest/`** — Data ingestion from Kaggle CSVs into DuckDB
- **`dbt/`** — dbt-core project with models, tests, transformations
- **`glossary/`** — YAML glossary + FAISS index for RAG context retrieval
- **`src/nlp/`** — Natural language parsing & intent extraction (Llama 3.1)
- **`src/sql/`** — SQL generation with parameterization and safety guards
- **`src/charts/`** — Plotly chart recommendation engine
- **`src/api/`** — FastAPI endpoints for RAG and intent parsing
- **`src/ui/`** — Streamlit application interface

---

## Development Workflow

### Environment Setup (Sprint 1 - Ticket 1)

**Virtual Environment**: Always activate `ask-your-data-env` before work
```powershell
# Windows PowerShell
.\ask-your-data-env\Scripts\activate
```

**Dependencies**: Installed via `pip install -r requirements.txt`
- Core: `duckdb`, `dbt-core`, `dbt-duckdb`
- API: `fastapi`, `uvicorn`, `pydantic`
- ML/AI: `faiss-cpu`, RAG support, Ollama integration
- UI: `streamlit`, `plotly`, `pandas`, `numpy`

**Verify Setup**: Run `python verify_installs.py` to confirm all imports

### Sprint-Based Development

**Development is organized in 3 sprints, executed sequentially by ticket:**

#### Sprint 1 — Foundation (Tickets 1-4)
- Environment setup
- Data ingestion (Olist → DuckDB)
- dbt transformations
- RAG glossary with FAISS

#### Sprint 2 — Core Features (Tickets 5-8)
- NL intent parsing
- SQL generation & execution
- Chart recommendation + narratives
- Streamlit UI integration

#### Sprint 3 — Production Ready (Tickets 9-12)
- Unit testing & evaluation
- Performance optimization & caching
- Dockerization
- Documentation & demo

### Running Tests

```powershell
# Run all tests
pytest tests/

# Run specific test module
pytest tests/test_sql_generation.py -v

# Run with coverage
pytest --cov=src tests/
```

### Database Operations

**DuckDB Instance**: `ask_your_data.db` (in-memory for dev, persistent for prod)

**Data Loading**:
```python
import duckdb
conn = duckdb.connect('ask_your_data.db')
conn.execute("SELECT * FROM mart.fct_orders LIMIT 10").df()
```

**dbt Commands**:
```powershell
# From dbt/ directory
cd dbt
dbt debug          # Verify connection
dbt run            # Execute models
dbt test           # Run data tests
dbt docs generate  # Generate documentation
dbt docs serve     # View docs at localhost:8080
```

### Running the Application

**Streamlit UI**:
```powershell
streamlit run src/ui/app.py
```

**FastAPI Backend**:
```powershell
uvicorn src.api.main:app --reload --port 8000
```

**Docker Deployment** (Sprint 3):
```powershell
docker build -t ask-your-data:latest .
docker run -p 8501:8501 -p 8000:8000 ask-your-data:latest
```

---

## Code Conventions & Patterns

### Code Organization

**Modular Structure**: Each sprint/ticket produces self-contained components
- One responsibility per module
- Clear separation: ingest → transform (dbt) → query → visualize

**Type Hints Required**: All functions use typing module
```python
from typing import Dict, List, Optional
from pydantic import BaseModel

def parse_intent(query: str) -> Intent:
    """Parse natural language query into structured intent."""
    ...
```

### Documentation Standards

**Every module/function requires**:
- **Docstrings** explaining purpose, inputs, outputs
- **Comments** for complex logic
- **Example usage** in docstring when applicable

Example:
```python
def generate_sql(intent: Intent, glossary: Dict[str, str]) -> str:
    """
    Generate safe, parameterized SQL from structured intent.
    
    Args:
        intent: Parsed Intent object with entities and filters
        glossary: Context from RAG lookup for column/table mapping
    
    Returns:
        Parameterized SQL string (no raw string interpolation)
    
    Example:
        >>> intent = Intent(metric="revenue", dimension="category")
        >>> sql = generate_sql(intent, glossary)
        >>> print(sql)
        SELECT category, SUM(price) FROM mart.fct_orders GROUP BY category
    """
    ...
```

### SQL Safety (Critical)

**Always use parameterized queries** — never string interpolation:
```python
# ✓ CORRECT
conn.execute("SELECT * FROM orders WHERE order_id = ?", [order_id])

# ✗ WRONG (SQL injection risk)
conn.execute(f"SELECT * FROM orders WHERE order_id = {order_id}")
```

**Validation**: Use `src/sql/validator.py` to check SQL before execution
- Block DDL/DML (DROP, DELETE, UPDATE, INSERT)
- Allow only SELECT statements
- Sanitize table/column names

### RAG & Glossary

**Glossary Format** (`glossary/business_terms.yaml`):
```yaml
revenue:
  description: "Total payment value from orders"
  sql_column: "payment_value"
  table: "mart.fct_orders"
  
customer_state:
  description: "Brazilian state where customer is located"
  sql_column: "customer_state"
  table: "mart.dim_customers"
```

**FAISS Index**: Built from glossary embeddings
- Use `glossary/build_index.py` to regenerate
- Query via `src/api/rag.py` endpoint

### Performance Optimization

**Caching**: Use `functools.lru_cache` for repeated operations
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_embedding(text: str) -> np.ndarray:
    """Cache embeddings to avoid recomputation."""
    ...
```

**Data Loading**: Prefer `duckdb.read_csv_auto()` for fast CSV ingestion

---

## Key Files & Directories

| Path | Purpose |
|------|---------|
| `ask_your_data.db` | Main DuckDB database (excluded from git) |
| `dbt/models/` | dbt transformation models (staging, marts) |
| `dbt/dbt_project.yml` | dbt configuration |
| `glossary/business_terms.yaml` | Business glossary for RAG |
| `src/ingest/data.py` | Data loading logic (Sprint 1, Ticket 2) |
| `src/nlp/intent_parser.py` | NL→Intent using Llama 3.1 (Sprint 2, Ticket 5) |
| `src/sql/generator.py` | Intent→SQL conversion (Sprint 2, Ticket 6) |
| `src/charts/recommender.py` | Chart type selection logic (Sprint 2, Ticket 7) |
| `src/ui/app.py` | Streamlit main application (Sprint 2, Ticket 8) |
| `tests/` | Unit and integration tests (Sprint 3, Ticket 9) |
| `Dockerfile` | Production deployment config (Sprint 3, Ticket 11) |

---

## Ticket Workflow

**When starting a new ticket**:
1. Reference the ticket number and sprint in comments
2. Explain what was added/changed (2-5 lines)
3. State dependencies on previous tickets
4. Update this file if new patterns emerge

**Example**:
```python
# Sprint 1 - Ticket 2: Data Ingestion
# Loads Olist CSVs into DuckDB using duckdb.read_csv_auto
# Creates calendar and country dimension tables
# Dependency: Ticket 1 (environment must be set up)
```

---

## Common Pitfalls

- **Forgetting to activate venv**: Always run `.\ask-your-data-env\Scripts\activate` first
- **SQL injection**: Never use f-strings for SQL — use parameterized queries
- **Missing dbt deps**: Run `dbt deps` if models fail to compile
- **FAISS index out of sync**: Rebuild with `python glossary/build_index.py` after glossary updates
- **Large outputs**: Use `.limit()` or `LIMIT` clauses when testing queries

---

## AI Assistant Guidelines

When generating code for this project:

1. **Always explain changes** — include purpose, why needed, how it connects to current sprint/ticket
2. **Follow modular structure** — place files in correct `src/` subdirectories
3. **Maintain safety** — validate SQL, sanitize inputs, use type hints
4. **Incremental development** — complete tickets sequentially, test after each
5. **Document everything** — docstrings, comments, and update this file when needed

**Example response format**:
```
✏️ Added sql/generator.py (Sprint 2 - Ticket 6)
Converts Intent objects to parameterized SQL. Uses RAG glossary for column mapping.
Validates queries with sql/validator.py before execution. Returns safe SELECT statements only.
```
