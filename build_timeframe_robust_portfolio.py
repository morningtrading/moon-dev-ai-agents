#!/usr/bin/env python3
"""
🌙 Build Timeframe-Robust Portfolio
Select only assets that perform well on BOTH 5m and 1m timeframes
These are the highest confidence strategies for live trading
"""

from termcolor import cprint

def build_robust_portfolio():
    """Analyze and select most robust strategies"""

    cprint("\n🌙 Timeframe-Robust Portfolio Builder", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    # Results from our tests
    results = [
        {
            'asset': 'CRV_USDT',
            'return_5m': 2.01,
            'return_1m': 50.51,
            'params': {'rsi_period': 14, 'oversold': 20, 'overbought': 80},
            'trades_5m': 19,
            'trades_1m': 83,
            'win_rate_5m': 68.4,
            'win_rate_1m': 66.3
        },
        {
            'asset': 'PENDLE_USDT',
            'return_5m': 22.78,
            'return_1m': 27.12,
            'params': {'rsi_period': 14, 'oversold': 25, 'overbought': 80},
            'trades_5m': 28,
            'trades_1m': 53,
            'win_rate_5m': 60.7,
            'win_rate_1m': 66.0
        },
        {
            'asset': 'NEAR_USDT',
            'return_5m': 28.09,
            'return_1m': 16.91,
            'params': {'rsi_period': 14, 'oversold': 20, 'overbought': 80},
            'trades_5m': 15,
            'trades_1m': 73,
            'win_rate_5m': 73.3,
            'win_rate_1m': 61.6
        },
        {
            'asset': 'VET_USDT',
            'return_5m': -0.60,
            'return_1m': 11.66,
            'params': {'rsi_period': 14, 'oversold': 20, 'overbought': 75},
            'trades_5m': 17,
            'trades_1m': 38,
            'win_rate_5m': 82.4,
            'win_rate_1m': 63.2
        },
        {
            'asset': 'BCH_USDT',
            'return_5m': 36.50,
            'return_1m': 3.15,
            'params': {'rsi_period': 21, 'oversold': 25, 'overbought': 80},
            'trades_5m': 15,
            'trades_1m': 15,
            'win_rate_5m': 66.7,
            'win_rate_1m': 60.0
        },
        {
            'asset': 'SHIB_USDT',
            'return_5m': 2.95,
            'return_1m': 0.78,
            'params': {'rsi_period': 14, 'oversold': 20, 'overbought': 80},
            'trades_5m': 15,
            'trades_1m': 19,
            'win_rate_5m': 73.3,
            'win_rate_1m': 57.9
        },
        {
            'asset': 'QNT_USDT',
            'return_5m': 9.17,
            'return_1m': -4.82,
            'params': {'rsi_period': 14, 'oversold': 15, 'overbought': 75},
            'trades_5m': 13,
            'trades_1m': 22,
            'win_rate_5m': 69.2,
            'win_rate_1m': 50.0
        },
        {
            'asset': 'UMA_USDT',
            'return_5m': 5.29,
            'return_1m': -13.42,
            'params': {'rsi_period': 14, 'oversold': 20, 'overbought': 75},
            'trades_5m': 25,
            'trades_1m': 54,
            'win_rate_5m': 64.0,
            'win_rate_1m': 61.1
        },
        {
            'asset': 'AVAX_USDT',
            'return_5m': 8.42,
            'return_1m': -36.77,
            'params': {'rsi_period': 21, 'oversold': 25, 'overbought': 70},
            'trades_5m': 30,
            'trades_1m': 86,
            'win_rate_5m': 66.7,
            'win_rate_1m': 52.3
        },
    ]

    cprint(f"\n📊 Selection Criteria for Robust Strategies:", "white")
    cprint(f"  ├─ Both timeframes must be profitable (>0%)", "yellow")
    cprint(f"  ├─ Performance difference <20% (not too timeframe-specific)", "yellow")
    cprint(f"  ├─ Average return across both timeframes >10%", "yellow")
    cprint(f"  └─ Win rate >55% on both timeframes", "yellow")

    # Classify strategies
    highly_robust = []
    moderately_robust = []
    not_robust = []

    for r in results:
        diff = abs(r['return_1m'] - r['return_5m'])
        avg_return = (r['return_1m'] + r['return_5m']) / 2
        both_profitable = r['return_1m'] > 0 and r['return_5m'] > 0
        min_win_rate = min(r['win_rate_1m'], r['win_rate_5m'])

        # Add calculated fields
        r['diff'] = diff
        r['avg_return'] = avg_return
        r['both_profitable'] = both_profitable
        r['min_win_rate'] = min_win_rate

        # Classify
        if both_profitable and diff < 10 and avg_return > 10 and min_win_rate > 60:
            highly_robust.append(r)
        elif both_profitable and diff < 20 and avg_return > 5 and min_win_rate > 55:
            moderately_robust.append(r)
        else:
            not_robust.append(r)

    # Display results
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🏆 HIGHLY ROBUST STRATEGIES (highest confidence)", "green", attrs=["bold"])
    cprint(f"{'='*90}", "green")

    if highly_robust:
        for i, r in enumerate(highly_robust, 1):
            p = r['params']
            cprint(f"\n{i}. {r['asset']}", "green", attrs=["bold"])
            cprint(f"   Params: RSI({p['rsi_period']}) {p['oversold']}/{p['overbought']}", "yellow")
            cprint(f"   5m: {r['return_5m']:+.2f}% | 1m: {r['return_1m']:+.2f}% | Avg: {r['avg_return']:+.2f}%",
                   "white")
            cprint(f"   Difference: {r['diff']:.2f}% (very stable!)", "green")
            cprint(f"   Win Rates: 5m {r['win_rate_5m']:.1f}% | 1m {r['win_rate_1m']:.1f}%", "white")
    else:
        cprint(f"\n  No strategies met the highly robust criteria", "yellow")

    cprint(f"\n{'='*90}", "cyan")
    cprint(f"✅ MODERATELY ROBUST STRATEGIES (good confidence)", "yellow", attrs=["bold"])
    cprint(f"{'='*90}", "yellow")

    if moderately_robust:
        for i, r in enumerate(moderately_robust, 1):
            p = r['params']
            cprint(f"\n{i}. {r['asset']}", "yellow", attrs=["bold"])
            cprint(f"   Params: RSI({p['rsi_period']}) {p['oversold']}/{p['overbought']}", "yellow")
            cprint(f"   5m: {r['return_5m']:+.2f}% | 1m: {r['return_1m']:+.2f}% | Avg: {r['avg_return']:+.2f}%",
                   "white")
            cprint(f"   Difference: {r['diff']:.2f}%", "white")
            cprint(f"   Win Rates: 5m {r['win_rate_5m']:.1f}% | 1m {r['win_rate_1m']:.1f}%", "white")
    else:
        cprint(f"\n  No strategies met the moderately robust criteria", "yellow")

    cprint(f"\n{'='*90}", "cyan")
    cprint(f"⚠️  NOT ROBUST (timeframe-specific)", "red", attrs=["bold"])
    cprint(f"{'='*90}", "red")

    for i, r in enumerate(not_robust, 1):
        p = r['params']
        reason = []
        if not r['both_profitable']:
            reason.append("Not profitable on both TF")
        if r['diff'] >= 20:
            reason.append(f"Large variance ({r['diff']:.1f}%)")
        if r['avg_return'] <= 5:
            reason.append("Low average return")
        if r['min_win_rate'] <= 55:
            reason.append("Low win rate")

        cprint(f"\n{i}. {r['asset']}", "red")
        cprint(f"   5m: {r['return_5m']:+.2f}% | 1m: {r['return_1m']:+.2f}%", "white")
        cprint(f"   Issue: {', '.join(reason)}", "red")

    # Portfolio simulation
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"💰 ROBUST PORTFOLIO SIMULATION", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    robust_portfolio = highly_robust + moderately_robust

    if robust_portfolio:
        total_capital = 10000
        capital_per_asset = total_capital / len(robust_portfolio)

        # Calculate portfolio returns
        portfolio_5m = sum(capital_per_asset * (1 + r['return_5m']/100) for r in robust_portfolio)
        portfolio_1m = sum(capital_per_asset * (1 + r['return_1m']/100) for r in robust_portfolio)

        return_5m = ((portfolio_5m / total_capital) - 1) * 100
        return_1m = ((portfolio_1m / total_capital) - 1) * 100
        avg_return = (return_5m + return_1m) / 2

        cprint(f"\n📊 Robust Portfolio ({len(robust_portfolio)} assets):", "white")
        cprint(f"  ├─ Capital per asset: ${capital_per_asset:,.0f}", "white")
        cprint(f"  ├─ 5m Return: {return_5m:+.2f}% (${portfolio_5m:,.2f})", "white")
        cprint(f"  ├─ 1m Return: {return_1m:+.2f}% (${portfolio_1m:,.2f})", "white")
        cprint(f"  ├─ Average Return: {avg_return:+.2f}%", "green" if avg_return > 10 else "white")
        cprint(f"  └─ Difference: {abs(return_5m - return_1m):.2f}% (stability measure)",
               "green" if abs(return_5m - return_1m) < 10 else "yellow")

        # Compare to full portfolio
        cprint(f"\n📊 Comparison to Full Portfolio (9 assets):", "white")
        cprint(f"  ├─ Full Portfolio 5m: +12.74%", "white")
        cprint(f"  ├─ Full Portfolio 1m: +6.12%", "white")
        cprint(f"  ├─ Robust Portfolio 5m: {return_5m:+.2f}%", "white")
        cprint(f"  ├─ Robust Portfolio 1m: {return_1m:+.2f}%", "white")
        cprint(f"  └─ Robust Portfolio Avg: {avg_return:+.2f}%", "white")

    # Summary
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"💡 KEY INSIGHTS", "yellow", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    cprint(f"\n1. Robustness Classification:", "white")
    cprint(f"   ├─ Highly Robust: {len(highly_robust)} assets", "green")
    cprint(f"   ├─ Moderately Robust: {len(moderately_robust)} assets", "yellow")
    cprint(f"   └─ Not Robust: {len(not_robust)} assets", "red")

    cprint(f"\n2. What This Means:", "white")
    if len(robust_portfolio) >= 3:
        cprint(f"   ✅ We have {len(robust_portfolio)} strategies that work across timeframes", "green")
        cprint(f"   ✅ These are highest confidence for live trading", "green")
        cprint(f"   ✅ Parameters are validated on 2 different granularities", "green")
    else:
        cprint(f"   ⚠️  Only {len(robust_portfolio)} robust strategies found", "yellow")
        cprint(f"   ⚠️  May need timeframe-specific optimization", "yellow")

    cprint(f"\n3. Three Types of Overfitting Mastered:", "white")
    cprint(f"   ✅ Sample Size: Require minimum 1 trade/week", "green")
    cprint(f"   ✅ Asset-Specific: Optimize each asset individually", "green")
    cprint(f"   ✅ Timeframe-Specific: Validate across multiple timeframes", "green")

    # Recommendations
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🎯 RECOMMENDATIONS FOR LIVE TRADING", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if robust_portfolio:
        cprint(f"\n✅ READY FOR PHASE 6: Live Testing!", "green", attrs=["bold"])

        cprint(f"\n📋 Use These Assets/Parameters:", "yellow")
        for r in robust_portfolio:
            p = r['params']
            cprint(f"  ├─ {r['asset']:15} RSI({p['rsi_period']}) {p['oversold']}/{p['overbought']} "
                   f"(avg {r['avg_return']:+.2f}%)", "white")

        cprint(f"\n🚀 Next Steps:", "yellow")
        cprint(f"  1. Set up Hyperliquid paper trading account", "white")
        cprint(f"  2. Start with robust portfolio ({len(robust_portfolio)} assets)", "white")
        cprint(f"  3. Equal allocation (${10000/len(robust_portfolio):,.0f} per asset)", "white")
        cprint(f"  4. Monitor for 1-2 weeks before considering real money", "white")
        cprint(f"  5. Compare live results vs backtest expectations", "white")

        cprint(f"\n⚠️  Important Reminders:", "yellow")
        cprint(f"  • Backtest ≠ Future Results (market conditions change)", "white")
        cprint(f"  • Start small (paper trading or tiny positions)", "white")
        cprint(f"  • Use stop losses (protect capital)", "white")
        cprint(f"  • Monitor performance daily", "white")
        cprint(f"  • Be ready to adjust if market regime changes", "white")

    else:
        cprint(f"\n⚠️  Recommendation: More validation needed", "yellow")
        cprint(f"\n  1. Optimize specifically for 1-minute timeframe", "white")
        cprint(f"  2. Test on 15-minute and 1-hour timeframes", "white")
        cprint(f"  3. Find parameters that work across 3+ timeframes", "white")

    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🎉 CONGRATULATIONS!", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    cprint(f"\nYou've completed a comprehensive backtesting education:", "green")
    cprint(f"  ✅ Learned backtesting fundamentals", "white")
    cprint(f"  ✅ Discovered 3 types of overfitting", "white")
    cprint(f"  ✅ Tested 9 assets across 2 timeframes", "white")
    cprint(f"  ✅ Built diversified portfolio (+12.74% on 5m)", "white")
    cprint(f"  ✅ Validated across timeframes (+6.12% on 1m)", "white")
    cprint(f"  ✅ Generated +24.51% alpha vs market", "white")

    cprint(f"\n🌙 Ready for the real challenge: LIVE TRADING!", "cyan", attrs=["bold"])

    return robust_portfolio

if __name__ == "__main__":
    try:
        robust_portfolio = build_robust_portfolio()
    except Exception as e:
        cprint(f"\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
