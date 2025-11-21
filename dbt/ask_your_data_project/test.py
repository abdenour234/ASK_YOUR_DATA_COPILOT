import duckdb

con = duckdb.connect(r"C:\Users\hp\OneDrive\Documents\Ai0\ASK_YOUR_DATA_COPILOT\ask_your_data.db")

# 1. Vérifier les tables existantes
print("=== TABLES DISPONIBLES ===")
print(con.execute("SHOW TABLES").fetchdf())

# 2. Vérifier la structure de la table stg_customers
print("\n=== STRUCTURE DE STG_CUSTOMERS ===")
print(con.execute("DESCRIBE stg_customers").fetchdf())

# 3. Vérifier les types avec plus de détails
print("\n=== TYPES DE DONNÉES DÉTAILLÉS ===")
print(con.execute("""
    SELECT 
        column_name,
        data_type,
        numeric_precision,
        numeric_scale,
        is_nullable
    FROM information_schema.columns 
    WHERE table_name = 'stg_customers'
""").fetchdf())

# 4. Afficher quelques données avec les types
print("\n=== PREMIÈRES LIGNES ===")
df = con.execute("SELECT * FROM stg_customers LIMIT 5").fetchdf()
print(df)
print(f"\nTypes Python des colonnes :")
print(df.dtypes)

# 5. Statistiques sur les colonnes pour vérifier la conversion
print("\n=== VÉRIFICATION CONVERSION ZIP ===")
zip_stats = con.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(zip_prefix) as non_nulls,
        SUM(CASE WHEN zip_prefix IS NULL THEN 1 ELSE 0 END) as nulls,
        MIN(zip_prefix) as min_zip,
        MAX(zip_prefix) as max_zip
    FROM stg_customers
""").fetchdf()
print(zip_stats)