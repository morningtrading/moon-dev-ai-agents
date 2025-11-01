#!/usr/bin/env python3
"""
🌙 Moon Dev's Backtest Executor
Runs the AI-generated strategy on BTC data
"""

from backtesting import Strategy, Backtest
import pandas as pd
import pandas_ta as ta
from termcolor import cprint
from pathlib import Path

# RSI Strategy (AI-generated)
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

if __name__ == "__main__":
    cprint("\n🌙 Moon Dev's RSI Backtest Executor", "cyan", attrs=["bold"])
    cprint("=" * 70, "cyan")

    # Load BTC data
    data_file = Path("src/data/rbi/BTC-USD-15m.csv")

    cprint(f"\n📊 Loading data: {data_file}", "cyan")
    df = pd.read_csv(data_file)

    # Prepare data for backtesting.py
    df['datetime'] = pd.to_datetime(df['datetime'].str.strip())
    df = df.rename(columns={
        ' open': 'Open',
        ' high': 'High',
        ' low': 'Low',
        ' close': 'Close',
        ' volume': 'Volume'
    })
    df = df[['datetime', 'Open', 'High', 'Low', 'Close', 'Volume']]
    df = df.set_index('datetime')

    cprint(f"✅ Loaded {len(df)} candles", "green")
    cprint(f"  ├─ From: {df.index[0]}", "white")
    cprint(f"  └─ To: {df.index[-1]}", "white")

    # Run backtest
    cprint(f"\n🚀 Running RSI backtest...", "cyan")
    cprint(f"  ├─ Strategy: Buy RSI<30, Sell RSI>70", "white")
    cprint(f"  ├─ Starting cash: $10,000", "white")
    cprint(f"  └─ Commission: 0.2%", "white")

    bt = Backtest(df, RSIStrategy, cash=10000, commission=.002)
    results = bt.run()

    # Display results
    cprint(f"\n📊 Backtest Results", "cyan", attrs=["bold"])
    cprint("=" * 70, "cyan")

    metrics = {
        "Return": f"{results['Return [%]']:.2f}%",
        "Buy & Hold Return": f"{results['Buy & Hold Return [%]']:.2f}%",
        "Sharpe Ratio": f"{results['Sharpe Ratio']:.2f}",
        "Sortino Ratio": f"{results['Sortino Ratio']:.2f}",
        "Max Drawdown": f"{results['Max. Drawdown [%]']:.2f}%",
        "Number of Trades": f"{results['# Trades']}",
        "Win Rate": f"{results['Win Rate [%]']:.2f}%",
        "Profit Factor": f"{results['Profit Factor']:.2f}",
        "Avg Trade": f"{results['Avg. Trade [%]']:.2f}%",
        "Final Equity": f"${results['Equity Final [$]']:,.2f}"
    }

    for key, value in metrics.items():
        color = "green" if "Return" in key and "%" in value and float(value.replace('%','')) > 0 else "white"
        cprint(f"  {key:20} {value}", color)

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

    cprint(f"\n💡 Note: This is historical data. Past performance ≠ future results!", "yellow")
    cprint(f"📌 Try more strategies with: python run_simple_backtest.py", "cyan")
