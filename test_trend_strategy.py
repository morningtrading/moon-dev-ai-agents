#!/usr/bin/env python3
"""
🌙 Test AI-Generated Trend Following Strategy
"""

import pandas as pd
import pandas_ta as ta
from backtesting import Backtest, Strategy
import numpy as np
from pathlib import Path
from termcolor import cprint

# Import the AI-generated strategy
class TrendFollowingStrategy(Strategy):
    ema_fast = 20
    ema_slow = 50
    adx_period = 14
    adx_threshold = 25
    atr_period = 14
    risk_per_trade = 0.02

    def init(self):
        close = pd.Series(self.data.Close)
        self.ema_fast_ind = self.I(ta.ema, close, length=self.ema_fast)
        self.ema_slow_ind = self.I(ta.ema, close, length=self.ema_slow)

        adx_data = ta.adx(self.data.High, self.data.Low, self.data.Close, length=self.adx_period)
        self.adx = self.I(lambda: adx_data[f'ADX_{self.adx_period}'])
        self.pdi = self.I(lambda: adx_data[f'DMP_{self.adx_period}'])
        self.ndi = self.I(lambda: adx_data[f'DMN_{self.adx_period}'])

        atr_data = ta.atr(self.data.High, self.data.Low, self.data.Close, length=self.atr_period)
        self.atr = self.I(lambda: atr_data)

        macd_data = ta.macd(self.data.Close)
        self.macd = self.I(lambda: macd_data['MACD_12_26_9'])
        self.macd_signal = self.I(lambda: macd_data['MACDs_12_26_9'])

        supertrend_data = ta.supertrend(self.data.High, self.data.Low, self.data.Close, length=10, multiplier=3)
        self.supertrend = self.I(lambda: supertrend_data['SUPERT_10_3.0'])
        self.supertrend_direction = self.I(lambda: supertrend_data['SUPERTd_10_3.0'])

    def next(self):
        current_price = self.data.Close[-1]

        if len(self.data) < max(self.ema_slow, self.adx_period, self.atr_period) + 10:
            return

        if self.atr[-1] > 0:
            stop_distance = self.atr[-1] * 2
            position_size = (self.equity * self.risk_per_trade) / stop_distance
            position_size = min(position_size, self.equity * 0.1)
        else:
            position_size = self.equity * 0.05

        trend_up_conditions = (
            self.ema_fast_ind[-1] > self.ema_slow_ind[-1] and
            self.adx[-1] > self.adx_threshold and
            self.pdi[-1] > self.ndi[-1] and
            self.macd[-1] > self.macd_signal[-1] and
            self.supertrend_direction[-1] == 1 and
            current_price > self.ema_slow_ind[-1]
        )

        trend_reversal_conditions = (
            self.ema_fast_ind[-1] < self.ema_slow_ind[-1] or
            self.supertrend_direction[-1] == -1 or
            self.macd[-1] < self.macd_signal[-1] or
            self.pdi[-1] < self.ndi[-1]
        )

        if not self.position and trend_up_conditions:
            stop_price = current_price - (self.atr[-1] * 2)
            self.buy(size=position_size, sl=stop_price)

        elif self.position and trend_reversal_conditions:
            self.position.close()

if __name__ == "__main__":
    cprint("\n🌙 Testing AI-Generated Trend Following Strategy", "cyan", attrs=["bold"])
    cprint("=" * 70, "cyan")

    # Load ETH data
    data_file = Path("/home/titus/Dropbox/user_data/data/binance/ETH_USDT-5m.feather")
    df = pd.read_feather(data_file)

    df = df.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    df = df.set_index('date')

    cprint(f"\n📊 Data: ETH_USDT", "white")
    cprint(f"  ├─ Candles: {len(df):,}", "white")
    cprint(f"  ├─ Period: {df.index[0]} to {df.index[-1]}", "white")
    cprint(f"  └─ Price: ${df['Close'].iloc[0]:,.2f} → ${df['Close'].iloc[-1]:,.2f}", "white")

    cprint(f"\n🚀 Running AI Strategy...", "cyan")
    cprint(f"  Strategy: Multi-indicator trend following", "white")
    cprint(f"  Indicators: EMA(20/50), ADX, MACD, Supertrend, ATR", "white")

    bt = Backtest(df, TrendFollowingStrategy, cash=10000, commission=.002)
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

        color = "green" if ("Return" in key and value > 0) else "white"
        cprint(f"  {key:20} {formatted}", color)

    cprint(f"\n{'='*70}", "cyan")

    strategy_return = results['Return [%]']
    buy_hold = results['Buy & Hold Return [%]']

    if strategy_return > 0 and strategy_return > buy_hold:
        cprint(f"🎉 AI STRATEGY WINS! Beat buy & hold by {strategy_return - buy_hold:.2f}%!", "green", attrs=["bold"])
    elif strategy_return > 0:
        cprint(f"✅ Profitable but didn't beat buy & hold", "yellow")
    else:
        cprint(f"❌ Strategy lost {strategy_return:.2f}%", "red")

    cprint(f"\n💡 Comparison:", "cyan")
    cprint(f"  ├─ AI Strategy: {strategy_return:.2f}%", "white")
    cprint(f"  ├─ Buy & Hold: {buy_hold:.2f}%", "white")
    cprint(f"  └─ Old RSI 30/70: -23.03% (for reference)", "red")
