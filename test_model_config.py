"""
Test model configuration and show which model is being used
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("OpenRouter Model Configuration Check")
print("=" * 80)

# Check API key
api_key = os.getenv("OPENROUTER_API_KEY")
if api_key:
    print(f"\n✓ API Key found: {api_key[:10]}...{api_key[-4:]}")
else:
    print("\n✗ API Key NOT found in environment")
    print("  Set OPENROUTER_API_KEY in your .env file")

# Check model setting
model = os.getenv("OPENROUTER_MODEL")
if model:
    print(f"✓ Model configured: {model}")
else:
    print("✗ Model NOT configured in .env")
    print("  Using default: openai/gpt-3.5-turbo")
    model = "openai/gpt-3.5-turbo"

# Check site settings
site_url = os.getenv("OPENROUTER_SITE_URL", "http://localhost:8501")
site_name = os.getenv("OPENROUTER_SITE_NAME", "Ask Your Data")
print(f"✓ Site URL: {site_url}")
print(f"✓ Site Name: {site_name}")

print("\n" + "=" * 80)
print("Recommended FREE Models for OpenRouter")
print("=" * 80)
print("\nAdd one of these to your .env file as OPENROUTER_MODEL:\n")

free_models = [
    ("google/gemini-2.0-flash-exp:free", "Google Gemini 2.0 Flash - FAST & FREE"),
    ("google/gemini-flash-1.5", "Google Gemini 1.5 Flash - Good balance"),
    ("meta-llama/llama-3.2-3b-instruct:free", "Llama 3.2 3B - Lightweight"),
    ("mistralai/mistral-7b-instruct:free", "Mistral 7B - Good quality"),
    ("nousresearch/hermes-3-llama-3.1-405b:free", "Hermes 3 405B - POWERFUL & FREE"),
]

for model_id, description in free_models:
    print(f"  • {model_id}")
    print(f"    {description}\n")

print("=" * 80)
print("How to fix the 402 Payment Required error:")
print("=" * 80)
print("\n1. Make sure you have credits in your OpenRouter account")
print("   Visit: https://openrouter.ai/credits")
print("\n2. Use a FREE model by setting in .env file:")
print("   OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free")
print("\n3. Or get free credits:")
print("   - Sign up gets you $1 free credit")
print("   - Link GitHub account for more credits")
print("   - Some models are completely free (marked with :free)")

print("\n" + "=" * 80)

# Test a simple API call
if api_key:
    print("\nTesting API call with current configuration...")
    print(f"Using model: {model}")
    
    import requests
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": site_url,
        "X-Title": site_name
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "Say 'test ok' and nothing else"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ SUCCESS! Model responded: {result['choices'][0]['message']['content']}")
            print(f"  Model used: {result.get('model', 'unknown')}")
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
            
            if response.status_code == 402:
                print("\n  → This is a 402 Payment Required error")
                print("  → Solution: Use a FREE model (see list above)")
                print("  → Add to .env: OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free")
                
    except Exception as e:
        print(f"✗ Error: {e}")

print("\n" + "=" * 80)
