#!/usr/bin/env python3
"""Test OpenRouter API key validity"""
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

print(f"🔍 Testing OpenRouter API Key")
print(f"  ├─ Key length: {len(api_key) if api_key else 0} chars")
if api_key:
    print(f"  ├─ Key prefix: {api_key[:15]}...")
    print(f"  └─ Key suffix: ...{api_key[-15:]}")
else:
    print(f"  └─ ❌ No API key found in .env!")
    exit(1)

try:
    print(f"\n📡 Creating OpenRouter client...")
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={
            "HTTP-Referer": "https://github.com/moon-dev-ai/trading",
            "X-Title": "Moon Dev AI Trading Test"
        }
    )

    print(f"📡 Testing API call with Meta Llama 3.2 (free)...")
    response = client.chat.completions.create(
        model="meta-llama/llama-3.2-3b-instruct:free",  # Different free model
        messages=[{"role": "user", "content": "Say OK"}],
        max_tokens=5
    )

    print(f"\n✅ SUCCESS! Your OpenRouter API key is VALID!")
    print(f"  └─ Response: {response.choices[0].message.content}")
    print(f"\n🎉 OpenRouter is working correctly!")

except Exception as e:
    error_msg = str(e)

    # Check if it's a rate limit error (which means key is valid!)
    if "429" in error_msg or "rate" in error_msg.lower():
        print(f"\n✅ GOOD NEWS! Your OpenRouter API key is VALID!")
        print(f"  ├─ The free model is temporarily rate-limited")
        print(f"  └─ This is normal - free models have usage limits")
        print(f"\n🎉 Your API key works! The system will use it successfully.")
    else:
        # Actual authentication error
        print(f"\n❌ FAILED! Your OpenRouter API key is INVALID or EXPIRED")
        print(f"  ├─ Error type: {type(e).__name__}")
        print(f"  └─ Error: {error_msg}")

        print(f"\n🔧 How to fix:")
        print(f"  1. Go to https://openrouter.ai/keys")
        print(f"  2. Sign in (or create free account)")
        print(f"  3. Click 'Create Key' button")
        print(f"  4. Copy the new key (starts with 'sk-or-v1-')")
        print(f"  5. Edit .env file and replace the OPENROUTER_API_KEY value")
        print(f"  6. Run this test again: python test_openrouter_key.py")
