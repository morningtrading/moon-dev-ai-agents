#!/usr/bin/env python3
"""
🌙 Moon Dev's Freqtrade Data Converter
Converts .feather files to CSV format for backtesting
"""

import pandas as pd
from pathlib import Path
from termcolor import cprint

# Paths
FREQTRADE_DATA_DIR = Path("/home/titus/freqtrade/user_data/data/binance")
OUTPUT_DIR = Path("/home/titus/moon-dev-ai-agents/src/data/rbi")

def convert_feather_to_csv(feather_file: Path, output_dir: Path):
    """Convert a single .feather file to CSV"""
    try:
        # Read feather file
        df = pd.read_feather(feather_file)
        
        # Rename columns to match backtesting.py format
        # Freqtrade format: date, open, high, low, close, volume
        # Backtesting.py format: datetime, open, high, low, close, volume
        if 'date' in df.columns:
            df = df.rename(columns={'date': 'datetime'})
        
        # Ensure datetime column
        if 'datetime' not in df.columns:
            cprint(f"⚠️ No datetime column in {feather_file.name}", "yellow")
            return False
        
        # Reorder columns
        columns_order = ['datetime', 'open', 'high', 'low', 'close', 'volume']
        df = df[columns_order]
        
        # Format datetime
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Create output filename (e.g., BTC_USDT-15m.feather -> BTC-USDT-15m.csv)
        output_name = feather_file.stem.replace('_USDT', '-USDT') + '.csv'
        output_path = output_dir / output_name
        
        # Save to CSV with proper formatting
        df.to_csv(output_path, index=False, 
                  float_format='%.8f',
                  date_format='%Y-%m-%d %H:%M:%S')
        
        # Get date range
        start_date = df['datetime'].min()
        end_date = df['datetime'].max()
        num_rows = len(df)
        
        cprint(f"✅ {feather_file.name} → {output_name}", "green")
        cprint(f"   📅 {start_date} to {end_date}", "cyan")
        cprint(f"   📊 {num_rows:,} candles", "cyan")
        
        return True
        
    except Exception as e:
        cprint(f"❌ Error converting {feather_file.name}: {e}", "red")
        return False

def main():
    """Convert all 15m feather files to CSV"""
    cprint("\n🌙 Moon Dev's Freqtrade Data Converter\n", "yellow", attrs=["bold"])
    
    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Find all 15m feather files
    feather_files = sorted(FREQTRADE_DATA_DIR.glob("*-15m.feather"))
    
    if not feather_files:
        cprint("❌ No 15m feather files found!", "red")
        return
    
    cprint(f"📁 Found {len(feather_files)} files to convert\n", "cyan")
    
    # Convert each file
    success_count = 0
    for feather_file in feather_files:
        if convert_feather_to_csv(feather_file, OUTPUT_DIR):
            success_count += 1
        print()
    
    # Summary
    cprint("=" * 70, "white")
    cprint(f"✨ Conversion Complete!", "green", attrs=["bold"])
    cprint(f"📊 Successfully converted: {success_count}/{len(feather_files)}", "cyan")
    cprint(f"📁 Output directory: {OUTPUT_DIR}", "cyan")
    cprint("=" * 70, "white")

if __name__ == "__main__":
    main()
