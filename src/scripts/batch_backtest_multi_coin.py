#!/usr/bin/env python3
"""
🌙 Moon Dev's Multi-Coin Batch Backtester
Tests multiple strategies across all available coins
"""

import subprocess
import pandas as pd
from pathlib import Path
from datetime import datetime
from termcolor import cprint
import sys
import re

# Paths
STRATEGIES_DIR = Path("/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/11_03_2025/backtests_working")
DATA_DIR = Path("/home/titus/moon-dev-ai-agents/src/data/rbi")
OUTPUT_DIR = Path("/home/titus/moon-dev-ai-agents/src/data/multi_coin_backtest")
RESULTS_CSV = OUTPUT_DIR / "multi_coin_backtest_results.csv"

# Create output directory
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_strategy_files():
    """Get all strategy Python files"""
    return sorted(STRATEGIES_DIR.glob("*.py"))

def get_data_files():
    """Get all 15m CSV data files"""
    return sorted(DATA_DIR.glob("*-USDT-15m.csv"))

def extract_coin_name(filepath: Path) -> str:
    """Extract coin name from filepath (e.g., BTC-USDT-15m.csv -> BTC)"""
    return filepath.stem.split('-')[0]

def extract_strategy_name(filepath: Path) -> str:
    """Extract strategy name from filepath"""
    # Pattern: T##_StrategyName_OPT_v#_##.#pct.py
    match = re.search(r'T\d+_(.+?)_OPT', filepath.stem)
    if match:
        return match.group(1)
    return filepath.stem

def run_backtest(strategy_file: Path, data_file: Path) -> dict:
    """Run a single backtest and extract results"""
    strategy_name = extract_strategy_name(strategy_file)
    coin_name = extract_coin_name(data_file)
    
    cprint(f"🔄 Testing {strategy_name} on {coin_name}...", "cyan")
    
    try:
        # Read the strategy file
        with open(strategy_file, 'r') as f:
            strategy_code = f.read()
        
        # Replace the data file path - handle multiple patterns
        modified_code = strategy_code
        
        # Pattern 1: Lines with os.path.join that mention 'rbi' or '.csv'
        # Match entire line and replace with simple assignment
        lines = modified_code.split('\n')
        for i, line in enumerate(lines):
            if 'os.path.join' in line and ('rbi' in line.lower() or '.csv' in line.lower()):
                # Extract variable name
                match = re.match(r'\s*(\w+)\s*=', line)
                if match:
                    var_name = match.group(1)
                    indent = len(line) - len(line.lstrip())
                    lines[i] = ' ' * indent + f'{var_name} = r"{data_file}"'
        modified_code = '\n'.join(lines)
        
        # Pattern 2: pd.read_csv direct calls
        modified_code = re.sub(
            r'pd\.read_csv\(["\'].*?["\']',
            f'pd.read_csv(r"{data_file}"',
            modified_code
        )
        
        # Create temporary modified strategy file
        temp_strategy = OUTPUT_DIR / f"temp_{strategy_name}_{coin_name}.py"
        with open(temp_strategy, 'w') as f:
            f.write(modified_code)
        
        # Run the backtest
        result = subprocess.run(
            [sys.executable, str(temp_strategy)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        # Parse output for stats
        output = result.stdout + result.stderr
        
        # Save output for debugging
        debug_file = OUTPUT_DIR / f"debug_{strategy_name}_{coin_name}.txt"
        with open(debug_file, 'w') as f:
            f.write(output)
        
        # Extract key metrics using regex (backtesting.py format)
        return_pct = extract_metric(output, r'Return \[%\]\s+([-\d.]+)')
        sharpe = extract_metric(output, r'Sharpe Ratio\s+([-\d.]+)')
        max_dd = extract_metric(output, r'Max\. Drawdown \[%\]\s+([-\d.]+)')
        num_trades = extract_metric(output, r'# Trades\s+(\d+)')
        win_rate = extract_metric(output, r'Win Rate \[%\]\s+([-\d.]+)')
        buy_hold = extract_metric(output, r'Buy & Hold Return \[%\]\s+([-\d.]+)')
        
        # Clean up temp file
        temp_strategy.unlink(missing_ok=True)
        
        if return_pct is not None:
            cprint(f"  ✅ {coin_name}: {return_pct}% return", "green")
        else:
            cprint(f"  ⚠️  {coin_name}: Could not parse results (see debug_{strategy_name}_{coin_name}.txt)", "yellow")
        
        return {
            'strategy': strategy_name,
            'coin': coin_name,
            'data_file': data_file.name,
            'return_pct': return_pct,
            'buy_hold_pct': buy_hold,
            'sharpe_ratio': sharpe,
            'max_drawdown_pct': max_dd,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'status': 'success' if return_pct is not None else 'parse_error',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except subprocess.TimeoutExpired:
        cprint(f"  ⏰ {coin_name}: Timeout", "red")
        return {
            'strategy': strategy_name,
            'coin': coin_name,
            'data_file': data_file.name,
            'status': 'timeout',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        cprint(f"  ❌ {coin_name}: Error - {e}", "red")
        return {
            'strategy': strategy_name,
            'coin': coin_name,
            'data_file': data_file.name,
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def extract_metric(text: str, pattern: str) -> float:
    """Extract a metric from text using regex"""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except:
            pass
    return None

def main():
    """Run batch backtests"""
    cprint("\n" + "=" * 70, "white")
    cprint("🌙 Moon Dev's Multi-Coin Batch Backtester", "yellow", attrs=["bold"])
    cprint("=" * 70 + "\n", "white")
    
    # Get files
    strategy_files = get_strategy_files()
    data_files = get_data_files()
    
    if not strategy_files:
        cprint("❌ No strategy files found!", "red")
        return
    
    if not data_files:
        cprint("❌ No data files found!", "red")
        return
    
    cprint(f"📊 Found {len(strategy_files)} strategies", "cyan")
    cprint(f"💰 Found {len(data_files)} coins", "cyan")
    cprint(f"🎯 Total backtests: {len(strategy_files) * len(data_files)}\n", "green")
    
    for strategy_file in strategy_files:
        cprint(f"  • {extract_strategy_name(strategy_file)}", "white")
    
    print()
    for data_file in data_files:
        cprint(f"  • {extract_coin_name(data_file)}", "white")
    
    print()
    input("Press Enter to start backtesting...")
    print()
    
    # Run all combinations
    results = []
    total = len(strategy_files) * len(data_files)
    current = 0
    
    for strategy_file in strategy_files:
        cprint(f"\n{'='*70}", "white")
        cprint(f"📈 Strategy: {extract_strategy_name(strategy_file)}", "yellow", attrs=["bold"])
        cprint(f"{'='*70}\n", "white")
        
        for data_file in data_files:
            current += 1
            cprint(f"[{current}/{total}] ", "magenta", end="")
            
            result = run_backtest(strategy_file, data_file)
            results.append(result)
    
    # Save results to CSV
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_CSV, index=False)
    
    # Summary
    cprint("\n" + "=" * 70, "white")
    cprint("✨ Batch Backtesting Complete!", "green", attrs=["bold"])
    cprint("=" * 70, "white")
    
    successful = len(df[df['status'] == 'success'])
    cprint(f"✅ Successful: {successful}/{total}", "green")
    cprint(f"📊 Results saved to: {RESULTS_CSV}", "cyan")
    
    # Show top performers
    if successful > 0:
        df_success = df[df['status'] == 'success'].copy()
        df_success['return_pct'] = pd.to_numeric(df_success['return_pct'], errors='coerce')
        top_10 = df_success.nlargest(10, 'return_pct')
        
        cprint("\n🏆 Top 10 Performers:", "yellow", attrs=["bold"])
        cprint("=" * 120, "white")
        cprint(
            f"{'#':<3} {'Strategy':<20} {'Coin':<6} {'Return':<9} {'B&H':<9} "
            f"{'Diff':<8} {'Drawdown':<10} {'Trades':<8} {'Win Rate':<18} {'Sharpe':<8}",
            "cyan", attrs=["bold"]
        )
        cprint("-" * 120, "white")
        
        for rank, (idx, row) in enumerate(top_10.iterrows(), 1):
            return_pct = row['return_pct'] if pd.notna(row['return_pct']) else 0
            buy_hold = row['buy_hold_pct'] if pd.notna(row['buy_hold_pct']) else 0
            diff = return_pct - buy_hold if buy_hold != 0 else return_pct
            dd = row['max_drawdown_pct'] if pd.notna(row['max_drawdown_pct']) else 0
            trades = int(row['num_trades']) if pd.notna(row['num_trades']) else 0
            win_rate = row['win_rate'] if pd.notna(row['win_rate']) else 0
            sharpe = row['sharpe_ratio'] if pd.notna(row['sharpe_ratio']) else 0
            
            # Calculate wins/losses
            if trades > 0 and win_rate > 0:
                wins = int(trades * win_rate / 100)
                losses = trades - wins
                win_loss = f"{wins}W/{losses}L"
            else:
                win_loss = "N/A"
            
            # Color code the diff
            diff_color = "green" if diff > 0 else "red"
            diff_symbol = "+" if diff > 0 else ""
            
            print(
                f"{rank:<3} {row['strategy']:<20} {row['coin']:<6} "
                f"{return_pct:>7.2f}%  {buy_hold:>7.2f}%  ",
                end=""
            )
            cprint(f"{diff_symbol}{diff:>6.2f}%", diff_color, end="")
            print(
                f"  {dd:>8.2f}%  {trades:>6}  "
                f"{win_rate:>6.1f}% ({win_loss:<9})  {sharpe:>6.2f}"
            )
    
    cprint("=" * 70 + "\n", "white")

if __name__ == "__main__":
    main()
