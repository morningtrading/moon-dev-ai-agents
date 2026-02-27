#!/usr/bin/env python3
"""
Period-based strategy filter
Requires strategies to be profitable in at least 2 out of 3 periods
"""
import pandas as pd
import subprocess
import sys
from pathlib import Path

def test_strategy_by_periods(strategy_file, data_dir):
    """Test strategy on each period separately"""
    
    periods = {
        'bear_2022': f'{data_dir}/BTC-USDT-2022-BEAR-15m.csv',
        'recovery_2023': f'{data_dir}/BTC-USD-15m.csv',  # Filtered to 2023 in strategy
        'bull_2025': f'{data_dir}/BTC-USDT-15m.csv'
    }
    
    # Read strategy code
    with open(strategy_file) as f:
        code = f.read()
    
    results = {}
    
    for period_name, data_file in periods.items():
        # Replace data path
        import re
        mod_code = re.sub(
            r"data = pd\.read_csv\('[^']+'\)",
            f"data = pd.read_csv(r'{data_file}')",
            code
        )
        
        # For recovery_2023, add date filter
        if period_name == 'recovery_2023':
            mod_code = mod_code.replace(
                "data = data.set_index('datetime')",
                "data = data[(data['datetime'] >= '2023-01-01') & (data['datetime'] <= '2023-12-31')]; data = data.set_index('datetime')"
            )
        
        # Run backtest
        temp_file = f"/tmp/test_{period_name}.py"
        with open(temp_file, 'w') as f:
            f.write(mod_code)
        
        try:
            res = subprocess.run(
                ['conda', 'run', '-n', 'tflow', 'python', temp_file],
                capture_output=True, text=True, timeout=60
            )
            
            # Parse return
            if "Return [%]" in res.stdout:
                for line in res.stdout.split('\n'):
                    if "Return [%]" in line and "Buy & Hold" not in line:
                        ret = float(line.split()[-1])
                        results[period_name] = ret
                        break
        except:
            results[period_name] = None
    
    return results

def passes_period_filter(results):
    """Check if profitable in at least 2 out of 3 periods"""
    profitable_periods = sum(1 for r in results.values() if r is not None and r > 0)
    return profitable_periods >= 2

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python period_filter.py <strategy_file>")
        sys.exit(1)
    
    strategy_file = sys.argv[1]
    data_dir = "/home/titus/moon-dev-ai-agents/src/data/rbi"
    
    results = test_strategy_by_periods(strategy_file, data_dir)
    
    print("Period-Based Performance:")
    for period, ret in results.items():
        status = "✅" if ret and ret > 0 else "❌"
        print(f"  {period}: {ret:.2f}% {status}" if ret else f"  {period}: FAILED ❌")
    
    if passes_period_filter(results):
        print("\n✅ PASS: Profitable in 2+ periods")
        sys.exit(0)
    else:
        print("\n❌ FAIL: Not profitable in enough periods")
        sys.exit(1)
