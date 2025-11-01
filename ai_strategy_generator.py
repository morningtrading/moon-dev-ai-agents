#!/usr/bin/env python3
import sys
sys.path.append('/home/titus/moon-dev-ai-agents')
from src.models.model_factory import ModelFactory
from termcolor import cprint

def generate_strategy_ideas():
    cprint("\n🌙 AI Strategy Generator", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")
    cprint(f"\n🤖 Analyzing results and generating new strategies...\n", "yellow")

    context = """You are an expert quantitative trading strategist. I've backtested RSI mean-reversion on 79 cryptocurrency pairs.

FINDINGS:
- Best: RSI(14) 20/80 = +6% to +29% over 3 months
- Market: Bear market (-22% average)
- Success: 19% of pairs, 39% in sideways markets
- Limitations: Modest returns

REQUIREMENTS:
- Min 1 trade/week
- Must work on BOTH time periods (walk-forward)
- Bear/sideways markets
- Commission: 0.2%

TASK: Propose 5 DIFFERENT strategy types for 30-100%+ returns over 3 months.

For each:
1. Name
2. Logic
3. Why better than RSI
4. Trade frequency
5. Risk level"""

    try:
        factory = ModelFactory()
        try:
            model = factory.get_model('deepseek')
            cprint(f"  Using: DeepSeek R1\n", "white")
        except:
            model = factory.get_model('claude')
            cprint(f"  Using: Claude\n", "white")

        response = model.generate_response(
            system_prompt="You are an expert quant strategist.",
            user_content=context,
            temperature=0.7,
            max_tokens=4000
        )

        cprint(f"{'='*90}", "cyan")
        cprint(f"🤖 AI STRATEGY PROPOSALS", "cyan", attrs=["bold"])
        cprint(f"{'='*90}\n", "cyan")
        cprint(response, "white")

        cprint(f"\n{'='*90}", "cyan")
        cprint(f"📋 NEXT STEPS", "yellow", attrs=["bold"])
        cprint(f"{'='*90}\n", "cyan")
        cprint(f"I can now:", "white")
        cprint(f"  A. Generate code for top strategies", "white")
        cprint(f"  B. Auto-backtest with walk-forward", "white")
        cprint(f"  C. Get different suggestions", "white")
        cprint(f"  D. Optimize RSI for higher returns\n", "white")

        return response
    except Exception as e:
        cprint(f"\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    generate_strategy_ideas()
