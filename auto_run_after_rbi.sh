#!/bin/bash
# 🌙 Moon Dev's Automated Strategy Testing Pipeline
# Waits for RBI to finish, then tests all strategies on all coins

echo "=========================================="
echo "🌙 Automated Strategy Testing Pipeline"
echo "=========================================="
echo ""

# Wait for RBI to finish
echo "⏳ Waiting for RBI agent to complete..."
while ps aux | grep -q "[r]bi_agent_pp_multi"; do
    sleep 60
    STRATEGIES=$(ls -1 /home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_04_2025/backtests_working/*.py 2>/dev/null | wc -l)
    echo "   [$(date +%H:%M)] RBI still running... ($STRATEGIES strategies so far)"
done

echo ""
echo "✅ RBI Agent completed!"
echo ""

# Count generated strategies
WORKING_DIR="/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_04_2025/backtests_working"
STRATEGY_COUNT=$(ls -1 $WORKING_DIR/*.py 2>/dev/null | wc -l)

echo "📊 Generated Strategies: $STRATEGY_COUNT"
echo ""

if [ $STRATEGY_COUNT -eq 0 ]; then
    echo "❌ No strategies generated. Check RBI logs."
    exit 1
fi

echo "📋 List of strategies:"
ls -1 $WORKING_DIR/*.py | xargs -n 1 basename
echo ""

# Create batch backtest script for leverage strategies
cat > /tmp/batch_leverage_test.py << 'EOF'
#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# Import the existing batch backtest script
sys.path.insert(0, '/home/titus/moon-dev-ai-agents/src/scripts')

# Get all strategies from today's folder
strategies_dir = Path("/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_04_2025/backtests_working")
strategy_files = sorted(strategies_dir.glob("*.py"))

if len(strategy_files) == 0:
    print("❌ No strategies found!")
    sys.exit(1)

print(f"🚀 Testing {len(strategy_files)} strategies on 27 coins...")
print(f"📊 Total backtests: {len(strategy_files) * 27}")
print("")

# Run batch backtest
from batch_backtest_multi_coin import *

# Override paths for today's strategies
STRATEGIES_DIR = strategies_dir
OUTPUT_DIR = Path("/home/titus/moon-dev-ai-agents/src/data/leverage_multi_coin_backtest")
RESULTS_CSV = OUTPUT_DIR / "leverage_results.csv"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Run main
if __name__ == "__main__":
    main()
EOF

chmod +x /tmp/batch_leverage_test.py

# Run multi-coin backtests
echo "=========================================="
echo "🚀 Starting Multi-Coin Backtests"
echo "=========================================="
echo ""

python3 /tmp/batch_leverage_test.py > /tmp/leverage_backtest.log 2>&1

# Generate summary report
echo ""
echo "=========================================="
echo "📊 FINAL RESULTS SUMMARY"
echo "=========================================="
echo ""

python3 << 'PYEOF'
import pandas as pd
from pathlib import Path

results_file = Path("/home/titus/moon-dev-ai-agents/src/data/leverage_multi_coin_backtest/leverage_results.csv")

if not results_file.exists():
    print("❌ Results file not found!")
    exit(1)

df = pd.read_csv(results_file)
df_success = df[df['status'] == 'success'].copy()

if len(df_success) == 0:
    print("❌ No successful backtests!")
    exit(1)

# Convert to numeric
for col in ['return_pct', 'buy_hold_pct', 'sharpe_ratio', 'max_drawdown_pct', 'num_trades', 'win_rate']:
    df_success[col] = pd.to_numeric(df_success[col], errors='coerce')

df_success['diff'] = df_success['return_pct'] - df_success['buy_hold_pct']
df_success['leverage_4x_return'] = df_success['return_pct'] * 4

print("="*100)
print("🏆 TOP 10 LEVERAGE STRATEGIES (4x Returns)")
print("="*100)
print("")

top_10 = df_success.nlargest(10, 'leverage_4x_return')

print(f"{'Rank':<5} {'Strategy':<30} {'Coin':<6} {'Return':<8} {'4x Return':<10} {'vs B&H':<10} {'Sharpe':<8} {'Trades':<8}")
print("-"*100)

for rank, (_, row) in enumerate(top_10.iterrows(), 1):
    ret = row['return_pct']
    ret_4x = row['leverage_4x_return']
    bh = row['buy_hold_pct']
    diff = ret_4x - bh
    sharpe = row['sharpe_ratio']
    trades = int(row['num_trades']) if pd.notna(row['num_trades']) else 0
    
    beat_symbol = "✅" if diff > 0 else "❌"
    
    print(f"{rank:<5} {row['strategy']:<30} {row['coin']:<6} {ret:>6.1f}%  {ret_4x:>8.1f}%  {diff:>+8.1f}% {beat_symbol}  {sharpe:>6.2f}  {trades:>6}")

print("")
print("="*100)
print("📈 SUMMARY STATS")
print("="*100)

# Overall stats
beat_bh = len(df_success[df_success['leverage_4x_return'] > df_success['buy_hold_pct']])
total = len(df_success)

print(f"Total successful backtests: {total}")
print(f"Strategies beating B&H (with 4x): {beat_bh} ({beat_bh/total*100:.1f}%)")
print(f"Average 4x leveraged return: {df_success['leverage_4x_return'].mean():.2f}%")
print(f"Average B&H return: {df_success['buy_hold_pct'].mean():.2f}%")
print(f"Average Sharpe ratio: {df_success['sharpe_ratio'].mean():.2f}")

print("")
print("✅ RESULTS SAVED TO:")
print(f"   {results_file}")
print("")

PYEOF

echo "=========================================="
echo "✨ PIPELINE COMPLETE!"
echo "=========================================="
echo ""
echo "📁 All results saved to:"
echo "   /home/titus/moon-dev-ai-agents/src/data/leverage_multi_coin_backtest/"
echo ""
echo "🌙 Good morning! Your strategies are ready for deployment."
