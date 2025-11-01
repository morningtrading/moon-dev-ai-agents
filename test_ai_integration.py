#!/usr/bin/env python3
"""
🌙 Moon Dev's AI Integration Test
Quick test to verify all AI providers are working
"""

from src.models.model_factory import ModelFactory
from termcolor import cprint

# Initialize factory once
factory = ModelFactory()

def test_ai_provider(provider_name):
    """Test a specific AI provider"""
    try:
        cprint(f"\n{'='*50}", "cyan")
        cprint(f"Testing {provider_name.upper()} provider...", "cyan")
        cprint(f"{'='*50}", "cyan")

        # Get model instance from factory
        model = factory.get_model(provider_name)

        # Simple test prompt
        system_prompt = "You are a helpful AI assistant. Be concise."
        user_content = "What is 2+2? Answer in one word."

        # Generate response
        cprint(f"  ├─ Sending test request...", "yellow")
        response = model.generate_response(
            system_prompt=system_prompt,
            user_content=user_content,
            temperature=0.1,
            max_tokens=10
        )

        cprint(f"  ├─ ✅ Response received!", "green")
        cprint(f"  └─ Answer: {response}", "white")
        return True

    except Exception as e:
        cprint(f"  └─ ❌ Error: {str(e)}", "red")
        return False

def main():
    cprint("\n🌙 Moon Dev's AI Integration Test", "cyan", attrs=["bold"])
    cprint("Testing all configured AI providers...\n", "cyan")

    # Test each provider
    providers = ["claude", "deepseek", "gemini", "xai"]

    results = {}
    for provider in providers:
        results[provider] = test_ai_provider(provider)

    # Summary
    cprint(f"\n{'='*50}", "cyan")
    cprint("📊 Test Results Summary", "cyan", attrs=["bold"])
    cprint(f"{'='*50}", "cyan")

    for provider, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        color = "green" if success else "red"
        cprint(f"  {provider:12} {status}", color)

    total = len(results)
    passed = sum(results.values())

    cprint(f"\n{'='*50}", "cyan")
    cprint(f"Total: {passed}/{total} providers working", "white", attrs=["bold"])

    if passed == total:
        cprint("\n🎉 ALL TESTS PASSED! Your AI integration is perfect!", "green", attrs=["bold"])
    else:
        cprint(f"\n⚠️ {total - passed} provider(s) failed. Check errors above.", "yellow")

if __name__ == "__main__":
    main()
