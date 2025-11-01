#!/usr/bin/env python3
"""
🌙 Download Walk-Forward Data for Top 15 Profitable Pairs
Fast targeted download - only pairs we know are profitable
"""

import ccxt
import pandas as pd
from pathlib import Path
from datetime import datetime
from termcolor import cprint
import time

OUTPUT_DIR = Path("/home/titus/Dropbox/user_data/data/binance_walkforward")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Time period: April-June 2025 (BEFORE our July-Oct training data)
START_DATE = "2025-04-01"
END_DATE = "2025-07-01"

# Top 15 profitable pairs from our comprehensive scan
TOP_15_PAIRS = [
    'NEAR/USDT',
    'PENDLE/USDT',
    'QTUM/USDT',
    'LRC/USDT',
    'BNB/USDT',
    'XTZ/USDT',
    'BCH/USDT',
    'AVAX/USDT',
    'ZRX/USDT',
    'ALGO/USDT',
    'RVN/USDT',
    'SHIB/USDT',
    'CRV/USDT',
    'UMA/USDT',
    'QNT/USDT'
]

def download_ohlcv(exchange, symbol, timeframe, start_date, end_date):
    """Download OHLCV data"""
    since = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
    end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

    all_data = []
    current_ts = since

    while current_ts < end_ts:
        try:
            ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=current_ts, limit=1000)
            if not ohlcv:
                break
            all_data.extend(ohlcv)
            current_ts = ohlcv[-1][0] + 1
            time.sleep(exchange.rateLimit / 1000)
        except Exception as e:
            cprint(f"    Error: {str(e)[:50]}", "red")
            break

    if not all_data:
        return None

    df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df = df.drop('timestamp', axis=1)
    df = df[df['date'] >= start_date]
    df = df[df['date'] < end_date]

    return df

def main():
    cprint("\n🌙 Downloading Walk-Forward Data - Top 15 Pairs Only", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    cprint(f"\n⚡ Fast Mode: Downloading only profitable pairs", "yellow")
    cprint(f"  ├─ Pairs: {len(TOP_15_PAIRS)}", "white")
    cprint(f"  ├─ Timeframes: 5m only (for speed)", "white")
    cprint(f"  └─ Period: {START_DATE} to {END_DATE}", "white")

    cprint(f"\n💡 Walk-Forward Test:", "yellow")
    cprint(f"  Training period: July-October 2025 (current data)", "white")
    cprint(f"  Testing period: April-June 2025 (new data)", "green")
    cprint(f"  Purpose: Validate strategies work in different time period!", "green")

    exchange = ccxt.binance({'enableRateLimit': True, 'options': {'defaultType': 'spot'}})
    exchange.load_markets()

    cprint(f"\n📥 Downloading...\n", "cyan")

    successful = 0
    failed = 0

    for i, symbol in enumerate(TOP_15_PAIRS, 1):
        pair_name = symbol.replace('/', '_')
        output_file = OUTPUT_DIR / f"{pair_name}-5m.feather"

        if output_file.exists():
            cprint(f"  [{i:2d}/{len(TOP_15_PAIRS)}] ✓ {pair_name:20} Already exists", "white")
            successful += 1
            continue

        try:
            df = download_ohlcv(exchange, symbol, '5m', START_DATE, END_DATE)

            if df is not None and len(df) > 0:
                df.reset_index(drop=True, inplace=True)
                df.to_feather(output_file)
                days = (df['date'].max() - df['date'].min()).days
                cprint(f"  [{i:2d}/{len(TOP_15_PAIRS)}] ✅ {pair_name:20} {len(df):,} candles ({days} days)", "green")
                successful += 1
            else:
                cprint(f"  [{i:2d}/{len(TOP_15_PAIRS)}] ⚠️  {pair_name:20} No data", "yellow")
                failed += 1

        except Exception as e:
            cprint(f"  [{i:2d}/{len(TOP_15_PAIRS)}] ❌ {pair_name:20} {str(e)[:30]}", "red")
            failed += 1

    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📊 DOWNLOAD COMPLETE", "green", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    cprint(f"\n✅ Downloaded: {successful}/{len(TOP_15_PAIRS)}", "green")
    if failed > 0:
        cprint(f"❌ Failed: {failed}", "red")

    cprint(f"\n📁 Files saved to: {OUTPUT_DIR}", "yellow")

    cprint(f"\n🚀 Ready to run walk-forward test!", "green", attrs=["bold"])
    cprint(f"  Next: Test RSI(14) 20/80 on April-June data", "white")
    cprint(f"  Compare: Returns from both periods", "white")
    cprint(f"  Goal: Find strategies that work ACROSS time!", "white")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n\n⚠️ Download interrupted", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
