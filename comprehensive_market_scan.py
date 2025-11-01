#!/usr/bin/env python3
"""
🌙 Comprehensive Market Scan - All 79 Pairs
Scan EVERY asset to find all profitable RSI opportunities
Build complete knowledge of the market landscape
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
            'best_trade': results['Best Trade [%]'],
            'worst_trade': results['Worst Trade [%]'],
            'final_equity': results['Equity Final [$]']
        }
    except Exception as e:
        return None

def comprehensive_scan():
    """Scan all 79 pairs with standard RSI strategy"""

    cprint("\n🌙 Comprehensive Market Scan - All 79 Pairs", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    # Standard strategy we've been using
    standard_params = {'rsi_period': 14, 'oversold': 20, 'overbought': 80}

    cprint(f"\n📊 Strategy: RSI(14) 20/80", "yellow")
    cprint(f"  ├─ The strategy that worked on 9/9 initial profitable assets", "white")
    cprint(f"  ├─ Testing on ALL 79 pairs to find complete opportunity set", "white")
    cprint(f"  └─ Filter: Minimum 1 trade per week for statistical validity", "white")

    # Find all 5m files
    files = sorted(DATA_DIR.glob("*-5m.feather"))

    cprint(f"\n🔍 Found {len(files)} trading pairs to analyze...\n", "cyan")

    results = []
    errors = []

    for i, file in enumerate(files, 1):
        pair = file.stem.replace('-5m', '')

        try:
            # Load data
            df = pd.read_feather(file)
            df = df.rename(columns={
                'open': 'Open', 'high': 'High', 'low': 'Low',
                'close': 'Close', 'volume': 'Volume'
            })
            df = df.set_index('date')

            # Calculate market return
            market_return = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100

            # Run backtest
            result = run_backtest(df, standard_params)

            if result:
                days = (df.index[-1] - df.index[0]).days
                weeks = days / 7
                min_trades = weeks  # 1 per week

                # Store result
                res = {
                    'pair': pair,
                    'return': result['return'],
                    'market_return': market_return,
                    'alpha': result['return'] - market_return,
                    'trades': result['trades'],
                    'trades_per_week': result['trades_per_week'],
                    'win_rate': result['win_rate'],
                    'sharpe': result['sharpe'],
                    'max_dd': result['max_dd'],
                    'avg_trade': result['avg_trade'],
                    'best_trade': result['best_trade'],
                    'worst_trade': result['worst_trade'],
                    'meets_min_trades': result['trades'] >= min_trades,
                    'profitable': result['return'] > 0
                }
                results.append(res)

                # Progress indicator
                status = "🎯" if res['profitable'] and res['meets_min_trades'] else \
                         "✓" if res['profitable'] else "✗"

                color = "green" if res['profitable'] and res['meets_min_trades'] else \
                        "yellow" if res['profitable'] else "white"

                cprint(f"  [{i:3d}/{len(files)}] {status} {pair:20} "
                       f"Return: {result['return']:+7.2f}% | "
                       f"Trades: {result['trades']:3d} ({result['trades_per_week']:.1f}/wk) | "
                       f"WR: {result['win_rate']:5.1f}%", color)

        except Exception as e:
            errors.append({'pair': pair, 'error': str(e)})
            cprint(f"  [{i:3d}/{len(files)}] ✗ {pair:20} ERROR: {str(e)[:40]}", "red")

    # Analysis
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📊 COMPREHENSIVE SCAN RESULTS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if not results:
        cprint(f"\n⚠️ No valid results!", "red")
        return

    # Statistics
    total_tested = len(results)
    profitable = [r for r in results if r['profitable']]
    unprofitable = [r for r in results if not r['profitable']]

    meets_min_trades = [r for r in results if r['meets_min_trades']]
    profitable_and_valid = [r for r in results if r['profitable'] and r['meets_min_trades']]

    avg_return_all = sum(r['return'] for r in results) / len(results)
    avg_return_profitable = sum(r['return'] for r in profitable) / len(profitable) if profitable else 0
    avg_market_return = sum(r['market_return'] for r in results) / len(results)

    cprint(f"\n📈 Overall Statistics:", "white")
    cprint(f"  ├─ Total Pairs Tested: {total_tested}", "white")
    cprint(f"  ├─ Profitable: {len(profitable)} ({len(profitable)/total_tested*100:.1f}%)",
           "green" if len(profitable) > 0 else "red")
    cprint(f"  ├─ Unprofitable: {len(unprofitable)} ({len(unprofitable)/total_tested*100:.1f}%)", "white")
    cprint(f"  ├─ Meet Min Trades: {len(meets_min_trades)} ({len(meets_min_trades)/total_tested*100:.1f}%)", "white")
    cprint(f"  └─ Profitable + Valid: {len(profitable_and_valid)} ({len(profitable_and_valid)/total_tested*100:.1f}%)",
           "green" if len(profitable_and_valid) > 0 else "yellow")

    cprint(f"\n💰 Return Statistics:", "white")
    cprint(f"  ├─ Average Strategy Return: {avg_return_all:+.2f}%",
           "green" if avg_return_all > 0 else "red")
    cprint(f"  ├─ Average Market Return: {avg_market_return:+.2f}%", "white")
    cprint(f"  ├─ Average Alpha: {avg_return_all - avg_market_return:+.2f}%",
           "green" if avg_return_all > avg_market_return else "red")
    cprint(f"  └─ Avg Return (Profitable Only): {avg_return_profitable:+.2f}%", "green")

    # Sort by return
    results.sort(key=lambda x: x['return'], reverse=True)

    # Top performers
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🏆 TOP 20 PERFORMERS (All Pairs)", "green", attrs=["bold"])
    cprint(f"{'='*90}", "green")

    for i, r in enumerate(results[:20], 1):
        valid = "✅" if r['meets_min_trades'] else "⚠️ "
        color = "green" if r['meets_min_trades'] else "yellow"

        cprint(f"\n{i:2d}. {r['pair']:20} {valid}", color, attrs=["bold"])
        cprint(f"    Return: {r['return']:+7.2f}% | Market: {r['market_return']:+7.2f}% | Alpha: {r['alpha']:+7.2f}%",
               "white")
        cprint(f"    Trades: {r['trades']:3d} ({r['trades_per_week']:.1f}/wk) | WR: {r['win_rate']:5.1f}% | "
               f"Sharpe: {r['sharpe']:.2f}", "white")
        cprint(f"    Avg Trade: {r['avg_trade']:+.2f}% | Best: {r['best_trade']:+.2f}% | "
               f"Worst: {r['worst_trade']:+.2f}%", "white")

    # Valid profitable strategies only
    if profitable_and_valid:
        cprint(f"\n{'='*90}", "cyan")
        cprint(f"✅ STATISTICALLY VALID PROFITABLE STRATEGIES ({len(profitable_and_valid)} pairs)",
               "green", attrs=["bold"])
        cprint(f"{'='*90}", "green")

        profitable_and_valid.sort(key=lambda x: x['return'], reverse=True)

        for i, r in enumerate(profitable_and_valid, 1):
            cprint(f"\n{i:2d}. {r['pair']:20}", "green", attrs=["bold"])
            cprint(f"    Return: {r['return']:+7.2f}% | Alpha: {r['alpha']:+7.2f}%", "white")
            cprint(f"    Trades: {r['trades']:3d} ({r['trades_per_week']:.1f}/wk) | WR: {r['win_rate']:5.1f}%",
                   "white")

    # Bottom performers
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"💀 WORST 10 PERFORMERS (Avoid These!)", "red", attrs=["bold"])
    cprint(f"{'='*90}", "red")

    for i, r in enumerate(results[-10:], 1):
        cprint(f"\n{i:2d}. {r['pair']:20}", "red")
        cprint(f"    Return: {r['return']:+7.2f}% | Market: {r['market_return']:+7.2f}%", "white")
        cprint(f"    Trades: {r['trades']:3d} ({r['trades_per_week']:.1f}/wk) | WR: {r['win_rate']:5.1f}%",
               "white")

    # Market condition analysis
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📊 MARKET CONDITION ANALYSIS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    uptrends = [r for r in results if r['market_return'] > 15]
    downtrends = [r for r in results if r['market_return'] < -15]
    sideways = [r for r in results if -15 <= r['market_return'] <= 15]

    cprint(f"\n📈 Market Conditions in Dataset:", "white")
    cprint(f"  ├─ Uptrends (>15%): {len(uptrends)} pairs", "green")
    cprint(f"  ├─ Downtrends (<-15%): {len(downtrends)} pairs", "red")
    cprint(f"  └─ Sideways (-15% to 15%): {len(sideways)} pairs", "yellow")

    # RSI performance by market condition
    uptrend_profitable = [r for r in uptrends if r['profitable']]
    downtrend_profitable = [r for r in downtrends if r['profitable']]
    sideways_profitable = [r for r in sideways if r['profitable']]

    cprint(f"\n💡 RSI Strategy Success Rate by Market Condition:", "yellow")
    cprint(f"  ├─ Uptrends: {len(uptrend_profitable)}/{len(uptrends)} profitable "
           f"({len(uptrend_profitable)/len(uptrends)*100 if uptrends else 0:.1f}%)",
           "green" if uptrends and len(uptrend_profitable)/len(uptrends) > 0.5 else "red")
    cprint(f"  ├─ Downtrends: {len(downtrend_profitable)}/{len(downtrends)} profitable "
           f"({len(downtrend_profitable)/len(downtrends)*100 if downtrends else 0:.1f}%)",
           "green" if downtrends and len(downtrend_profitable)/len(downtrends) > 0.5 else "red")
    cprint(f"  └─ Sideways: {len(sideways_profitable)}/{len(sideways)} profitable "
           f"({len(sideways_profitable)/len(sideways)*100 if sideways else 0:.1f}%)",
           "green" if sideways and len(sideways_profitable)/len(sideways) > 0.5 else "red")

    # Portfolio simulation
    if profitable_and_valid:
        cprint(f"\n{'='*90}", "cyan")
        cprint(f"💰 MEGA PORTFOLIO SIMULATION", "cyan", attrs=["bold"])
        cprint(f"{'='*90}", "cyan")

        # Different portfolio scenarios
        portfolios = [
            ("Top 5", profitable_and_valid[:5]),
            ("Top 10", profitable_and_valid[:10]),
            ("Top 20", profitable_and_valid[:20] if len(profitable_and_valid) >= 20 else profitable_and_valid),
            ("All Valid", profitable_and_valid)
        ]

        for name, assets in portfolios:
            if not assets:
                continue

            total_capital = 10000
            capital_per_asset = total_capital / len(assets)

            total_value = sum(capital_per_asset * (1 + r['return']/100) for r in assets)
            portfolio_return = ((total_value / total_capital) - 1) * 100

            avg_alpha = sum(r['alpha'] for r in assets) / len(assets)
            avg_win_rate = sum(r['win_rate'] for r in assets) / len(assets)

            cprint(f"\n{name} Portfolio ({len(assets)} assets):", "yellow")
            cprint(f"  ├─ Capital per asset: ${capital_per_asset:,.0f}", "white")
            cprint(f"  ├─ Portfolio Return: {portfolio_return:+.2f}%",
                   "green" if portfolio_return > 10 else "white")
            cprint(f"  ├─ Average Alpha: {avg_alpha:+.2f}%", "white")
            cprint(f"  ├─ Average Win Rate: {avg_win_rate:.1f}%", "white")
            cprint(f"  └─ Final Value: ${total_value:,.2f}", "white")

    # Summary insights
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"💡 KEY INSIGHTS FROM COMPLETE MARKET SCAN", "yellow", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    cprint(f"\n1. RSI Strategy Success Rate:", "white")
    success_rate = len(profitable_and_valid) / total_tested * 100
    cprint(f"   └─ {len(profitable_and_valid)}/{total_tested} pairs are profitable with valid sample size "
           f"({success_rate:.1f}%)",
           "green" if success_rate > 20 else "yellow" if success_rate > 10 else "red")

    cprint(f"\n2. Market Environment:", "white")
    if avg_market_return < -5:
        cprint(f"   └─ Average market return {avg_market_return:.2f}% (bear market/down trending)", "red")
        cprint(f"   └─ This is PERFECT for mean-reversion strategies!", "green")
    elif avg_market_return > 5:
        cprint(f"   └─ Average market return {avg_market_return:.2f}% (bull market/up trending)", "green")
        cprint(f"   └─ Mean-reversion underperforms in strong trends", "yellow")
    else:
        cprint(f"   └─ Average market return {avg_market_return:.2f}% (sideways/choppy)", "yellow")
        cprint(f"   └─ IDEAL conditions for RSI mean-reversion", "green")

    cprint(f"\n3. Alpha Generation:", "white")
    if avg_return_all > avg_market_return:
        cprint(f"   └─ Strategy beats market by {avg_return_all - avg_market_return:.2f}% on average!", "green")
    else:
        cprint(f"   └─ Strategy underperforms market by {abs(avg_return_all - avg_market_return):.2f}%", "red")

    cprint(f"\n4. Best Opportunities:", "white")
    if profitable_and_valid:
        top_3 = profitable_and_valid[:3]
        cprint(f"   Top 3 assets for RSI(14) 20/80:", "green")
        for r in top_3:
            cprint(f"   ├─ {r['pair']:15} {r['return']:+7.2f}% ({r['trades']} trades, {r['win_rate']:.1f}% WR)",
                   "white")

    # Errors summary
    if errors:
        cprint(f"\n⚠️  Errors Encountered: {len(errors)}", "yellow")
        for err in errors[:5]:
            cprint(f"   ├─ {err['pair']}: {err['error'][:50]}", "white")

    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🎯 RECOMMENDATIONS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if len(profitable_and_valid) >= 10:
        cprint(f"\n✅ Excellent! You have {len(profitable_and_valid)} valid profitable strategies", "green")
        cprint(f"\n📋 Next Steps:", "yellow")
        cprint(f"  1. Build diversified portfolio with top 10-20 performers", "white")
        cprint(f"  2. Validate top performers on 1-minute timeframe", "white")
        cprint(f"  3. Select 5-10 most robust for live testing", "white")
        cprint(f"  4. Move to Hyperliquid paper trading", "white")
    elif len(profitable_and_valid) >= 5:
        cprint(f"\n✅ Good! You have {len(profitable_and_valid)} valid profitable strategies", "green")
        cprint(f"\n📋 Next Steps:", "yellow")
        cprint(f"  1. Validate these on 1-minute timeframe", "white")
        cprint(f"  2. Consider asset-specific optimization for each", "white")
        cprint(f"  3. Build focused portfolio with your best 3-5", "white")
    else:
        cprint(f"\n⚠️  Only {len(profitable_and_valid)} valid profitable strategies found", "yellow")
        cprint(f"\n📋 Recommendations:", "yellow")
        cprint(f"  1. Try different RSI parameters (optimize each asset)", "white")
        cprint(f"  2. Test different strategy types (trend-following)", "white")
        cprint(f"  3. Focus on assets in sideways/down markets", "white")

    return results

if __name__ == "__main__":
    try:
        results = comprehensive_scan()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Scan interrupted", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
