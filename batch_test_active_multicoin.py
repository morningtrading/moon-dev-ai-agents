#!/usr/bin/env python3
"""
Batch backtest active strategies on multiple coins
Generated automatically
"""
import subprocess
import os
import re
from pathlib import Path
import pandas as pd
from datetime import datetime

# Configuration
STRATEGIES = [
    r'/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T09_AnchoredReversion_OPT_v6_1.5pct.py',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T03_MomentumCrest_OPT_v5_1.1pct.py',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T03_MomentumCrest_OPT_v8_3.3pct.py',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T12_MitigativeBreaker_OPT_v1_5.4pct.py',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T17_ConfluenceSweep_OPT_v7_2.4pct.py',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T06_StructuralRetest_OPT_v2_1.6pct.py',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T06_StructuralRetest_OPT_v3_3.0pct.py',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T10_EquispacedFilter_OPT_v1_9.9pct.py',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T10_EquispacedFilter_OPT_v3_26.5pct.py',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T08_SequentialRetest_OPT_v4_1.6pct.py',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T08_SequentialRetest_OPT_v5_4.2pct.py',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_05_2025/backtests_working/T07_StableInfluxTrigger_DEBUG_v1_141.3pct.py',
]

DATA_FILES = [
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/ADA-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/APT-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/ASTR-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/AVAX-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/BNB-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/BTC-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/DOGE-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/DOT-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/ETH-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/FET-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/HBAR-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/KSM-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/LDO-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/LINK-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/LTC-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/NEAR-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/PEPE-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/POL-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/RENDER-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/SAND-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/SEI-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/SOL-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/SUI-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/TAO-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/TON-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/UNI-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/XLM-USDT-15m.csv',
    r'/home/titus/moon-dev-ai-agents/src/data/rbi/strategy_ideas.csv',
]

OUTPUT_DIR = Path("/home/titus/moon-dev-ai-agents/multi_coin_active_results")
OUTPUT_DIR.mkdir(exist_ok=True)

CONDA_ENV = "tflow"

def modify_strategy_for_data(strategy_code, data_file):
    """Replace the data file path in strategy code"""
    lines = strategy_code.split('\n')
    for i, line in enumerate(lines):
        if 'pd.read_csv' in line and ('.csv' in line or 'BTC' in line):
            # Find the variable name
            match = re.match(r'\s*(\w+)\s*=', line)
            if match:
                var_name = match.group(1)
                indent = len(line) - len(line.lstrip())
                lines[i] = ' ' * indent + f'{var_name} = pd.read_csv(r"{data_file}")'
    
    return '\n'.join(lines)

def run_backtest(strategy_file, data_file):
    """Run a single backtest"""
    strategy_name = Path(strategy_file).stem
    coin_name = Path(data_file).stem.split('-')[0]
    
    # Read strategy code
    with open(strategy_file, 'r') as f:
        strategy_code = f.read()
    
    # Modify for this data file
    modified_code = modify_strategy_for_data(strategy_code, data_file)
    
    # Create temp file
    temp_file = OUTPUT_DIR / f"temp_{strategy_name}_{coin_name}.py"
    with open(temp_file, 'w') as f:
        f.write(modified_code)
    
    # Run backtest
    log_file = OUTPUT_DIR / f"{strategy_name}_{coin_name}.log"
    
    try:
        result = subprocess.run(
            ['conda', 'run', '-n', CONDA_ENV, 'python', str(temp_file)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Save log
        with open(log_file, 'w') as f:
            f.write(result.stdout)
            if result.stderr:
                f.write("\n\nSTDERR:\n")
                f.write(result.stderr)
        
        # Parse return
        if "Return [%]" in result.stdout:
            for line in result.stdout.split('\n'):
                if "Return [%]" in line:
                    ret_str = line.split()[-1]
                    try:
                        return float(ret_str)
                    except:
                        pass
        
        return None
        
    except Exception as e:
        with open(log_file, 'w') as f:
            f.write(f"Error: {str(e)}")
        return None
    finally:
        if temp_file.exists():
            temp_file.unlink()

# Main execution
if __name__ == "__main__":
    print("=" * 70)
    print("Multi-Coin Batch Backtest - Active Strategies")
    print("=" * 70)
    print(f"Strategies: {len(STRATEGIES)}")
    print(f"Coins: {len(DATA_FILES)}")
    print(f"Total backtests: {len(STRATEGIES) * len(DATA_FILES)}")
    print()
    
    results = []
    total = len(STRATEGIES) * len(DATA_FILES)
    current = 0
    
    for strategy_file in STRATEGIES:
        strategy_name = Path(strategy_file).stem
        
        for data_file in DATA_FILES:
            current += 1
            coin_name = Path(data_file).stem.split('-')[0]
            
            print(f"[{current}/{total}] {strategy_name} on {coin_name}...", end=' ')
            
            ret = run_backtest(strategy_file, data_file)
            
            if ret is not None:
                print(f"✓ {ret:>7.2f}%")
                results.append({
                    'strategy': strategy_name,
                    'coin': coin_name,
                    'return': ret
                })
            else:
                print("✗ FAILED")
    
    # Save results
    if results:
        results_df = pd.DataFrame(results)
        results_csv = OUTPUT_DIR / f"multi_coin_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        results_df.to_csv(results_csv, index=False)
        
        print()
        print("=" * 70)
        print(f"✅ Results saved to: {results_csv}")
        print(f"Total successful backtests: {len(results)}/{total}")
        print("=" * 70)
