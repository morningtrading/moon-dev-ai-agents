#!/usr/bin/env python3
"""
🌙 Moon Dev's Binance Data Backtest
Uses your real Binance OHLC data for backtesting
"""

from backtesting import Strategy, Backtest
import pandas as pd
import pandas_ta as ta
from termcolor import cprint
from pathlib import Path

# RSI Strategy (same as before)
class RSIStrategy(Strategy):
    rsi_period = 14
    oversold = 30
    overbought = 70

    def init(self):
        close = pd.Series(self.data.Close)
        self.rsi = self.I(ta.rsi, close, length=self.rsi_period)

    def next(self):
        if self.rsi[-1] < self.oversold and not self.position:
            self.buy()
        elif self.rsi[-1] > self.overbought and self.position:
            self.position.close()

def backtest_pair(pair_name, timeframe='5m'):
    """Backtest a trading pair"""

    cprint(f"\n{'='*70}", "cyan")
    cprint(f"🌙 Backtesting {pair_name} ({timeframe})", "cyan", attrs=["bold"])
    cprint(f"{'='*70}", "cyan")

    # Load data
    data_file = Path(f"/home/titus/Dropbox/user_data/data/binance/{pair_name}-{timeframe}.feather")

    if not data_file.exists():
        cprint(f"❌ Data file not found: {data_file}", "red")
        return None

    df = pd.read_feather(data_file)

    # Prepare for backtesting.py
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    df = df.set_index('date')

    cprint(f"\n📊 Data loaded:", "white")
    cprint(f"  ├─ Rows: {len(df):,}", "white")
    cprint(f"  ├─ From: {df.index[0]}", "white")
    cprint(f"  ├─ To: {df.index[-1]}", "white")
    cprint(f"  ├─ First price: ${df['Close'].iloc[0]:,.2f}", "white")
    cprint(f"  └─ Last price: ${df['Close'].iloc[-1]:,.2f}", "white")

    # Run backtest
    cprint(f"\n🚀 Running RSI backtest...", "cyan")
    cprint(f"  ├─ Strategy: Buy RSI<30, Sell RSI>70", "white")
    cprint(f"  ├─ Starting cash: $10,000", "white")
    cprint(f"  └─ Commission: 0.2%", "white")

    bt = Backtest(df, RSIStrategy, cash=10000, commission=.002)
    results = bt.run()

    # Display results
    cprint(f"\n📊 Results", "cyan", attrs=["bold"])
    cprint("=" * 70, "cyan")

    metrics = {
        "Return": results['Return [%]'],
        "Buy & Hold Return": results['Buy & Hold Return [%]'],
        "Sharpe Ratio": results['Sharpe Ratio'],
        "Max Drawdown": results['Max. Drawdown [%]'],
        "Number of Trades": results['# Trades'],
        "Win Rate": results['Win Rate [%]'],
        "Final Equity": results['Equity Final [$]']
    }

    for key, value in metrics.items():
        if isinstance(value, float):
            if 'Return' in key or 'Drawdown' in key or 'Win Rate' in key:
                formatted = f"{value:.2f}%"
            elif 'Equity' in key:
                formatted = f"${value:,.2f}"
            else:
                formatted = f"{value:.2f}"
        else:
            formatted = str(value)

        color = "green" if "Return" in key and value > 0 else "white"
        cprint(f"  {key:20} {formatted}", color)

    # Verdict
    strategy_return = results['Return [%]']
    buy_hold_return = results['Buy & Hold Return [%]']

    cprint(f"\n{'=' * 70}", "cyan")

    if strategy_return > buy_hold_return and strategy_return > 0:
        cprint(f"🎉 Strategy OUTPERFORMED buy & hold! (+{strategy_return - buy_hold_return:.2f}%)", "green", attrs=["bold"])
    elif strategy_return > 0:
        cprint(f"✅ Strategy profitable but underperformed buy & hold", "yellow")
    else:
        cprint(f"❌ Strategy lost money ({strategy_return:.2f}%)", "red")

    return results

if __name__ == "__main__":
    cprint("\n🌙 Moon Dev's Binance Data Backtester", "cyan", attrs=["bold"])
    cprint("Testing RSI strategy on your Binance data", "cyan")

    # Test on ETH (cheaper than BTC, no margin issues)
    backtest_pair("ETH_USDT", timeframe="5m")

    cprint(f"\n💡 Try other pairs:", "yellow")
    cprint(f"  python backtest_with_binance_data.py", "white")
    cprint(f"  - Edit the pair name to test DOGE_USDT, SOL_USDT, etc.", "white")
