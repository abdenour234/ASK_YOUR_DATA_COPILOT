# Ask Your Data Copilot - Complete Application Flow

**Date**: November 28, 2025  
**Purpose**: End-to-end flow from user query to visualization with code, inputs, and outputs

---

## 🎯 Complete User Journey

**User Query**: *"What are the top selling product categories?"*

This document traces the complete flow through all 6 steps with actual code, inputs, and outputs.

---

## 📊 STEP 1: RAG Retrieval (CURRENT - Ticket 4 ✅)

### **Purpose**: Find relevant business definitions for the query

### **Input**
```python
user_query = "What are the top selling product categories?"
```

### **Code** (`src/api/main.py` → `src/api/rag.py`)

```python
# FastAPI endpoint receives request
@app.get("/context/{query}")
async def get_sql_context(query: str, top_k: int = 5):
    retriever = get_retriever()
    context = retriever.get_context_for_sql(query, top_k=top_k)
    return context
```

```python
# GlossaryRetriever.get_context_for_sql() method
class GlossaryRetriever:
    def get_context_for_sql(self, query: str, top_k: int = 5) -> Dict:
        # 1. Convert query to embedding (384-dimensional vector)
        query_embedding = self.model.encode(
            query, 
            convert_to_numpy=True
        ).reshape(1, -1)
        
        # 2. Normalize for cosine similarity
        faiss.normalize_L2(query_embedding)
        
        # 3. Search FAISS index
        distances, indices = self.index.search(query_embedding, top_k * 2)
        
        # 4. Retrieve matching documents
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.documents):
                doc = self.documents[idx]
                metadata = self.metadata[idx]
                results.append(RetrievalResult(
                    type=metadata['type'],
                    name=metadata['name'],
                    description=metadata.get('description', ''),
                    score=float(distance),
                    metadata=metadata
                ))
        
        # 5. Categorize by type
        metrics = [r for r in results if r.type == 'metric']
        dimensions = [r for r in results if r.type == 'dimension']
        business_terms = [r for r in results if r.type == 'business_term']
        common_patterns = [r for r in results if r.type == 'common_query']
        
        # 6. Return structured context
        return {
            "query": query,
            "metrics": [self._format_metric(m) for m in metrics[:top_k]],
            "dimensions": [self._format_dimension(d) for d in dimensions[:top_k]],
            "business_terms": [self._format_business_term(bt) for bt in business_terms[:top_k]],
            "common_patterns": [self._format_pattern(cp) for cp in common_patterns[:top_k]],
            "all_results": [self._format_result(r) for r in results[:top_k]]
        }
```

### **Processing Steps**

#### 1. Query → Embedding Conversion
```python
# Input
query = "What are the top selling product categories?"

# sentence-transformers processes the text
embedding = model.encode(query)

# Output: 384-dimensional vector
array([0.0234, -0.1234, 0.4567, -0.2345, 0.7890, ..., 0.3456])
# Shape: (384,)
```

#### 2. FAISS Similarity Search
```python
# Input: Query embedding + FAISS index with 38 glossary embeddings
query_embedding = array([[0.0234, -0.1234, ..., 0.3456]])  # Shape: (1, 384)

# FAISS computes cosine similarity with all 38 stored embeddings
distances, indices = index.search(query_embedding, k=10)

# Output: Top 10 matches
distances = array([[0.7234, 0.6851, 0.6514, 0.6311, 0.5972, ...]])
indices = array([[25, 13, 8, 34, 21, ...]])
# Index 25 = "top_selling_products" business term
# Index 13 = "product_category" dimension
# Index 8 = "revenue" metric
# Index 34 = "Top 10 product categories" common query
```

#### 3. Retrieve Matching Documents
```python
# For each index, get the stored document and metadata
idx = 25  # "top_selling_products"

document = documents[25]
# "business_term: top_selling_products. Products with highest sales volume or revenue. Maps to: product_category. Requires: product_category, revenue."

metadata = metadata_list[25]
# {
#   'type': 'business_term',
#   'name': 'top_selling_products',
#   'description': 'Products with highest sales volume or revenue',
#   'maps_to': 'product_category',
#   'requires': ['product_category', 'revenue']
# }

score = distances[0][0]  # 0.7234
```

#### 4. Categorize Results
```python
# Separate results by type
all_results = [
    RetrievalResult(type='business_term', name='top_selling_products', score=0.7234, ...),
    RetrievalResult(type='common_query', name='Top 10 product categories', score=0.6851, ...),
    RetrievalResult(type='dimension', name='product_category', score=0.6514, ...),
    RetrievalResult(type='metric', name='revenue', score=0.5972, ...),
    RetrievalResult(type='metric', name='product_count', score=0.5123, ...),
]

# Filter by type
metrics = [r for r in all_results if r.type == 'metric']
# → [revenue (0.5972), product_count (0.5123)]

dimensions = [r for r in all_results if r.type == 'dimension']
# → [product_category (0.6514)]

business_terms = [r for r in all_results if r.type == 'business_term']
# → [top_selling_products (0.7234)]

common_patterns = [r for r in all_results if r.type == 'common_query']
# → [Top 10 product categories (0.6851)]
```

### **Output** (JSON Response)

```json
{
  "query": "What are the top selling product categories?",
  "metrics": [
    {
      "name": "revenue",
      "description": "Total payment value from completed orders",
      "sql_column": "payment_value",
      "table": "raw.order_payments",
      "aggregation": "SUM",
      "formula": "SUM(payment_value)",
      "score": 0.5972
    },
    {
      "name": "product_count",
      "description": "Number of products sold or available",
      "sql_column": "product_id",
      "table": "raw.products",
      "aggregation": "COUNT",
      "formula": "COUNT(DISTINCT product_id)",
      "score": 0.5123
    }
  ],
  "dimensions": [
    {
      "name": "product_category",
      "description": "Category of the product in Portuguese",
      "sql_column": "product_category_name",
      "table": "raw.products",
      "score": 0.6514
    }
  ],
  "business_terms": [
    {
      "name": "top_selling_products",
      "description": "Products with highest sales volume or revenue",
      "maps_to": "product_category",
      "requires": ["product_category", "revenue"],
      "score": 0.7234
    }
  ],
  "common_patterns": [
    {
      "query": "Top 10 product categories",
      "intent": "top_n",
      "metrics": ["revenue"],
      "dimensions": ["product_category"],
      "sql_pattern": "SELECT product_category, SUM(revenue) FROM ... GROUP BY product_category ORDER BY revenue DESC LIMIT 10",
      "score": 0.6851
    }
  ]
}
```

### **HTTP Request/Response**

```bash
# Request
GET http://localhost:8000/context/What are the top selling product categories?

# Response Headers
HTTP/1.1 200 OK
Content-Type: application/json

# Response Body (above JSON)
```

---

## 🧠 STEP 2: Intent Parsing (Sprint 2 - Ticket 5 - NOT YET BUILT)

### **Purpose**: Extract structured intent from natural language

### **Input**
```python
user_query = "What are the top selling product categories?"

rag_context = {
  "metrics": [{"name": "revenue", "sql_column": "payment_value", ...}],
  "dimensions": [{"name": "product_category", "sql_column": "product_category_name", ...}],
  "business_terms": [{"name": "top_selling_products", ...}],
  "common_patterns": [{"query": "Top 10 product categories", ...}]
}
```

### **Code** (`src/nlp/intent_parser.py` - TO BE CREATED)

```python
from typing import Dict, List, Optional
from pydantic import BaseModel
import ollama

class Intent(BaseModel):
    """Structured intent extracted from user query."""
    intent_type: str  # 'top_n', 'group_by', 'filter', 'time_series', 'comparison'
    metrics: List[str]
    dimensions: List[str]
    filters: List[Dict[str, any]]
    order_by: Optional[str]
    limit: Optional[int]
    time_grain: Optional[str]  # 'day', 'month', 'year'
    confidence: float

class IntentParser:
    def __init__(self):
        self.model_name = "llama3.1:8b"
    
    def parse(self, query: str, rag_context: Dict) -> Intent:
        """Parse natural language query into structured intent."""
        
        # Build prompt with RAG context
        prompt = f"""
You are an expert SQL query intent parser for an e-commerce analytics system.

USER QUERY: "{query}"

AVAILABLE CONTEXT FROM KNOWLEDGE BASE:

Metrics (what to measure):
{self._format_metrics(rag_context['metrics'])}

Dimensions (how to group/filter):
{self._format_dimensions(rag_context['dimensions'])}

Similar Patterns Found:
{self._format_patterns(rag_context['common_patterns'])}

TASK: Extract structured intent from the user query.

Determine:
1. Intent type: top_n, group_by, filter, time_series, comparison
2. Which metrics to calculate
3. Which dimensions to group by or filter on
4. Any filters to apply
5. Sort order
6. Limit (if asking for "top N")
7. Time grain (if temporal analysis)

Respond ONLY with valid JSON matching this structure:
{{
  "intent_type": "top_n",
  "metrics": ["revenue"],
  "dimensions": ["product_category"],
  "filters": [],
  "order_by": "revenue DESC",
  "limit": 10,
  "time_grain": null,
  "confidence": 0.95
}}
"""
        
        # Call Llama 3.1 via Ollama
        response = ollama.generate(
            model=self.model_name,
            prompt=prompt,
            options={
                "temperature": 0.1,  # Low temperature for consistency
                "top_p": 0.9
            }
        )
        
        # Parse JSON response
        intent_json = self._extract_json(response['response'])
        
        return Intent(**intent_json)
    
    def _format_metrics(self, metrics: List[Dict]) -> str:
        lines = []
        for m in metrics:
            lines.append(f"  - {m['name']}: {m['description']}")
            lines.append(f"    SQL: {m['aggregation']}({m['sql_column']}) from {m['table']}")
        return "\n".join(lines)
    
    def _format_dimensions(self, dimensions: List[Dict]) -> str:
        lines = []
        for d in dimensions:
            lines.append(f"  - {d['name']}: {d['description']}")
            lines.append(f"    SQL: {d['sql_column']} from {d['table']}")
        return "\n".join(lines)
    
    def _format_patterns(self, patterns: List[Dict]) -> str:
        lines = []
        for p in patterns:
            lines.append(f"  - \"{p['query']}\" (intent: {p['intent']})")
            lines.append(f"    Pattern: {p['sql_pattern']}")
        return "\n".join(lines)
    
    def _extract_json(self, response_text: str) -> Dict:
        """Extract JSON from LLM response."""
        import json
        import re
        
        # Find JSON in response (handles LLM adding explanations)
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            raise ValueError(f"No JSON found in response: {response_text}")


# Usage
parser = IntentParser()
intent = parser.parse(
    query="What are the top selling product categories?",
    rag_context=rag_context
)
```

### **LLM Processing**

#### Prompt Sent to Llama 3.1
```
You are an expert SQL query intent parser for an e-commerce analytics system.

USER QUERY: "What are the top selling product categories?"

AVAILABLE CONTEXT FROM KNOWLEDGE BASE:

Metrics (what to measure):
  - revenue: Total payment value from completed orders
    SQL: SUM(payment_value) from raw.order_payments
  - product_count: Number of products sold or available
    SQL: COUNT(DISTINCT product_id) from raw.products

Dimensions (how to group/filter):
  - product_category: Category of the product in Portuguese
    SQL: product_category_name from raw.products

Similar Patterns Found:
  - "Top 10 product categories" (intent: top_n)
    Pattern: SELECT product_category, SUM(revenue) FROM ... GROUP BY product_category ORDER BY revenue DESC LIMIT 10

TASK: Extract structured intent from the user query.
[... instructions ...]

Respond ONLY with valid JSON matching this structure:
{
  "intent_type": "top_n",
  "metrics": ["revenue"],
  "dimensions": ["product_category"],
  "filters": [],
  "order_by": "revenue DESC",
  "limit": 10,
  "time_grain": null,
  "confidence": 0.95
}
```

#### LLM Response
```json
{
  "intent_type": "top_n",
  "metrics": ["revenue"],
  "dimensions": ["product_category"],
  "filters": [],
  "order_by": "revenue DESC",
  "limit": 10,
  "time_grain": null,
  "confidence": 0.95
}
```

### **Output** (Structured Intent Object)

```python
Intent(
    intent_type='top_n',
    metrics=['revenue'],
    dimensions=['product_category'],
    filters=[],
    order_by='revenue DESC',
    limit=10,
    time_grain=None,
    confidence=0.95
)
```

---

## 🔧 STEP 3: SQL Generation (Sprint 2 - Ticket 6 - NOT YET BUILT)

### **Purpose**: Convert intent + RAG context into safe, executable SQL

### **Input**
```python
intent = Intent(
    intent_type='top_n',
    metrics=['revenue'],
    dimensions=['product_category'],
    filters=[],
    order_by='revenue DESC',
    limit=10,
    time_grain=None,
    confidence=0.95
)

rag_context = {
  "metrics": [
    {
      "name": "revenue",
      "sql_column": "payment_value",
      "table": "raw.order_payments",
      "aggregation": "SUM"
    }
  ],
  "dimensions": [
    {
      "name": "product_category",
      "sql_column": "product_category_name",
      "table": "raw.products"
    }
  ]
}
```

### **Code** (`src/sql/generator.py` - TO BE CREATED)

```python
from typing import Dict, List
import duckdb

class SQLGenerator:
    def __init__(self, db_path: str = "ask_your_data.db"):
        self.conn = duckdb.connect(db_path)
        
        # Table relationships (from glossary relationships section)
        self.relationships = {
            ('raw.orders', 'raw.customers'): 'orders.customer_id = customers.customer_id',
            ('raw.orders', 'raw.order_items'): 'orders.order_id = order_items.order_id',
            ('raw.order_items', 'raw.products'): 'order_items.product_id = products.product_id',
            ('raw.order_items', 'raw.sellers'): 'order_items.seller_id = sellers.seller_id',
            ('raw.orders', 'raw.order_payments'): 'orders.order_id = order_payments.order_id',
            ('raw.order_payments', 'raw.order_items'): 'order_payments.order_id = order_items.order_id',
        }
    
    def generate(self, intent: Intent, rag_context: Dict) -> str:
        """Generate SQL from intent and RAG context."""
        
        # 1. Determine required tables
        tables = self._get_required_tables(intent, rag_context)
        
        # 2. Build SELECT clause
        select_clause = self._build_select(intent, rag_context)
        
        # 3. Build FROM clause with JOINs
        from_clause = self._build_from_with_joins(tables)
        
        # 4. Build WHERE clause (filters)
        where_clause = self._build_where(intent)
        
        # 5. Build GROUP BY clause
        group_by_clause = self._build_group_by(intent, rag_context)
        
        # 6. Build ORDER BY clause
        order_by_clause = self._build_order_by(intent)
        
        # 7. Build LIMIT clause
        limit_clause = self._build_limit(intent)
        
        # 8. Assemble SQL
        sql = f"""
{select_clause}
{from_clause}
{where_clause}
{group_by_clause}
{order_by_clause}
{limit_clause}
        """.strip()
        
        return sql
    
    def _get_required_tables(self, intent: Intent, rag_context: Dict) -> List[str]:
        """Determine which tables are needed."""
        tables = set()
        
        # From metrics
        for metric_name in intent.metrics:
            metric = next((m for m in rag_context['metrics'] if m['name'] == metric_name), None)
            if metric:
                tables.add(metric['table'])
        
        # From dimensions
        for dim_name in intent.dimensions:
            dim = next((d for d in rag_context['dimensions'] if d['name'] == dim_name), None)
            if dim:
                tables.add(dim['table'])
        
        return list(tables)
    
    def _build_select(self, intent: Intent, rag_context: Dict) -> str:
        """Build SELECT clause."""
        select_parts = []
        
        # Add dimensions
        for dim_name in intent.dimensions:
            dim = next((d for d in rag_context['dimensions'] if d['name'] == dim_name), None)
            if dim:
                table_alias = self._get_alias(dim['table'])
                select_parts.append(f"{table_alias}.{dim['sql_column']} AS {dim_name}")
        
        # Add metrics
        for metric_name in intent.metrics:
            metric = next((m for m in rag_context['metrics'] if m['name'] == metric_name), None)
            if metric:
                table_alias = self._get_alias(metric['table'])
                agg = metric['aggregation']
                col = metric['sql_column']
                select_parts.append(f"{agg}({table_alias}.{col}) AS {metric_name}")
        
        return "SELECT\n    " + ",\n    ".join(select_parts)
    
    def _build_from_with_joins(self, tables: List[str]) -> str:
        """Build FROM clause with necessary JOINs."""
        if len(tables) == 1:
            table = tables[0]
            alias = self._get_alias(table)
            return f"FROM {table} {alias}"
        
        # Find join path (simplified - uses predefined relationships)
        # In production, use graph traversal to find shortest path
        
        # For this example: order_payments → order_items → products
        if 'raw.order_payments' in tables and 'raw.products' in tables:
            return """FROM raw.order_payments op
JOIN raw.order_items oi ON op.order_id = oi.order_id
JOIN raw.products p ON oi.product_id = p.product_id"""
        
        # Fallback: join all tables (simplified)
        from_parts = [f"{tables[0]} {self._get_alias(tables[0])}"]
        for i in range(1, len(tables)):
            table = tables[i]
            alias = self._get_alias(table)
            # Find join condition
            join_key = (tables[i-1], table)
            if join_key in self.relationships:
                condition = self.relationships[join_key]
                from_parts.append(f"JOIN {table} {alias} ON {condition}")
        
        return "FROM " + "\n".join(from_parts)
    
    def _build_where(self, intent: Intent) -> str:
        """Build WHERE clause from filters."""
        if not intent.filters:
            return ""
        
        conditions = []
        for filter_obj in intent.filters:
            # Example: {"dimension": "order_status", "operator": "=", "value": "delivered"}
            conditions.append(f"{filter_obj['dimension']} {filter_obj['operator']} '{filter_obj['value']}'")
        
        return "WHERE " + " AND ".join(conditions)
    
    def _build_group_by(self, intent: Intent, rag_context: Dict) -> str:
        """Build GROUP BY clause."""
        if not intent.dimensions:
            return ""
        
        group_parts = []
        for dim_name in intent.dimensions:
            dim = next((d for d in rag_context['dimensions'] if d['name'] == dim_name), None)
            if dim:
                table_alias = self._get_alias(dim['table'])
                group_parts.append(f"{table_alias}.{dim['sql_column']}")
        
        return "GROUP BY " + ", ".join(group_parts)
    
    def _build_order_by(self, intent: Intent) -> str:
        """Build ORDER BY clause."""
        if not intent.order_by:
            return ""
        return f"ORDER BY {intent.order_by}"
    
    def _build_limit(self, intent: Intent) -> str:
        """Build LIMIT clause."""
        if not intent.limit:
            return ""
        return f"LIMIT {intent.limit}"
    
    def _get_alias(self, table: str) -> str:
        """Get table alias."""
        aliases = {
            'raw.order_payments': 'op',
            'raw.order_items': 'oi',
            'raw.products': 'p',
            'raw.orders': 'o',
            'raw.customers': 'c',
            'raw.sellers': 's'
        }
        return aliases.get(table, table.split('.')[-1][0])


# Usage
generator = SQLGenerator()
sql = generator.generate(intent, rag_context)
```

### **Output** (Generated SQL)

```sql
SELECT
    p.product_category_name AS product_category,
    SUM(op.payment_value) AS revenue
FROM raw.order_payments op
JOIN raw.order_items oi ON op.order_id = oi.order_id
JOIN raw.products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY revenue DESC
LIMIT 10
```

### **SQL Validation** (`src/sql/validator.py` - TO BE CREATED)

```python
import re
from typing import Tuple, List

class SQLValidator:
    """Validates SQL for safety before execution."""
    
    # Dangerous SQL keywords
    FORBIDDEN_KEYWORDS = [
        'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE',
        'TRUNCATE', 'EXEC', 'EXECUTE', '--', ';--', '/*', '*/'
    ]
    
    def validate(self, sql: str) -> Tuple[bool, List[str]]:
        """
        Validate SQL query for safety.
        Returns: (is_valid, list_of_errors)
        """
        errors = []
        sql_upper = sql.upper()
        
        # 1. Check for forbidden keywords
        for keyword in self.FORBIDDEN_KEYWORDS:
            if keyword in sql_upper:
                errors.append(f"Forbidden keyword: {keyword}")
        
        # 2. Must start with SELECT
        if not sql_upper.strip().startswith('SELECT'):
            errors.append("Query must start with SELECT")
        
        # 3. Check for SQL injection patterns
        injection_patterns = [
            r"'\s*OR\s+'1'\s*=\s*'1",  # ' OR '1'='1
            r";\s*DROP",                 # ; DROP
            r"UNION\s+SELECT",           # UNION SELECT
        ]
        for pattern in injection_patterns:
            if re.search(pattern, sql_upper):
                errors.append(f"Potential SQL injection detected: {pattern}")
        
        # 4. Check table names exist (query information_schema)
        # ... implementation ...
        
        is_valid = len(errors) == 0
        return is_valid, errors


# Usage
validator = SQLValidator()
is_valid, errors = validator.validate(sql)

if is_valid:
    print("✓ SQL is safe to execute")
else:
    print("✗ SQL validation failed:")
    for error in errors:
        print(f"  - {error}")
```

**Validation Result**:
```
✓ SQL is safe to execute
```

---

## 💾 STEP 4: DuckDB Execution

### **Purpose**: Execute SQL and return results as DataFrame

### **Input**
```sql
SELECT
    p.product_category_name AS product_category,
    SUM(op.payment_value) AS revenue
FROM raw.order_payments op
JOIN raw.order_items oi ON op.order_id = oi.order_id
JOIN raw.products p ON oi.product_id = p.product_id
GROUP BY p.product_category_name
ORDER BY revenue DESC
LIMIT 10
```

### **Code**

```python
import duckdb
import pandas as pd

# Connect to database
conn = duckdb.connect('ask_your_data.db')

# Execute query
result = conn.execute(sql)

# Convert to pandas DataFrame
df = result.df()

# Close connection
conn.close()
```

### **DuckDB Internal Processing**

```
1. Parse SQL
   ├─ Identify tables: order_payments, order_items, products
   ├─ Identify joins: order_id, product_id
   ├─ Identify aggregation: SUM(payment_value)
   └─ Identify grouping: product_category_name

2. Optimize query plan
   ├─ Push down filters (none in this case)
   ├─ Choose join order (broadcast join for products)
   └─ Parallel execution plan

3. Execute
   ├─ Scan order_payments: 103,886 rows
   ├─ Hash join with order_items on order_id: 112,650 rows
   ├─ Hash join with products on product_id
   ├─ Group by product_category_name (71 groups)
   ├─ Aggregate SUM(payment_value) per group
   ├─ Sort by revenue DESC
   └─ Take top 10

4. Return result set
```

### **Output** (pandas DataFrame)

```python
df
```

```
         product_category     revenue
0           beleza_saude  1234567.89
1           informatica   987654.32
2      moveis_decoracao   876543.21
3        esporte_lazer   765432.10
4    relogios_presentes   654321.09
5      cama_mesa_banho   543210.98
6            telefonia   432109.87
7           automotivo   321098.76
8           brinquedos   210987.65
9   ferramentas_jardim   109876.54
```

```python
# DataFrame info
df.shape  # (10, 2)
df.dtypes
# product_category     object
# revenue             float64

df.head()
#         product_category     revenue
# 0           beleza_saude  1234567.89
# 1           informatica   987654.32
# 2      moveis_decoracao   876543.21
# 3        esporte_lazer   765432.10
# 4    relogios_presentes   654321.09
```

---

## 📊 STEP 5: Chart Recommendation & Narrative (Sprint 2 - Ticket 7)

### **Purpose**: Choose appropriate visualization and generate insights

### **Input**
```python
df = pd.DataFrame({
    'product_category': ['beleza_saude', 'informatica', 'moveis_decoracao', ...],
    'revenue': [1234567.89, 987654.32, 876543.21, ...]
})

intent = Intent(
    intent_type='top_n',
    metrics=['revenue'],
    dimensions=['product_category'],
    limit=10
)

user_query = "What are the top selling product categories?"
```

### **Code** (`src/charts/recommender.py` - TO BE CREATED)

```python
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Tuple
import pandas as pd

class ChartRecommender:
    """Recommends and generates charts based on data shape and intent."""
    
    def recommend_and_generate(
        self, 
        df: pd.DataFrame, 
        intent: Intent,
        user_query: str
    ) -> Tuple[go.Figure, str]:
        """
        Returns: (plotly_figure, chart_config_json)
        """
        
        # Analyze data
        num_metrics = len(intent.metrics)
        num_dimensions = len(intent.dimensions)
        row_count = len(df)
        
        # Determine chart type
        chart_type = self._determine_chart_type(
            num_metrics, num_dimensions, row_count, intent.intent_type
        )
        
        # Generate chart
        fig = self._generate_chart(df, chart_type, intent)
        
        # Chart config
        config = {
            "type": chart_type,
            "x": intent.dimensions[0] if intent.dimensions else None,
            "y": intent.metrics[0] if intent.metrics else None,
            "title": self._generate_title(user_query)
        }
        
        return fig, config
    
    def _determine_chart_type(
        self, 
        num_metrics: int, 
        num_dimensions: int, 
        row_count: int,
        intent_type: str
    ) -> str:
        """Determine best chart type."""
        
        # Decision tree for chart selection
        if intent_type == 'top_n':
            if row_count <= 15:
                return 'bar_horizontal'  # Horizontal bar for rankings
            else:
                return 'bar_vertical'
        
        elif intent_type == 'time_series':
            return 'line'
        
        elif intent_type == 'comparison' and num_dimensions == 1:
            return 'bar_vertical'
        
        elif intent_type == 'comparison' and num_dimensions == 2:
            return 'grouped_bar'
        
        elif num_dimensions == 0 and num_metrics == 1:
            return 'metric_card'  # Single number display
        
        else:
            # Default
            return 'bar_vertical'
    
    def _generate_chart(
        self, 
        df: pd.DataFrame, 
        chart_type: str, 
        intent: Intent
    ) -> go.Figure:
        """Generate Plotly figure."""
        
        if chart_type == 'bar_horizontal':
            # Horizontal bar chart (good for rankings)
            fig = px.bar(
                df,
                x=intent.metrics[0],
                y=intent.dimensions[0],
                orientation='h',
                title=f"Top {len(df)} {intent.dimensions[0].replace('_', ' ').title()} by {intent.metrics[0].replace('_', ' ').title()}",
                labels={
                    intent.metrics[0]: intent.metrics[0].replace('_', ' ').title(),
                    intent.dimensions[0]: intent.dimensions[0].replace('_', ' ').title()
                }
            )
            
            # Customize layout
            fig.update_layout(
                height=500,
                showlegend=False,
                yaxis={'categoryorder': 'total ascending'},  # Sort by value
                hovermode='closest'
            )
            
            # Format hover
            fig.update_traces(
                hovertemplate='<b>%{y}</b><br>Revenue: R$%{x:,.2f}<extra></extra>'
            )
            
            return fig
        
        elif chart_type == 'bar_vertical':
            # Vertical bar chart
            fig = px.bar(df, x=intent.dimensions[0], y=intent.metrics[0])
            return fig
        
        elif chart_type == 'line':
            # Line chart (time series)
            fig = px.line(df, x=intent.dimensions[0], y=intent.metrics[0])
            return fig
        
        else:
            # Default
            fig = px.bar(df, x=intent.dimensions[0], y=intent.metrics[0])
            return fig
    
    def _generate_title(self, user_query: str) -> str:
        """Generate chart title from user query."""
        # Capitalize first letter
        return user_query[0].upper() + user_query[1:]


# Usage
recommender = ChartRecommender()
fig, chart_config = recommender.recommend_and_generate(df, intent, user_query)
```

### **Chart Output** (Plotly Figure)

```python
# fig is a Plotly Figure object
fig.show()  # Opens in browser

# Or get as JSON for Streamlit
fig_json = fig.to_json()
```

**Visual representation**:
```
┌─────────────────────────────────────────────────────────────┐
│ Top 10 Product Category by Revenue                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ beleza_saude         ████████████████████████ R$1,234,568  │
│ informatica          ███████████████████ R$987,654         │
│ moveis_decoracao     █████████████████ R$876,543           │
│ esporte_lazer        ██████████████ R$765,432              │
│ relogios_presentes   ████████████ R$654,321                │
│ cama_mesa_banho      ██████████ R$543,211                  │
│ telefonia            ████████ R$432,110                    │
│ automotivo           ██████ R$321,099                      │
│ brinquedos           ████ R$210,988                        │
│ ferramentas_jardim   ██ R$109,877                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### **Narrative Generation** (`src/charts/narrative.py` - TO BE CREATED)

```python
import ollama
from typing import Dict
import pandas as pd

class NarrativeGenerator:
    """Generates natural language insights from data."""
    
    def __init__(self):
        self.model_name = "llama3.1:8b"
    
    def generate(
        self, 
        df: pd.DataFrame, 
        user_query: str, 
        rag_context: Dict
    ) -> str:
        """Generate narrative insights."""
        
        # Prepare data summary
        data_summary = self._summarize_data(df)
        
        # Build prompt
        prompt = f"""
You are a data analyst explaining insights to a business user.

USER ASKED: "{user_query}"

DATA RESULTS:
{data_summary}

CONTEXT:
{self._format_context(rag_context)}

TASK: Write a concise 2-3 sentence insight highlighting:
1. The top result
2. Key patterns or comparisons
3. Business implication (if applicable)

Use specific numbers. Be conversational but professional.
Respond in plain text (no markdown).
"""
        
        # Call LLM
        response = ollama.generate(
            model=self.model_name,
            prompt=prompt,
            options={"temperature": 0.7}
        )
        
        return response['response'].strip()
    
    def _summarize_data(self, df: pd.DataFrame) -> str:
        """Create text summary of DataFrame."""
        lines = []
        lines.append(f"Total rows: {len(df)}")
        lines.append(f"\nTop 5 results:")
        
        for idx, row in df.head(5).iterrows():
            line = f"  {idx+1}. " + ", ".join([f"{col}: {val:,.2f}" if isinstance(val, float) else f"{col}: {val}" for col, val in row.items()])
            lines.append(line)
        
        if len(df) > 5:
            lines.append(f"  ... and {len(df) - 5} more")
        
        # Add totals if numeric columns exist
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            lines.append(f"\nTotals:")
            for col in numeric_cols:
                lines.append(f"  {col}: {df[col].sum():,.2f}")
        
        return "\n".join(lines)
    
    def _format_context(self, rag_context: Dict) -> str:
        """Format RAG context for prompt."""
        lines = []
        if rag_context.get('metrics'):
            lines.append(f"Metric: {rag_context['metrics'][0]['name']} = {rag_context['metrics'][0]['description']}")
        if rag_context.get('dimensions'):
            lines.append(f"Dimension: {rag_context['dimensions'][0]['name']} = {rag_context['dimensions'][0]['description']}")
        return "\n".join(lines)


# Usage
narrative_gen = NarrativeGenerator()
narrative = narrative_gen.generate(df, user_query, rag_context)
```

### **LLM Prompt**

```
You are a data analyst explaining insights to a business user.

USER ASKED: "What are the top selling product categories?"

DATA RESULTS:
Total rows: 10

Top 5 results:
  1. product_category: beleza_saude, revenue: 1,234,567.89
  2. product_category: informatica, revenue: 987,654.32
  3. product_category: moveis_decoracao, revenue: 876,543.21
  4. product_category: esporte_lazer, revenue: 765,432.10
  5. product_category: relogios_presentes, revenue: 654,321.09
  ... and 5 more

Totals:
  revenue: 6,640,998.86

CONTEXT:
Metric: revenue = Total payment value from completed orders
Dimension: product_category = Category of the product in Portuguese

TASK: Write a concise 2-3 sentence insight highlighting:
1. The top result
2. Key patterns or comparisons
3. Business implication (if applicable)

Use specific numbers. Be conversational but professional.
Respond in plain text (no markdown).
```

### **Output** (Generated Narrative)

```
The Beauty & Health (beleza_saude) category leads with R$1.23M in revenue, 
representing 18.6% of the total R$6.64M from the top 10 categories. 
Electronics (informatica) and Home Decor (moveis_decoracao) follow at R$988K 
and R$877K respectively, with the top three categories accounting for nearly 
46% of total revenue. This concentration suggests focusing marketing efforts 
on these high-performing categories could yield the greatest ROI.
```

---

## 🖥️ STEP 6: Streamlit UI Display (Sprint 2 - Ticket 8)

### **Purpose**: Present results interactively to user

### **Input**
```python
user_query = "What are the top selling product categories?"
fig = <Plotly Figure object>
narrative = "The Beauty & Health (beleza_saude) category leads with..."
sql = "SELECT p.product_category_name AS product_category..."
df = <pandas DataFrame with 10 rows>
```

### **Code** (`src/ui/app.py` - TO BE CREATED)

```python
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
from src.charts.recommender import ChartRecommender
from src.charts.narrative import NarrativeGenerator
import duckdb

# Page config
st.set_page_config(
    page_title="Ask Your Data Copilot",
    page_icon="🤖",
    layout="wide"
)

# Title
st.title("🤖 Ask Your Data Copilot")
st.markdown("*Ask questions about your e-commerce data in plain English*")

# Sidebar - RAG API status
with st.sidebar:
    st.header("⚙️ System Status")
    
    # Check RAG API
    try:
        response = requests.get("http://localhost:8000/")
        status = response.json()
        st.success(f"✅ RAG API: Online")
        st.metric("Glossary Entries", status['total_entries'])
    except:
        st.error("❌ RAG API: Offline")
        st.stop()
    
    # Database info
    conn = duckdb.connect('ask_your_data.db')
    table_count = conn.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'raw'").fetchone()[0]
    st.metric("Database Tables", table_count)
    conn.close()
    
    st.divider()
    
    # Example queries
    st.subheader("💡 Try asking:")
    examples = [
        "What are the top selling product categories?",
        "Show me revenue by state",
        "What is the average order value?",
        "How many orders were placed each month?",
        "Which payment methods are most popular?"
    ]
    for example in examples:
        if st.button(example, key=example):
            st.session_state['query'] = example

# Main query input
if 'query' not in st.session_state:
    st.session_state['query'] = ""

query = st.text_input(
    "Ask a question about your data:",
    value=st.session_state['query'],
    placeholder="e.g., What are the top selling product categories?"
)

if st.button("🔍 Analyze", type="primary") or (query and query != st.session_state.get('last_query', '')):
    st.session_state['last_query'] = query
    
    if not query:
        st.warning("Please enter a question")
        st.stop()
    
    # Progress indicator
    with st.spinner("🧠 Understanding your question..."):
        # STEP 1: RAG Retrieval
        rag_response = requests.get(f"http://localhost:8000/context/{query}")
        rag_context = rag_response.json()
        
        st.success(f"✓ Found {len(rag_context['metrics'])} relevant metrics, {len(rag_context['dimensions'])} dimensions")
    
    with st.spinner("🔧 Generating SQL..."):
        # STEP 2 & 3: Intent Parsing + SQL Generation
        # (For demo, using simplified version)
        from src.nlp.intent_parser import IntentParser
        from src.sql.generator import SQLGenerator
        
        parser = IntentParser()
        intent = parser.parse(query, rag_context)
        
        generator = SQLGenerator()
        sql = generator.generate(intent, rag_context)
        
        st.success("✓ SQL generated")
    
    with st.spinner("💾 Executing query..."):
        # STEP 4: DuckDB Execution
        conn = duckdb.connect('ask_your_data.db')
        df = conn.execute(sql).df()
        conn.close()
        
        st.success(f"✓ Retrieved {len(df)} rows")
    
    with st.spinner("📊 Creating visualization..."):
        # STEP 5: Chart Recommendation
        recommender = ChartRecommender()
        fig, chart_config = recommender.recommend_and_generate(df, intent, query)
        
        # Generate narrative
        narrative_gen = NarrativeGenerator()
        narrative = narrative_gen.generate(df, query, rag_context)
        
        st.success("✓ Visualization ready")
    
    # STEP 6: Display Results
    st.divider()
    st.subheader(f"Results: {query}")
    
    # Layout: Chart | Insights
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📝 Key Insights")
        st.info(narrative)
        
        st.markdown("### 📊 Data Summary")
        st.metric("Total Rows", len(df))
        
        # Show numeric summaries
        numeric_cols = df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            st.metric(
                f"Total {col.replace('_', ' ').title()}", 
                f"R${df[col].sum():,.2f}"
            )
    
    # Expandable sections
    with st.expander("🔍 View SQL Query"):
        st.code(sql, language="sql")
    
    with st.expander("📋 View Raw Data"):
        st.dataframe(df, use_container_width=True)
    
    with st.expander("🧠 RAG Context (Debug)"):
        st.json(rag_context)
    
    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=f"results_{query[:30]}.csv",
        mime="text/csv"
    )
```

### **Visual Output** (Streamlit UI)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ 🤖 Ask Your Data Copilot                                                 │
│ Ask questions about your e-commerce data in plain English                │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ Ask a question about your data:                                          │
│ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ What are the top selling product categories?                        │ │
│ └─────────────────────────────────────────────────────────────────────┘ │
│                                                  [🔍 Analyze]             │
│                                                                           │
├──────────────────────────────────────────────────────────────────────────┤
│ Results: What are the top selling product categories?                    │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ ┌────────────────────────────────┬──────────────────────────────────┐   │
│ │  CHART (Interactive)           │  📝 Key Insights                 │   │
│ │                                │                                  │   │
│ │  Top 10 Product Category       │  The Beauty & Health             │   │
│ │  by Revenue                    │  (beleza_saude) category leads   │   │
│ │                                │  with R$1.23M in revenue,        │   │
│ │  beleza_saude    ██████████    │  representing 18.6% of the total │   │
│ │  informatica     ████████      │  R$6.64M from the top 10         │   │
│ │  moveis_decoracao ███████      │  categories...                   │   │
│ │  esporte_lazer   ██████        │                                  │   │
│ │  ...                           │  📊 Data Summary                 │   │
│ │                                │  Total Rows: 10                  │   │
│ │  [Hover for details]           │  Total Revenue: R$6,640,998.86   │   │
│ └────────────────────────────────┴──────────────────────────────────┘   │
│                                                                           │
│ ▼ 🔍 View SQL Query                                                      │
│ ▼ 📋 View Raw Data                                                       │
│ ▼ 🧠 RAG Context (Debug)                                                 │
│                                                                           │
│ [📥 Download CSV]                                                        │
│                                                                           │
└──────────────────────────────────────────────────────────────────────────┘

SIDEBAR:
┌─────────────────────────┐
│ ⚙️ System Status        │
├─────────────────────────┤
│ ✅ RAG API: Online      │
│ Glossary Entries: 38    │
│ Database Tables: 9      │
├─────────────────────────┤
│ 💡 Try asking:          │
│ • What are the top...   │
│ • Show me revenue...    │
│ • What is the average...│
│ • How many orders...    │
│ • Which payment...      │
└─────────────────────────┘
```

---

## 🔄 Complete Data Flow Summary

```
USER INPUT
  "What are the top selling product categories?"
        ↓
┌─────────────────────────────────────────────────┐
│ STEP 1: RAG Retrieval (Ticket 4 ✅)            │
│ Input: Query string                             │
│ Process: Embedding → FAISS search → Categorize │
│ Output: Metrics, dimensions, patterns (JSON)    │
│ Time: ~50ms                                     │
└─────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────┐
│ STEP 2: Intent Parsing (Ticket 5 ⏳)           │
│ Input: Query + RAG context                      │
│ Process: Llama 3.1 extracts intent              │
│ Output: Structured Intent object                │
│ Time: ~2s                                       │
└─────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────┐
│ STEP 3: SQL Generation (Ticket 6 ⏳)           │
│ Input: Intent + RAG context                     │
│ Process: Build SELECT/FROM/JOIN/WHERE/GROUP BY  │
│ Output: Parameterized SQL string                │
│ Time: ~100ms                                    │
└─────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────┐
│ STEP 4: DuckDB Execution                        │
│ Input: SQL query                                │
│ Process: Parse → Optimize → Execute             │
│ Output: pandas DataFrame                        │
│ Time: ~200ms                                    │
└─────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────┐
│ STEP 5: Visualization (Ticket 7 ⏳)            │
│ Input: DataFrame + Intent                       │
│ Process: Chart recommendation + LLM narrative   │
│ Output: Plotly Figure + insight text            │
│ Time: ~3s                                       │
└─────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────┐
│ STEP 6: Streamlit Display (Ticket 8 ⏳)        │
│ Input: All outputs from Steps 1-5              │
│ Process: Render UI components                   │
│ Output: Interactive web page                    │
│ Time: ~100ms                                    │
└─────────────────────────────────────────────────┘
        ↓
USER SEES RESULT
  📊 Chart + 📝 Insights + 💾 Download option
  
Total Time: ~6 seconds
```

---

## 📝 Key Takeaways

### **Current State** (After Ticket 4)
- ✅ **RAG system operational**: Glossary searchable via FastAPI
- ✅ **FAISS index built**: 38 entries, 384-dim embeddings
- ✅ **Semantic search working**: Returns relevant metrics/dimensions

### **Next Steps** (Sprint 2)
- ⏳ **Ticket 5**: Integrate Llama 3.1 for intent parsing
- ⏳ **Ticket 6**: Build SQL generator with safety validation
- ⏳ **Ticket 7**: Implement chart recommendation + narrative generation
- ⏳ **Ticket 8**: Create Streamlit UI connecting all components

### **Why This Architecture Works**

1. **Modular**: Each step is independent and testable
2. **Safe**: SQL validation prevents injection
3. **Scalable**: Add more glossary entries without code changes
4. **Transparent**: User sees SQL and can download raw data
5. **Intelligent**: LLM handles natural language, not hardcoded rules

---

**End of Complete Flow Documentation**
