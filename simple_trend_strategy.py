#!/usr/bin/env python3
"""
🌙 Simple But Effective Trend Following Strategy
Uses EMA crossover - the classic trend follower
"""

import pandas as pd
import pandas_ta as ta
from backtesting import Backtest, Strategy
from pathlib import Path
from termcolor import cprint

class SimpleTrendStrategy(Strategy):
    """
    Simple EMA Crossover with momentum filter
    - Buy when fast EMA crosses above slow EMA (uptrend)
    - Sell when fast EMA crosses below slow EMA (downtrend)
    - Only trade when price is trending (above both EMAs)
    """
    fast_ema = 10
    slow_ema = 30
    momentum_ema = 100  # Long-term trend filter

    def init(self):
        close = pd.Series(self.data.Close)
        # Calculate EMAs
        self.ema_fast = self.I(ta.ema, close, length=self.fast_ema)
        self.ema_slow = self.I(ta.ema, close, length=self.slow_ema)
        self.ema_momentum = self.I(ta.ema, close, length=self.momentum_ema)

    def next(self):
        price = self.data.Close[-1]

        # Wait for all indicators to be ready
        if len(self.data) < self.momentum_ema + 10:
            return

        # Trend following logic:
        # 1. Fast EMA > Slow EMA = Uptrend
        # 2. Price > Momentum EMA = Strong uptrend
        # 3. Cross signals entry/exit

        # ENTRY: Fast crosses above slow AND price above long-term trend
        if (not self.position and
            self.ema_fast[-1] > self.ema_slow[-1] and
            self.ema_fast[-2] <= self.ema_slow[-2] and  # Just crossed
            price > self.ema_momentum[-1]):  # Above long-term trend
            self.buy()

        # EXIT: Fast crosses below slow (trend reversal)
        elif (self.position and
              (self.ema_fast[-1] < self.ema_slow[-1] or
               price < self.ema_momentum[-1])):  # Or drops below long-term trend
            self.position.close()

if __name__ == "__main__":
    cprint("\n🌙 Simple Trend Following Strategy Test", "cyan", attrs=["bold"])
    cprint("=" * 70, "cyan")

    # Load ETH data
    data_file = Path("/home/titus/Dropbox/user_data/data/binance/ETH_USDT-5m.feather")
    df = pd.read_feather(data_file)

    df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    df = df.set_index('date')

    cprint(f"\n📊 Data: ETH_USDT (5m)", "white")
    cprint(f"  ├─ Candles: {len(df):,}", "white")
    cprint(f"  ├─ Period: {df.index[0]} to {df.index[-1]}", "white")
    cprint(f"  └─ Price: ${df['Close'].iloc[0]:,.2f} → ${df['Close'].iloc[-1]:,.2f}", "white")

    buy_hold_pct = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100

    cprint(f"\n🚀 Running Simple Trend Strategy...", "cyan")
    cprint(f"  Strategy: EMA(10/30) crossover with EMA(100) filter", "white")
    cprint(f"  Logic: Buy trend confirmations, sell trend reversals", "white")

    bt = Backtest(df, SimpleTrendStrategy, cash=10000, commission=.002)
    results = bt.run()

    cprint(f"\n📊 Results", "cyan", attrs=["bold"])
    cprint("=" * 70, "cyan")

    metrics = {
        "Return": results['Return [%]'],
        "Buy & Hold": results['Buy & Hold Return [%]'],
        "Sharpe Ratio": results['Sharpe Ratio'],
        "Max Drawdown": results['Max. Drawdown [%]'],
        "Trades": results['# Trades'],
        "Win Rate": results['Win Rate [%]'],
        "Avg Trade": results['Avg. Trade [%]'],
        "Final Equity": results['Equity Final [$]']
    }

    for key, value in metrics.items():
        if isinstance(value, float):
            if 'Return' in key or 'Drawdown' in key or 'Win Rate' in key or 'Trade' in key:
                formatted = f"{value:.2f}%"
            elif 'Equity' in key:
                formatted = f"${value:,.2f}"
            else:
                formatted = f"{value:.2f}"
        else:
            formatted = str(value)

        color = "green" if ("Return" in key and value > 0) else "white"
        cprint(f"  {key:20} {formatted}", color)

    cprint(f"\n{'='*70}", "cyan")

    strategy_return = results['Return [%]']
    buy_hold = results['Buy & Hold Return [%]']

    if strategy_return > 0 and strategy_return > buy_hold:
        diff = strategy_return - buy_hold
        cprint(f"🎉 STRATEGY WINS! Beat buy & hold by {diff:.2f}%!", "green", attrs=["bold"])
        cprint(f"   🚀 You would have made ${(10000 * strategy_return/100):,.2f}!", "green")
    elif strategy_return > 0:
        cprint(f"✅ Strategy is profitable: +{strategy_return:.2f}%", "green")
        cprint(f"   But buy & hold was better: +{buy_hold:.2f}%", "yellow")
    else:
        cprint(f"❌ Strategy lost {strategy_return:.2f}%", "red")

    cprint(f"\n📊 Comparison with Previous Strategies:", "cyan")
    cprint(f"  ├─ EMA Trend Following: {strategy_return:.2f}% ← THIS STRATEGY", "white")
    cprint(f"  ├─ Buy & Hold: {buy_hold:.2f}%", "white")
    cprint(f"  ├─ RSI 20/80 (best mean-reversion): -10.98%", "red")
    cprint(f"  └─ RSI 30/70 (original): -23.03%", "red")

    cprint(f"\n💡 Key Insight:", "yellow")
    if strategy_return > -10:
        cprint(f"   Trend following is WAY better than mean-reversion for uptrends!", "green")
    else:
        cprint(f"   Try different parameters or test on a different asset", "white")
