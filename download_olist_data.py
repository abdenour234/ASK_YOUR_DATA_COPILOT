"""
Sprint 1 - Ticket 2: Data Ingestion - Download Helper
Downloads the Olist Brazilian E-commerce dataset from Kaggle.

IMPORTANT: Before running this script:
1. Create a Kaggle account at https://www.kaggle.com
2. Go to Account Settings > API > Create New API Token
3. Download kaggle.json and place it in C:\\Users\\<username>\\.kaggle\\kaggle.json
4. Or set KAGGLE_USERNAME and KAGGLE_KEY environment variables

Dataset: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
"""

import os
import sys
import zipfile
from pathlib import Path


def check_kaggle_credentials():
    """Verify Kaggle credentials are configured."""
    kaggle_dir = Path.home() / ".kaggle"
    kaggle_json = kaggle_dir / "kaggle.json"
    
    has_env = os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY")
    has_file = kaggle_json.exists()
    
    if not (has_env or has_file):
        print("❌ Kaggle credentials not found!")
        print("\nPlease configure Kaggle API credentials:")
        print("1. Go to https://www.kaggle.com/account")
        print("2. Click 'Create New API Token'")
        print(f"3. Place kaggle.json in: {kaggle_dir}")
        print("\nOr set environment variables:")
        print("   $env:KAGGLE_USERNAME='your_username'")
        print("   $env:KAGGLE_KEY='your_api_key'")
        return False
    
    if has_file and not has_env:
        # Ensure proper permissions (Unix-like)
        try:
            os.chmod(kaggle_json, 0o600)
        except:
            pass
    
    return True


def download_olist_dataset():
    """Download Olist dataset from Kaggle."""
    
    if not check_kaggle_credentials():
        return False
    
    # Import kaggle after credentials check
    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError:
        print("❌ Kaggle package not installed. Run: pip install kaggle")
        return False
    
    # Dataset details
    dataset = "olistbr/brazilian-ecommerce"
    download_path = Path("data/raw")
    download_path.mkdir(parents=True, exist_ok=True)
    
    print(f"📦 Downloading Olist dataset: {dataset}")
    print(f"📁 Destination: {download_path.absolute()}")
    
    try:
        # Authenticate and download
        api = KaggleApi()
        api.authenticate()
        
        print("\n⏳ Downloading files from Kaggle...")
        api.dataset_download_files(
            dataset,
            path=str(download_path),
            unzip=True,
            quiet=False
        )
        
        print("\n✅ Download complete!")
        
        # List downloaded files
        csv_files = list(download_path.glob("*.csv"))
        print(f"\n📊 Found {len(csv_files)} CSV files:")
        for csv_file in sorted(csv_files):
            size_mb = csv_file.stat().st_size / (1024 * 1024)
            print(f"   • {csv_file.name} ({size_mb:.2f} MB)")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error downloading dataset: {e}")
        print("\nTroubleshooting:")
        print("• Verify Kaggle credentials are correct")
        print("• Check internet connection")
        print("• Ensure you've accepted the dataset terms at:")
        print(f"  https://www.kaggle.com/datasets/{dataset}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Olist Dataset Download Helper")
    print("Sprint 1 - Ticket 2: Data Ingestion")
    print("=" * 60)
    print()
    
    success = download_olist_dataset()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ Ready for data ingestion!")
        print("Next step: Run 'python src/ingest/data.py'")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ Download failed. Please fix errors and try again.")
        print("=" * 60)
        sys.exit(1)
