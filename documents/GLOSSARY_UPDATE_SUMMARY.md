# Glossary Update Summary

**Date**: November 28, 2025  
**Version**: 2.0 (updated from 1.0)  
**Reason**: Align glossary with dbt transformations and mart schema

---

## Overview

Updated the business glossary (`glossary/business_terms.yaml`) to reflect your dbt data transformations, including:
- Mart tables (fact_orders, fact_order_items, dim_customers, dim_products, dim_sellers)
- Staging transformations (cleaned columns, renamed timestamps)
- Dimension enrichments (regions, English translations, calendar attributes)

---

## Key Changes

### 1. **Table References Updated**

**Old**: References to `raw.*` tables  
**New**: References to both staging (`stg_*`) and mart tables

#### Example:
```yaml
# OLD
revenue:
  table: "raw.order_payments"
  
# NEW
revenue:
  table: "stg_order_payments"
  mart_table: "fact_order_items"
  join_required: true
```

---

### 2. **Timestamp Column Transformations**

Your dbt staging models renamed timestamp columns for consistency:

| Old Column | New Column | Table |
|------------|------------|-------|
| `order_purchase_timestamp` | `order_purchase_ts` | stg_orders |
| `order_approved_at` | `order_approved_ts` | stg_orders |
| `order_delivered_customer_date` | `delivered_customer_ts` | stg_orders |
| `order_delivered_carrier_date` | `delivered_carrier_ts` | stg_orders |
| `shipping_limit_date` | `shipping_limit_ts` | stg_order_items |

**Updated glossary** to use the new `*_ts` column names.

---

### 3. **New Enriched Dimensions**

Added dimensions from your mart transformations:

#### **Customer Region** (from dim_customers)
```yaml
customer_region:
  description: "Brazilian geographic region"
  sql_column: "customer_region"
  table: "dim_customers"
  possible_values: ["North", "Northeast", "Central-West", "Southeast", "South"]
  notes: "Enriched from brazilian_states dimension table"
```

#### **Seller Region** (from dim_sellers)
```yaml
seller_region:
  description: "Brazilian geographic region for sellers"
  sql_column: "seller_region"
  table: "dim_sellers"
  notes: "Enriched from brazilian_states dimension table"
```

#### **Calendar Attributes** (from fact_orders)
```yaml
purchase_year:
  sql_column: "purchase_year"
  table: "fact_orders"
  notes: "Enriched from calendar dimension via date join"
  
purchase_month:
  sql_column: "purchase_month"
  table: "fact_orders"
  
purchase_day_name:
  sql_column: "purchase_day_name"
  table: "fact_orders"
  
purchase_is_weekend:
  sql_column: "purchase_is_weekend"
  table: "fact_orders"
  data_type: "boolean"
```

#### **Product Category English** (from dim_products)
```yaml
product_category_english:
  description: "Product category translated to English"
  sql_column: "product_category_name_english"
  table: "dim_products"
  notes: "Enriched from product_category_translation table"
```

---

### 4. **Data Cleaning Notes**

Added notes about staging transformations:

```yaml
order_status:
  notes: "Cleaned in staging: LOWER(TRIM(order_status))"
  possible_values: ["delivered", "shipped", "canceled", ...] # all lowercase
  
payment_type:
  notes: "Cleaned in staging: LOWER(TRIM(payment_type))"
  possible_values: ["credit_card", "boleto", "voucher", "debit_card"] # all lowercase
```

---

### 5. **Updated Relationships**

Replaced raw table relationships with mart schema relationships:

#### **New Relationships**:
```yaml
fact_orders_to_dim_customers:
  from_table: "fact_orders"
  to_table: "dim_customers"
  relationship_type: "many_to_one"
  
fact_orders_to_calendar:
  from_table: "fact_orders"
  from_column: "purchase_date_key"
  to_table: "calendar"
  to_column: "date_key"
  
fact_order_items_to_dim_products:
  from_table: "fact_order_items"
  to_table: "dim_products"
  notes: "Use for product category analysis with English translations"
  
fact_order_items_to_dim_sellers:
  from_table: "fact_order_items"
  to_table: "dim_sellers"
  notes: "Use for seller region and location analysis"
```

---

### 6. **Enhanced SQL Patterns**

Updated common queries to show complete JOIN patterns using mart tables:

#### **Example: Revenue by Region**
```yaml
- query: "Show revenue by region"
  tables: ["fact_orders", "dim_customers", "stg_order_payments"]
  sql_pattern: |
    SELECT c.customer_region, SUM(p.payment_value) as revenue
    FROM fact_orders o
    JOIN dim_customers c ON o.customer_id = c.customer_id
    JOIN stg_order_payments p ON o.order_id = p.order_id
    GROUP BY c.customer_region
    ORDER BY revenue DESC
  notes: "Uses enriched customer_region from dim_customers"
```

#### **Example: Top Product Categories (English)**
```yaml
- query: "Top 10 product categories by revenue"
  tables: ["fact_order_items", "dim_products", "stg_order_payments"]
  sql_pattern: |
    SELECT p.product_category_name_english, SUM(pay.payment_value) as revenue
    FROM fact_order_items i
    JOIN dim_products p ON i.product_id = p.product_id
    JOIN stg_order_payments pay ON i.order_id = pay.order_id
    GROUP BY p.product_category_name_english
    ORDER BY revenue DESC
    LIMIT 10
  notes: "Uses English category names from dim_products"
```

#### **Example: Weekend vs Weekday Sales**
```yaml
- query: "Weekend vs weekday sales comparison"
  tables: ["fact_orders", "stg_order_payments"]
  sql_pattern: |
    SELECT 
      o.purchase_is_weekend,
      COUNT(DISTINCT o.order_id) as order_count,
      SUM(p.payment_value) as revenue
    FROM fact_orders o
    JOIN stg_order_payments p ON o.order_id = p.order_id
    GROUP BY o.purchase_is_weekend
  notes: "Uses calendar-enriched purchase_is_weekend flag"
```

---

## Mart Schema Summary

Your dbt transformations created the following mart structure:

### **Fact Tables**

#### `fact_orders`
- **Grain**: One row per order
- **Columns**: order_id, customer_id, order_status, order_purchase_ts, order_approved_ts, delivered_carrier_ts, delivered_customer_ts, estimated_delivery_date
- **Enrichments**: purchase_date_key, purchase_year, purchase_month, purchase_day_name, purchase_is_weekend (from calendar)

#### `fact_order_items`
- **Grain**: One row per order item
- **Columns**: order_id, order_item_id, product_id, seller_id, price, freight_value, shipping_limit_ts
- **Enrichments**: shipping_limit_date_key (from calendar)

### **Dimension Tables**

#### `dim_customers`
- **Columns**: customer_id, customer_unique_id, zip_prefix, customer_city, customer_state
- **Enrichments**: customer_region (from brazilian_states)

#### `dim_products`
- **Columns**: product_id, product_category_name, name_length, description_length, photos_qty, weight_g, length_cm, width_cm, height_cm
- **Enrichments**: product_category_name_english (from product_category_translation)

#### `dim_sellers`
- **Columns**: seller_id, zip_prefix, seller_city, seller_state
- **Enrichments**: seller_region (from brazilian_states)

### **Dimension Support Tables**

#### `calendar`
- **Columns**: date, date_key, year, month, day, day_name, is_weekend

#### `brazilian_states`
- **Columns**: state_code, region

---

## Staging Transformations Applied

Your staging models (`stg_*`) apply these transformations:

### **stg_orders**
- ✅ Convert all timestamp columns to TIMESTAMP type
- ✅ Clean order_status: `LOWER(TRIM(order_status))`
- ✅ Rename timestamp columns to `*_ts` suffix

### **stg_order_payments**
- ✅ Cast payment_value to DOUBLE
- ✅ Cast payment_sequential and installments to INTEGER
- ✅ Clean payment_type: `LOWER(TRIM(payment_type))`

### **stg_order_items**
- ✅ Cast price and freight_value to proper numeric types
- ✅ Convert shipping_limit_date to shipping_limit_ts (TIMESTAMP)

### **stg_customers**
- ✅ Preserve customer_id, customer_unique_id, zip_prefix, customer_city, customer_state
- ✅ Ready for region enrichment in dim_customers

### **stg_products**
- ✅ Preserve all product attributes
- ✅ Ready for English translation enrichment in dim_products

### **stg_sellers**
- ✅ Preserve seller attributes
- ✅ Ready for region enrichment in dim_sellers

---

## FAISS Index Update

✅ **Rebuilt FAISS index** with updated glossary:
- **Documents**: 48 (up from previous version)
- **Metrics**: 10
- **Dimensions**: 20 (up from 14 - added regions, calendar attributes, enrichments)
- **Business terms**: 9
- **Common queries**: 9 (updated with mart table JOINs)

**Files updated**:
- `glossary/glossary.index` (FAISS vector index)
- `glossary/glossary_metadata.pkl` (metadata for retrieval)

---

## Impact on Intent Parser (Ticket 5)

The updated glossary will **improve intent parsing accuracy** because:

1. **More Context**: RAG now provides mart table names and JOIN patterns
2. **Enriched Dimensions**: Parser knows about regions, calendar attributes, English translations
3. **Cleaner Values**: Parser expects lowercase values for order_status and payment_type
4. **Better Examples**: Common queries show complete SQL with proper table names

### Example RAG Context (Before vs After)

**Before**:
```
Dimension: customer_state
Table: raw.customers
```

**After**:
```
Dimension: customer_state
Table: stg_customers
Mart Table: dim_customers
Notes: Join with brazilian_states dimension for region mapping

Dimension: customer_region
Table: dim_customers
Possible Values: ["North", "Northeast", "Central-West", "Southeast", "South"]
Notes: Enriched from brazilian_states dimension table
```

---

## Next Steps

### 1️⃣ **Run dbt to Materialize Marts**

Your dbt models are defined but not yet materialized. To create the mart tables:

```bash
# Fix profile name mismatch first
# In dbt_project.yml, line 9, change:
profile: 'ask_your_data'
# To:
profile: 'ask_your_data_project'

# Then run dbt
cd dbt/ask_your_data_project
dbt run
```

This will create:
- `fact_orders`
- `fact_order_items`
- `dim_customers`
- `dim_products`
- `dim_sellers`

### 2️⃣ **Test RAG with Updated Glossary**

```bash
# Start RAG API
python -m uvicorn src.api.main:app --reload --port 8000

# Test retrieval
curl "http://localhost:8000/context/show%20revenue%20by%20region"
```

You should now see results mentioning `dim_customers`, `customer_region`, and mart tables.

### 3️⃣ **Test Intent Parser**

The intent parser will automatically benefit from the updated glossary:

```bash
python tests/test_intent_parser.py
```

Expected improvements:
- Better understanding of "region" queries
- Correct table references (mart tables instead of raw)
- Recognition of enriched dimensions (weekend, English categories, etc.)

### 4️⃣ **Ready for Ticket 6 (SQL Generation)**

The SQL generator can now use:
- Mart table names from glossary
- JOIN patterns from common_queries
- Enriched dimensions for more powerful queries

---

## Summary of Files Updated

| File | Status | Changes |
|------|--------|---------|
| `glossary/business_terms.yaml` | ✅ Updated | Version 2.0 with mart schema |
| `glossary/glossary.index` | ✅ Rebuilt | FAISS index with 48 documents |
| `glossary/glossary_metadata.pkl` | ✅ Rebuilt | Updated metadata |

---

**Completed by**: GitHub Copilot  
**Date**: November 28, 2025  
**Next Action**: Run `dbt run` to materialize mart tables, then proceed to Ticket 6 (SQL Generation)
