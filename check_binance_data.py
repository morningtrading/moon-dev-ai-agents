#!/usr/bin/env python3
"""
🌙 Check Binance OHLC Data
Quick script to inspect your Binance data collection
"""

import pandas as pd
from pathlib import Path
from termcolor import cprint

DATA_DIR = Path("/home/titus/Dropbox/user_data/data/binance")

cprint("\n🌙 Moon Dev's Binance Data Inspector", "cyan", attrs=["bold"])
cprint("=" * 70, "cyan")

# Count files
files_1m = list(DATA_DIR.glob("*-1m.feather"))
files_5m = list(DATA_DIR.glob("*-5m.feather"))

cprint(f"\n📊 Data Summary:", "cyan")
cprint(f"  ├─ 1-minute files: {len(files_1m)}", "white")
cprint(f"  └─ 5-minute files: {len(files_5m)}", "white")

# Sample one file to check format
if files_1m:
    sample_file = files_1m[0]
    cprint(f"\n📝 Sample File: {sample_file.name}", "yellow")

    try:
        df = pd.read_feather(sample_file)
        cprint(f"  ├─ Rows: {len(df):,}", "white")
        cprint(f"  ├─ Columns: {list(df.columns)}", "white")

        if len(df) > 0:
            # Try to find date column
            date_col = None
            for col in df.columns:
                if 'date' in col.lower() or 'time' in col.lower():
                    date_col = col
                    break

            if date_col:
                cprint(f"  ├─ First date: {df[date_col].iloc[0]}", "white")
                cprint(f"  └─ Last date: {df[date_col].iloc[-1]}", "white")
            else:
                cprint(f"  └─ Columns: {', '.join(df.columns)}", "white")
                cprint(f"\n📋 First few rows:", "cyan")
                print(df.head())

    except Exception as e:
        cprint(f"  └─ Error reading file: {e}", "red")

# List all available pairs
cprint(f"\n💰 Available Trading Pairs:", "cyan")
pairs = [f.stem.replace('-1m', '') for f in files_1m]
pairs.sort()

for i, pair in enumerate(pairs[:30], 1):  # Show first 30
    print(f"  {i:2d}. {pair}")

if len(pairs) > 30:
    cprint(f"  ... and {len(pairs) - 30} more pairs!", "yellow")

cprint(f"\n✅ Total: {len(pairs)} trading pairs available", "green")
cprint(f"💡 You can use any of these for backtesting!", "cyan")
