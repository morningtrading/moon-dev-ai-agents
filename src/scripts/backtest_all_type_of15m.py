#!/usr/bin/env python3
"""
🌙 Moon Dev's Multi-Symbol Batch Backtester
Runs 7 RBI strategies across 95 different 15m data files (stocks, forex, crypto, commodities, indices)
No AI - just raw backtesting.py execution in parallel.
"""

import subprocess
import pandas as pd
from pathlib import Path
from datetime import datetime
from multiprocessing import Pool, cpu_count
import re
import sys
import os

# ============================================================
# CONFIGURATION
# ============================================================

STRATEGIES_DIR = Path("/home/titus/moon-dev-ai-agents/src/data/rbi_pp_multi/02_28_2026/backtests_optimized")
DATA_DIR = Path("/home/titus/moon-dev-ai-agents/data")
OUTPUT_DIR = Path("/home/titus/moon-dev-ai-agents/src/data/multi_symbol_backtest")
RESULTS_CSV = OUTPUT_DIR / "GEN_95_symbol_results.csv"
TEMP_DIR = OUTPUT_DIR / "temp"
DEBUG_DIR = OUTPUT_DIR / "debug"

# 7 working strategies from the RBI run
STRATEGY_FILES = [
    STRATEGIES_DIR / "T03_DynamicBreakout_BEST_OOS_PASS_IS-0_OOS0.03776pct.py",
    STRATEGIES_DIR / "T01_SqueezeBreakout_BEST_OOS_FAIL_IS-19_OOS-10.13495pct.py",
    STRATEGIES_DIR / "T02_KineticCrossover_BEST_OOS_FAIL_IS-9_OOS-6.83865pct.py",
    STRATEGIES_DIR / "T04_TemporalBias_OPT_v3.py",
    STRATEGIES_DIR / "T05_VelocityConfirmation_BEST_OOS_FAIL_IS-91_OOS-89.12955pct.py",
    STRATEGIES_DIR / "T08_GeneticArchitect_BEST_OOS_FAIL_IS-76_OOS-30.13988pct.py",
    STRATEGIES_DIR / "T17_ChartistBreakout_BEST_OOS_FAIL_IS-57_OOS-73.3071pct.py",
]

CONDA_ENV = "tflow"
TIMEOUT_SECONDS = 60
NUM_WORKERS = 8

# ============================================================
# HELPERS
# ============================================================

def extract_strategy_name(filepath: Path) -> str:
    """Extract clean strategy name from filepath"""
    match = re.search(r'T\d+_(\w+?)(?:_BEST|_OPT)', filepath.stem)
    if match:
        return match.group(1)
    return filepath.stem

def extract_symbol_name(filepath: Path) -> str:
    """Extract symbol name from data filepath (e.g., BTCUSD_15m.csv -> BTCUSD)"""
    return filepath.stem.replace("_15m", "")

def modify_strategy_for_data(strategy_code: str, data_file: Path) -> str:
    """
    Modify strategy code to use a different data file.
    Handles column mapping: time->datetime, tick_volume->volume
    """
    modified = strategy_code

    # 1) Replace the CSV path in pd.read_csv(...) calls
    modified = re.sub(
        r"pd\.read_csv\(['\"].*?['\"]\)",
        f"pd.read_csv(r'{data_file}')",
        modified,
    )

    # Also handle data_path variable assignments pointing to CSV
    modified = re.sub(
        r"(data_path\s*=\s*)['\"].*?\.csv['\"]",
        f"\\1r'{data_file}'",
        modified,
    )

    # 2) Inject column rename right after pd.read_csv line
    #    This maps: time->datetime, tick_volume->volume
    inject_line = (
        "\n# --- INJECTED: column mapping for multi-symbol data ---\n"
        "if 'time' in data.columns and 'datetime' not in data.columns:\n"
        "    data = data.rename(columns={'time': 'datetime'})\n"
        "if 'tick_volume' in data.columns and 'volume' not in data.columns:\n"
        "    data = data.rename(columns={'tick_volume': 'volume'})\n"
        "for _col in ['open','high','low','close','volume','tick_volume']:\n"
        "    if _col in data.columns:\n"
        "        data[_col] = data[_col].astype(float)\n"
        "# --- END INJECTION ---\n"
    )

    # Find the line with pd.read_csv and inject after it
    lines = modified.split('\n')
    new_lines = []
    injected = False
    for line in lines:
        new_lines.append(line)
        if not injected and 'pd.read_csv' in line and 'data' in line:
            # Get the indentation of the read_csv line
            indent = len(line) - len(line.lstrip())
            # Indent the injection to match
            indented_inject = '\n'.join(
                (' ' * indent + l if l.strip() else l) for l in inject_line.split('\n')
            )
            new_lines.append(indented_inject)
            injected = True

    return '\n'.join(new_lines)

def extract_metric(text: str, pattern: str):
    """Extract a numeric metric from backtest output"""
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        try:
            return float(match.group(1))
        except (ValueError, IndexError):
            pass
    return None

def calculate_consecutive_stats(output: str) -> dict:
    """Calculate max consecutive wins/losses from backtest output"""
    try:
        # Look for the Trades table section in backtesting.py output
        # Format: EntryTime, ExitTime, ..., PnL%, ...
        lines = output.split('\n')
        
        pnl_values = []
        in_trades_section = False
        
        for line in lines:
            # Detect trades table (look for PnL or P/L column)
            if 'PnL' in line or 'P/L' in line or 'ReturnPct' in line:
                in_trades_section = True
                continue
            
            # Exit trades section when we hit another table or summary
            if in_trades_section and ('Start' in line or '=====' in line or 'Duration' in line):
                break
            
            # Parse PnL values (look for percentage signs)
            if in_trades_section and '%' in line:
                # Try to extract the percentage value
                parts = line.split()
                for part in parts:
                    if '%' in part:
                        try:
                            val = float(part.replace('%', '').strip())
                            pnl_values.append(val)
                        except ValueError:
                            continue
        
        # Calculate consecutive wins/losses
        if len(pnl_values) == 0:
            return {'max_consecutive_wins': 0, 'max_consecutive_losses': 0}
        
        max_wins = 0
        max_losses = 0
        current_wins = 0
        current_losses = 0
        
        for pnl in pnl_values:
            if pnl > 0:
                current_wins += 1
                current_losses = 0
                max_wins = max(max_wins, current_wins)
            elif pnl < 0:
                current_losses += 1
                current_wins = 0
                max_losses = max(max_losses, current_losses)
            # pnl == 0 resets both
            else:
                current_wins = 0
                current_losses = 0
        
        return {
            'max_consecutive_wins': max_wins,
            'max_consecutive_losses': max_losses
        }
    except Exception:
        return {'max_consecutive_wins': 0, 'max_consecutive_losses': 0}

def analyze_data_file(data_file: Path) -> dict:
    """Quick analysis of data file to get bar count, time span, IS/OOS detection"""
    try:
        # Read just the datetime column for speed
        df = pd.read_csv(data_file, usecols=[0], nrows=None)
        first_col = df.columns[0]
        
        # Parse dates
        dates = pd.to_datetime(df[first_col])
        
        num_bars = len(dates)
        start_date = dates.min()
        end_date = dates.max()
        time_span_days = (end_date - start_date).days
        
        # Detect IS/OOS based on common patterns
        file_name = data_file.stem.upper()
        if 'ODD' in file_name or 'IS-ODD' in file_name:
            data_type = 'IS-ODD'
        elif 'EVEN' in file_name or 'OOS-EVEN' in file_name:
            data_type = 'OOS-EVEN'
        elif 'IS' in file_name and 'OOS' not in file_name:
            data_type = 'IS'
        elif 'OOS' in file_name:
            data_type = 'OOS'
        else:
            # Check if it's alternating months based on actual dates
            months = dates.dt.month.unique()
            if len(months) > 0:
                odd_months = sum(1 for m in months if m % 2 == 1)
                even_months = sum(1 for m in months if m % 2 == 0)
                if odd_months > 0 and even_months == 0:
                    data_type = 'IS-ODD'
                elif even_months > 0 and odd_months == 0:
                    data_type = 'OOS-EVEN'
                else:
                    data_type = 'FULL'
            else:
                data_type = 'FULL'
        
        return {
            'num_bars': num_bars,
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'time_span_days': time_span_days,
            'data_type': data_type
        }
    except Exception as e:
        return {
            'num_bars': 0,
            'start_date': 'unknown',
            'end_date': 'unknown',
            'time_span_days': 0,
            'data_type': 'ERROR'
        }

def run_single_backtest(args: tuple) -> dict:
    """Run a single strategy+symbol backtest (called by Pool workers)"""
    strategy_file, data_file, job_index, total_jobs = args
    strategy_name = extract_strategy_name(strategy_file)
    symbol = extract_symbol_name(data_file)
    
    # Analyze data file first
    data_info = analyze_data_file(data_file)

    try:
        # Read strategy source
        with open(strategy_file, 'r') as f:
            strategy_code = f.read()

        # Modify for this data file
        modified_code = modify_strategy_for_data(strategy_code, data_file)

        # Write temp file
        temp_file = TEMP_DIR / f"{strategy_name}_{symbol}.py"
        with open(temp_file, 'w') as f:
            f.write(modified_code)

        # Run backtest via conda
        result = subprocess.run(
            ['conda', 'run', '-n', CONDA_ENV, '--no-capture-output', 'python', str(temp_file)],
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
        )

        output = result.stdout + '\n' + result.stderr

        # Save debug output
        debug_file = DEBUG_DIR / f"{strategy_name}_{symbol}.txt"
        with open(debug_file, 'w') as f:
            f.write(output)

        # Parse metrics from backtesting.py output
        return_pct = extract_metric(output, r'Return \[%\]\s+([-\d.]+)')
        buy_hold = extract_metric(output, r'Buy & Hold Return \[%\]\s+([-\d.]+)')
        sharpe = extract_metric(output, r'Sharpe Ratio\s+([-\d.]+)')
        max_dd = extract_metric(output, r'Max\. Drawdown \[%\]\s+([-\d.]+)')
        num_trades = extract_metric(output, r'# Trades\s+(\d+)')
        win_rate = extract_metric(output, r'Win Rate \[%\]\s+([-\d.]+)')
        exposure = extract_metric(output, r'Exposure Time \[%\]\s+([-\d.]+)')
        sortino = extract_metric(output, r'Sortino Ratio\s+([-\d.]+)')
        
        # Calculate consecutive wins/losses
        consecutive_stats = calculate_consecutive_stats(output)

        # Determine status with enhanced details
        reason = 'unknown'
        if return_pct is not None:
            status = 'success'
            trades = int(num_trades) if num_trades is not None else 0
            wr = win_rate if win_rate is not None else 0
            
            # Get consecutive stats
            max_cons_wins = consecutive_stats.get('max_consecutive_wins', 0)
            max_cons_losses = consecutive_stats.get('max_consecutive_losses', 0)
            
            # Build detailed status tag
            if return_pct == 0.0:
                # Explain why 0.0%
                if trades == 0:
                    tag = f"0.0% (NO TRADES)"
                    reason = "no_trades"
                elif wr == 0:
                    tag = f"0.0% ({trades}T, ALL LOSSES! MaxL:{max_cons_losses})"
                    reason = "all_losses"
                else:
                    tag = f"0.0% ({trades}T, {wr:.0f}%WR, MaxW:{max_cons_wins}/L:{max_cons_losses})"
                    reason = "breakeven"
            else:
                # Show return with trade count, win rate, and max consecutive
                tag = f"{return_pct:+.1f}% ({trades}T, {wr:.0f}%WR, MaxW:{max_cons_wins}/L:{max_cons_losses})"
                reason = "normal"
        elif result.returncode != 0:
            status = 'error'
            tag = 'ERR'
            reason = 'error'
        else:
            status = 'parse_error'
            tag = 'PARSE'
            reason = 'parse_error'

        # Clean up temp file
        temp_file.unlink(missing_ok=True)

        # Enhanced progress display with data info
        bars_info = f"{data_info['num_bars']}bars/{data_info['time_span_days']}d"
        data_type_tag = data_info['data_type']
        print(f"[{job_index}/{total_jobs}] {strategy_name:>25} x {symbol:<15} ({bars_info}, {data_type_tag}) -> {tag}")

        return {
            'strategy': strategy_name,
            'symbol': symbol,
            'data_file': data_file.name,
            'return_pct': return_pct,
            'buy_hold_pct': buy_hold,
            'sharpe_ratio': sharpe,
            'sortino_ratio': sortino,
            'max_drawdown_pct': max_dd,
            'exposure_pct': exposure,
            'num_trades': num_trades,
            'win_rate': win_rate,
            'max_consecutive_wins': consecutive_stats.get('max_consecutive_wins', 0),
            'max_consecutive_losses': consecutive_stats.get('max_consecutive_losses', 0),
            'status': status,
            'reason': reason,
            'num_bars': data_info['num_bars'],
            'time_span_days': data_info['time_span_days'],
            'data_type': data_info['data_type'],
            'start_date': data_info['start_date'],
            'end_date': data_info['end_date'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

    except subprocess.TimeoutExpired:
        bars_info = f"{data_info['num_bars']}bars/{data_info['time_span_days']}d"
        data_type_tag = data_info['data_type']
        print(f"[{job_index}/{total_jobs}] {strategy_name:>25} x {symbol:<15} ({bars_info}, {data_type_tag}) -> TIMEOUT")
        return {
            'strategy': strategy_name, 'symbol': symbol, 'data_file': data_file.name,
            'status': 'timeout',
            'num_bars': data_info['num_bars'],
            'time_span_days': data_info['time_span_days'],
            'data_type': data_info['data_type'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
    except Exception as e:
        bars_info = f"{data_info['num_bars']}bars/{data_info['time_span_days']}d"
        data_type_tag = data_info['data_type']
        print(f"[{job_index}/{total_jobs}] {strategy_name:>25} x {symbol:<15} ({bars_info}, {data_type_tag}) -> CRASH: {e}")
        return {
            'strategy': strategy_name, 'symbol': symbol, 'data_file': data_file.name,
            'status': 'error', 'error': str(e),
            'num_bars': data_info['num_bars'],
            'time_span_days': data_info['time_span_days'],
            'data_type': data_info['data_type'],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }

# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 80)
    print("🌙 Moon Dev's Multi-Symbol Batch Backtester")
    print("=" * 80)

    # Create output dirs
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    DEBUG_DIR.mkdir(parents=True, exist_ok=True)

    # Validate strategies exist
    strategies = [s for s in STRATEGY_FILES if s.exists()]
    if not strategies:
        print("❌ No strategy files found!")
        return
    print(f"\n📈 Strategies ({len(strategies)}):")
    for s in strategies:
        print(f"   • {extract_strategy_name(s)}")

    # Get all 15m data files
    data_files = sorted(DATA_DIR.glob("*_15m.csv"))
    if not data_files:
        print("❌ No data files found in", DATA_DIR)
        return
    print(f"\n💰 Symbols ({len(data_files)}):")
    symbols = [extract_symbol_name(f) for f in data_files]
    # Print in rows of 10
    for i in range(0, len(symbols), 10):
        print(f"   {', '.join(symbols[i:i+10])}")

    total = len(strategies) * len(data_files)
    print(f"\n🎯 Total backtests: {len(strategies)} strategies × {len(data_files)} symbols = {total}")
    print(f"⚡ Workers: {NUM_WORKERS}")
    print(f"⏰ Timeout: {TIMEOUT_SECONDS}s per backtest")
    print()

    # Build job list
    jobs = []
    idx = 0
    for strategy_file in strategies:
        for data_file in data_files:
            idx += 1
            jobs.append((strategy_file, data_file, idx, total))

    # Run in parallel
    start_time = datetime.now()
    print(f"🚀 Starting at {start_time.strftime('%H:%M:%S')}...\n")

    with Pool(NUM_WORKERS) as pool:
        results = pool.map(run_single_backtest, jobs)

    elapsed = (datetime.now() - start_time).total_seconds()

    # Save results
    df = pd.DataFrame(results)
    df.to_csv(RESULTS_CSV, index=False)

    # ============================================================
    # SUMMARY
    # ============================================================
    print("\n" + "=" * 80)
    print("✨ BATCH BACKTESTING COMPLETE")
    print("=" * 80)
    print(f"⏱  Elapsed: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    print(f"📊 Results saved to: {RESULTS_CSV}")

    successful = df[df['status'] == 'success']
    failed = df[df['status'] != 'success']
    print(f"✅ Successful: {len(successful)}/{total}")
    print(f"❌ Failed/Timeout: {len(failed)}/{total}")

    if len(successful) == 0:
        print("\n⚠️  No successful backtests to summarize.")
        return

    successful = successful.copy()
    for col in ['return_pct', 'buy_hold_pct', 'sharpe_ratio', 'max_drawdown_pct', 'num_trades', 'win_rate']:
        successful[col] = pd.to_numeric(successful[col], errors='coerce')

    # --- Per-Strategy Summary ---
    print("\n📊 PER-STRATEGY AVERAGES:")
    print("-" * 100)
    print(f"{'Strategy':<25} {'Avg Return%':>11} {'Avg Sharpe':>11} {'Avg MaxDD%':>11} {'Avg Trades':>11} {'Win%':>8} {'#OK':>5}")
    print("-" * 100)
    for strat in sorted(successful['strategy'].unique()):
        s = successful[successful['strategy'] == strat]
        print(
            f"{strat:<25} "
            f"{s['return_pct'].mean():>10.2f}% "
            f"{s['sharpe_ratio'].mean():>10.2f} "
            f"{s['max_drawdown_pct'].mean():>10.2f}% "
            f"{s['num_trades'].mean():>10.1f} "
            f"{s['win_rate'].mean():>7.1f}% "
            f"{len(s):>4}"
        )

    # --- Top 20 Performers ---
    top20 = successful.nlargest(20, 'return_pct')
    print(f"\n🏆 TOP 20 PERFORMERS:")
    print("-" * 120)
    print(
        f"{'#':<3} {'Strategy':<25} {'Symbol':<15} {'Return%':>9} {'B&H%':>9} "
        f"{'Sharpe':>8} {'MaxDD%':>9} {'Trades':>7} {'WinRate':>8}"
    )
    print("-" * 120)
    for rank, (_, row) in enumerate(top20.iterrows(), 1):
        ret = row['return_pct'] if pd.notna(row['return_pct']) else 0
        bh = row['buy_hold_pct'] if pd.notna(row['buy_hold_pct']) else 0
        sh = row['sharpe_ratio'] if pd.notna(row['sharpe_ratio']) else 0
        dd = row['max_drawdown_pct'] if pd.notna(row['max_drawdown_pct']) else 0
        tr = int(row['num_trades']) if pd.notna(row['num_trades']) else 0
        wr = row['win_rate'] if pd.notna(row['win_rate']) else 0
        print(
            f"{rank:<3} {row['strategy']:<25} {row['symbol']:<15} "
            f"{ret:>8.2f}% {bh:>8.2f}% {sh:>7.2f} {dd:>8.2f}% {tr:>6} {wr:>7.1f}%"
        )

    # --- Bottom 10 Worst ---
    bottom10 = successful.nsmallest(10, 'return_pct')
    print(f"\n💀 BOTTOM 10 WORST:")
    print("-" * 120)
    for rank, (_, row) in enumerate(bottom10.iterrows(), 1):
        ret = row['return_pct'] if pd.notna(row['return_pct']) else 0
        print(
            f"{rank:<3} {row['strategy']:<25} {row['symbol']:<15} {ret:>8.2f}%"
        )

    # --- Profitable counts ---
    profitable = successful[successful['return_pct'] > 0]
    print(f"\n📈 Profitable backtests: {len(profitable)}/{len(successful)} ({100*len(profitable)/len(successful):.1f}%)")

    # Per-strategy profit rate
    print("\n📊 PROFIT RATE BY STRATEGY:")
    for strat in sorted(successful['strategy'].unique()):
        s = successful[successful['strategy'] == strat]
        p = s[s['return_pct'] > 0]
        print(f"   {strat:<25} {len(p)}/{len(s)} profitable ({100*len(p)/len(s):.0f}%)")

    # --- STRATEGY SCORING SYSTEM ---
    print("\n" + "=" * 100)
    print("🏆 COMPREHENSIVE STRATEGY SCORING (Best = 100)")
    print("=" * 100)
    print("Scoring: PnL(30%) + Sharpe(25%) + WinRate(20%) + MaxDD(15%) + ConsecLoss(10%)")
    print("-" * 100)
    
    strategy_scores = []
    for strat in sorted(successful['strategy'].unique()):
        s = successful[successful['strategy'] == strat]
        
        # Calculate component scores (0-100 scale)
        avg_return = s['return_pct'].mean()
        avg_sharpe = s['sharpe_ratio'].mean()
        avg_win_rate = s['win_rate'].mean()
        avg_max_dd = s['max_drawdown_pct'].mean()
        avg_max_cons_loss = s['max_consecutive_losses'].mean()
        
        # Score PnL (30% weight): Normalize to 0-100 scale
        # Excellent: >5%, Good: >2%, Poor: <0%
        pnl_score = min(100, max(0, (avg_return + 5) * 10))  # -5% to +5% -> 0-100
        
        # Score Sharpe Ratio (25% weight)
        # Excellent: >2, Good: >1, Poor: <0
        sharpe_score = min(100, max(0, (avg_sharpe + 2) * 25))  # -2 to +2 -> 0-100
        
        # Score Win Rate (20% weight)
        # Already 0-100%
        win_rate_score = avg_win_rate
        
        # Score Max Drawdown (15% weight) - INVERTED (lower is better)
        # Excellent: <5%, Good: <10%, Poor: >20%
        dd_score = min(100, max(0, 100 - abs(avg_max_dd) * 5))  # 0-20% DD -> 100-0
        
        # Score Max Consecutive Losses (10% weight) - INVERTED (lower is better)
        # Excellent: <3, Good: <6, Poor: >10
        cons_loss_score = min(100, max(0, 100 - avg_max_cons_loss * 10))  # 0-10 losses -> 100-0
        
        # Weighted total score
        total_score = (
            pnl_score * 0.30 +
            sharpe_score * 0.25 +
            win_rate_score * 0.20 +
            dd_score * 0.15 +
            cons_loss_score * 0.10
        )
        
        strategy_scores.append({
            'strategy': strat,
            'total_score': total_score,
            'pnl_score': pnl_score,
            'sharpe_score': sharpe_score,
            'win_rate_score': win_rate_score,
            'dd_score': dd_score,
            'cons_loss_score': cons_loss_score,
            'avg_return': avg_return,
            'avg_sharpe': avg_sharpe,
            'avg_win_rate': avg_win_rate,
            'avg_max_dd': avg_max_dd,
            'avg_max_cons_loss': avg_max_cons_loss
        })
    
    # Sort by total score
    strategy_scores = sorted(strategy_scores, key=lambda x: x['total_score'], reverse=True)
    
    print(f"{'Rank':<5} {'Strategy':<25} {'Score':>6} {'PnL':>7} {'Sharpe':>7} {'WinRate':>8} {'MaxDD':>7} {'MaxCL':>6}")
    print("-" * 100)
    
    for rank, score_data in enumerate(strategy_scores, 1):
        grade = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else "  "
        
        print(
            f"{grade} {rank:<3} {score_data['strategy']:<25} "
            f"{score_data['total_score']:>6.1f} "
            f"{score_data['avg_return']:>6.2f}% "
            f"{score_data['avg_sharpe']:>6.2f} "
            f"{score_data['avg_win_rate']:>7.1f}% "
            f"{score_data['avg_max_dd']:>6.2f}% "
            f"{score_data['avg_max_cons_loss']:>5.1f}"
        )
    
    print("-" * 100)
    print("\n📊 SCORE INTERPRETATION:")
    print("   90-100: 🌟 Excellent - Deploy with confidence")
    print("   70-89:  ✅ Good - Solid performer")
    print("   50-69:  ⚠️  Moderate - Use with caution")
    print("   30-49:  ⚠️  Poor - Needs improvement")
    print("   0-29:   ❌ Failing - Do not deploy")
    
    # Identify best strategy
    if strategy_scores:
        best = strategy_scores[0]
        print(f"\n🏆 BEST STRATEGY: {best['strategy']}")
        print(f"   Overall Score: {best['total_score']:.1f}/100")
        print(f"   Avg Return: {best['avg_return']:.2f}%")
        print(f"   Avg Sharpe: {best['avg_sharpe']:.2f}")
        print(f"   Avg Win Rate: {best['avg_win_rate']:.1f}%")
        print(f"   Avg Max DD: {best['avg_max_dd']:.2f}%")
        print(f"   Avg Max Consecutive Losses: {best['avg_max_cons_loss']:.1f}")

    print("\n" + "=" * 100)
    print("🌙 Done!")
    print("=" * 100)


if __name__ == "__main__":
    main()
