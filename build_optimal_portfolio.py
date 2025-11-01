#!/usr/bin/env python3
"""
🌙 Build Optimal Multi-Asset Portfolio
Optimize RSI parameters for EACH asset individually
Then show how a diversified portfolio would perform
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
    except:
        return None

def optimize_for_asset(df, asset_name, min_trades_per_week=1.0):
    """Find best RSI parameters for a single asset"""

    cprint(f"\n🔍 Optimizing {asset_name}...", "cyan")

    # Parameter grid (smaller for speed)
    rsi_periods = [14, 21]
    oversold_levels = [15, 20, 25, 30]
    overbought_levels = [70, 75, 80, 85]

    results = []
    days = (df.index[-1] - df.index[0]).days
    weeks = days / 7
    min_trades = weeks * min_trades_per_week

    for rsi_period in rsi_periods:
        for oversold in oversold_levels:
            for overbought in overbought_levels:
                if overbought - oversold < 30:
                    continue

                params = {
                    'rsi_period': rsi_period,
                    'oversold': oversold,
                    'overbought': overbought
                }

                result = run_backtest(df, params)

                if result and result['trades'] >= min_trades:
                    results.append({
                        'params': params,
                        **result
                    })

    if not results:
        cprint(f"  ❌ No valid strategies found (need {min_trades:.0f}+ trades)", "red")
        return None

    # Sort by return
    results.sort(key=lambda x: x['return'], reverse=True)
    best = results[0]

    p = best['params']
    cprint(f"  ✅ Best: RSI({p['rsi_period']}) {p['oversold']}/{p['overbought']} = "
           f"{best['return']:+.2f}% ({best['trades']} trades, {best['win_rate']:.1f}% WR)",
           "green" if best['return'] > 15 else "white")

    return best

def build_portfolio():
    """Optimize each asset individually and build a portfolio"""

    cprint("\n🌙 Building Optimal Multi-Asset Portfolio", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    # Target assets
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

    cprint(f"\n📊 Strategy: Optimize RSI parameters for each asset individually", "white")
    cprint(f"  ├─ Requirement: Minimum 1 trade per week", "white")
    cprint(f"  └─ Goal: Find best parameters for EACH asset, not one-size-fits-all", "white")

    portfolio = []

    for asset in target_assets:
        try:
            file_path = DATA_DIR / f"{asset}-5m.feather"
            if not file_path.exists():
                continue

            df = pd.read_feather(file_path)
            df = df.rename(columns={
                'open': 'Open', 'high': 'High', 'low': 'Low',
                'close': 'Close', 'volume': 'Volume'
            })
            df = df.set_index('date')

            # Optimize for this specific asset
            best = optimize_for_asset(df, asset)

            if best:
                market_return = ((df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1) * 100
                portfolio.append({
                    'asset': asset,
                    'params': best['params'],
                    'return': best['return'],
                    'market_return': market_return,
                    'alpha': best['return'] - market_return,
                    'trades': best['trades'],
                    'trades_per_week': best['trades_per_week'],
                    'win_rate': best['win_rate'],
                    'sharpe': best['sharpe'],
                    'max_dd': best['max_dd']
                })

        except Exception as e:
            cprint(f"\n❌ Error processing {asset}: {e}", "red")

    # Portfolio analysis
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🏆 OPTIMIZED PORTFOLIO RESULTS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    if not portfolio:
        cprint(f"\n⚠️ No valid strategies found!", "red")
        return

    # Sort by return
    portfolio.sort(key=lambda x: x['return'], reverse=True)

    # Summary stats
    avg_return = sum(p['return'] for p in portfolio) / len(portfolio)
    avg_market = sum(p['market_return'] for p in portfolio) / len(portfolio)
    avg_alpha = sum(p['alpha'] for p in portfolio) / len(portfolio)
    avg_trades_pw = sum(p['trades_per_week'] for p in portfolio) / len(portfolio)
    avg_win_rate = sum(p['win_rate'] for p in portfolio) / len(portfolio)

    cprint(f"\n📊 Portfolio Summary ({len(portfolio)} assets):", "white")
    cprint(f"  ├─ Average Strategy Return: {avg_return:+.2f}%", "green" if avg_return > 0 else "red")
    cprint(f"  ├─ Average Market Return: {avg_market:+.2f}%", "white")
    cprint(f"  ├─ Average Alpha: {avg_alpha:+.2f}%", "green" if avg_alpha > 0 else "red")
    cprint(f"  ├─ Average Trades/Week: {avg_trades_pw:.2f}", "white")
    cprint(f"  └─ Average Win Rate: {avg_win_rate:.1f}%", "white")

    # Show individual results
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📋 INDIVIDUAL ASSET STRATEGIES", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    for i, p in enumerate(portfolio, 1):
        params = p['params']
        color = "green" if p['return'] > 20 else "yellow" if p['return'] > 10 else "white"

        cprint(f"\n{i}. {p['asset']}", color, attrs=["bold"])
        cprint(f"   Optimal Params: RSI({params['rsi_period']}) {params['oversold']}/{params['overbought']}",
               "yellow")
        cprint(f"   Strategy Return: {p['return']:+.2f}% (Market: {p['market_return']:+.2f}%, Alpha: {p['alpha']:+.2f}%)",
               "white")
        cprint(f"   Trading Stats: {p['trades']} trades ({p['trades_per_week']:.1f}/wk), {p['win_rate']:.1f}% WR",
               "white")
        cprint(f"   Risk Metrics: Sharpe {p['sharpe']:.2f}, Max DD {p['max_dd']:.2f}%", "white")

    # Portfolio allocation simulation
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"💰 PORTFOLIO ALLOCATION SIMULATION", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    total_capital = 10000
    capital_per_asset = total_capital / len(portfolio)

    cprint(f"\n📊 Scenario: Equal allocation across {len(portfolio)} assets", "white")
    cprint(f"  ├─ Total Capital: ${total_capital:,.0f}", "white")
    cprint(f"  └─ Per Asset: ${capital_per_asset:,.0f}", "white")

    total_portfolio_value = 0
    for p in portfolio:
        asset_final = capital_per_asset * (1 + p['return']/100)
        total_portfolio_value += asset_final

    portfolio_return = ((total_portfolio_value / total_capital) - 1) * 100

    cprint(f"\n💵 Portfolio Performance:", "white")
    cprint(f"  ├─ Starting Capital: ${total_capital:,.0f}", "white")
    cprint(f"  ├─ Final Portfolio Value: ${total_portfolio_value:,.2f}", "white")
    cprint(f"  ├─ Portfolio Return: {portfolio_return:+.2f}%",
           "green" if portfolio_return > 0 else "red")
    cprint(f"  └─ Profit/Loss: ${total_portfolio_value - total_capital:+,.2f}",
           "green" if portfolio_return > 0 else "red")

    # Compare to benchmarks
    cprint(f"\n📊 Benchmark Comparison:", "white")
    cprint(f"  ├─ Optimized Portfolio: {portfolio_return:+.2f}%", "green" if portfolio_return > avg_market else "white")
    cprint(f"  ├─ Average Market (B&H): {avg_market:+.2f}%", "white")
    cprint(f"  └─ Alpha vs Market: {portfolio_return - avg_market:+.2f}%",
           "green" if portfolio_return > avg_market else "red")

    # Risk-adjusted performance
    cprint(f"\n⚖️  Risk-Adjusted Metrics:", "white")
    avg_sharpe = sum(p['sharpe'] for p in portfolio) / len(portfolio)
    avg_max_dd = sum(p['max_dd'] for p in portfolio) / len(portfolio)
    cprint(f"  ├─ Average Sharpe Ratio: {avg_sharpe:.2f}", "white")
    cprint(f"  └─ Average Max Drawdown: {avg_max_dd:.2f}%", "white")

    # Top performers
    cprint(f"\n🏆 Top 3 Performers:", "yellow", attrs=["bold"])
    for i, p in enumerate(portfolio[:3], 1):
        params = p['params']
        cprint(f"  {i}. {p['asset']:15} RSI({params['rsi_period']}) {params['oversold']}/{params['overbought']:3} → {p['return']:+6.2f}%",
               "green")

    # Diversification benefit
    best_single = portfolio[0]['return']
    diversification_benefit = portfolio_return - best_single

    cprint(f"\n💡 Key Insights:", "yellow", attrs=["bold"])
    cprint(f"\n  1. Asset-Specific Optimization Works!", "white")
    cprint(f"     └─ Each asset has its own optimal RSI parameters", "white")

    cprint(f"\n  2. Portfolio Return: {portfolio_return:+.2f}%", "white")
    if portfolio_return > 0:
        cprint(f"     └─ Profitable across {len(portfolio)} diverse assets!", "green")
    else:
        cprint(f"     └─ Portfolio would have lost money", "red")

    cprint(f"\n  3. Alpha Generation: {portfolio_return - avg_market:+.2f}%", "white")
    if portfolio_return > avg_market:
        cprint(f"     └─ Beat market by {portfolio_return - avg_market:.2f}%!", "green")
    else:
        cprint(f"     └─ Underperformed market", "red")

    cprint(f"\n  4. Diversification Effect:", "white")
    if diversification_benefit < 0:
        cprint(f"     └─ Reduced risk but also reduced returns vs single best asset", "yellow")
        cprint(f"     └─ Best single: {best_single:.2f}% vs Portfolio: {portfolio_return:.2f}%", "white")
    else:
        cprint(f"     └─ Diversification improved returns!", "green")

    # Next steps
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"🎯 NEXT STEPS", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    cprint(f"\n1. ✅ Asset-Specific Optimization: DONE", "green")
    cprint(f"   └─ Each asset has optimal parameters", "white")

    cprint(f"\n2. 📊 Further Validation:", "yellow")
    cprint(f"   ├─ Test these parameters on 1-minute timeframe", "white")
    cprint(f"   ├─ Test on different time periods (walk-forward)", "white")
    cprint(f"   └─ Check if parameters are stable over time", "white")

    cprint(f"\n3. 🎨 Portfolio Construction:", "yellow")
    cprint(f"   ├─ Select top 3-5 performers", "white")
    cprint(f"   ├─ Consider risk-adjusted returns (Sharpe ratio)", "white")
    cprint(f"   └─ Allocate more capital to better performers", "white")

    cprint(f"\n4. 🚀 Live Testing:", "yellow")
    cprint(f"   ├─ Start with Hyperliquid paper trading", "white")
    cprint(f"   ├─ Test on real-time data", "white")
    cprint(f"   └─ Monitor performance vs backtest", "white")

    return portfolio

if __name__ == "__main__":
    try:
        portfolio = build_portfolio()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Portfolio building interrupted", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
