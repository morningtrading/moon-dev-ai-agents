#!/usr/bin/env python3
"""
🌙 Timeframe Validation: Test 5m-Optimized Strategies on 1m Data
Critical test: Do our parameters work on different timeframe?
If yes → parameters are robust
If no → we overfit to 5-minute timeframe
"""

import pandas as pd
import pandas_ta as ta
from pathlib import Path
from termcolor import cprint
from backtesting import Backtest, Strategy

DATA_DIR = Path("/home/titus/Dropbox/user_data/data/binance")

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
    """Run backtest with parameters"""
    try:
        bt = Backtest(df, RSIStrategy, cash=10000, commission=.002)
        results = bt.run(**params)

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
            'final_equity': results['Equity Final [$]']
        }
    except Exception as e:
        return None

def validate_timeframe():
    """Test 5m-optimized strategies on 1m data"""

    cprint("\n🌙 Timeframe Validation Test", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    # These are the OPTIMAL parameters we found on 5-minute data
    optimized_5m_strategies = {
        'BCH_USDT': {'rsi_period': 21, 'oversold': 25, 'overbought': 80},
        'NEAR_USDT': {'rsi_period': 14, 'oversold': 20, 'overbought': 80},
        'PENDLE_USDT': {'rsi_period': 14, 'oversold': 25, 'overbought': 80},
        'QNT_USDT': {'rsi_period': 14, 'oversold': 15, 'overbought': 75},
        'AVAX_USDT': {'rsi_period': 21, 'oversold': 25, 'overbought': 70},
        'UMA_USDT': {'rsi_period': 14, 'oversold': 20, 'overbought': 75},
        'SHIB_USDT': {'rsi_period': 14, 'oversold': 20, 'overbought': 80},
        'CRV_USDT': {'rsi_period': 14, 'oversold': 20, 'overbought': 80},
        'VET_USDT': {'rsi_period': 14, 'oversold': 20, 'overbought': 75},
    }

    # Store 5m returns for comparison
    returns_5m = {
        'BCH_USDT': 36.50,
        'NEAR_USDT': 28.09,
        'PENDLE_USDT': 22.78,
        'QNT_USDT': 9.17,
        'AVAX_USDT': 8.42,
        'UMA_USDT': 5.29,
        'SHIB_USDT': 2.95,
        'CRV_USDT': 2.01,
        'VET_USDT': -0.60,
    }

    cprint(f"\n📊 Test Strategy:", "white")
    cprint(f"  ├─ Optimized on: 5-minute data", "yellow")
    cprint(f"  ├─ Testing on: 1-minute data", "green")
    cprint(f"  └─ Goal: Validate parameter robustness across timeframes", "white")

    cprint(f"\n💡 Why This Matters:", "yellow")
    cprint(f"  If strategies work on BOTH timeframes:", "white")
    cprint(f"    ✅ Parameters are robust (not overfit to specific granularity)", "green")
    cprint(f"    ✅ More likely to work in live trading", "green")
    cprint(f"  If strategies FAIL on 1-minute:", "white")
    cprint(f"    ❌ Overfit to 5-minute timeframe", "red")
    cprint(f"    ❌ Need different parameters for live trading", "red")

    results = []

    for asset, params in optimized_5m_strategies.items():
        try:
            # Load 1-minute data
            file_path = DATA_DIR / f"{asset}-1m.feather"
            if not file_path.exists():
                cprint(f"\n❌ {asset}: 1m data not found", "red")
                continue

            df = pd.read_feather(file_path)
            df = df.rename(columns={
                'open': 'Open', 'high': 'High', 'low': 'Low',
                'close': 'Close', 'volume': 'Volume'
            })
            df = df.set_index('date')

            cprint(f"\n🔍 Testing {asset}...", "cyan")
            cprint(f"  Parameters from 5m: RSI({params['rsi_period']}) {params['oversold']}/{params['overbought']}",
                   "yellow")

            # Test on 1-minute data
            result_1m = run_backtest(df, params)

            if result_1m:
                return_5m = returns_5m[asset]
                return_1m = result_1m['return']
                difference = return_1m - return_5m

                # Classify result
                if abs(difference) < 5:
                    status = "✅ VERY SIMILAR"
                    color = "green"
                elif abs(difference) < 15:
                    status = "⚠️  DIFFERENT"
                    color = "yellow"
                else:
                    status = "❌ VERY DIFFERENT"
                    color = "red"

                cprint(f"  5m Return: {return_5m:+.2f}%", "white")
                cprint(f"  1m Return: {return_1m:+.2f}%", "white")
                cprint(f"  Difference: {difference:+.2f}%", color)
                cprint(f"  Status: {status}", color)
                cprint(f"  1m Stats: {result_1m['trades']} trades ({result_1m['trades_per_week']:.1f}/wk), {result_1m['win_rate']:.1f}% WR",
                       "white")

                results.append({
                    'asset': asset,
                    'params': params,
                    'return_5m': return_5m,
                    'return_1m': return_1m,
                    'difference': difference,
                    'trades_1m': result_1m['trades'],
                    'trades_per_week_1m': result_1m['trades_per_week'],
                    'win_rate_1m': result_1m['win_rate'],
                    'sharpe_1m': result_1m['sharpe'],
                    'max_dd_1m': result_1m['max_dd']
                })

            else:
                cprint(f"  ❌ Backtest failed on 1m data", "red")

        except Exception as e:
            cprint(f"\n❌ Error testing {asset}: {e}", "red")

    # Analysis
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📊 TIMEFRAME VALIDATION RESULTS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if not results:
        cprint(f"\n⚠️ No results to analyze!", "red")
        return

    # Calculate statistics
    avg_return_5m = sum(r['return_5m'] for r in results) / len(results)
    avg_return_1m = sum(r['return_1m'] for r in results) / len(results)
    avg_difference = sum(abs(r['difference']) for r in results) / len(results)
    avg_trades_pw_1m = sum(r['trades_per_week_1m'] for r in results) / len(results)
    avg_win_rate_1m = sum(r['win_rate_1m'] for r in results) / len(results)

    cprint(f"\n📈 Average Performance:", "white")
    cprint(f"  ├─ 5-minute timeframe: {avg_return_5m:+.2f}%", "white")
    cprint(f"  ├─ 1-minute timeframe: {avg_return_1m:+.2f}%", "white")
    cprint(f"  └─ Average Absolute Difference: {avg_difference:.2f}%", "white")

    cprint(f"\n📊 1-Minute Trading Stats:", "white")
    cprint(f"  ├─ Average Trades/Week: {avg_trades_pw_1m:.2f}", "white")
    cprint(f"  └─ Average Win Rate: {avg_win_rate_1m:.1f}%", "white")

    # Classify correlation
    very_similar = sum(1 for r in results if abs(r['difference']) < 5)
    similar = sum(1 for r in results if 5 <= abs(r['difference']) < 15)
    different = sum(1 for r in results if abs(r['difference']) >= 15)

    cprint(f"\n🎯 Parameter Robustness:", "white")
    cprint(f"  ├─ Very Similar (<5% diff): {very_similar}/{len(results)}", "green")
    cprint(f"  ├─ Different (5-15% diff): {similar}/{len(results)}", "yellow")
    cprint(f"  └─ Very Different (>15% diff): {different}/{len(results)}", "red")

    # Sort by 1m performance
    results.sort(key=lambda x: x['return_1m'], reverse=True)

    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🏆 1-MINUTE PERFORMANCE RANKING", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    for i, r in enumerate(results, 1):
        p = r['params']
        color = "green" if r['return_1m'] > 20 else "yellow" if r['return_1m'] > 10 else "white"

        cprint(f"\n{i}. {r['asset']}", color, attrs=["bold"])
        cprint(f"   Params: RSI({p['rsi_period']}) {p['oversold']}/{p['overbought']}", "yellow")
        cprint(f"   5m: {r['return_5m']:+.2f}% → 1m: {r['return_1m']:+.2f}% (Δ {r['difference']:+.2f}%)", "white")
        cprint(f"   1m Stats: {r['trades_1m']} trades ({r['trades_per_week_1m']:.1f}/wk), {r['win_rate_1m']:.1f}% WR",
               "white")
        cprint(f"   Risk: Sharpe {r['sharpe_1m']:.2f}, Max DD {r['max_dd_1m']:.2f}%", "white")

    # Portfolio simulation on 1m
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"💰 PORTFOLIO SIMULATION ON 1-MINUTE DATA", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    total_capital = 10000
    capital_per_asset = total_capital / len(results)
    total_portfolio_value_1m = sum(capital_per_asset * (1 + r['return_1m']/100) for r in results)
    portfolio_return_1m = ((total_portfolio_value_1m / total_capital) - 1) * 100

    # Original 5m portfolio return
    portfolio_return_5m = 12.74

    cprint(f"\n📊 Equal-Weight Portfolio:", "white")
    cprint(f"  ├─ Capital: ${total_capital:,.0f} across {len(results)} assets", "white")
    cprint(f"  ├─ 5m Portfolio Return: {portfolio_return_5m:+.2f}%", "white")
    cprint(f"  ├─ 1m Portfolio Return: {portfolio_return_1m:+.2f}%", "white")
    cprint(f"  └─ Difference: {portfolio_return_1m - portfolio_return_5m:+.2f}%",
           "green" if abs(portfolio_return_1m - portfolio_return_5m) < 5 else "yellow")

    # Verdict
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"⚖️  VERDICT: PARAMETER ROBUSTNESS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if avg_difference < 5:
        cprint(f"\n✅ EXCELLENT! Parameters are very robust!", "green", attrs=["bold"])
        cprint(f"   Average difference of only {avg_difference:.2f}% between timeframes", "green")
        cprint(f"   These parameters should work well in live trading", "green")
    elif avg_difference < 10:
        cprint(f"\n✅ GOOD! Parameters are reasonably robust", "green")
        cprint(f"   Average difference of {avg_difference:.2f}% between timeframes", "white")
        cprint(f"   Some variation is expected across timeframes", "white")
    elif avg_difference < 20:
        cprint(f"\n⚠️  MODERATE: Parameters show some timeframe sensitivity", "yellow")
        cprint(f"   Average difference of {avg_difference:.2f}% between timeframes", "yellow")
        cprint(f"   Consider testing on additional timeframes (15m, 1h)", "white")
    else:
        cprint(f"\n❌ WARNING: Parameters are timeframe-specific!", "red")
        cprint(f"   Average difference of {avg_difference:.2f}% between timeframes", "red")
        cprint(f"   May be overfit to 5-minute granularity", "red")

    # Additional insights
    cprint(f"\n💡 Key Insights:", "yellow", attrs=["bold"])

    cprint(f"\n  1. Trade Frequency on 1-Minute:", "white")
    cprint(f"     └─ {avg_trades_pw_1m:.2f} trades per week", "white")
    if avg_trades_pw_1m > 3:
        cprint(f"     └─ Much more active than 5m (good for faster execution)", "green")
    elif avg_trades_pw_1m > 1:
        cprint(f"     └─ Still meets statistical significance requirement", "green")
    else:
        cprint(f"     └─ Warning: Below minimum trade frequency", "red")

    cprint(f"\n  2. Win Rate Consistency:", "white")
    cprint(f"     └─ 1m average win rate: {avg_win_rate_1m:.1f}%", "white")
    if avg_win_rate_1m > 60:
        cprint(f"     └─ Excellent win rate maintained!", "green")
    elif avg_win_rate_1m > 50:
        cprint(f"     └─ Acceptable win rate", "white")
    else:
        cprint(f"     └─ Win rate declined on 1m data", "yellow")

    cprint(f"\n  3. Portfolio-Level Robustness:", "white")
    diff = abs(portfolio_return_1m - portfolio_return_5m)
    cprint(f"     └─ Portfolio return difference: {diff:.2f}%", "white")
    if diff < 5:
        cprint(f"     └─ Portfolio is very stable across timeframes!", "green")
    elif diff < 10:
        cprint(f"     └─ Portfolio shows good consistency", "white")
    else:
        cprint(f"     └─ Portfolio performance varies by timeframe", "yellow")

    # Next steps
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🎯 NEXT STEPS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if avg_difference < 10 and portfolio_return_1m > 5:
        cprint(f"\n✅ Validation PASSED! Ready for next phase:", "green")
        cprint(f"\n1. 🚀 Move to Live Testing (Hyperliquid Paper Trading)", "yellow")
        cprint(f"   ├─ Test with real-time data", "white")
        cprint(f"   ├─ Experience execution challenges", "white")
        cprint(f"   └─ Validate without risking real money", "white")

        cprint(f"\n2. 📊 Additional Validation (Optional):", "yellow")
        cprint(f"   ├─ Test on 15-minute and 1-hour timeframes", "white")
        cprint(f"   ├─ Walk-forward testing (test on future data)", "white")
        cprint(f"   └─ Out-of-sample validation", "white")

    else:
        cprint(f"\n⚠️  Further optimization recommended:", "yellow")
        cprint(f"\n1. 🔧 Optimize specifically for 1-minute timeframe", "yellow")
        cprint(f"   └─ Find parameters that work best on 1m data", "white")

        cprint(f"\n2. 📊 Test on additional timeframes:", "yellow")
        cprint(f"   └─ 15m and 1h to find most robust parameters", "white")

        cprint(f"\n3. 🎯 Focus on most robust assets:", "yellow")
        cprint(f"   └─ Build portfolio with assets that performed well on BOTH timeframes", "white")

    return results

if __name__ == "__main__":
    try:
        results = validate_timeframe()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Validation interrupted", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
