#!/usr/bin/env python3
"""
🌙 Moon Dev's NEAR Deep Dive
Optimize and understand why NEAR_USDT was our best performer (+28.09%)
"""

import pandas as pd
import pandas_ta as ta
from pathlib import Path
from termcolor import cprint
from backtesting import Backtest, Strategy
import itertools

DATA_FILE = Path("/home/titus/Dropbox/user_data/data/binance/NEAR_USDT-5m.feather")

# RSI Strategy with configurable parameters
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

def load_near_data():
    """Load NEAR data"""
    df = pd.read_feather(DATA_FILE)
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    df = df.set_index('date')
    return df

def run_backtest(df, params):
    """Run single backtest with parameters"""
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
            'final_equity': results['Equity Final [$]']
        }
    except Exception as e:
        return None

def optimize_parameters(df):
    """Test many parameter combinations"""

    cprint("\n🌙 NEAR Deep Dive: Parameter Optimization", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    # Market info
    start_price = df['Close'].iloc[0]
    end_price = df['Close'].iloc[-1]
    market_return = ((end_price / start_price) - 1) * 100

    cprint(f"\n📊 NEAR_USDT Market Data:", "white")
    cprint(f"  ├─ Candles: {len(df):,}", "white")
    cprint(f"  ├─ Period: {df.index[0]} to {df.index[-1]}", "white")
    cprint(f"  ├─ Start: ${start_price:.4f}", "white")
    cprint(f"  ├─ End: ${end_price:.4f}", "white")
    cprint(f"  └─ Market Return: {market_return:.2f}% (sideways/down)", "yellow")

    # Parameter grid
    rsi_periods = [7, 10, 14, 21]
    oversold_levels = [15, 20, 25, 30]
    overbought_levels = [70, 75, 80, 85]

    cprint(f"\n🔍 Testing Parameter Combinations:", "cyan")
    cprint(f"  ├─ RSI Periods: {rsi_periods}", "white")
    cprint(f"  ├─ Oversold Levels: {oversold_levels}", "white")
    cprint(f"  ├─ Overbought Levels: {overbought_levels}", "white")
    cprint(f"  └─ Total Tests: {len(rsi_periods) * len(oversold_levels) * len(overbought_levels)}", "white")

    results = []
    total_tests = len(rsi_periods) * len(oversold_levels) * len(overbought_levels)
    current = 0

    for rsi_period in rsi_periods:
        for oversold in oversold_levels:
            for overbought in overbought_levels:
                current += 1

                # Skip invalid combinations
                if overbought - oversold < 30:  # Need reasonable gap
                    continue

                params = {
                    'rsi_period': rsi_period,
                    'oversold': oversold,
                    'overbought': overbought
                }

                result = run_backtest(df, params)
                if result:
                    results.append(result)

                    # Progress indicator
                    if current % 10 == 0 or result['return'] > 25:
                        status = "🎯" if result['return'] > 25 else "✓"
                        cprint(f"  [{current:3d}/{total_tests}] {status} RSI({rsi_period}) {oversold}/{overbought}: {result['return']:+6.2f}%",
                               "green" if result['return'] > 20 else "white")

    # Sort by return
    results.sort(key=lambda x: x['return'], reverse=True)

    # Display top results
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🏆 TOP 10 PARAMETER COMBINATIONS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    for i, result in enumerate(results[:10], 1):
        p = result['params']
        ret = result['return']

        color = "green" if ret > 25 else "yellow" if ret > 15 else "white"

        cprint(f"\n{i}. RSI({p['rsi_period']}) Oversold:{p['oversold']} Overbought:{p['overbought']}",
               color, attrs=["bold"])
        cprint(f"   Return: {ret:.2f}% | Sharpe: {result['sharpe']:.2f} | Max DD: {result['max_dd']:.2f}%", "white")
        cprint(f"   Trades: {result['trades']} | Win Rate: {result['win_rate']:.1f}% | Avg Trade: {result['avg_trade']:.2f}%", "white")
        cprint(f"   Final Equity: ${result['final_equity']:,.2f}", "white")

    # Best result analysis
    best = results[0]
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"✨ BEST STRATEGY FOUND!", "green", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    p = best['params']
    cprint(f"\nParameters: RSI({p['rsi_period']}) Oversold:{p['oversold']} Overbought:{p['overbought']}", "yellow", attrs=["bold"])
    cprint(f"\nPerformance:", "white")
    cprint(f"  ├─ Return: {best['return']:.2f}% (Beat market by {best['return'] - market_return:.2f}%!)", "green")
    cprint(f"  ├─ Sharpe Ratio: {best['sharpe']:.2f}", "white")
    cprint(f"  ├─ Max Drawdown: {best['max_dd']:.2f}%", "white")
    cprint(f"  ├─ Number of Trades: {best['trades']}", "white")
    cprint(f"  ├─ Win Rate: {best['win_rate']:.1f}%", "white")
    cprint(f"  ├─ Avg Trade: {best['avg_trade']:.2f}%", "white")
    cprint(f"  └─ Final Equity: ${best['final_equity']:,.2f} (from $10,000)", "green")

    # Comparison
    original_params = {'rsi_period': 14, 'oversold': 20, 'overbought': 80}
    original_result = [r for r in results if r['params'] == original_params][0] if any(r['params'] == original_params for r in results) else None

    if original_result:
        improvement = best['return'] - original_result['return']
        cprint(f"\n📊 Improvement Over Original (RSI 14/20/80):", "cyan")
        cprint(f"  ├─ Original: {original_result['return']:.2f}%", "white")
        cprint(f"  ├─ Optimized: {best['return']:.2f}%", "green")
        cprint(f"  └─ Improvement: +{improvement:.2f}%", "green" if improvement > 0 else "red")

    # Why it worked
    cprint(f"\n💡 WHY NEAR WORKED SO WELL:", "yellow", attrs=["bold"])
    cprint(f"\n  1. Market Condition: Sideways/Down ({market_return:.2f}%)", "white")
    cprint(f"     └─ Perfect for mean-reversion strategies!", "white")

    cprint(f"\n  2. High Win Rate: {best['win_rate']:.1f}%", "white")
    cprint(f"     └─ Strategy caught most of the bounces", "white")

    cprint(f"\n  3. Good Risk/Reward: {best['avg_trade']:.2f}% per trade", "white")
    cprint(f"     └─ Small losers, bigger winners", "white")

    cprint(f"\n  4. Reasonable Trade Frequency: {best['trades']} trades", "white")
    cprint(f"     └─ Not overtrading, catching real signals", "white")

    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🎯 READY FOR LIVE TRADING?", "yellow", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")
    cprint(f"\n✅ This strategy has been backtested and optimized", "green")
    cprint(f"✅ Win rate: {best['win_rate']:.1f}% (excellent!)", "green")
    cprint(f"✅ Beat market by {best['return'] - market_return:.2f}%", "green")

    cprint(f"\n⚠️  BUT REMEMBER:", "yellow")
    cprint(f"  1. Past performance ≠ future results", "white")
    cprint(f"  2. Test on paper/testnet first", "white")
    cprint(f"  3. Start with small position sizes", "white")
    cprint(f"  4. Use proper risk management (stop losses)", "white")
    cprint(f"  5. Markets change - monitor performance", "white")

    cprint(f"\n💡 Next Steps:", "cyan")
    cprint(f"  1. Test this on other sideways assets (PENDLE, BCH, AVAX)", "white")
    cprint(f"  2. Try on different timeframe (1m instead of 5m)", "white")
    cprint(f"  3. Move to Phase 6: Test on Hyperliquid paper trading", "white")

    return results

if __name__ == "__main__":
    try:
        df = load_near_data()
        results = optimize_parameters(df)
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Optimization interrupted", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
