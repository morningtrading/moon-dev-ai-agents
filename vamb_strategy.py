#!/usr/bin/env python3
"""
🌙 Volatility-Adjusted Momentum Breakout (VAMB)
AI-Generated Strategy: Ride strong breakouts with volatility filtering
Simpler than RARF - focuses on catching explosive moves
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
from pathlib import Path
from termcolor import cprint
from backtesting import Backtest, Strategy

class VAMBStrategy(Strategy):
    """
    Momentum Breakout with ATR Volatility Filter
    - Entry: Price breaks above 20-day high + ATR > median
    - Exit: Trailing stop at 2.5x ATR or 10-day time limit
    """

    breakout_period = 20  # 20-day rolling high
    atr_period = 14
    atr_filter_period = 30  # ATR median period
    atr_multiplier = 2.5  # Trailing stop distance
    max_hold_days = 10  # Time-based exit

    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        high = pd.Series(self.data.High, index=self.data.index)
        low = pd.Series(self.data.Low, index=self.data.index)

        # Calculate indicators
        self.rolling_high = self.I(lambda x: pd.Series(x).rolling(self.breakout_period).max(),
                                     self.data.Close)
        self.atr = self.I(ta.atr, high, low, close, length=self.atr_period)

        # Calculate ATR median for volatility filter
        self.atr_median = self.I(lambda x: pd.Series(x).rolling(self.atr_filter_period).median(),
                                  self.atr)

        # Track entry prices and bars for trailing stop
        self.entry_price = None
        self.entry_bar = None

    def next(self):
        # Wait for indicators to be ready
        if len(self.data) < max(self.breakout_period, self.atr_filter_period) + 10:
            return

        current_price = self.data.Close[-1]

        # Entry logic
        if not self.position:
            # Reset tracking
            self.entry_price = None
            self.entry_bar = None

            # Check breakout condition
            if len(self.rolling_high) > 1:
                prev_high = self.rolling_high[-2]

                # Breakout: price closes above previous 20-day high
                if current_price > prev_high:
                    # Volatility filter: ATR must be above its median
                    if self.atr[-1] > self.atr_median[-1]:
                        self.buy()
                        self.entry_price = current_price
                        self.entry_bar = len(self.data)

        # Exit logic
        else:
            # Calculate trailing stop
            if self.entry_price and self.atr[-1] > 0:
                # Highest price since entry
                bars_held = len(self.data) - self.entry_bar

                # Get highest price since entry
                recent_high = max([self.data.Close[i] for i in range(self.entry_bar - 1, len(self.data))])

                # Trailing stop: 2.5x ATR below highest price
                trailing_stop = recent_high - (self.atr_multiplier * self.atr[-1])

                # Exit conditions
                if current_price < trailing_stop:
                    self.position.close()  # Hit trailing stop
                elif bars_held >= self.max_hold_days * 288:  # 288 = 5-min bars per day
                    self.position.close()  # Time-based exit

def load_data(file_path):
    """Load data"""
    df = pd.read_feather(file_path)
    df = df.rename(columns={
        'open': 'Open', 'high': 'High', 'low': 'Low',
        'close': 'Close', 'volume': 'Volume'
    })
    df = df.set_index('date')
    return df

def run_backtest(df, strategy_class):
    """Run backtest"""
    try:
        bt = Backtest(df, strategy_class, cash=10000, commission=.002)
        results = bt.run()

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
        cprint(f"      Backtest error: {str(e)[:50]}", "red")
        return None

def test_vamb_strategy():
    """Test VAMB on top 6 robust pairs"""

    cprint("\n🌙 Testing Volatility-Adjusted Momentum Breakout (VAMB)", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    cprint(f"\n🚀 AI Strategy: VAMB (Simpler than RARF)", "yellow")
    cprint(f"  Logic: Catch explosive breakouts with volatility confirmation", "white")
    cprint(f"  • Entry: Break above 20-day high + ATR > median", "white")
    cprint(f"  • Exit: Trailing stop 2.5x ATR or 10 days max", "white")
    cprint(f"  • Why: Rides momentum, filters noise with volatility", "white")

    data_dir_train = Path("/home/titus/Dropbox/user_data/data/binance")
    data_dir_test = Path("/home/titus/Dropbox/user_data/data/binance_walkforward")

    pairs = ['PENDLE_USDT', 'XTZ_USDT', 'QTUM_USDT', 'BCH_USDT', 'BNB_USDT', 'AVAX_USDT']

    cprint(f"\n🧪 Testing on 6 ultra-robust pairs with walk-forward\n", "cyan")

    results = []

    for i, pair in enumerate(pairs, 1):
        try:
            # Training period
            train_file = data_dir_train / f"{pair}-5m.feather"
            df_train = load_data(train_file)
            train_result = run_backtest(df_train, VAMBStrategy)

            # Testing period
            test_file = data_dir_test / f"{pair}-5m.feather"
            df_test = load_data(test_file)
            test_result = run_backtest(df_test, VAMBStrategy)

            if train_result and test_result:
                avg_return = (train_result['return'] + test_result['return']) / 2

                color = "green" if avg_return > 15 else "yellow" if avg_return > 8 else "white"

                cprint(f"  [{i}/6] {pair:15} "
                       f"Train: {train_result['return']:+6.2f}% | "
                       f"Test: {test_result['return']:+6.2f}% | "
                       f"Avg: {avg_return:+6.2f}%", color)

                results.append({
                    'pair': pair,
                    'train_return': train_result['return'],
                    'test_return': test_result['return'],
                    'avg_return': avg_return,
                    'train_trades': train_result['trades'],
                    'test_trades': test_result['trades'],
                    'train_tpw': train_result['trades_per_week'],
                    'test_tpw': test_result['trades_per_week'],
                    'train_wr': train_result['win_rate'],
                    'test_wr': test_result['win_rate']
                })

        except Exception as e:
            cprint(f"  [{i}/6] {pair:15} Error: {str(e)[:40]}", "red")

    if not results:
        cprint(f"\n❌ No results!", "red")
        return

    # Analysis
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📊 VAMB PERFORMANCE ANALYSIS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    avg_train = sum(r['train_return'] for r in results) / len(results)
    avg_test = sum(r['test_return'] for r in results) / len(results)
    avg_overall = sum(r['avg_return'] for r in results) / len(results)
    avg_trades = sum(r['train_trades'] + r['test_trades'] for r in results) / (len(results) * 2)

    cprint(f"\n💰 VAMB Returns:", "white")
    cprint(f"  ├─ Training Period: {avg_train:+.2f}%", "white")
    cprint(f"  ├─ Testing Period: {avg_test:+.2f}%", "white")
    cprint(f"  └─ Average: {avg_overall:+.2f}%", "green" if avg_overall > 15 else "white")

    cprint(f"\n📊 Trading Stats:", "white")
    cprint(f"  ├─ Average Trades: {avg_trades:.1f} per period", "white")
    avg_tpw = sum(r['train_tpw'] + r['test_tpw'] for r in results) / (len(results) * 2)
    cprint(f"  └─ Trade Frequency: {avg_tpw:.1f} per week", "white")

    # Compare to RSI and RARF
    rsi_baseline = {
        'PENDLE_USDT': 29.15,
        'XTZ_USDT': 11.52,
        'QTUM_USDT': 11.23,
        'BCH_USDT': 9.21,
        'BNB_USDT': 6.85,
        'AVAX_USDT': 6.68
    }
    rsi_avg = sum(rsi_baseline.values()) / len(rsi_baseline)
    rarf_avg = -28.29  # From previous test

    cprint(f"\n📊 STRATEGY COMPARISON:", "cyan", attrs=["bold"])
    cprint(f"  ├─ RSI(14) 20/80:  {rsi_avg:+6.2f}% ✅ (Baseline)", "green")
    cprint(f"  ├─ VAMB Breakout:  {avg_overall:+6.2f}%",
           "green" if avg_overall > rsi_avg else "red")
    cprint(f"  └─ RARF ML:        {rarf_avg:+6.2f}% ❌ (Failed)", "red")

    # Detailed comparison
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📋 DETAILED RESULTS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    for r in results:
        pair = r['pair']
        rsi_return = rsi_baseline.get(pair, 0)
        vamb_return = r['avg_return']
        improvement = vamb_return - rsi_return

        color = "green" if improvement > 0 else "red"

        cprint(f"\n{pair:15}", "yellow", attrs=["bold"])
        cprint(f"  RSI:  {rsi_return:+6.2f}%", "white")
        cprint(f"  VAMB: {vamb_return:+6.2f}% ({improvement:+.2f}%)", color)
        cprint(f"  Trades: {r['train_trades']+r['test_trades']} total, "
               f"{r['train_wr']:.1f}%/{r['test_wr']:.1f}% WR", "white")

    # Verdict
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"⚖️  FINAL VERDICT", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if avg_overall > rsi_avg + 10:
        cprint(f"\n🎉 BREAKTHROUGH! VAMB significantly beats RSI!", "green", attrs=["bold"])
        cprint(f"   +{avg_overall - rsi_avg:.2f}% improvement", "green")
        cprint(f"\n✅ Momentum breakouts work better than mean-reversion!", "green")
        cprint(f"✅ Volatility filtering adds real edge", "green")
    elif avg_overall > rsi_avg + 5:
        cprint(f"\n✅ VAMB beats RSI baseline!", "green")
        cprint(f"   +{avg_overall - rsi_avg:.2f}% improvement", "white")
    elif avg_overall > rsi_avg:
        cprint(f"\n✅ VAMB slightly outperforms RSI", "green")
        cprint(f"   +{avg_overall - rsi_avg:.2f}% improvement", "white")
    elif avg_overall > 0:
        cprint(f"\n⚠️  VAMB underperforms RSI but still profitable", "yellow")
        cprint(f"   {avg_overall - rsi_avg:.2f}% vs baseline", "white")
        cprint(f"\n   RSI remains the better choice", "white")
    else:
        cprint(f"\n❌ VAMB failed (loses money)", "red")
        cprint(f"   {avg_overall:.2f}% return", "white")
        cprint(f"\n   RSI is clearly superior", "white")

    cprint(f"\n💡 Key Learnings:", "yellow")
    cprint(f"  1. Tested 3 strategies: RSI (simple), VAMB (medium), RARF (complex)", "white")
    cprint(f"  2. Walk-forward validation is critical", "white")
    cprint(f"  3. Simpler strategies often work best", "white")

    winner = "RSI" if rsi_avg > max(avg_overall, rarf_avg) else "VAMB" if avg_overall > rarf_avg else "None"

    cprint(f"\n🏆 WINNER: {winner} ({rsi_avg if winner == 'RSI' else avg_overall if winner == 'VAMB' else 0:.2f}%)",
           "green", attrs=["bold"])

    cprint(f"\n🎯 Recommendation:", "cyan")
    if winner == "RSI":
        cprint(f"  • Deploy RSI(14) 20/80 on Hyperliquid paper trading", "white")
        cprint(f"  • Focus on top performers: PENDLE, XTZ, QTUM", "white")
        cprint(f"  • Monitor for 1-2 weeks before considering real money", "white")
    elif winner == "VAMB":
        cprint(f"  • Deploy VAMB breakout strategy", "white")
        cprint(f"  • Higher returns but verify with more testing", "white")
        cprint(f"  • Consider hybrid: RSI for base, VAMB for momentum", "white")

    return results

if __name__ == "__main__":
    try:
        results = test_vamb_strategy()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Test interrupted", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
