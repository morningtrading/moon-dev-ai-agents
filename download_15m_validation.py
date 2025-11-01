#!/usr/bin/env python3
"""
🌙 Download 15m Data for Third Validation Period
April 2025 - July 2025 (15-minute timeframe)
Test RSI(14) 20/80 on different timeframe for ultimate robustness check
"""

import ccxt
import pandas as pd
from pathlib import Path
from termcolor import cprint
from datetime import datetime

# Top 5 performers
TOP_5_PAIRS = ['PENDLE/USDT', 'XTZ/USDT', 'QTUM/USDT', 'BCH/USDT', 'BNB/USDT']

START_DATE = "2025-04-01 00:00:00"
END_DATE = "2025-07-01 00:00:00"
TIMEFRAME = "15m"

OUTPUT_DIR = Path("/home/titus/Dropbox/user_data/data/binance_15m_validation")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def download_pair(exchange, symbol, start_date, end_date, timeframe='15m'):
    """Download OHLCV data for a single pair"""

    start_ts = int(datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S").timestamp() * 1000)
    end_ts = int(datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S").timestamp() * 1000)

    all_candles = []
    current_ts = start_ts

    while current_ts < end_ts:
        try:
            candles = exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                since=current_ts,
                limit=1000
            )

            if not candles:
                break

            all_candles.extend(candles)
            current_ts = candles[-1][0] + 1

            # Rate limiting
            import time
            time.sleep(0.5)

        except Exception as e:
            cprint(f"   Error: {str(e)[:50]}", "red")
            break

    if not all_candles:
        return None

    # Convert to DataFrame
    df = pd.DataFrame(all_candles, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
    df['date'] = pd.to_datetime(df['date'], unit='ms')

    # Filter to exact date range
    df = df[(df['date'] >= start_date) & (df['date'] < end_date)]

    return df

def main():
    cprint("\n🌙 Downloading 15m Data for Third Validation Period", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    cprint(f"\n📊 Period: April 1 - July 1, 2025 (15-minute timeframe)", "yellow")
    cprint(f"🎯 Pairs: Top 5 performers from RSI testing", "white")
    cprint(f"📁 Output: {OUTPUT_DIR}\n", "white")

    exchange = ccxt.binance()

    for i, symbol in enumerate(TOP_5_PAIRS, 1):
        pair_name = symbol.replace('/', '_')
        output_file = OUTPUT_DIR / f"{pair_name}-15m.feather"

        cprint(f"[{i}/5] Downloading {symbol:15} ", "white", end='')

        try:
            df = download_pair(exchange, symbol, START_DATE, END_DATE, TIMEFRAME)

            if df is not None and len(df) > 0:
                df.to_feather(output_file)

                days = (df['date'].max() - df['date'].min()).days
                cprint(f"✅ {len(df):,} candles ({days} days)", "green")
            else:
                cprint(f"❌ No data", "red")

        except Exception as e:
            cprint(f"❌ Error: {str(e)[:40]}", "red")

    cprint(f"\n{'='*90}", "cyan")
    cprint(f"✅ Download complete!", "green", attrs=["bold"])
    cprint(f"\n💡 This is the 3rd independent validation period:", "yellow")
    cprint(f"  1. Training: July-Oct 2025 (5m)", "white")
    cprint(f"  2. Testing: April-June 2025 (5m)", "white")
    cprint(f"  3. Validation: April-July 2025 (15m) ← NEW!", "green")
    cprint(f"\nIf RSI works on all 3 periods → Ultimate robustness confirmed!", "green")

if __name__ == "__main__":
    main()
