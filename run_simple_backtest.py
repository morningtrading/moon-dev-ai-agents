#!/usr/bin/env python3
"""
🌙 Moon Dev's Simple Backtest Runner
Quick test of RBI agent with corrected paths for Linux
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models.model_factory import ModelFactory
from termcolor import cprint
import pandas as pd

def run_simple_backtest():
    """Run a simple RSI backtest on BTC data"""

    cprint("\n🌙 Moon Dev's Simple Backtest Runner", "cyan", attrs=["bold"])
    cprint("=" * 60, "cyan")

    # 1. Load the data
    data_file = project_root / "src/data/rbi/BTC-USD-15m.csv"

    cprint(f"\n📊 Loading data from: {data_file}", "cyan")

    if not data_file.exists():
        cprint(f"❌ Data file not found: {data_file}", "red")
        return

    df = pd.read_csv(data_file)
    cprint(f"✅ Loaded {len(df)} rows of BTC data", "green")
    cprint(f"  ├─ Date range: {df.iloc[0]['datetime']} to {df.iloc[-1]['datetime']}", "white")
    cprint(f"  └─ Columns: {', '.join(df.columns)}", "white")

    # 2. Read the strategy idea
    ideas_file = project_root / "src/data/rbi_pp_multi/ideas.txt"

    with open(ideas_file, 'r') as f:
        strategy_idea = f.read().strip()

    cprint(f"\n💡 Strategy Idea:", "yellow")
    cprint(f"  {strategy_idea}", "white")

    # 3. Initialize AI model
    cprint(f"\n🤖 Initializing AI model...", "cyan")
    factory = ModelFactory()
    model = factory.get_model("deepseek")  # Use cheap DeepSeek for testing

    if not model:
        cprint("❌ Could not initialize AI model", "red")
        return

    cprint(f"✅ AI model ready: DeepSeek", "green")

    # 4. Generate backtest code
    cprint(f"\n🔨 Generating backtest code with AI...", "cyan")

    system_prompt = """You are an expert Python backtesting developer.
Generate clean, working backtesting.py code based on the strategy idea provided.

IMPORTANT REQUIREMENTS:
1. Use the backtesting.py library
2. Use pandas_ta for indicators (NOT backtesting.lib)
3. Import: from backtesting import Strategy, Backtest
4. Import: import pandas_ta as ta
5. The data will have columns: datetime, open, high, low, close, volume
6. Keep the code simple and clean
7. Only return the Python code, no explanations"""

    user_content = f"""Create a backtest for this strategy:

{strategy_idea}

Data format:
- Columns: datetime, open, high, low, close, volume
- 15-minute BTC data from 2023

Generate the complete Python code for the strategy."""

    cprint(f"  ├─ Sending request to AI...", "yellow")

    response = model.generate_response(
        system_prompt=system_prompt,
        user_content=user_content,
        temperature=0.3,
        max_tokens=2000
    )

    # Extract code from response
    code = str(response)
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]

    code = code.strip()

    cprint(f"  └─ ✅ Code generated ({len(code)} chars)", "green")

    # 5. Save the generated code
    output_file = project_root / "test_strategy.py"
    with open(output_file, 'w') as f:
        f.write(code)

    cprint(f"\n💾 Saved strategy code to: {output_file}", "green")

    # 6. Show the code
    cprint(f"\n📝 Generated Code:", "cyan")
    cprint("=" * 60, "cyan")
    print(code)
    cprint("=" * 60, "cyan")

    cprint(f"\n✅ Backtest code generation complete!", "green")
    cprint(f"\n📌 Next steps:", "yellow")
    cprint(f"  1. Review the code above", "white")
    cprint(f"  2. Run it manually: python test_strategy.py", "white")
    cprint(f"  3. Or use the full RBI agent for automated testing", "white")

if __name__ == "__main__":
    try:
        run_simple_backtest()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Interrupted by user", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
