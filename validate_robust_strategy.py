#!/usr/bin/env python3
"""
🌙 Validate Robust Strategy Across Multiple Assets
Test if RSI(21) 25/75 works on all our profitable assets
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

        # Calculate time period for trades per week
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

def validate_across_assets():
    """Test robust strategy on all previously profitable assets"""

    cprint("\n🌙 Robust Strategy Validation Across Assets", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    # Assets that were profitable with RSI 20/80
    target_assets = [
        'NEAR_USDT',
        'PENDLE_USDT',
        'VET_USDT',
        'BCH_USDT',
        'AVAX_USDT',
        'SHIB_USDT',
        'CRV_USDT',
        'UMA_USDT',
        'QNT_USDT'
    ]

    # Two strategies to compare
    original_params = {'rsi_period': 14, 'oversold': 20, 'overbought': 80}
    robust_params = {'rsi_period': 21, 'oversold': 25, 'overbought': 75}

    cprint(f"\n📊 Testing Strategy on {len(target_assets)} Assets:", "white")
    cprint(f"  ├─ Original: RSI(14) 20/80", "yellow")
    cprint(f"  └─ Robust: RSI(21) 25/75 (found from NEAR optimization)", "green")

    results = []

    for i, asset in enumerate(target_assets, 1):
        try:
            # Load data
            file_path = DATA_DIR / f"{asset}-5m.feather"
            if not file_path.exists():
                cprint(f"  [{i:2d}/{len(target_assets)}] ✗ {asset:15} File not found", "red")
                continue

            df = pd.read_feather(file_path)
            df = df.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            df = df.set_index('date')

            # Test both strategies
            original_result = run_backtest(df, original_params)
            robust_result = run_backtest(df, robust_params)

            if original_result and robust_result:
                # Calculate market return
                market_return = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100

                result = {
                    'asset': asset,
                    'market_return': market_return,
                    'original_return': original_result['return'],
                    'original_trades': original_result['trades'],
                    'original_trades_per_week': original_result['trades_per_week'],
                    'original_win_rate': original_result['win_rate'],
                    'robust_return': robust_result['return'],
                    'robust_trades': robust_result['trades'],
                    'robust_trades_per_week': robust_result['trades_per_week'],
                    'robust_win_rate': robust_result['win_rate'],
                    'improvement': robust_result['return'] - original_result['return']
                }
                results.append(result)

                # Progress indicator
                status = "🎯" if robust_result['return'] > original_result['return'] else "✓"
                improvement = robust_result['return'] - original_result['return']
                cprint(f"  [{i:2d}/{len(target_assets)}] {status} {asset:15} "
                       f"Original: {original_result['return']:+6.2f}% → "
                       f"Robust: {robust_result['return']:+6.2f}% "
                       f"({improvement:+.2f}%)",
                       "green" if improvement > 0 else "yellow")
            else:
                cprint(f"  [{i:2d}/{len(target_assets)}] ✗ {asset:15} Backtest failed", "red")

        except Exception as e:
            cprint(f"  [{i:2d}/{len(target_assets)}] ✗ {asset:15} Error: {str(e)[:40]}", "red")

    # Analysis
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📊 VALIDATION RESULTS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if not results:
        cprint(f"\n⚠️ No results to analyze!", "red")
        return

    # Count wins
    robust_wins = sum(1 for r in results if r['improvement'] > 0)
    original_wins = sum(1 for r in results if r['improvement'] < 0)
    ties = sum(1 for r in results if r['improvement'] == 0)

    cprint(f"\n🏆 Head-to-Head Comparison:", "white")
    cprint(f"  ├─ Robust Strategy Wins: {robust_wins}/{len(results)}", "green" if robust_wins > original_wins else "white")
    cprint(f"  ├─ Original Strategy Wins: {original_wins}/{len(results)}", "green" if original_wins > robust_wins else "white")
    cprint(f"  └─ Ties: {ties}/{len(results)}", "white")

    # Average performance
    avg_original = sum(r['original_return'] for r in results) / len(results)
    avg_robust = sum(r['robust_return'] for r in results) / len(results)
    avg_improvement = sum(r['improvement'] for r in results) / len(results)

    cprint(f"\n📈 Average Performance:", "white")
    cprint(f"  ├─ Original RSI(14) 20/80: {avg_original:+.2f}%", "white")
    cprint(f"  ├─ Robust RSI(21) 25/75: {avg_robust:+.2f}%", "green" if avg_robust > avg_original else "white")
    cprint(f"  └─ Average Improvement: {avg_improvement:+.2f}%", "green" if avg_improvement > 0 else "red")

    # Trade frequency analysis
    avg_original_tpw = sum(r['original_trades_per_week'] for r in results) / len(results)
    avg_robust_tpw = sum(r['robust_trades_per_week'] for r in results) / len(results)

    cprint(f"\n📊 Trade Frequency (Trades per Week):", "white")
    cprint(f"  ├─ Original: {avg_original_tpw:.2f}", "white")
    cprint(f"  ├─ Robust: {avg_robust_tpw:.2f}", "white")
    cprint(f"  └─ Both meet minimum 1/week? {avg_robust_tpw >= 1 and avg_original_tpw >= 1}",
           "green" if avg_robust_tpw >= 1 and avg_original_tpw >= 1 else "yellow")

    # Detailed breakdown
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📋 DETAILED ASSET BREAKDOWN", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    # Sort by improvement
    results.sort(key=lambda x: x['improvement'], reverse=True)

    for i, r in enumerate(results, 1):
        color = "green" if r['improvement'] > 0 else "red" if r['improvement'] < 0 else "yellow"

        cprint(f"\n{i}. {r['asset']}", color, attrs=["bold"])
        cprint(f"   Market Return: {r['market_return']:+.2f}%", "white")
        cprint(f"   Original: {r['original_return']:+.2f}% ({r['original_trades']} trades, {r['original_trades_per_week']:.1f}/wk, {r['original_win_rate']:.1f}% WR)", "white")
        cprint(f"   Robust:   {r['robust_return']:+.2f}% ({r['robust_trades']} trades, {r['robust_trades_per_week']:.1f}/wk, {r['robust_win_rate']:.1f}% WR)", "white")
        cprint(f"   Improvement: {r['improvement']:+.2f}%", color)

    # Conclusion
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"💡 CONCLUSION", "yellow", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if avg_improvement > 5:
        cprint(f"\n✅ ROBUST STRATEGY IS SIGNIFICANTLY BETTER!", "green", attrs=["bold"])
        cprint(f"   Average improvement of {avg_improvement:+.2f}% across {len(results)} assets", "green")
        cprint(f"   Use RSI(21) 25/75 as your default strategy!", "green")
    elif avg_improvement > 0:
        cprint(f"\n✅ Robust strategy is slightly better", "green")
        cprint(f"   Average improvement of {avg_improvement:+.2f}% across {len(results)} assets", "white")
        cprint(f"   Both strategies are viable, but robust has edge", "white")
    elif avg_improvement > -5:
        cprint(f"\n⚠️  Strategies perform similarly", "yellow")
        cprint(f"   Average difference of {avg_improvement:+.2f}% across {len(results)} assets", "white")
        cprint(f"   Choose based on asset-specific performance", "white")
    else:
        cprint(f"\n❌ Original strategy performs better overall", "red")
        cprint(f"   Robust strategy underperforms by {abs(avg_improvement):.2f}% on average", "red")
        cprint(f"   The NEAR optimization may not generalize well", "red")

    # Next steps
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🎯 NEXT STEPS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    cprint(f"\n1. 📊 Further Validation:", "yellow")
    cprint(f"   ├─ Test on 1-minute timeframe data", "white")
    cprint(f"   └─ Scan all 79 pairs for more opportunities", "white")

    cprint(f"\n2. 🔧 Optimization:", "yellow")
    cprint(f"   ├─ Optimize parameters for each asset individually", "white")
    cprint(f"   └─ Find asset-specific best parameters", "white")

    cprint(f"\n3. 📈 Portfolio Building:", "yellow")
    cprint(f"   ├─ Select top 3-5 assets with best performance", "white")
    cprint(f"   ├─ Allocate capital across multiple strategies", "white")
    cprint(f"   └─ Diversify to reduce risk", "white")

    cprint(f"\n4. 🚀 Live Testing:", "yellow")
    cprint(f"   ├─ Move to Hyperliquid paper trading", "white")
    cprint(f"   └─ Test strategies with real market conditions", "white")

    return results

if __name__ == "__main__":
    try:
        results = validate_across_assets()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Validation interrupted", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
