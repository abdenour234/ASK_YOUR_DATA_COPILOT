"""
Setup script for configuring .env file with OpenRouter API key.
Run this before using the intent parser.
"""

import os
import shutil


def setup_env_file():
    """Guide user through .env file setup."""
    print("=" * 70)
    print("  Ask Your Data Copilot - Environment Setup")
    print("=" * 70)
    print()
    
    # Check if .env already exists
    if os.path.exists('.env'):
        print("⚠️  .env file already exists")
        response = input("Do you want to overwrite it? (y/n): ").strip().lower()
        if response != 'y':
            print("Setup cancelled. Your existing .env file was not modified.")
            return
    
    # Check if .env.example exists
    if not os.path.exists('.env.example'):
        print("❌ ERROR: .env.example not found")
        print("Please ensure you're running this from the project root directory.")
        return
    
    print("\n📋 Setting up .env file...")
    print()
    print("You'll need:")
    print("1. OpenRouter API Key (required)")
    print("   Get it from: https://openrouter.ai/keys")
    print()
    
    # Get API key
    api_key = input("Enter your OpenRouter API key: ").strip()
    
    if not api_key:
        print("❌ ERROR: API key cannot be empty")
        return
    
    # Get optional site info
    site_url = input("Enter your site URL (press Enter for default 'http://localhost:8501'): ").strip()
    if not site_url:
        site_url = "http://localhost:8501"
    
    site_name = input("Enter your site name (press Enter for default 'Ask Your Data Copilot'): ").strip()
    if not site_name:
        site_name = "Ask Your Data Copilot"
    
    # Get model preference
    print("\nAvailable models:")
    print("1. openai/gpt-4o (recommended - fastest, most accurate)")
    print("2. openai/gpt-4-turbo (good balance)")
    print("3. meta-llama/llama-3.1-70b-instruct (open source)")
    print("4. anthropic/claude-3-opus (alternative)")
    
    model_choice = input("\nSelect model (1-4, press Enter for default #1): ").strip()
    
    models = {
        "1": "openai/gpt-4o",
        "2": "openai/gpt-4-turbo",
        "3": "meta-llama/llama-3.1-70b-instruct",
        "4": "anthropic/claude-3-opus"
    }
    
    model = models.get(model_choice, "openai/gpt-4o")
    
    # Create .env file
    env_content = f"""# OpenRouter API Configuration
# Get your API key from: https://openrouter.ai/keys
OPENROUTER_API_KEY={api_key}

# Optional: Your site information for OpenRouter rankings
OPENROUTER_SITE_URL={site_url}
OPENROUTER_SITE_NAME={site_name}

# OpenRouter Model Selection
# Options: openai/gpt-4o, openai/gpt-4-turbo, anthropic/claude-3-opus, meta-llama/llama-3.1-70b-instruct
OPENROUTER_MODEL={model}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("\n✅ .env file created successfully!")
    print(f"\nConfiguration:")
    print(f"  Model: {model}")
    print(f"  Site URL: {site_url}")
    print(f"  Site Name: {site_name}")
    print()
    print("⚠️  IMPORTANT: Never commit .env file to git!")
    print("   (.env is already in .gitignore)")
    print()
    print("You can now run: python tests/test_intent_parser.py")


if __name__ == "__main__":
    setup_env_file()
