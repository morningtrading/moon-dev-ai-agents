#!/usr/bin/env python3
"""
🌙 Robust NEAR Analysis
Filter for strategies with ENOUGH trades (minimum 1 per week)
Focus on statistical significance, not lucky outliers
"""

import pandas as pd
import pandas_ta as ta
from pathlib import Path
from termcolor import cprint
from backtesting import Backtest, Strategy

DATA_FILE = Path("/home/titus/Dropbox/user_data/data/binance/NEAR_USDT-5m.feather")

class RSIStrategy(Strategy):
    rsi_period = 14
    oversold = 20
    overbought = 80

    def init(self):
        close = pd.Series(self.data.Close)
        self.rsi = self.I(ta.rsi, close, length=self.rsi_period)

    def next(self):
        if self.rsi[-1] < self.oversold and not self.position:
            self.buy()
        elif self.rsi[-1] > self.overbought and self.position:
            self.position.close()

def run_backtest(df, params):
    """Run single backtest"""
    try:
        bt = Backtest(df, RSIStrategy, cash=10000, commission=.002)
        results = bt.run(**params)
        return {
            'params': params,
            'return': results['Return [%]'],
            'sharpe': results['Sharpe Ratio'],
            'max_dd': results['Max. Drawdown [%]'],
            'trades': results['# Trades'],
            'win_rate': results['Win Rate [%]'],
            'avg_trade': results['Avg. Trade [%]'],
            'best_trade': results['Best Trade [%]'],
            'worst_trade': results['Worst Trade [%]'],
            'final_equity': results['Equity Final [$]']
        }
    except:
        return None

def analyze_robust_strategies():
    """Find strategies with enough trades for statistical significance"""

    cprint("\n🌙 NEAR Robust Analysis: Statistical Significance", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    # Load data
    df = pd.read_feather(DATA_FILE)
    df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    df = df.set_index('date')

    # Calculate time period
    days = (df.index[-1] - df.index[0]).days
    weeks = days / 7

    cprint(f"\n📊 Data Period:", "white")
    cprint(f"  ├─ Days: {days}", "white")
    cprint(f"  ├─ Weeks: {weeks:.1f}", "white")
    cprint(f"  └─ Minimum Trades Needed: {int(weeks)} (1 per week)", "yellow")

    min_trades = int(weeks)

    # Test parameter combinations
    cprint(f"\n🔍 Testing with minimum {min_trades} trades requirement...", "cyan")

    rsi_periods = [7, 10, 14, 21]
    oversold_levels = [15, 20, 25, 30]
    overbought_levels = [70, 75, 80, 85]

    results = []
    for rsi_period in rsi_periods:
        for oversold in oversold_levels:
            for overbought in overbought_levels:
                if overbought - oversold < 30:
                    continue

                params = {'rsi_period': rsi_period, 'oversold': oversold, 'overbought': overbought}
                result = run_backtest(df, params)

                if result and result['trades'] >= min_trades:  # FILTER: Enough trades!
                    results.append(result)

    cprint(f"  └─ Found {len(results)} strategies with {min_trades}+ trades\n", "green")

    # Sort by return
    results.sort(key=lambda x: x['return'], reverse=True)

    # Display robust results
    cprint(f"{'='*90}", "cyan")
    cprint(f"🏆 TOP ROBUST STRATEGIES (statistically significant)", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if not results:
        cprint(f"\n⚠️ No strategies met the minimum trade requirement!", "red")
        return

    for i, result in enumerate(results[:10], 1):
        p = result['params']
        ret = result['return']

        color = "green" if ret > 20 else "yellow" if ret > 10 else "white"

        cprint(f"\n{i}. RSI({p['rsi_period']}) Oversold:{p['oversold']} Overbought:{p['overbought']}",
               color, attrs=["bold"])
        cprint(f"   Return: {ret:.2f}% | Sharpe: {result['sharpe']:.2f} | Max DD: {result['max_dd']:.2f}%", "white")
        cprint(f"   Trades: {result['trades']} ({result['trades']/weeks:.1f} per week) | Win Rate: {result['win_rate']:.1f}%", "white")
        cprint(f"   Avg Trade: {result['avg_trade']:.2f}% | Best: {result['best_trade']:.2f}% | Worst: {result['worst_trade']:.2f}%", "white")

    # Best robust strategy
    best = results[0]
    p = best['params']

    cprint(f"\n{'='*90}", "cyan")
    cprint(f"✅ BEST STATISTICALLY SIGNIFICANT STRATEGY", "green", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    cprint(f"\nParameters: RSI({p['rsi_period']}) Oversold:{p['oversold']} Overbought:{p['overbought']}", "yellow", attrs=["bold"])

    cprint(f"\n📊 Performance Metrics:", "white")
    cprint(f"  ├─ Return: {best['return']:.2f}%", "green")
    cprint(f"  ├─ Sharpe Ratio: {best['sharpe']:.2f}", "white")
    cprint(f"  ├─ Max Drawdown: {best['max_dd']:.2f}%", "white")
    cprint(f"  ├─ Final Equity: ${best['final_equity']:,.2f}", "green")

    cprint(f"\n📈 Trade Statistics (IMPORTANT!):", "white")
    cprint(f"  ├─ Total Trades: {best['trades']}", "white")
    cprint(f"  ├─ Trades per Week: {best['trades']/weeks:.2f}", "green" if best['trades']/weeks >= 1 else "yellow")
    cprint(f"  ├─ Win Rate: {best['win_rate']:.1f}%", "green" if best['win_rate'] > 60 else "white")
    cprint(f"  ├─ Avg Trade: {best['avg_trade']:.2f}%", "white")
    cprint(f"  ├─ Best Trade: {best['best_trade']:.2f}%", "white")
    cprint(f"  └─ Worst Trade: {best['worst_trade']:.2f}%", "white")

    cprint(f"\n💡 WHY THIS IS BETTER:", "yellow", attrs=["bold"])
    cprint(f"\n  1. Sample Size: {best['trades']} trades vs 2 trades (luck)", "white")
    cprint(f"     └─ {best['trades']} trades is statistically meaningful!", "white")

    cprint(f"\n  2. Consistent Activity: {best['trades']/weeks:.2f} trades/week", "white")
    cprint(f"     └─ Regular signals, not waiting months for a trade", "white")

    cprint(f"\n  3. Win Rate: {best['win_rate']:.1f}%", "white")
    cprint(f"     └─ Proven over many trades, not just 2 lucky ones", "white")

    cprint(f"\n  4. Risk Management: See best/worst trades", "white")
    cprint(f"     └─ You know what to expect in wins AND losses", "white")

    # Compare to lucky strategy
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"⚠️  COMPARISON: Robust vs Lucky Strategy", "yellow", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    cprint(f"\nLucky Strategy (RSI 21, 15/80):", "red")
    cprint(f"  ├─ Return: 97.71% (looks amazing!)", "white")
    cprint(f"  ├─ Trades: 2 (way too few)", "red")
    cprint(f"  └─ Problem: Could be pure luck, won't repeat", "red")

    cprint(f"\nRobust Strategy (RSI {p['rsi_period']}, {p['oversold']}/{p['overbought']}):", "green")
    cprint(f"  ├─ Return: {best['return']:.2f}% (realistic)", "white")
    cprint(f"  ├─ Trades: {best['trades']} (statistically valid)", "green")
    cprint(f"  └─ Confidence: Much higher chance of repeating", "green")

    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🎯 NEXT STEPS:", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    cprint(f"\n✅ Use RSI({p['rsi_period']}) {p['oversold']}/{p['overbought']} for NEAR", "green")
    cprint(f"✅ Test this on your other 8 profitable assets", "white")
    cprint(f"✅ Require minimum {min_trades} trades on all backtests", "white")
    cprint(f"✅ Never trust strategies with <10 trades", "yellow")

    return results

if __name__ == "__main__":
    try:
        analyze_robust_strategies()
    except Exception as e:
        cprint(f"\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
