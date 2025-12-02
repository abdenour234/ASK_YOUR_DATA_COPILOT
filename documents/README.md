# Ask Your Data — Natural Language to SQL Copilot

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![DuckDB](https://img.shields.io/badge/DuckDB-v0.9+-orange.svg)](https://duckdb.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent Natural Language to SQL copilot that interprets queries, generates SQL dynamically, executes on DuckDB, and returns interactive data tables.

---

## 🎯 What This Project Does

Ask Your Data converts natural language questions into SQL queries and executes them on a Brazilian e-commerce dataset:

**Example:**
```
User: "What are the top 10 customer states by revenue?"
  ↓
System: Parses intent → Generates SQL → Executes query → Returns table
  ↓
Result: Interactive table showing SP, RJ, MG... with revenue values
```

**Key Features:**
- ✅ **Natural Language Understanding**: GPT-4o (OpenRouter API) parses user questions
- ✅ **Smart SQL Generation**: Template-based SQL builder (100% accurate, no hallucinations)
- ✅ **RAG Context**: FAISS vector search for business glossary lookup
- ✅ **Fast Analytics**: DuckDB executes queries in <100ms
- ✅ **Data Transformations**: dbt-core manages 11 clean tables from raw CSVs
- ✅ **Modern UI**: Streamlit interface with query history and details
- ✅ **Multi-layer Security**: SQL validation, injection prevention, read-only mode

---

## 🏗️ Architecture

```
┌──────────────┐      ┌─────────────┐      ┌──────────────┐      ┌─────────┐
│ User Query   │ ───> │ Intent      │ ───> │ SQL          │ ───> │ DuckDB  │
│ (Natural     │      │ Parser      │      │ Generator    │      │ Execute │
│  Language)   │      │ (GPT-4o +   │      │ (Templates)  │      │         │
└──────────────┘      │  RAG/FAISS) │      └──────────────┘      └────┬────┘
                      └─────────────┘                                  │
                                                                        │
┌──────────────┐      ┌─────────────────────────────────────────────┬─┘
│ Streamlit UI │ <─── │ DataFrame Result (pandas)                   │
│ - Data Table │      │ - 10 rows × 2 columns                       │
│ - Metrics    │      │ - Execution time: 45ms                      │
│ - SQL View   │      │ - Result hash for validation                │
└──────────────┘      └─────────────────────────────────────────────┘
```

**Tech Stack:**
- **Database**: DuckDB 0.9+ (in-memory analytical database)
- **Transformations**: dbt-core 1.7+ with dbt-duckdb adapter
- **NLP**: OpenRouter API (GPT-4o) for intent parsing
- **RAG**: FAISS vector store for glossary/context retrieval
- **Frontend**: Streamlit 1.x (web interface)
- **Visualization**: Pandas DataFrames (interactive tables)
- **Data**: Olist Brazilian E-Commerce (100k orders, 11 tables, 1.5M+ rows)

---

## 🚀 Complete Setup Guide (Step-by-Step)

### ✅ **Prerequisites**

Before starting, ensure you have:

| Requirement | Version | Download Link | Check Command |
|-------------|---------|---------------|---------------|
| Python | 3.11 or higher | [python.org](https://www.python.org/downloads/) | `python --version` |
| Git | Latest | [git-scm.com](https://git-scm.com/) | `git --version` |
| Text Editor | Any | [VS Code](https://code.visualstudio.com/) (recommended) | - |
| Internet | Active | For API calls and package downloads | - |

---

### 📥 **STEP 1: Clone the Repository**

```powershell
# Clone the project
git clone https://github.com/yourusername/ask-your-data-copilot.git

# Navigate to project folder
cd ask-your-data-copilot

# Verify you're in the right place
ls  # Should see: data/, dbt/, src/, requirements.txt, etc.
```

---

### 🐍 **STEP 2: Create Python Virtual Environment**

**Why?** Isolates project dependencies from your system Python.

**Windows PowerShell:**
```powershell
# Create virtual environment
python -m venv ask-your-data-env

# Activate it
.\ask-your-data-env\Scripts\activate

# You should see (ask-your-data-env) in your prompt
```

**Unix/Mac/Linux:**
```bash
# Create virtual environment
python3 -m venv ask-your-data-env

# Activate it
source ask-your-data-env/bin/activate

# You should see (ask-your-data-env) in your prompt
```

**Troubleshooting:**
- If activation fails on Windows: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- If `python` not found: Try `python3` or `py`

---

### 📦 **STEP 3: Install Dependencies**

```powershell
# Make sure virtual environment is activated (you should see the prefix)
# Install all required packages (~200+ dependencies)
pip install -r requirements.txt

# This will take 2-5 minutes depending on your internet speed
# Key packages installed:
# - streamlit (UI framework)
# - duckdb (database)
# - dbt-core + dbt-duckdb (transformations)
# - faiss-cpu (vector search)
# - sentence-transformers (embeddings)
# - pandas, numpy (data manipulation)
# - requests (HTTP calls)
```

**Verify Installation:**
```powershell
# Run verification script
python verify_installs.py

# Expected output:
# ✓ streamlit: 1.x.x
# ✓ duckdb: 0.9.x
# ✓ dbt-core: 1.7.x
# ✓ faiss-cpu: 1.x.x
# ... (all packages should pass)
```

**Common Issues:**
- **"No module named 'pip'"**: Upgrade pip with `python -m ensurepip --upgrade`
- **Build errors on Windows**: Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
- **Slow installation**: Use `pip install -r requirements.txt --no-cache-dir`

---

### 🗄️ **STEP 4: Download & Setup Dataset**

The project uses the **Olist Brazilian E-Commerce Dataset** from Kaggle.

**Option A: Download from Kaggle (Recommended)**

1. **Get Kaggle Account**: Sign up at [kaggle.com](https://www.kaggle.com/)
2. **Download Dataset**: Visit [Olist Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
3. **Extract Files**: Unzip all CSV files
4. **Place in Project**:
   ```powershell
   # Copy all CSV files to data/raw/ folder
   # Expected files (9 CSVs):
   # - olist_customers_dataset.csv
   # - olist_orders_dataset.csv
   # - olist_order_items_dataset.csv
   # - olist_order_payments_dataset.csv
   # - olist_order_reviews_dataset.csv
   # - olist_products_dataset.csv
   # - olist_sellers_dataset.csv
   # - olist_geolocation_dataset.csv
   # - product_category_name_translation.csv
   ```

**Option B: Use Provided Data (If Available)**

If the repository includes `ask_your_data.db`, skip to Step 6.

**Verify Dataset:**
```powershell
# Check that CSV files exist
ls data/raw/

# Should show 9 CSV files
```

---

### 🔧 **STEP 5: Run Data Ingestion & dbt Transformations**

**5.1 Ingest Raw Data into DuckDB:**

```powershell
# Load CSVs into DuckDB database
python src/ingest/data.py

# This creates ask_your_data.db (40-50 MB)
# Takes ~30-60 seconds
# Expected output:
# ✓ Loaded 99,441 orders
# ✓ Loaded 99,441 customers
# ✓ Loaded 112,650 order items
# ... (11 tables total)
```

**5.2 Run dbt Transformations:**

```powershell
# Navigate to dbt project
cd dbt/ask_your_data_project

# Install dbt dependencies (if any)
dbt deps

# Run all models (staging + marts)
dbt run

# Expected output:
# Completed successfully
# Done. PASS=15 WARN=0 ERROR=0 SKIP=0 TOTAL=15

# Run data quality tests
dbt test

# Expected output:
# Completed successfully
# Done. PASS=8 WARN=0 ERROR=0 SKIP=0 TOTAL=8

# Return to project root
cd ../..
```

**What dbt Does:**
- **Staging Layer**: Cleans raw data (null handling, type casting, deduplication)
- **Mart Layer**: Creates analytical tables (fact_orders, dim_customers, dim_products, etc.)
- **Tests**: Validates data quality (uniqueness, not null, relationships)

**Verify dbt Output:**
```powershell
# Check that mart tables exist
python -c "import duckdb; conn = duckdb.connect('ask_your_data.db'); result = conn.execute('SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = ''mart'' ORDER BY table_name').df(); print(result if len(result) > 0 else 'No mart schema found - dbt transformations need to be run')"

# Should show:
# - fact_orders
# - fact_order_items
# - dim_customers
# - dim_products
# - dim_sellers
# - stg_order_payments
# - stg_order_reviews
```

---

### 🔑 **STEP 6: Configure API Keys**

**6.1 Get OpenRouter API Key:**

1. Sign up at [openrouter.ai](https://openrouter.ai/)
2. Navigate to **Keys** section
3. Create new API key
4. Copy the key (starts with `sk-or-v1-...`)

**6.2 Create `.env` File:**

```powershell
# Create .env file in project root
New-Item -ItemType File -Path .env

# Add API key (use your actual key)
@"
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
OPENROUTER_MODEL=openai/gpt-4o
OPENROUTER_SITE_URL=http://localhost:8501
OPENROUTER_SITE_NAME=Ask Your Data Copilot
"@ | Set-Content .env
```

**Unix/Mac:**
```bash
# Create .env file
cat > .env << EOF
OPENROUTER_API_KEY=sk-or-v1-your-actual-api-key-here
OPENROUTER_MODEL=openai/gpt-4o
OPENROUTER_SITE_URL=http://localhost:8501
OPENROUTER_SITE_NAME=Ask Your Data Copilot
EOF
```

**⚠️ IMPORTANT:**
- Never commit `.env` to Git (already in `.gitignore`)
- Keep your API key secret
- Free tier: $5 credit (enough for ~500 queries)

**Verify API Key:**
```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('API Key loaded:', bool(os.getenv('OPENROUTER_API_KEY')))"

# Should print: API Key loaded: True
```

---

### 🔍 **STEP 7: Build RAG Glossary Index**

The system uses FAISS to search business terms for better SQL generation.

```powershell
# Build FAISS index from glossary YAML
python glossary/build_index.py

# Expected output:
# Loading glossary from: glossary/business_terms.yaml
# Found 25 business terms
# Building FAISS index...
# ✓ Index saved to: glossary/glossary.index
# ✓ Embeddings saved to: glossary/embeddings.npy

# Verify index file exists
ls glossary/

# Should show:
# - business_terms.yaml
# - build_index.py
# - glossary.index
# - embeddings.npy (or .pkl)
```

**What This Does:**
- Loads business glossary (metrics, dimensions, patterns)
- Creates vector embeddings using sentence-transformers
- Builds FAISS index for fast semantic search
- Used by Intent Parser to understand domain-specific terms

---

### ▶️ **STEP 8: Run the Application**

**8.1 Start Streamlit UI:**

```powershell
# Make sure you're in project root and venv is activated
streamlit run src/ui/app.py

# Expected output:
# You can now view your Streamlit app in your browser.
# Local URL: http://localhost:8501
# Network URL: http://192.168.x.x:8501

# Browser should open automatically
# If not, visit: http://localhost:8501
```

**8.2 Test the Application:**

1. **Check System Status**:
   - Sidebar should show ✅ "OpenRouter API Connected"
   - Sidebar should show ✅ "Connected to DuckDB" with "Total Orders: 99,441"

2. **Try Example Queries**:
   - Click "Top 10 states by revenue" in sidebar
   - Click "🚀 Run Query" button
   - Should see progress: Parsing → Generating SQL → Executing → Complete
   - Results table should display 10 states with revenue

3. **Try Custom Query**:
   ```
   What are the top 5 product categories by order count?
   ```
   - Should return table with 5 categories and their counts

4. **Check Query Details**:
   - Expand "🔍 Query Details" section
   - **Intent Analysis** tab: Shows parsed intent (type, metrics, dimensions)
   - **Generated SQL** tab: Shows actual SQL query
   - **Execution Stats** tab: Shows performance metrics

---

## 🎓 Using the Application

### Example Queries You Can Try:

| Query | What It Does |
|-------|--------------|
| `Top 10 states by revenue` | Returns states ranked by total sales |
| `Total revenue` | Calculates sum of all payments |
| `Monthly revenue for 2017` | Shows revenue trend month-by-month |
| `Delivered orders in SP` | Counts delivered orders in São Paulo state |
| `Top product categories` | Lists categories by revenue (default top 10) |
| `Weekend vs weekday orders` | Compares order counts by weekend flag |
| `Average order value by region` | Shows AOV grouped by customer region |

### Query Patterns Supported:

- **Top N**: "Top 10 X by Y"
- **Aggregation**: "Total revenue", "Average price"
- **Time Series**: "Monthly revenue", "Orders by year"
- **Filtering**: "Orders in SP", "Revenue where status = delivered"
- **Grouping**: "Revenue by region", "Count by category"
- **Comparison**: "Weekend vs weekday", "Region A vs Region B"

### Understanding Results:

**Single Value Results** (Aggregations):
- Displayed as large metric cards
- Example: "Total Revenue: R$ 16,008,872.12"

**Multi-Row Results** (Top N, Groups, Time Series):
- Displayed as interactive tables
- Sortable columns
- Copy/download options

**Query Details Panel**:
- **Intent**: Shows how system understood your question
- **SQL**: Shows generated query (educational!)
- **Stats**: Execution time, row count, result hash

---

## 📁 Project Structure


## 📁 Project Structure

```
ask_your_data_copilot/
├── ask_your_data.db          # DuckDB database (40-50 MB, generated)
├── .env                      # API keys (create this, never commit!)
├── requirements.txt          # Python dependencies
│
├── data/
│   ├── raw/                  # 9 CSV files from Kaggle (you download these)
│   └── processed/            # Intermediate files (auto-generated)
│
├── dbt/
│   └── ask_your_data_project/
│       ├── dbt_project.yml   # dbt configuration
│       ├── models/
│       │   ├── staging/      # stg_* tables (data cleaning)
│       │   └── marts/        # fact_*, dim_* tables (analytics layer)
│       └── tests/            # Data quality tests
│
├── glossary/
│   ├── business_terms.yaml   # Business glossary (25+ terms)
│   ├── build_index.py        # FAISS index builder script
│   ├── glossary.index        # FAISS index (auto-generated)
│   └── embeddings.npy        # Vector embeddings (auto-generated)
│
├── src/
│   ├── ingest/
│   │   └── data.py           # CSV → DuckDB loader
│   │
│   ├── nlp/
│   │   ├── intent_parser.py  # NL → Intent (GPT-4o + RAG)
│   │   └── models.py         # Intent, Filter dataclasses
│   │
│   ├── sql/
│   │   ├── generator.py      # Intent → SQL (main logic)
│   │   ├── templates.py      # SQL template builders (519 lines)
│   │   ├── validator.py      # SQL safety checks
│   │   └── executor.py       # SQL → DataFrame (DuckDB)
│   │
│   ├── api/
│   │   ├── main.py           # FastAPI app (optional)
│   │   └── rag.py            # RAG retriever (FAISS search)
│   │
│   └── ui/
│       └── app.py            # Streamlit interface (main entry point)
│
├── tests/
│   ├── test_intent_parser.py
│   ├── test_sql_generator.py
│   └── test_rag_api.py
│
├── documents/                # All documentation (you're here!)
│   ├── README.md             # This setup guide
│   ├── QUERY_FLOW_DOCUMENTATION.md  # Technical flow details
│   ├── SPRINT1_TICKET1_COMPLETE.md
│   ├── SPRINT1_TICKET2_COMPLETE.md
│   └── ... (other completion docs)
│
└── ask-your-data-env/        # Virtual environment (auto-generated)
    ├── Scripts/              # Activation scripts (Windows)
    ├── bin/                  # Activation scripts (Unix)
    └── Lib/site-packages/    # Installed packages
```

**Key Files to Know:**
- **`src/ui/app.py`**: Main application - run this with Streamlit
- **`.env`**: Your API keys - create this manually
- **`ask_your_data.db`**: Database file - auto-generated from CSVs
- **`glossary/business_terms.yaml`**: Business glossary - edit to add new terms
- **`dbt/ask_your_data_project/models/`**: SQL transformations

---

## 🧪 Testing & Validation

### Run Unit Tests:

```powershell
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_sql_generator.py -v

# Run with coverage report
pytest --cov=src tests/
```

### Manual Testing:

**Test Database Connection:**
```powershell
# Check that raw data was loaded
python -c "import duckdb; conn = duckdb.connect('ask_your_data.db'); print(conn.execute('SELECT COUNT(*) FROM raw.orders').fetchone()[0], 'orders loaded')"

# Should print: 99441 orders loaded (or similar number)
```

**Test Intent Parser:**
```powershell
python -c "from src.nlp.intent_parser import IntentParser; parser = IntentParser(); result = parser.parse('Top 10 states by revenue'); print('Success!' if result.success else result.error)"

# Should print: Success!
```

**Test RAG Retriever:**
```powershell
python -c "from src.api.rag import get_retriever; retriever = get_retriever(); context = retriever.get_context_for_sql('revenue', top_k=3); print(f'Found {len(context.get(\"metrics\", []))} metrics')"

# Should print: Found 3 metrics (or similar)
```

### Check Data Quality:

```powershell
# Verify all mart tables exist
python verify_marts.py

# Expected output:
# ✓ fact_orders: 99,441 rows
# ✓ fact_order_items: 112,650 rows
# ✓ dim_customers: 99,441 rows
# ✓ dim_products: 32,951 rows
# ✓ dim_sellers: 3,095 rows
# ✓ stg_order_payments: 103,886 rows
# ✓ stg_order_reviews: 99,224 rows
```

---

## 🔧 Troubleshooting

### Common Issues & Solutions:

#### **1. Virtual Environment Not Activating**

**Symptoms**: `activate` command doesn't work

**Solutions**:
```powershell
# Windows - Run as Administrator:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then try again:
.\ask-your-data-env\Scripts\activate
```

#### **2. "ModuleNotFoundError" After Installing Requirements**

**Symptoms**: `ModuleNotFoundError: No module named 'streamlit'` (or other)

**Solutions**:
```powershell
# Make sure venv is activated (check for prefix in prompt)
# Reinstall requirements:
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### **3. DuckDB File Not Found**

**Symptoms**: `FileNotFoundError: ask_your_data.db`

**Solutions**:
```powershell
# Re-run data ingestion:
python src/ingest/data.py

# If CSV files are missing, download from Kaggle first
```

#### **4. API Key Not Working**

**Symptoms**: "API key not found" or "Unauthorized"

**Solutions**:
```powershell
# Check .env file exists in project root
cat .env

# Verify format (no quotes, no spaces around =):
OPENROUTER_API_KEY=sk-or-v1-...

# Test loading:
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.getenv('OPENROUTER_API_KEY'))"
```

#### **5. dbt Run Fails**

**Symptoms**: `dbt run` shows errors

**Solutions**:
```powershell
# Check dbt version (should be 1.7+):
dbt --version

# Reinstall dbt packages:
cd dbt/ask_your_data_project
dbt clean
dbt deps
dbt run

# Check database exists:
ls ../../ask_your_data.db
```

#### **6. FAISS Index Build Fails**

**Symptoms**: Error building glossary index

**Solutions**:
```powershell
# Install sentence-transformers separately:
pip install sentence-transformers

# Rebuild index:
python glossary/build_index.py

# If still fails, check glossary YAML syntax:
python -c "import yaml; yaml.safe_load(open('glossary/business_terms.yaml'))"
```

#### **7. Streamlit App Won't Start**

**Symptoms**: `streamlit: command not found` or port already in use

**Solutions**:
```powershell
# Make sure venv is activated
# Check Streamlit installed:
pip show streamlit

# If port 8501 is in use:
streamlit run src/ui/app.py --server.port 8502

# Or kill existing process (Windows):
netstat -ano | findstr :8501
taskkill /PID <process_id> /F
```

#### **8. Slow Query Performance**

**Symptoms**: Queries take >5 seconds

**Solutions**:
- Check DuckDB file size (should be ~40-50 MB)
- Restart Streamlit app (clears cache)
- Check API response time (OpenRouter can be slow during peak hours)
- Verify dbt models ran successfully (`dbt test`)

---

## 📊 Dataset Information

**Source**: [Olist Brazilian E-Commerce Dataset (Kaggle)](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

**Size**: ~40 MB (compressed), ~100 MB (uncompressed CSVs)

**Records**:
- 99,441 orders
- 112,650 order items
- 99,441 customers
- 32,951 products
- 3,095 sellers
- 103,886 payments
- 99,224 reviews

**Time Period**: September 2016 - October 2018

**Geographic Coverage**: All Brazilian states (27 states)

**Tables Created by dbt**:

| Table | Type | Rows | Description |
|-------|------|------|-------------|
| `mart.fact_orders` | Fact | 99,441 | Order-level facts with customer info |
| `mart.fact_order_items` | Fact | 112,650 | Item-level facts with product/seller |
| `mart.dim_customers` | Dimension | 99,441 | Customer master data |
| `mart.dim_products` | Dimension | 32,951 | Product catalog with categories |
| `mart.dim_sellers` | Dimension | 3,095 | Seller information |
| `mart.stg_order_payments` | Staging | 103,886 | Payment transactions |
| `mart.stg_order_reviews` | Staging | 99,224 | Customer reviews |

---

## 🔐 Security & Best Practices

### SQL Injection Prevention:

The system has **4 layers of protection**:

1. **Intent-Based Parsing**: LLM converts NL to structured Intent (no SQL in user input)
2. **Template-Based Generation**: SQL built from safe templates (no string interpolation)
3. **Validation Layer**: SQLValidator checks for dangerous keywords (DROP, DELETE, EXEC, etc.)
4. **Read-Only Mode**: DuckDB connection only allows SELECT statements

**Blocked Operations**:
- ❌ DROP TABLE
- ❌ DELETE FROM
- ❌ UPDATE SET
- ❌ INSERT INTO
- ❌ ALTER TABLE
- ❌ EXEC / xp_cmdshell
- ✅ SELECT (allowed)

### API Key Security:

- **Never commit `.env`** to Git (already in `.gitignore`)
- **Rotate keys regularly** (every 90 days)
- **Use environment variables** in production
- **Monitor usage** on OpenRouter dashboard

### Data Privacy:

- Dataset is **public** (Olist released under CC BY-NC-SA 4.0)
- Customer IDs are **anonymized** in original dataset
- No PII (personally identifiable information) in queries

---

## 📚 Additional Documentation

For developers and advanced users:

- **[QUERY_FLOW_DOCUMENTATION.md](QUERY_FLOW_DOCUMENTATION.md)**: Complete technical flow from user query to SQL result (1,000+ lines)
- **[.github/copilot-instructions.md](../.github/copilot-instructions.md)**: AI coding guidelines and project conventions
- **Sprint Completion Docs**: `SPRINT1_TICKET1_COMPLETE.md`, `SPRINT2_TICKET5_COMPLETE.md`, etc.

### Key Concepts:

- **Intent Object**: Structured representation of user query (intent_type, metrics, dimensions, filters)
- **SQL Templates**: Reusable SQL patterns for different intent types (top_n, aggregation, time_series, etc.)
- **RAG (Retrieval-Augmented Generation)**: FAISS-powered glossary search to enhance intent parsing
- **dbt Marts**: Transformed tables optimized for analytics (fact/dimension star schema)

### Architecture Deep Dive:

See [QUERY_FLOW_DOCUMENTATION.md](QUERY_FLOW_DOCUMENTATION.md) for:
- Step-by-step code execution with line numbers
- Input/output examples at each stage
- Data structure definitions (Intent, SQLTemplate, ExecutionResult)
- Error handling strategies
- Performance optimization tips

---

## 🤝 Contributing

### Development Workflow:

1. **Activate virtual environment**:
   ```powershell
   .\ask-your-data-env\Scripts\activate
   ```

2. **Create feature branch**:
   ```powershell
   git checkout -b feature/your-feature-name
   ```

3. **Make changes** and add tests:
   ```powershell
   # Edit code in src/
   # Add tests in tests/
   pytest tests/test_your_feature.py
   ```

4. **Run full test suite**:
   ```powershell
   pytest tests/ -v
   ```

5. **Commit and push**:
   ```powershell
   git add .
   git commit -m "Add: your feature description"
   git push origin feature/your-feature-name
   ```

### Adding New Features:

**Add New Metric** (e.g., "average_delivery_time"):
1. Edit `glossary/business_terms.yaml` - add metric definition
2. Edit `src/sql/templates.py` - add to `_get_metric_aggregation()`
3. Rebuild glossary: `python glossary/build_index.py`
4. Test: Try query "What is the average delivery time?"

**Add New Dimension** (e.g., "seller_region"):
1. Edit `glossary/business_terms.yaml` - add dimension
2. Edit `src/sql/templates.py`:
   - Add to `DIMENSION_TABLES`
   - Add to `_get_dimension_alias()`
   - Add to `_get_required_tables()`
3. Rebuild glossary
4. Test: Try query "Top sellers by region"

**Add New Intent Type** (e.g., "percentile"):
1. Edit `src/nlp/models.py` - add to Intent dataclass
2. Edit `src/sql/generator.py` - add `_generate_percentile()` method
3. Edit `src/sql/templates.py` - add `build_percentile_query()` method
4. Add tests in `tests/test_sql_generator.py`

---

## 🐳 Docker Deployment (Optional)

For production deployment:

```powershell
# Build image
docker build -t ask-your-data:latest .

# Run container
docker run -p 8501:8501 -e OPENROUTER_API_KEY=your-key ask-your-data:latest

# Visit: http://localhost:8501
```

**Docker Compose** (with environment file):
```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8501:8501"
    env_file:
      - .env
    volumes:
      - ./ask_your_data.db:/app/ask_your_data.db
```

---

## 📄 License

MIT License - see [LICENSE](../LICENSE) file for details.

**You are free to:**
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Use privately

**Conditions:**
- Include original license and copyright notice
- State changes made to the code

---

## 🙏 Acknowledgments

- **Dataset**: [Olist](https://olist.com/) for releasing Brazilian E-Commerce dataset on Kaggle
- **LLM**: OpenAI GPT-4o via [OpenRouter](https://openrouter.ai/)
- **Tools**: 
  - [DuckDB](https://duckdb.org/) - Fast in-memory analytics
  - [dbt Labs](https://www.getdbt.com/) - Data transformation framework
  - [Streamlit](https://streamlit.io/) - Rapid web app development
  - [FAISS](https://github.com/facebookresearch/faiss) - Vector similarity search

---

## 📞 Support

### Getting Help:

1. **Check Documentation**: Read [QUERY_FLOW_DOCUMENTATION.md](QUERY_FLOW_DOCUMENTATION.md)
2. **Search Issues**: Check existing GitHub issues
3. **Ask Questions**: Open new issue with `question` label
4. **Report Bugs**: Open issue with `bug` label + steps to reproduce

### Quick Links:

- **Repository**: [github.com/yourusername/ask-your-data-copilot](https://github.com/yourusername/ask-your-data-copilot)
- **Issues**: [github.com/yourusername/ask-your-data-copilot/issues](https://github.com/yourusername/ask-your-data-copilot/issues)
- **Dataset**: [kaggle.com/datasets/olistbr/brazilian-ecommerce](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **OpenRouter**: [openrouter.ai](https://openrouter.ai/)

---

## 📈 Project Status

**Current Version**: v3.0.0  
**Last Updated**: November 28, 2025

**Completed Features**:
- ✅ Sprint 1: Environment setup, data ingestion, dbt transformations, RAG glossary
- ✅ Sprint 2: Intent parsing (GPT-4o), SQL generation, execution, Streamlit UI
- ⏳ Sprint 3: Testing, optimization, deployment (in progress)

**Database**: `ask_your_data.db` — 11 tables, 99,441 orders, 40.76 MB

**System Performance**:
- Intent Parsing: 500-1500ms (OpenRouter API)
- SQL Generation: 10-20ms (template-based)
- Query Execution: 20-100ms (DuckDB)
- **Total Latency**: ~600-1800ms (average 850ms)

---

**🚀 Ready to start? Follow the setup steps above and you'll be querying data in natural language within 15 minutes!**
├── glossary/                # RAG glossary
│   ├── business_terms.yaml  # Domain vocabulary
│   ├── build_index.py       # FAISS index builder
│   └── index.faiss          # Vector index (generated)
├── src/
│   ├── ingest/              # Data ingestion
│   ├── nlp/                 # NL parsing & intents
│   ├── sql/                 # SQL generation & safety
│   ├── charts/              # Chart recommendations
│   ├── api/                 # FastAPI routes
│   └── ui/                  # Streamlit app
├── tests/                   # Unit & integration tests
├── .github/
│   └── copilot-instructions.md  # AI coding guidelines
├── Dockerfile               # Production deployment
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🧩 Development Sprints

**Sprint 1 — Foundation** (Tickets 1-4)
- ✅ Environment setup & dependency installation
- ✅ Data ingestion (Olist → DuckDB) — 1.5M+ rows, 11 tables
- ⏳ dbt transformations
- ⏳ RAG glossary with FAISS

**Sprint 2 — Core Features** (Tickets 5-8)
- ⏳ NL intent parsing (Llama 3.1)
- ⏳ SQL generation & execution
- ⏳ Chart recommendation + narratives
- ⏳ Streamlit UI integration

**Sprint 3 — Production** (Tickets 9-12)
- ⏳ Unit testing & evaluation
- ⏳ Performance optimization
- ⏳ Dockerization
- ⏳ Documentation & demo

## 🧪 Testing

```powershell
# Run all tests
pytest tests/

# With coverage report
pytest --cov=src tests/

# Specific test module
pytest tests/test_sql_generation.py -v
```

## 📊 Dataset

**Olist Brazilian E-Commerce** (Kaggle):
- 100k orders (2016-2018)
- Customer, product, seller, payment, review data
- Geolocation information

Tables ingested: `orders`, `customers`, `products`, `sellers`, `order_items`, `payments`, `reviews`

## 🔐 Security

- **SQL Injection Prevention**: Parameterized queries only (no string interpolation)
- **Query Validation**: Block DDL/DML operations (DROP, DELETE, UPDATE)
- **Read-Only Mode**: DuckDB connection limited to SELECT statements

## 🐳 Docker Deployment

```powershell
# Build image
docker build -t ask-your-data:latest .

# Run container
docker run -p 8501:8501 -p 8000:8000 ask-your-data:latest
```

## 🤝 Contributing

See `.github/copilot-instructions.md` for AI-assisted development guidelines.

**Development Workflow**:
1. Activate virtual environment
2. Check out new branch for ticket
3. Follow sprint/ticket sequence
4. Add tests for new features
5. Update documentation

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- **Dataset**: Olist Brazilian E-Commerce (Kaggle)
- **LLM**: Llama 3.1 (Meta AI) via Ollama
- **Tools**: DuckDB, dbt Labs, Streamlit, FastAPI

---

**Status**: Sprint 1 in progress (Environment ✅ | Data Ingestion ✅)

**Database**: `ask_your_data.db` — 11 tables, 1.5M+ rows, 40.76 MB

For detailed AI coding guidelines, see [.github/copilot-instructions.md](.github/copilot-instructions.md)
