#!/usr/bin/env python3
"""
🌙 RSI(25/85) Validation
Test if the improved parameters are truly robust across all 3 periods
Compare RSI(25/85) vs RSI(20/80) baseline
"""

import pandas as pd
import pandas_ta as ta
from pathlib import Path
from termcolor import cprint
from backtesting import Backtest, Strategy

# Data directories
PERIOD1_DIR = Path("/home/titus/Dropbox/user_data/data/binance")  # Jul-Oct 5m
PERIOD2_DIR = Path("/home/titus/Dropbox/user_data/data/binance_walkforward")  # Apr-Jun 5m
PERIOD3_DIR = Path("/home/titus/Dropbox/user_data/data/binance_15m_validation")  # Apr-Jul 15m

# Top 4 pairs
TOP_PAIRS = ['PENDLE_USDT', 'BCH_USDT', 'BNB_USDT', 'QTUM_USDT']

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
            'avg_trade': results['Avg. Trade [%]'],
        }
    except Exception as e:
        return None

def validate_25_85():
    """Validate RSI(25/85) across all periods"""

    cprint("\n🌙 RSI(25/85) Validation Test", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    cprint(f"\n🎯 Objective: Validate if RSI(25/85) is truly superior to RSI(20/80)", "yellow")
    cprint(f"  Testing on 4 pairs × 3 periods = 12 validation tests\n", "white")

    cprint(f"📊 Parameters:", "white")
    cprint(f"  Baseline: RSI(20/80) ← Our original validated strategy", "cyan")
    cprint(f"  Candidate: RSI(25/85) ← Parameter sweep winner", "green")

    # Store results
    all_results = {
        'baseline': {},  # RSI(20/80)
        'candidate': {}   # RSI(25/85)
    }

    periods = [
        ('Period 1 (Jul-Oct 5m)', PERIOD1_DIR, '5m'),
        ('Period 2 (Apr-Jun 5m)', PERIOD2_DIR, '5m'),
        ('Period 3 (Apr-Jul 15m)', PERIOD3_DIR, '15m')
    ]

    # Run backtests
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🔬 Running Validation Tests...\n", "cyan")

    for pair in TOP_PAIRS:
        cprint(f"\n📈 {pair}", "yellow", attrs=["bold"])

        all_results['baseline'][pair] = {}
        all_results['candidate'][pair] = {}

        for period_name, data_dir, timeframe in periods:
            file_path = data_dir / f"{pair}-{timeframe}.feather"

            if not file_path.exists():
                cprint(f"  ⚠️  {period_name}: Missing data", "yellow")
                continue

            df = load_data(file_path)

            # Test baseline (20/80)
            baseline_result = run_backtest(df, 20, 80)

            # Test candidate (25/85)
            candidate_result = run_backtest(df, 25, 85)

            if baseline_result and candidate_result:
                all_results['baseline'][pair][period_name] = baseline_result
                all_results['candidate'][pair][period_name] = candidate_result

                baseline_ret = baseline_result['return']
                candidate_ret = candidate_result['return']
                improvement = candidate_ret - baseline_ret

                # Determine color
                if improvement > 5:
                    color = "green"
                    status = "✅"
                elif improvement > 0:
                    color = "white"
                    status = "⚪"
                elif improvement > -5:
                    color = "yellow"
                    status = "⚠️ "
                else:
                    color = "red"
                    status = "❌"

                cprint(f"  {period_name}:", "white")
                cprint(f"    20/80: {baseline_ret:+6.2f}% | 25/85: {candidate_ret:+6.2f}% | "
                       f"{status} Δ {improvement:+.2f}%", color)

    # Analysis
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📊 VALIDATION ANALYSIS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    # Calculate improvement for each pair
    pair_improvements = {}

    for pair in TOP_PAIRS:
        if pair not in all_results['baseline'] or pair not in all_results['candidate']:
            continue

        baseline_returns = []
        candidate_returns = []

        for period in all_results['baseline'][pair]:
            if period in all_results['candidate'][pair]:
                baseline_returns.append(all_results['baseline'][pair][period]['return'])
                candidate_returns.append(all_results['candidate'][pair][period]['return'])

        if baseline_returns and candidate_returns:
            avg_baseline = sum(baseline_returns) / len(baseline_returns)
            avg_candidate = sum(candidate_returns) / len(candidate_returns)
            improvement = avg_candidate - avg_baseline

            pair_improvements[pair] = {
                'baseline': avg_baseline,
                'candidate': avg_candidate,
                'improvement': improvement,
                'improvement_pct': (improvement / abs(avg_baseline) * 100) if avg_baseline != 0 else 0
            }

    # Display summary
    cprint(f"\n💰 Performance Summary:\n", "white")

    for pair in TOP_PAIRS:
        if pair not in pair_improvements:
            continue

        data = pair_improvements[pair]
        baseline = data['baseline']
        candidate = data['candidate']
        improvement = data['improvement']
        improvement_pct = data['improvement_pct']

        color = "green" if improvement > 5 else "white" if improvement > 0 else "red"

        cprint(f"  {pair:15}", "yellow", attrs=["bold"])
        cprint(f"    20/80: {baseline:+6.2f}%", "cyan")
        cprint(f"    25/85: {candidate:+6.2f}% ({improvement:+.2f}% / {improvement_pct:+.1f}%)", color)

    # Overall statistics
    if pair_improvements:
        avg_baseline = sum(p['baseline'] for p in pair_improvements.values()) / len(pair_improvements)
        avg_candidate = sum(p['candidate'] for p in pair_improvements.values()) / len(pair_improvements)
        avg_improvement = avg_candidate - avg_baseline
        avg_improvement_pct = (avg_improvement / abs(avg_baseline) * 100) if avg_baseline != 0 else 0

        cprint(f"\n{'='*90}", "cyan")
        cprint(f"📈 OVERALL RESULTS", "cyan", attrs=["bold"])
        cprint(f"{'='*90}", "cyan")

        cprint(f"\n  Average Performance Across All Pairs & Periods:", "white")
        cprint(f"    RSI(20/80): {avg_baseline:+6.2f}%", "cyan")
        cprint(f"    RSI(25/85): {avg_candidate:+6.2f}%", "green" if avg_improvement > 0 else "red")
        cprint(f"    Improvement: {avg_improvement:+6.2f}% ({avg_improvement_pct:+.1f}%)",
               "green" if avg_improvement > 0 else "red")

        # Count improvements
        better_count = sum(1 for p in pair_improvements.values() if p['improvement'] > 0)
        worse_count = sum(1 for p in pair_improvements.values() if p['improvement'] < 0)

        cprint(f"\n  Consistency Check:", "white")
        cprint(f"    Better: {better_count}/4 pairs", "green" if better_count >= 3 else "white")
        cprint(f"    Worse: {worse_count}/4 pairs", "red" if worse_count >= 2 else "white")

    # Final verdict
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"⚖️  FINAL VERDICT", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if avg_improvement > 5 and better_count >= 3:
        cprint(f"\n🎉 VALIDATION PASSED! RSI(25/85) is SUPERIOR!", "green", attrs=["bold"])
        cprint(f"   ✅ {avg_improvement:+.2f}% average improvement", "green")
        cprint(f"   ✅ Better on {better_count}/4 pairs consistently", "green")
        cprint(f"   ✅ Improvement is robust across periods", "green")
        cprint(f"\n   Recommendation: Deploy RSI(25/85) for live trading", "green", attrs=["bold"])

    elif avg_improvement > 0 and better_count >= 3:
        cprint(f"\n✅ VALIDATION PASSED! RSI(25/85) is better overall", "green")
        cprint(f"   {avg_improvement:+.2f}% average improvement", "white")
        cprint(f"   Better on {better_count}/4 pairs", "white")
        cprint(f"\n   Recommendation: Use RSI(25/85) - modest but consistent improvement", "green")

    elif better_count == 2 and worse_count == 2:
        cprint(f"\n⚠️  MIXED RESULTS: No clear winner", "yellow")
        cprint(f"   Both parameters work, but for different pairs", "white")
        cprint(f"\n   Options:", "yellow")
        cprint(f"   A. Use RSI(20/80) - safer, already validated", "white")
        cprint(f"   B. Use RSI(25/85) - higher potential, but mixed", "white")
        cprint(f"   C. Use asset-specific parameters for maximum returns", "white")

    else:
        cprint(f"\n❌ VALIDATION FAILED: RSI(25/85) is NOT better", "red")
        cprint(f"   {avg_improvement:+.2f}% average change", "white")
        cprint(f"   Worse on {worse_count}/4 pairs", "red")
        cprint(f"\n   Recommendation: Stick with RSI(20/80) - parameter sweep was misleading", "red")

    # Show best performing setup
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🏆 TOP PERFORMERS", "green", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if pair_improvements:
        sorted_pairs = sorted(pair_improvements.items(), key=lambda x: x[1]['candidate'], reverse=True)

        for i, (pair, data) in enumerate(sorted_pairs, 1):
            cprint(f"\n{i}. {pair}", "green", attrs=["bold"])
            cprint(f"   RSI(20/80): {data['baseline']:+6.2f}%", "cyan")
            cprint(f"   RSI(25/85): {data['candidate']:+6.2f}%", "green" if data['improvement'] > 0 else "red")
            cprint(f"   Impact: {data['improvement']:+.2f}% ({data['improvement_pct']:+.1f}%)",
                   "green" if data['improvement'] > 0 else "red")

    return all_results, pair_improvements

if __name__ == "__main__":
    try:
        results, improvements = validate_25_85()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Test interrupted", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
