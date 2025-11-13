# Sprint 1 - Ticket 2: Data Ingestion

## ✅ Completed Tasks

### 1. Dataset Analysis
- **9 CSV files identified** from Olist Brazilian E-commerce dataset
- Date range: September 2016 to October 2018
- Total raw records: ~1.55 million rows

### 2. Data Ingestion Script Created

✏️ **`src/ingest/data.py`** — Automated DuckDB loader

**Key Features**:
- Uses `duckdb.read_csv_auto()` for fast, automatic type inference
- Creates organized schemas: `raw` and `dimensions`
- Handles all 9 Olist CSV files automatically
- Generates calendar dimension (2016-2025) with date attributes
- Creates Brazilian states dimension with regional mapping
- Comprehensive error handling and progress reporting

**Class**: `OlistDataIngester`
- `load_csv_files()`: Bulk CSV ingestion with auto-detection
- `create_calendar_dimension()`: Date dimension with 17 attributes
- `create_country_dimension()`: Brazilian states with regions
- `run_full_ingestion()`: Complete pipeline execution

### 3. Database Schema

**Raw Tables** (9 tables):
| Table | Rows | Description |
|-------|------|-------------|
| `raw.customers` | 99,441 | Customer information |
| `raw.geolocation` | 1,000,163 | Geographic coordinates |
| `raw.orders` | 99,441 | Order master records |
| `raw.order_items` | 112,650 | Line items per order |
| `raw.order_payments` | 103,886 | Payment transactions |
| `raw.order_reviews` | 99,224 | Customer reviews |
| `raw.products` | 32,951 | Product catalog |
| `raw.sellers` | 3,095 | Seller information |
| `raw.product_category_translation` | 71 | Category translations |

**Dimension Tables** (2 tables):
| Table | Rows | Description |
|-------|------|-------------|
| `dimensions.calendar` | 3,653 | Date dimension 2016-2025 |
| `dimensions.brazilian_states` | 27 | State/region mapping |

**Total**: 11 tables, 1,554,602 rows, 40.76 MB

### 4. Data Verification

✏️ **`src/ingest/verify_data.py`** — Quality checks

**Validation Results**:
- ✅ All schemas created (raw, dimensions)
- ✅ All 11 tables loaded successfully
- ✅ No NULL primary keys
- ✅ Date range validated: 2016-09-04 to 2018-10-17
- ✅ 99.2% of orders have line items
- ✅ Calendar covers full date range needed
- ✅ All 27 Brazilian states mapped

### 5. Calendar Dimension Attributes

The `dimensions.calendar` table includes:
- **Date fields**: date_key, date, year, quarter, month, week, day
- **Names**: month_name, day_name
- **Week context**: day_of_week (1=Mon, 7=Sun), is_weekend
- **Period flags**: is_month_start, is_month_end, is_quarter_start, is_quarter_end, is_year_start, is_year_end

**Use case**: Time-series analysis, period comparisons, trend detection

### 6. Brazilian States Dimension

Maps 27 Brazilian states to regions:
- **North**: 7 states (AC, AP, AM, PA, RO, RR, TO)
- **Northeast**: 9 states (AL, BA, CE, MA, PB, PE, PI, RN, SE)
- **Central-West**: 4 states (DF, GO, MT, MS)
- **Southeast**: 4 states (ES, MG, RJ, SP)
- **South**: 3 states (PR, RS, SC)

**Use case**: Geographic analysis, regional sales comparisons

## 📊 Data Quality Summary

| Metric | Value | Status |
|--------|-------|--------|
| Tables created | 11 | ✅ |
| Total rows | 1,554,602 | ✅ |
| NULL primary keys | 0 | ✅ |
| Orders with items | 99.2% | ✅ |
| Date coverage | 2016-2025 | ✅ |
| Database size | 40.76 MB | ✅ |

## 🔧 Usage Examples

### Load Data (Re-run)
```powershell
.\ask-your-data-env\Scripts\activate
python src/ingest/data.py
```

### Verify Data
```powershell
python src/ingest/verify_data.py
```

### Query Data (Python)
```python
import duckdb

conn = duckdb.connect('ask_your_data.db', read_only=True)

# Get order summary
result = conn.execute("""
    SELECT 
        order_status,
        COUNT(*) as order_count,
        COUNT(DISTINCT customer_id) as unique_customers
    FROM raw.orders
    GROUP BY order_status
    ORDER BY order_count DESC
""").fetchdf()

print(result)
conn.close()
```

### Query Data (DuckDB CLI)
```powershell
# Install DuckDB CLI if needed
# https://duckdb.org/docs/installation/

duckdb ask_your_data.db

-- Example queries
SELECT COUNT(*) FROM raw.orders;
SELECT * FROM dimensions.calendar WHERE year = 2017 LIMIT 10;
SELECT state_code, state_name, region FROM dimensions.brazilian_states;
```

## 📝 Code Patterns Established

### 1. DuckDB Fast Loading
```python
# Use read_csv_auto for automatic type inference
conn.execute(f"""
    CREATE TABLE {table_name} AS 
    SELECT * FROM read_csv_auto('{csv_path}', 
        header=true, 
        nullstr='',
        dateformat='%Y-%m-%d %H:%M:%S'
    )
""")
```

### 2. Pandas Integration
```python
# Register DataFrame as temporary table
conn.register('temp_table', dataframe)
conn.execute("CREATE TABLE final_table AS SELECT * FROM temp_table")
conn.unregister('temp_table')
```

### 3. Schema Organization
```python
# Separate raw data from dimensions
conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
conn.execute("CREATE SCHEMA IF NOT EXISTS dimensions")
```

## 🎯 Next Steps (Sprint 1 - Ticket 3)

**dbt Transformations**: Create staging and mart models

1. Initialize dbt project in `dbt/` directory
2. Configure `dbt_project.yml` for DuckDB adapter
3. Create staging models (1:1 with raw tables)
4. Build fact tables (orders, order_items)
5. Build dimension tables (customers, products, sellers)
6. Add data quality tests
7. Document models

**Dependencies**: Ticket 2 (this ticket) must be complete

## ⚠️ Important Notes

- **Database location**: `ask_your_data.db` (excluded from git)
- **Re-running ingestion**: Script drops and recreates tables
- **Date formats**: Auto-detected by DuckDB (`%Y-%m-%d %H:%M:%S`)
- **Performance**: DuckDB loads 1.5M+ rows in seconds
- **Read-only access**: Use `read_only=True` for queries to prevent locks

## 📋 Files Created/Modified

| File | Purpose |
|------|---------|
| `src/ingest/data.py` | Main ingestion script |
| `src/ingest/verify_data.py` | Data validation script |
| `ask_your_data.db` | DuckDB database (40.76 MB) |
| `SPRINT1_TICKET2_COMPLETE.md` | This documentation |

## ✨ Ticket 2 Complete!

**Status**: Sprint 1 - Ticket 2 COMPLETE ✅

**Effort**: S (1 day) — **Actual**: Complete ✅

**Dependencies Met**: Ticket 1 (environment setup)

**Blocks**: Ticket 3 (dbt transformations) — READY TO START
