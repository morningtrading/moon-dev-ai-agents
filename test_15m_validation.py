#!/usr/bin/env python3
"""
🌙 Third Validation: RSI(14) 20/80 on 15m Timeframe
Ultimate robustness test - different timeframe + overlapping period
"""

import pandas as pd
import pandas_ta as ta
from pathlib import Path
from termcolor import cprint
from backtesting import Backtest, Strategy

DATA_DIR = Path("/home/titus/Dropbox/user_data/data/binance_15m_validation")

class RSIStrategy(Strategy):
    rsi_period = 14
    oversold = 20
    overbought = 80

    def init(self):
        close = pd.Series(self.data.Close, index=self.data.index)
        self.rsi = self.I(ta.rsi, close, length=self.rsi_period)

    def next(self):
        if self.rsi[-1] < self.oversold and not self.position:
            self.buy()
        elif self.rsi[-1] > self.overbought and self.position:
            self.position.close()

def load_data(file_path):
    """Load and prepare data"""
    df = pd.read_feather(file_path)
    df = df.rename(columns={
        'open': 'Open', 'high': 'High', 'low': 'Low',
        'close': 'Close', 'volume': 'Volume'
    })
    df = df.set_index('date')
    return df

def run_backtest(df):
    """Run backtest with RSI(14) 20/80"""
    try:
        bt = Backtest(df, RSIStrategy, cash=10000, commission=.002)
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
        cprint(f"      Error: {str(e)[:50]}", "red")
        return None

def test_15m_validation():
    """Test RSI on 15m timeframe for ultimate validation"""

    cprint("\n🌙 Third Validation: RSI(14) 20/80 on 15m Timeframe", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    cprint(f"\n📊 Testing Period: April 1 - July 1, 2025 (15-minute bars)", "yellow")
    cprint(f"🎯 Strategy: RSI(14) 20/80 (unchanged parameters)", "white")
    cprint(f"💡 This validates timeframe robustness\n", "white")

    pairs = ['PENDLE_USDT', 'XTZ_USDT', 'QTUM_USDT', 'BCH_USDT', 'BNB_USDT']

    # Previous results for comparison
    period1_results = {  # Training: July-Oct 2025 (5m)
        'PENDLE_USDT': 32.36,
        'XTZ_USDT': 10.22,
        'QTUM_USDT': 12.84,
        'BCH_USDT': 8.92,
        'BNB_USDT': 7.68
    }

    period2_results = {  # Testing: April-June 2025 (5m)
        'PENDLE_USDT': 25.94,
        'XTZ_USDT': 12.83,
        'QTUM_USDT': 9.62,
        'BCH_USDT': 9.50,
        'BNB_USDT': 6.01
    }

    results = []

    cprint(f"🧪 Testing {len(pairs)} pairs on 15m timeframe...\\n", "cyan")

    for i, pair in enumerate(pairs, 1):
        file_path = DATA_DIR / f"{pair}-15m.feather"

        if not file_path.exists():
            cprint(f"  [{i}/5] ❌ {pair:15} Missing data", "red")
            continue

        try:
            df = load_data(file_path)
            result = run_backtest(df)

            if result:
                ret = result['return']

                # Get previous period results
                period1 = period1_results.get(pair, 0)
                period2 = period2_results.get(pair, 0)
                avg_previous = (period1 + period2) / 2

                # Determine color based on performance
                if ret > 10:
                    color = "green"
                    status = "✅"
                elif ret > 5:
                    color = "yellow"
                    status = "⚠️ "
                elif ret > 0:
                    color = "white"
                    status = "⚠️ "
                else:
                    color = "red"
                    status = "❌"

                cprint(f"  [{i}/5] {status} {pair:15} "
                       f"15m: {ret:+6.2f}% | "
                       f"5m Avg: {avg_previous:+6.2f}% | "
                       f"Trades: {result['trades']}", color)

                results.append({
                    'pair': pair,
                    'period3_return': ret,  # 15m validation
                    'period1_return': period1,  # 5m training
                    'period2_return': period2,  # 5m testing
                    'avg_5m': avg_previous,
                    'trades': result['trades'],
                    'trades_per_week': result['trades_per_week'],
                    'win_rate': result['win_rate'],
                    'sharpe': result['sharpe'],
                    'all_positive': period1 > 0 and period2 > 0 and ret > 0
                })

        except Exception as e:
            cprint(f"  [{i}/5] ❌ {pair:15} Error: {str(e)[:30]}", "red")

    # Analysis
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📊 THIRD VALIDATION ANALYSIS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if not results:
        cprint(f"\n⚠️ No results!", "red")
        return

    # Calculate averages
    avg_15m = sum(r['period3_return'] for r in results) / len(results)
    avg_5m_train = sum(r['period1_return'] for r in results) / len(results)
    avg_5m_test = sum(r['period2_return'] for r in results) / len(results)
    avg_5m_combined = (avg_5m_train + avg_5m_test) / 2

    cprint(f"\n💰 Performance Comparison:", "white")
    cprint(f"  ├─ Period 1 (Jul-Oct 5m): {avg_5m_train:+.2f}%", "white")
    cprint(f"  ├─ Period 2 (Apr-Jun 5m): {avg_5m_test:+.2f}%", "white")
    cprint(f"  ├─ Period 3 (Apr-Jul 15m): {avg_15m:+.2f}%",
           "green" if avg_15m > 8 else "yellow" if avg_15m > 5 else "white")
    cprint(f"  └─ Overall Average: {(avg_5m_combined + avg_15m) / 2:+.2f}%", "white")

    # Consistency check
    all_profitable = [r for r in results if r['all_positive']]

    cprint(f"\n🎯 Robustness Metrics:", "white")
    cprint(f"  ├─ Profitable on ALL 3 periods: {len(all_profitable)}/5",
           "green" if len(all_profitable) >= 4 else "yellow")
    cprint(f"  └─ 15m vs 5m correlation: {'HIGH' if abs(avg_15m - avg_5m_combined) < 5 else 'MODERATE' if abs(avg_15m - avg_5m_combined) < 10 else 'LOW'}",
           "green" if abs(avg_15m - avg_5m_combined) < 5 else "yellow")

    # Detailed results
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📋 DETAILED RESULTS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    for r in results:
        consistent = r['all_positive']

        cprint(f"\n{r['pair']:15}", "green" if consistent else "yellow", attrs=["bold"])
        cprint(f"  Period 1 (Jul-Oct 5m): {r['period1_return']:+6.2f}%", "white")
        cprint(f"  Period 2 (Apr-Jun 5m): {r['period2_return']:+6.2f}%", "white")
        cprint(f"  Period 3 (Apr-Jul 15m): {r['period3_return']:+6.2f}%",
               "green" if r['period3_return'] > 8 else "white")
        cprint(f"  Trades: {r['trades']} ({r['trades_per_week']:.1f}/week), "
               f"WR: {r['win_rate']:.1f}%, Sharpe: {r['sharpe']:.2f}", "white")
        cprint(f"  Status: {'✅ Profitable on all 3 periods' if consistent else '⚠️  Mixed results'}",
               "green" if consistent else "yellow")

    # Final verdict
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"⚖️  FINAL VERDICT", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    consistency_rate = len(all_profitable) / len(results) * 100

    cprint(f"\n📊 Triple Validation Results:", "white")
    cprint(f"  ├─ Consistency Rate: {consistency_rate:.0f}% ({len(all_profitable)}/5 pairs)", "white")
    cprint(f"  ├─ Average 15m Return: {avg_15m:+.2f}%", "white")
    cprint(f"  └─ vs 5m Average: {avg_5m_combined:+.2f}%", "white")

    if consistency_rate >= 80 and avg_15m > 5:
        cprint(f"\n🎉 ULTIMATE VALIDATION PASSED!", "green", attrs=["bold"])
        cprint(f"   ✅ RSI(14) 20/80 works across:", "green")
        cprint(f"      • Multiple time periods (Jul-Oct, Apr-Jun, Apr-Jul)", "green")
        cprint(f"      • Multiple timeframes (5m AND 15m)", "green")
        cprint(f"      • {len(all_profitable)}/5 pairs profitable on ALL tests", "green")
        cprint(f"\n   Strategy is TRULY ROBUST! Ready for live testing!", "green", attrs=["bold"])
    elif consistency_rate >= 60 and avg_15m > 0:
        cprint(f"\n✅ STRONG VALIDATION!", "green")
        cprint(f"   RSI(14) 20/80 shows good consistency", "white")
        cprint(f"   {len(all_profitable)}/5 pairs work on all periods", "white")
        cprint(f"   Consider live paper trading on consistent pairs", "white")
    elif avg_15m > 0:
        cprint(f"\n⚠️  MODERATE VALIDATION", "yellow")
        cprint(f"   Strategy is profitable but with some variance", "white")
        cprint(f"   Focus on the {len(all_profitable)} consistently profitable pairs", "white")
    else:
        cprint(f"\n❌ VALIDATION FAILED", "red")
        cprint(f"   Strategy doesn't work on 15m timeframe", "red")
        cprint(f"   May be timeframe-specific overfitting", "red")

    # Recommendations
    if len(all_profitable) > 0:
        cprint(f"\n{'='*90}", "cyan")
        cprint(f"🚀 RECOMMENDED FOR LIVE TESTING", "green", attrs=["bold"])
        cprint(f"{'='*90}", "cyan")

        all_profitable.sort(key=lambda x: (x['period1_return'] + x['period2_return'] + x['period3_return'])/3, reverse=True)

        for i, r in enumerate(all_profitable, 1):
            avg_all = (r['period1_return'] + r['period2_return'] + r['period3_return']) / 3
            cprint(f"\n{i}. {r['pair']:15}", "green", attrs=["bold"])
            cprint(f"   Average across all 3 periods: {avg_all:+.2f}%", "white")
            cprint(f"   ├─ Period 1: {r['period1_return']:+.2f}%", "white")
            cprint(f"   ├─ Period 2: {r['period2_return']:+.2f}%", "white")
            cprint(f"   └─ Period 3: {r['period3_return']:+.2f}%", "white")

        cprint(f"\n🎯 Next Step: Hyperliquid Paper Trading", "cyan")
        cprint(f"  Deploy RSI(14) 20/80 on these {len(all_profitable)} pairs", "white")
        cprint(f"  Monitor for 1-2 weeks before real capital", "white")

    return results

if __name__ == "__main__":
    try:
        results = test_15m_validation()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Test interrupted", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
