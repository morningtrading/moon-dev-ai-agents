#!/usr/bin/env python3
"""
Test script to verify all AI service API keys are correctly configured
"""
import os
from dotenv import load_dotenv
import requests
import json

load_dotenv()

def test_anthropic():
    """Test Anthropic (Claude) API"""
    api_key = os.getenv("ANTHROPIC_KEY")
    if not api_key or api_key == "your_anthropic_key_here":
        return False, "API key not configured"
    
    try:
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": "claude-3-haiku-20240307",
            "max_tokens": 10,
            "messages": [{"role": "user", "content": "Say hi"}]
        }
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            return True, f"Working - {response.json()['content'][0]['text'][:50]}"
        else:
            return False, f"Error {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, str(e)

def test_deepseek():
    """Test DeepSeek API"""
    api_key = os.getenv("DEEPSEEK_KEY")
    if not api_key or api_key == "your_deepseek_key_here":
        return False, "API key not configured"
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "Say hi"}],
            "max_tokens": 10
        }
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            return True, f"Working - {response.json()['choices'][0]['message']['content'][:50]}"
        else:
            return False, f"Error {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, str(e)

def test_gemini():
    """Test Google Gemini API"""
    api_key = os.getenv("GEMINI_KEY")
    if not api_key or api_key == "your_gemini_key_here":
        return False, "API key not configured"
    
    try:
        # Use latest available model
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key={api_key}"
        data = {
            "contents": [{"parts": [{"text": "Say hi"}]}],
            "generationConfig": {"maxOutputTokens": 50}
        }
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            # Handle both text and thoughts format
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate:
                    content = candidate['content']
                    if 'parts' in content and len(content['parts']) > 0:
                        # Try text first, then thoughts
                        part = content['parts'][0]
                        text = part.get('text', part.get('thought', 'No text found'))
                        return True, f"Working - {text[:50]}"
            return False, f"Unexpected response format: {str(result)[:100]}"
        else:
            return False, f"Error {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, str(e)

def test_grok():
    """Test Grok (xAI) API"""
    api_key = os.getenv("GROK_API_KEY")
    if not api_key or api_key == "your_grok_api_key_here":
        return False, "API key not configured"
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "grok-2-latest",
            "messages": [{"role": "user", "content": "Say hi"}],
            "max_tokens": 10
        }
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            return True, f"Working - {response.json()['choices'][0]['message']['content'][:50]}"
        else:
            return False, f"Error {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, str(e)

def test_openrouter():
    """Test OpenRouter API"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key or api_key == "your_openrouter_key_here":
        return False, "API key not configured"
    
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/moon-dev-ai"
        }
        data = {
            "model": "meta-llama/llama-3.3-70b-instruct:free",
            "messages": [{"role": "user", "content": "Say hi"}],
            "max_tokens": 10
        }
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        if response.status_code == 200:
            return True, f"Working - {response.json()['choices'][0]['message']['content'][:50]}"
        else:
            return False, f"Error {response.status_code}: {response.text[:100]}"
    except Exception as e:
        return False, str(e)

def main():
    print("🌙 Testing Moon Dev AI Services Configuration 🌙\n")
    print("=" * 60)
    
    tests = [
        ("Anthropic (Claude)", test_anthropic),
        ("DeepSeek", test_deepseek),
        ("Google Gemini", test_gemini),
        ("Grok (xAI)", test_grok),
        ("OpenRouter", test_openrouter),
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🔍 Testing {name}...")
        success, message = test_func()
        results.append((name, success, message))
        
        if success:
            print(f"   ✅ {name}: {message}")
        else:
            print(f"   ❌ {name}: {message}")
    
    print("\n" + "=" * 60)
    print("\n📊 Summary:")
    working = sum(1 for _, success, _ in results if success)
    total = len(results)
    print(f"   Working: {working}/{total}")
    
    print("\n✅ Working services:")
    for name, success, _ in results:
        if success:
            print(f"   • {name}")
    
    failed = [name for name, success, _ in results if not success]
    if failed:
        print("\n❌ Not working:")
        for name in failed:
            print(f"   • {name}")

if __name__ == "__main__":
    main()
