#!/usr/bin/env python3
"""
🌙 Moon Dev's Strategy Optimizer
Test multiple strategy variations to find what works
"""

from backtesting import Strategy, Backtest
import pandas as pd
import pandas_ta as ta
from termcolor import cprint
from pathlib import Path
import itertools

# Strategy 1: RSI with different parameters
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

# Strategy 2: Moving Average Crossover
class MACrossStrategy(Strategy):
    fast_period = 10
    slow_period = 30

    def init(self):
        close = pd.Series(self.data.Close)
        self.fast_ma = self.I(ta.sma, close, length=self.fast_period)
        self.slow_ma = self.I(ta.sma, close, length=self.slow_period)

    def next(self):
        if self.fast_ma[-1] > self.slow_ma[-1] and not self.position:
            self.buy()
        elif self.fast_ma[-1] < self.slow_ma[-1] and self.position:
            self.position.close()

# Strategy 3: Bollinger Bands Mean Reversion
class BollingerStrategy(Strategy):
    bb_period = 20
    bb_std = 2

    def init(self):
        close = pd.Series(self.data.Close)
        bb = ta.bbands(close, length=self.bb_period, std=self.bb_std)
        self.lower = self.I(lambda: bb[f'BBL_{self.bb_period}_{self.bb_std}.0'])
        self.upper = self.I(lambda: bb[f'BBU_{self.bb_period}_{self.bb_std}.0'])

    def next(self):
        if self.data.Close[-1] < self.lower[-1] and not self.position:
            self.buy()
        elif self.data.Close[-1] > self.upper[-1] and self.position:
            self.position.close()

def load_data(pair_name, timeframe='5m'):
    """Load Binance data"""
    data_file = Path(f"/home/titus/Dropbox/user_data/data/binance/{pair_name}-{timeframe}.feather")

    if not data_file.exists():
        return None

    df = pd.read_feather(data_file)
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    df = df.set_index('date')
    return df

def run_single_test(df, strategy_class, params, pair_name):
    """Run a single backtest"""
    bt = Backtest(df, strategy_class, cash=10000, commission=.002)
    results = bt.run(**params)

    return {
        'Pair': pair_name,
        'Strategy': strategy_class.__name__,
        'Params': str(params),
        'Return': results['Return [%]'],
        'BuyHold': results['Buy & Hold Return [%]'],
        'Sharpe': results['Sharpe Ratio'],
        'MaxDD': results['Max. Drawdown [%]'],
        'Trades': results['# Trades'],
        'WinRate': results['Win Rate [%]'],
    }

def optimize_strategies(pair_name='ETH_USDT', timeframe='5m'):
    """Test multiple strategy variations"""

    cprint("\n🌙 Moon Dev's Strategy Optimizer", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    # Load data
    df = load_data(pair_name, timeframe)
    if df is None:
        cprint(f"❌ Could not load data for {pair_name}", "red")
        return

    cprint(f"\n📊 Testing on {pair_name} ({len(df):,} candles)", "white")
    cprint(f"  ├─ Period: {df.index[0]} to {df.index[-1]}", "white")
    cprint(f"  └─ Price: ${df['Close'].iloc[0]:,.2f} → ${df['Close'].iloc[-1]:,.2f}", "white")

    results_list = []

    # Test 1: Different RSI parameters
    cprint(f"\n🔍 Testing RSI variations...", "cyan")
    rsi_params = [
        {'rsi_period': 14, 'oversold': 20, 'overbought': 80},  # Less sensitive
        {'rsi_period': 14, 'oversold': 25, 'overbought': 75},  # Moderate
        {'rsi_period': 14, 'oversold': 30, 'overbought': 70},  # Original
        {'rsi_period': 21, 'oversold': 30, 'overbought': 70},  # Longer period
        {'rsi_period': 7, 'oversold': 30, 'overbought': 70},   # Shorter period
    ]

    for params in rsi_params:
        try:
            result = run_single_test(df, RSIStrategy, params, pair_name)
            results_list.append(result)
            ret = result['Return']
            color = "green" if ret > 0 else "red"
            cprint(f"  ├─ {params}: {ret:.2f}%", color)
        except Exception as e:
            cprint(f"  ├─ {params}: Error - {str(e)[:50]}", "red")

    # Test 2: Moving Average Crossovers
    cprint(f"\n🔍 Testing MA Crossover variations...", "cyan")
    ma_params = [
        {'fast_period': 5, 'slow_period': 20},
        {'fast_period': 10, 'slow_period': 30},
        {'fast_period': 20, 'slow_period': 50},
    ]

    for params in ma_params:
        try:
            result = run_single_test(df, MACrossStrategy, params, pair_name)
            results_list.append(result)
            ret = result['Return']
            color = "green" if ret > 0 else "red"
            cprint(f"  ├─ Fast {params['fast_period']}, Slow {params['slow_period']}: {ret:.2f}%", color)
        except Exception as e:
            cprint(f"  ├─ {params}: Error - {str(e)[:50]}", "red")

    # Test 3: Bollinger Bands
    cprint(f"\n🔍 Testing Bollinger Bands variations...", "cyan")
    bb_params = [
        {'bb_period': 20, 'bb_std': 2},
        {'bb_period': 20, 'bb_std': 2.5},
        {'bb_period': 30, 'bb_std': 2},
    ]

    for params in bb_params:
        try:
            result = run_single_test(df, BollingerStrategy, params, pair_name)
            results_list.append(result)
            ret = result['Return']
            color = "green" if ret > 0 else "red"
            cprint(f"  ├─ Period {params['bb_period']}, Std {params['bb_std']}: {ret:.2f}%", color)
        except Exception as e:
            cprint(f"  ├─ {params}: Error - {str(e)[:50]}", "red")

    # Sort by return
    results_list.sort(key=lambda x: x['Return'], reverse=True)

    # Display top results
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📊 TOP 5 STRATEGIES", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    for i, result in enumerate(results_list[:5], 1):
        ret = result['Return']
        bh = result['BuyHold']
        color = "green" if ret > 0 else "red"

        cprint(f"\n{i}. {result['Strategy']}", "yellow", attrs=["bold"])
        cprint(f"   Parameters: {result['Params']}", "white")
        cprint(f"   Return: {ret:.2f}% (vs Buy&Hold: {bh:.2f}%)", color)
        cprint(f"   Sharpe: {result['Sharpe']:.2f} | Max DD: {result['MaxDD']:.2f}%", "white")
        cprint(f"   Trades: {result['Trades']} | Win Rate: {result['WinRate']:.2f}%", "white")

    # Best strategy
    best = results_list[0]
    cprint(f"\n{'='*90}", "cyan")
    if best['Return'] > 0:
        cprint(f"🏆 BEST STRATEGY: {best['Strategy']} with {best['Return']:.2f}% return!", "green", attrs=["bold"])
        if best['Return'] > best['BuyHold']:
            cprint(f"   ✨ Outperformed buy & hold by {best['Return'] - best['BuyHold']:.2f}%!", "green")
    else:
        cprint(f"⚠️ No profitable strategies found on this data", "yellow")
        cprint(f"   Buy & Hold: {best['BuyHold']:.2f}% | Best Strategy: {best['Return']:.2f}%", "white")

    cprint(f"\n💡 Next steps:", "cyan")
    cprint(f"  1. Try different pairs: python strategy_optimizer.py", "white")
    cprint(f"  2. Test on different timeframes (1m vs 5m)", "white")
    cprint(f"  3. Use AI to generate completely new strategies", "white")

    return results_list

if __name__ == "__main__":
    try:
        optimize_strategies('ETH_USDT', timeframe='5m')
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Interrupted by user", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
