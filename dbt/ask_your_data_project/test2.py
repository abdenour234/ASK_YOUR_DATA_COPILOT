import duckdb

con = duckdb.connect(r"C:\Users\hp\OneDrive\Documents\Ai0\ASK_YOUR_DATA_COPILOT\ask_your_data.db")

# lister toutes les tables / vues staging
tables = con.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='main'
      AND table_name LIKE 'stg_%'
""").fetchdf()
print("Tables / Vues staging :")
print(tables)

# voir les colonnes et types
columns = con.execute("""
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_name LIKE 'stg_%'
    ORDER BY table_name, ordinal_position
""").fetchdf()
print("\nColonnes et types :")
print(columns)
