#!/usr/bin/env python3
"""
🌙 Download Binance Historical Data for Walk-Forward Testing
Download April-June 2025 data (3 months BEFORE current Jul-Oct period)
This tests if strategies work across different time periods
"""

import ccxt
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from termcolor import cprint
import time

# Output directory
OUTPUT_DIR = Path("/home/titus/Dropbox/user_data/data/binance_walkforward")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Time period for walk-forward test
START_DATE = "2025-04-01"  # April 1, 2025
END_DATE = "2025-07-01"    # July 1, 2025 (3 months)

def download_ohlcv(exchange, symbol, timeframe, start_date, end_date):
    """Download OHLCV data from Binance"""

    # Convert dates to timestamps
    since = int(datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000)
    end_ts = int(datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000)

    all_data = []
    current_ts = since

    while current_ts < end_ts:
        try:
            # Fetch data
            ohlcv = exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                since=current_ts,
                limit=1000  # Max per request
            )

            if not ohlcv:
                break

            all_data.extend(ohlcv)

            # Move to next batch
            current_ts = ohlcv[-1][0] + 1

            # Rate limiting
            time.sleep(exchange.rateLimit / 1000)

        except Exception as e:
            cprint(f"    Error fetching data: {e}", "red")
            break

    if not all_data:
        return None

    # Convert to DataFrame
    df = pd.DataFrame(all_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['date'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
    df = df.drop('timestamp', axis=1)

    # Filter to exact date range
    df = df[df['date'] >= start_date]
    df = df[df['date'] < end_date]

    return df

def download_all_pairs():
    """Download walk-forward data for all pairs"""

    cprint("\n🌙 Downloading Walk-Forward Test Data", "cyan", attrs=["bold"])
    cprint("=" * 90, "cyan")

    cprint(f"\n📊 Time Period:", "white")
    cprint(f"  ├─ Start: {START_DATE}", "yellow")
    cprint(f"  ├─ End: {END_DATE}", "yellow")
    cprint(f"  └─ Duration: 3 months (91 days)", "yellow")

    cprint(f"\n💡 Why This Matters:", "yellow")
    cprint(f"  Current data: July-October 2025", "white")
    cprint(f"  New data: April-June 2025 (3 months EARLIER)", "white")
    cprint(f"  Test: Do strategies work in DIFFERENT time period?", "green")
    cprint(f"  Detects: Time-period overfitting (Type 4!)", "green")

    # Initialize Binance exchange
    exchange = ccxt.binance({
        'enableRateLimit': True,
        'options': {'defaultType': 'spot'}
    })

    # Get all USDT pairs
    cprint(f"\n🔍 Fetching available pairs...", "cyan")
    markets = exchange.load_markets()
    usdt_pairs = [s for s in markets.keys() if s.endswith('/USDT')]

    cprint(f"  Found {len(usdt_pairs)} USDT pairs\n", "green")

    # Download both timeframes
    timeframes = ['5m', '1m']

    successful = 0
    failed = 0

    for timeframe in timeframes:
        cprint(f"\n{'='*90}", "cyan")
        cprint(f"⏱️  Downloading {timeframe.upper()} Data", "cyan", attrs=["bold"])
        cprint(f"{'='*90}", "cyan")

        for i, symbol in enumerate(usdt_pairs, 1):
            pair_name = symbol.replace('/', '_')
            output_file = OUTPUT_DIR / f"{pair_name}-{timeframe}.feather"

            # Skip if already exists
            if output_file.exists():
                cprint(f"  [{i:3d}/{len(usdt_pairs)}] ✓ {pair_name:20} Already exists", "white")
                successful += 1
                continue

            try:
                df = download_ohlcv(exchange, symbol, timeframe, START_DATE, END_DATE)

                if df is not None and len(df) > 0:
                    # Save as feather
                    df.reset_index(drop=True, inplace=True)
                    df.to_feather(output_file)

                    days = (df['date'].max() - df['date'].min()).days

                    cprint(f"  [{i:3d}/{len(usdt_pairs)}] ✅ {pair_name:20} "
                           f"{len(df):,} candles ({days} days)", "green")
                    successful += 1
                else:
                    cprint(f"  [{i:3d}/{len(usdt_pairs)}] ⚠️  {pair_name:20} No data available", "yellow")
                    failed += 1

            except Exception as e:
                cprint(f"  [{i:3d}/{len(usdt_pairs)}] ❌ {pair_name:20} Error: {str(e)[:40]}", "red")
                failed += 1

    # Summary
    cprint(f"\n{'='*90}", "cyan")
    cprint(f"📊 DOWNLOAD SUMMARY", "cyan", attrs=["bold"])
    cprint(f"{'='*90}", "cyan")

    cprint(f"\n✅ Successful: {successful}", "green")
    cprint(f"❌ Failed: {failed}", "red" if failed > 0 else "white")
    cprint(f"\n📁 Data saved to: {OUTPUT_DIR}", "yellow")

    cprint(f"\n🎯 Next Steps:", "cyan")
    cprint(f"  1. Run same strategies on new data period", "white")
    cprint(f"  2. Compare results: April-June vs July-October", "white")
    cprint(f"  3. Strategies that work on BOTH = truly robust!", "white")
    cprint(f"  4. Detect Type 4 overfitting: time-period specific", "white")

if __name__ == "__main__":
    try:
        download_all_pairs()

        # Update requirements.txt
        cprint(f"\n📦 Updating requirements.txt...", "cyan")
        import subprocess
        subprocess.run(["pip", "freeze"], stdout=open("requirements.txt", "w"))
        cprint(f"  ✅ requirements.txt updated", "green")

    except KeyboardInterrupt:
        cprint("\n\n⚠️ Download interrupted", "yellow")
    except Exception as e:
        cprint(f"\n\n❌ Error: {e}", "red")
        import traceback
        traceback.print_exc()
