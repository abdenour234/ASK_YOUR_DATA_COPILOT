"""
Sprint 1 - Ticket 2: Data Ingestion
Loads Olist Brazilian E-commerce dataset from CSV files into DuckDB.
Creates raw tables, calendar dimension, and country mapping.

Dependency: Ticket 1 (environment setup)
"""

import duckdb
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List


class OlistDataIngester:
    """Handles ingestion of Olist dataset into DuckDB."""
    
    def __init__(self, db_path: str = "ask_your_data.db", data_dir: str = "data/raw"):
        """
        Initialize the data ingester.
        
        Args:
            db_path: Path to DuckDB database file
            data_dir: Directory containing CSV files
        """
        self.db_path = db_path
        self.data_dir = Path(data_dir)
        self.conn = None
        
        # CSV file mapping (filename -> table name)
        self.csv_mappings = {
            "olist_customers_dataset.csv": "customers",
            "olist_geolocation_dataset.csv": "geolocation",
            "olist_orders_dataset.csv": "orders",
            "olist_order_items_dataset.csv": "order_items",
            "olist_order_payments_dataset.csv": "order_payments",
            "olist_order_reviews_dataset.csv": "order_reviews",
            "olist_products_dataset.csv": "products",
            "olist_sellers_dataset.csv": "sellers",
            "product_category_name_translation.csv": "product_category_translation",
        }
    
    def connect(self) -> None:
        """Establish connection to DuckDB."""
        self.conn = duckdb.connect(self.db_path)
        print(f"✓ Connected to DuckDB: {self.db_path}")
    
    def close(self) -> None:
        """Close DuckDB connection."""
        if self.conn:
            self.conn.close()
            print("✓ Connection closed")
    
    def create_schema(self) -> None:
        """Create schema for organizing tables."""
        self.conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        self.conn.execute("CREATE SCHEMA IF NOT EXISTS dimensions")
        print("✓ Created schemas: raw, dimensions")
    
    def load_csv_files(self) -> Dict[str, int]:
        """
        Load all Olist CSV files into DuckDB using read_csv_auto.
        
        Returns:
            Dictionary mapping table names to row counts
        """
        row_counts = {}
        
        for csv_file, table_name in self.csv_mappings.items():
            csv_path = self.data_dir / csv_file
            
            if not csv_path.exists():
                print(f"⚠ Warning: {csv_file} not found, skipping...")
                continue
            
            # Use DuckDB's read_csv_auto for fast, automatic type detection
            table_full_name = f"raw.{table_name}"
            
            try:
                # Drop table if exists (for re-runs)
                self.conn.execute(f"DROP TABLE IF EXISTS {table_full_name}")
                
                # Create table from CSV with automatic type inference
                self.conn.execute(f"""
                    CREATE TABLE {table_full_name} AS 
                    SELECT * FROM read_csv_auto('{csv_path}', 
                        header=true, 
                        nullstr='',
                        dateformat='%Y-%m-%d %H:%M:%S'
                    )
                """)
                
                # Get row count
                result = self.conn.execute(f"SELECT COUNT(*) FROM {table_full_name}").fetchone()
                count = result[0]
                row_counts[table_name] = count
                
                print(f"✓ Loaded {table_name:35} {count:>10,} rows")
                
            except Exception as e:
                print(f"✗ Error loading {csv_file}: {e}")
                raise
        
        return row_counts
    
    def create_calendar_dimension(self, start_year: int = 2016, end_year: int = 2025) -> int:
        """
        Generate a calendar dimension table with date attributes.
        
        Args:
            start_year: Starting year for calendar
            end_year: Ending year for calendar
        
        Returns:
            Number of rows created
        """
        # Generate date range
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Create calendar dataframe with date attributes
        calendar_df = pd.DataFrame({
            'date_key': date_range.strftime('%Y%m%d').astype(int),
            'date': date_range,
            'year': date_range.year,
            'quarter': date_range.quarter,
            'month': date_range.month,
            'month_name': date_range.strftime('%B'),
            'week': date_range.isocalendar().week,
            'day': date_range.day,
            'day_of_week': date_range.dayofweek + 1,  # 1=Monday, 7=Sunday
            'day_name': date_range.strftime('%A'),
            'is_weekend': (date_range.dayofweek >= 5).astype(int),
            'is_month_start': date_range.is_month_start.astype(int),
            'is_month_end': date_range.is_month_end.astype(int),
            'is_quarter_start': date_range.is_quarter_start.astype(int),
            'is_quarter_end': date_range.is_quarter_end.astype(int),
            'is_year_start': date_range.is_year_start.astype(int),
            'is_year_end': date_range.is_year_end.astype(int),
        })
        
        # Drop table if exists
        self.conn.execute("DROP TABLE IF EXISTS dimensions.calendar")
        
        # Register DataFrame as DuckDB table
        self.conn.register('calendar_temp', calendar_df)
        self.conn.execute("""
            CREATE TABLE dimensions.calendar AS 
            SELECT * FROM calendar_temp
        """)
        self.conn.unregister('calendar_temp')
        
        row_count = len(calendar_df)
        print(f"✓ Created calendar dimension:           {row_count:>10,} rows ({start_year}-{end_year})")
        
        return row_count
    
    def create_country_dimension(self) -> int:
        """
        Create a country/state mapping table for Brazilian states.
        
        Returns:
            Number of rows created
        """
        # Brazilian states with full names
        states_data = {
            'state_code': ['AC', 'AL', 'AP', 'AM', 'BA', 'CE', 'DF', 'ES', 'GO', 
                          'MA', 'MT', 'MS', 'MG', 'PA', 'PB', 'PR', 'PE', 'PI', 
                          'RJ', 'RN', 'RS', 'RO', 'RR', 'SC', 'SP', 'SE', 'TO'],
            'state_name': [
                'Acre', 'Alagoas', 'Amapá', 'Amazonas', 'Bahia', 'Ceará', 
                'Distrito Federal', 'Espírito Santo', 'Goiás', 'Maranhão', 
                'Mato Grosso', 'Mato Grosso do Sul', 'Minas Gerais', 'Pará', 
                'Paraíba', 'Paraná', 'Pernambuco', 'Piauí', 'Rio de Janeiro', 
                'Rio Grande do Norte', 'Rio Grande do Sul', 'Rondônia', 'Roraima', 
                'Santa Catarina', 'São Paulo', 'Sergipe', 'Tocantins'
            ],
            'region': [
                'North', 'Northeast', 'North', 'North', 'Northeast', 'Northeast',
                'Central-West', 'Southeast', 'Central-West', 'Northeast', 
                'Central-West', 'Central-West', 'Southeast', 'North', 'Northeast',
                'South', 'Northeast', 'Northeast', 'Southeast', 'Northeast', 
                'South', 'North', 'North', 'South', 'Southeast', 'Northeast', 'North'
            ],
            'country': ['Brazil'] * 27
        }
        
        states_df = pd.DataFrame(states_data)
        
        # Drop table if exists
        self.conn.execute("DROP TABLE IF EXISTS dimensions.brazilian_states")
        
        # Register and create table
        self.conn.register('states_temp', states_df)
        self.conn.execute("""
            CREATE TABLE dimensions.brazilian_states AS 
            SELECT * FROM states_temp
        """)
        self.conn.unregister('states_temp')
        
        row_count = len(states_df)
        print(f"✓ Created Brazilian states dimension:   {row_count:>10,} rows")
        
        return row_count
    
    def create_indexes(self) -> None:
        """Create indexes on key columns for query performance."""
        # Note: DuckDB doesn't support traditional indexes like PostgreSQL,
        # but we can document key columns here for dbt transformations
        print("✓ Index creation skipped (DuckDB uses automatic indexing)")
    
    def get_table_summary(self) -> pd.DataFrame:
        """
        Get summary of all tables in the database.
        
        Returns:
            DataFrame with table statistics
        """
        result = self.conn.execute("""
            SELECT 
                table_schema,
                table_name,
                (SELECT COUNT(*) FROM information_schema.columns c 
                 WHERE c.table_schema = t.table_schema 
                 AND c.table_name = t.table_name) as column_count
            FROM information_schema.tables t
            WHERE table_schema IN ('raw', 'dimensions')
            ORDER BY table_schema, table_name
        """).fetchdf()
        
        # Add row counts
        row_counts = []
        for _, row in result.iterrows():
            count = self.conn.execute(
                f"SELECT COUNT(*) FROM {row['table_schema']}.{row['table_name']}"
            ).fetchone()[0]
            row_counts.append(count)
        
        result['row_count'] = row_counts
        return result
    
    def run_full_ingestion(self) -> None:
        """Execute complete data ingestion pipeline."""
        print("=" * 70)
        print("Starting Olist Dataset Ingestion (Sprint 1 - Ticket 2)")
        print("=" * 70)
        
        try:
            # Connect to database
            self.connect()
            
            # Create schemas
            self.create_schema()
            
            print("\n📦 Loading CSV files into raw schema...")
            print("-" * 70)
            csv_counts = self.load_csv_files()
            
            print("\n🗓️  Creating dimension tables...")
            print("-" * 70)
            calendar_count = self.create_calendar_dimension()
            states_count = self.create_country_dimension()
            
            print("\n📊 Database Summary:")
            print("=" * 70)
            summary = self.get_table_summary()
            print(summary.to_string(index=False))
            
            print("\n" + "=" * 70)
            print("✅ Data ingestion completed successfully!")
            print("=" * 70)
            print(f"📁 Database location: {Path(self.db_path).absolute()}")
            print(f"📈 Total tables created: {len(summary)}")
            print(f"📊 Total rows ingested: {summary['row_count'].sum():,}")
            print("=" * 70)
            
        except Exception as e:
            print(f"\n❌ Error during ingestion: {e}")
            raise
        
        finally:
            self.close()


def main():
    """Main entry point for data ingestion."""
    ingester = OlistDataIngester(
        db_path="ask_your_data.db",
        data_dir="data/raw"
    )
    ingester.run_full_ingestion()


if __name__ == "__main__":
    main()
