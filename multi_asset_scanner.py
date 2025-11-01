#!/usr/bin/env python3
"""
🌙 Moon Dev's Multi-Asset Market Scanner
Find which coins were in uptrends, downtrends, or sideways
Then match the right strategy to each!
"""

import pandas as pd
import pandas_ta as ta
from pathlib import Path
from termcolor import cprint
from backtesting import Backtest, Strategy

DATA_DIR = Path("/home/titus/Dropbox/user_data/data/binance")

# Simple RSI Strategy (best mean-reversion we found)
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

def analyze_market_condition(df):
    """Determine if market was uptrend, downtrend, or sideways"""
    start_price = df['Close'].iloc[0]
    end_price = df['Close'].iloc[-1]
    pct_change = ((end_price / start_price) - 1) * 100

    # Calculate volatility (how much it moved)
    returns = df['Close'].pct_change()
    volatility = returns.std() * 100

    # Classify market
    if pct_change > 15:
        condition = "UPTREND"
        color = "green"
        suggested_strategy = "Trend-Following"
    elif pct_change < -15:
        condition = "DOWNTREND"
        color = "red"
        suggested_strategy = "Short or Avoid"
    else:
        condition = "SIDEWAYS"
        color = "yellow"
        suggested_strategy = "Mean-Reversion"

    return {
        'condition': condition,
        'pct_change': pct_change,
        'volatility': volatility,
        'color': color,
        'suggested_strategy': suggested_strategy,
        'start_price': start_price,
        'end_price': end_price
    }

def quick_backtest(df, strategy_class):
    """Run a quick backtest"""
    try:
        bt = Backtest(df, strategy_class, cash=10000, commission=.002)
        results = bt.run()
        return {
            'return': results['Return [%]'],
            'trades': results['# Trades'],
            'win_rate': results['Win Rate [%]']
        }
    except Exception as e:
        return {'return': None, 'trades': 0, 'win_rate': 0}

def scan_all_assets(timeframe='5m', max_assets=20):
    """Scan multiple assets and find the best opportunities"""

    cprint("\n🌙 Moon Dev's Multi-Asset Market Scanner", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    files = list(DATA_DIR.glob(f"*-{timeframe}.feather"))
    files = files[:max_assets]  # Limit for speed

    cprint(f"\n📊 Scanning {len(files)} assets on {timeframe} timeframe...", "white")

    results = []

    for i, file in enumerate(files, 1):
        pair = file.stem.replace(f'-{timeframe}', '')

        try:
            # Load data
            df = pd.read_feather(file)
            df = df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            df = df.set_index('date')

            # Analyze market condition
            market = analyze_market_condition(df)

            # Quick backtest with RSI 20/80
            backtest = quick_backtest(df, RSIStrategy)

            result = {
                'pair': pair,
                'condition': market['condition'],
                'pct_change': market['pct_change'],
                'suggested': market['suggested_strategy'],
                'strategy_return': backtest['return'],
                'trades': backtest['trades'],
                'win_rate': backtest['win_rate'],
                'buy_hold': market['pct_change'],
                'start_price': market['start_price'],
                'end_price': market['end_price']
            }

            results.append(result)

            # Progress
            status = f"✓" if backtest['return'] and backtest['return'] > 0 else "✗"
            cprint(f"  [{i:2d}/{len(files)}] {status} {pair:15} {market['condition']:10} {market['pct_change']:+7.2f}%", market['color'])

        except Exception as e:
            cprint(f"  [{i:2d}/{len(files)}] ✗ {pair:15} ERROR: {str(e)[:30]}", "red")

    # Sort and display results
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📊 ANALYSIS COMPLETE", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    # Group by market condition
    uptrends = [r for r in results if r['condition'] == 'UPTREND']
    downtrends = [r for r in results if r['condition'] == 'DOWNTREND']
    sideways = [r for r in results if r['condition'] == 'SIDEWAYS']

    cprint(f"\n📈 Market Conditions Found:", "white")
    cprint(f"  ├─ Uptrends: {len(uptrends)} assets", "green")
    cprint(f"  ├─ Downtrends: {len(downtrends)} assets", "red")
    cprint(f"  └─ Sideways: {len(sideways)} assets", "yellow")

    # Find profitable strategies
    profitable = [r for r in results if r['strategy_return'] and r['strategy_return'] > 0]

    if profitable:
        profitable.sort(key=lambda x: x['strategy_return'], reverse=True)

        cprint(f"\n🎉 PROFITABLE STRATEGIES FOUND! ({len(profitable)} assets)", "green", attrs=["bold"])
        cprint(f"{'='*90}", "green")

        for i, r in enumerate(profitable[:10], 1):  # Top 10
            cprint(f"\n{i}. {r['pair']}", "yellow", attrs=["bold"])
            cprint(f"   Market: {r['condition']} ({r['pct_change']:+.2f}%)", "white")
            cprint(f"   RSI 20/80 Return: {r['strategy_return']:.2f}%", "green")
            cprint(f"   Trades: {r['trades']} | Win Rate: {r['win_rate']:.1f}%", "white")
            cprint(f"   Price: ${r['start_price']:.4f} → ${r['end_price']:.4f}", "white")

    else:
        cprint(f"\n⚠️ No profitable strategies found with RSI 20/80", "yellow")
        cprint(f"   This means mean-reversion didn't work well in this period", "white")

    # Best sideways market for mean-reversion
    if sideways:
        sideways.sort(key=lambda x: abs(x['pct_change']))
        cprint(f"\n💡 BEST SIDEWAYS MARKETS (for mean-reversion):", "cyan")
        for r in sideways[:5]:
            cprint(f"  ├─ {r['pair']:15} Change: {r['pct_change']:+6.2f}%", "yellow")

    # Best uptrends (if you want to test trend-following)
    if uptrends:
        uptrends.sort(key=lambda x: x['pct_change'], reverse=True)
        cprint(f"\n🚀 STRONGEST UPTRENDS (test trend-following here):", "cyan")
        for r in uptrends[:5]:
            cprint(f"  ├─ {r['pair']:15} Change: {r['pct_change']:+6.2f}%", "green")

    cprint(f"\n{'='*90}", "cyan")
    cprint(f"💡 Next Steps:", "yellow")
    cprint(f"  1. Test trend-following on strong uptrends above", "white")
    cprint(f"  2. Test mean-reversion on sideways markets", "white")
    cprint(f"  3. Avoid downtrends (or learn short selling)", "white")
    cprint(f"  4. Focus on assets where RSI 20/80 was profitable!", "white")

    return results

if __name__ == "__main__":
    try:
        results = scan_all_assets(timeframe='5m', max_assets=30)  # Scan 30 pairs
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Scan interrupted", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
