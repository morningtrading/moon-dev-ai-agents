#!/usr/bin/env python3
"""
🌙 RSI Parameter Sensitivity Analysis
Test RSI ±5 around 20/80 to validate parameter robustness
"""

import pandas as pd
import pandas_ta as ta
from pathlib import Path
from termcolor import cprint
from backtesting import Backtest, Strategy
import numpy as np

# Data directories for all 3 periods
PERIOD1_DIR = Path("/home/titus/Dropbox/user_data/data/binance")  # Jul-Oct 5m
PERIOD2_DIR = Path("/home/titus/Dropbox/user_data/data/binance_walkforward")  # Apr-Jun 5m
PERIOD3_DIR = Path("/home/titus/Dropbox/user_data/data/binance_15m_validation")  # Apr-Jul 15m

# Top 4 validated pairs
TOP_PAIRS = ['PENDLE_USDT', 'BCH_USDT', 'BNB_USDT', 'QTUM_USDT']

# Parameter ranges
OVERSOLD_VALUES = [15, 20, 25]
OVERBOUGHT_VALUES = [75, 80, 85]

class RSIStrategy(Strategy):
    rsi_period = 14
    oversold = 20
    overbought = 80

    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        self.rsi = self.I(ta.rsi, close, length=self.rsi_period)

    def next(self):
        if self.rsi[-1] < self.oversold and not self.position:
            self.buy()
        elif self.rsi[-1] > self.overbought and self.position:
            self.position.close()

def load_data(file_path):
    """Load and prepare data"""
    df = pd.read_feather(file_path)
    df = df.rename(columns={
        'open': 'Open', 'high': 'High', 'low': 'Low',
        'close': 'Close', 'volume': 'Volume'
    })
    df = df.set_index('date')
    return df

def run_backtest(df, oversold, overbought):
    """Run backtest with specific RSI parameters"""
    try:
        bt = Backtest(df, RSIStrategy, cash=10000, commission=.002)
        results = bt.run(oversold=oversold, overbought=overbought)

        days = (df.index[-1] - df.index[0]).days
        weeks = days / 7

        return {
            'return': results['Return [%]'],
            'sharpe': results['Sharpe Ratio'],
            'max_dd': results['Max. Drawdown [%]'],
            'trades': results['# Trades'],
            'trades_per_week': results['# Trades'] / weeks if weeks > 0 else 0,
            'win_rate': results['Win Rate [%]'],
        }
    except Exception as e:
        return None

def parameter_sweep():
    """Comprehensive parameter sensitivity analysis"""

    cprint("\n🌙 RSI Parameter Sensitivity Analysis", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    cprint(f"\n📊 Testing RSI parameter robustness:", "yellow")
    cprint(f"  Oversold:   {OVERSOLD_VALUES} (current: 20)", "white")
    cprint(f"  Overbought: {OVERBOUGHT_VALUES} (current: 80)", "white")
    cprint(f"  Combinations: {len(OVERSOLD_VALUES)} × {len(OVERBOUGHT_VALUES)} = {len(OVERSOLD_VALUES) * len(OVERBOUGHT_VALUES)}", "white")

    cprint(f"\n🎯 Testing on:", "yellow")
    cprint(f"  • 4 pairs: {', '.join(TOP_PAIRS)}", "white")
    cprint(f"  • 3 periods: Jul-Oct 5m, Apr-Jun 5m, Apr-Jul 15m", "white")
    cprint(f"  • Total backtests: {len(TOP_PAIRS)} × 3 × {len(OVERSOLD_VALUES) * len(OVERBOUGHT_VALUES)} = {len(TOP_PAIRS) * 3 * len(OVERSOLD_VALUES) * len(OVERBOUGHT_VALUES)}", "white")

    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🔬 Running Parameter Sweep...\n", "cyan")

    # Store all results
    all_results = {}

    total_tests = 0
    successful_tests = 0

    for pair in TOP_PAIRS:
        all_results[pair] = {}

        cprint(f"\n📈 {pair}", "yellow", attrs=["bold"])

        # Test on all 3 periods
        periods = [
            ('Period 1 (Jul-Oct 5m)', PERIOD1_DIR, '5m'),
            ('Period 2 (Apr-Jun 5m)', PERIOD2_DIR, '5m'),
            ('Period 3 (Apr-Jul 15m)', PERIOD3_DIR, '15m')
        ]

        for period_name, data_dir, timeframe in periods:
            file_path = data_dir / f"{pair}-{timeframe}.feather"

            if not file_path.exists():
                cprint(f"  ⚠️  {period_name}: Missing data", "yellow")
                continue

            df = load_data(file_path)
            all_results[pair][period_name] = {}

            cprint(f"  {period_name}:", "white")

            # Test all parameter combinations
            for oversold in OVERSOLD_VALUES:
                for overbought in OVERBOUGHT_VALUES:
                    total_tests += 1
                    result = run_backtest(df, oversold, overbought)

                    if result:
                        successful_tests += 1
                        combo = f"{oversold}/{overbought}"
                        all_results[pair][period_name][combo] = result

                        # Show current baseline (20/80)
                        if oversold == 20 and overbought == 80:
                            cprint(f"    RSI({oversold}/{overbought}): {result['return']:+6.2f}% "
                                   f"({result['trades']} trades, {result['win_rate']:.1f}% WR) ← Current", "cyan")

    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📊 PARAMETER SENSITIVITY ANALYSIS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    cprint(f"\n✅ Completed {successful_tests}/{total_tests} backtests\n", "green")

    # Analyze results for each pair
    for pair in TOP_PAIRS:
        if pair not in all_results or not all_results[pair]:
            continue

        cprint(f"\n{'='*90}", "cyan")
        cprint(f"📊 {pair} - PARAMETER MATRIX", "yellow", attrs=["bold"])
        cprint(f"{'='*90}", "cyan")

        # Calculate average returns across all 3 periods for each combo
        combo_averages = {}

        for oversold in OVERSOLD_VALUES:
            for overbought in OVERBOUGHT_VALUES:
                combo = f"{oversold}/{overbought}"
                returns = []

                for period_name in all_results[pair]:
                    if combo in all_results[pair][period_name]:
                        returns.append(all_results[pair][period_name][combo]['return'])

                if returns:
                    combo_averages[combo] = sum(returns) / len(returns)

        # Display matrix
        cprint(f"\n  Average Return Across All 3 Periods:\n", "white")
        cprint(f"                   Overbought", "white")
        cprint(f"              75       80       85", "white")
        cprint(f"         ┌────────┬────────┬────────┐", "white")

        for i, oversold in enumerate(OVERSOLD_VALUES):
            row_label = f"    {oversold}  │" if i == 1 else f"       │"
            if i == 0:
                row_label = f"    {oversold}  │"
            elif i == 1:
                row_label = f"O   {oversold}  │"
            elif i == 2:
                row_label = f"    {oversold}  │"

            row_values = []
            for overbought in OVERBOUGHT_VALUES:
                combo = f"{oversold}/{overbought}"
                if combo in combo_averages:
                    val = combo_averages[combo]
                    # Highlight current 20/80
                    if oversold == 20 and overbought == 80:
                        row_values.append(f"\033[1m{val:+6.1f}\033[0m")  # Bold
                    else:
                        row_values.append(f"{val:+6.1f}")
                else:
                    row_values.append("  N/A ")

            values_str = " │ ".join(row_values)
            cprint(f"{row_label} {values_str} │", "white")

            if i < len(OVERSOLD_VALUES) - 1:
                cprint(f"         ├────────┼────────┼────────┤", "white")

        cprint(f"         └────────┴────────┴────────┘", "white")
        cprint(f"  (Bold = Current 20/80 parameters)", "cyan")

        # Find best parameters for this pair
        if combo_averages:
            best_combo = max(combo_averages.items(), key=lambda x: x[1])
            worst_combo = min(combo_averages.items(), key=lambda x: x[1])
            current_return = combo_averages.get('20/80', 0)

            cprint(f"\n  Best:    RSI({best_combo[0]}) = {best_combo[1]:+.2f}%", "green")
            cprint(f"  Current: RSI(20/80) = {current_return:+.2f}%", "cyan")
            cprint(f"  Worst:   RSI({worst_combo[0]}) = {worst_combo[1]:+.2f}%", "red")
            cprint(f"  Range:   {best_combo[1] - worst_combo[1]:.2f}% spread", "white")

            # Parameter sensitivity
            if best_combo[1] - current_return < 2:
                cprint(f"  ✅ Current parameters are near-optimal!", "green")
            elif best_combo[1] - current_return < 5:
                cprint(f"  ⚠️  Found slightly better parameters", "yellow")
            else:
                cprint(f"  🔴 Current parameters may be suboptimal", "red")

        # Show period-by-period detail for 20/80
        cprint(f"\n  Current (20/80) Performance by Period:", "cyan")
        for period_name in all_results[pair]:
            if '20/80' in all_results[pair][period_name]:
                res = all_results[pair][period_name]['20/80']
                cprint(f"    {period_name}: {res['return']:+6.2f}%", "white")

    # Overall robustness analysis
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"⚖️  OVERALL ROBUSTNESS ANALYSIS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    # Calculate how many pairs have 20/80 as optimal or near-optimal
    optimal_count = 0
    near_optimal_count = 0

    for pair in TOP_PAIRS:
        combo_averages = {}
        for oversold in OVERSOLD_VALUES:
            for overbought in OVERBOUGHT_VALUES:
                combo = f"{oversold}/{overbought}"
                returns = []
                for period_name in all_results[pair]:
                    if combo in all_results[pair][period_name]:
                        returns.append(all_results[pair][period_name][combo]['return'])
                if returns:
                    combo_averages[combo] = sum(returns) / len(returns)

        if combo_averages:
            best_return = max(combo_averages.values())
            current_return = combo_averages.get('20/80', 0)

            if current_return == best_return:
                optimal_count += 1
            elif best_return - current_return < 3:
                near_optimal_count += 1

    cprint(f"\n📊 Parameter Robustness:", "white")
    cprint(f"  ├─ 20/80 is optimal: {optimal_count}/4 pairs", "green" if optimal_count >= 2 else "white")
    cprint(f"  ├─ 20/80 is near-optimal (<3% diff): {near_optimal_count}/4 pairs", "white")
    cprint(f"  └─ Total robust: {optimal_count + near_optimal_count}/4 pairs", "green" if optimal_count + near_optimal_count >= 3 else "yellow")

    # Final verdict
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🎯 FINAL VERDICT", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if optimal_count >= 3:
        cprint(f"\n🎉 EXCELLENT! RSI(20/80) is optimal or near-optimal!", "green", attrs=["bold"])
        cprint(f"   No parameter overfitting detected", "green")
        cprint(f"   Strategy is robust across parameter space", "green")
        cprint(f"   ✅ Safe to deploy with 20/80 parameters", "green")
    elif optimal_count + near_optimal_count >= 3:
        cprint(f"\n✅ GOOD! RSI(20/80) is in the optimal range", "green")
        cprint(f"   Parameters are robust (not overfit)", "white")
        cprint(f"   Small adjustments don't significantly change results", "white")
        cprint(f"   ✅ Safe to deploy with 20/80 parameters", "green")
    elif optimal_count + near_optimal_count >= 2:
        cprint(f"\n⚠️  MODERATE: RSI(20/80) works but may not be optimal", "yellow")
        cprint(f"   Consider testing the best parameters found", "white")
        cprint(f"   ⚠️  Review best combinations before deploying", "yellow")
    else:
        cprint(f"\n🔴 WARNING: Parameter sensitivity detected!", "red")
        cprint(f"   20/80 may be suboptimal for most pairs", "red")
        cprint(f"   🔴 Consider optimizing parameters before live trading", "red")

    return all_results

if __name__ == "__main__":
    try:
        results = parameter_sweep()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Test interrupted", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
