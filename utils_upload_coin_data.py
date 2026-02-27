#!/usr/bin/env python3
"""
Utils: Upload Coin Data for Backtesting
========================================

Converts feather files to CSV format and uploads them to moon-dev-ai-agents
for use with RBI Agent v2 Simple backtesting.

Usage:
    python utils_upload_coin_data.py /path/to/coin_data.feather
    python utils_upload_coin_data.py /home/titus/freqtrade/user_data/data/binance/SUI_USDT-5m.feather

Output:
    - CSV file: /home/titus/moon-dev-ai-agents/src/data/SUI_USDT-5m.csv
    - Updates COIN variable in rbi_agent_v2_simple.py if requested
"""

import os
import sys
import pandas as pd
from pathlib import Path
from typing import Tuple
import re


def extract_coin_name(file_path: str) -> str:
    """
    Extract coin name from feather filename.
    
    Examples:
        SUI_USDT-5m.feather -> SUI
        BNB_USDT-15m.feather -> BNB
        BTC-USD-15m.feather -> BTC
    """
    filename = os.path.basename(file_path)
    # Remove extension
    name = filename.replace('.feather', '')
    
    # Extract coin name (before _ or -)
    match = re.match(r'([A-Z]+)', name)
    if match:
        return match.group(1)
    return 'UNKNOWN'


def get_timeframe(file_path: str) -> str:
    """
    Extract timeframe from filename.
    
    Examples:
        SUI_USDT-5m.feather -> 5m
        BNB_USDT-15m.feather -> 15m
    """
    filename = os.path.basename(file_path)
    match = re.search(r'-(\d+m)\.feather', filename)
    if match:
        return match.group(1)
    return '15m'  # Default


def validate_file(file_path: str) -> bool:
    """Validate that the feather file exists and is readable."""
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        return False
    
    if not file_path.endswith('.feather'):
        print(f"❌ Error: File must be .feather format, got: {file_path}")
        return False
    
    return True


def feather_to_csv(feather_path: str) -> Tuple[pd.DataFrame, str]:
    """
    Convert feather file to CSV.
    
    Returns:
        Tuple of (DataFrame, output_csv_path)
    """
    print(f"\n📊 Processing: {os.path.basename(feather_path)}")
    
    try:
        # Read feather
        df = pd.read_feather(feather_path)
        print(f"✅ Loaded {len(df)} rows")
        
        # Ensure required columns
        required_cols = {'date', 'open', 'high', 'low', 'close', 'volume'}
        df_cols = set(df.columns)
        
        if not required_cols.issubset(df_cols):
            print(f"⚠️  Warning: Expected columns {required_cols}")
            print(f"   Found: {df_cols}")
        
        # Extract coin name and create output path
        coin_name = extract_coin_name(feather_path)
        timeframe = get_timeframe(feather_path)
        
        output_dir = '/home/titus/moon-dev-ai-agents/src/data'
        output_filename = f"{coin_name}_USDT-{timeframe}.csv"
        output_path = os.path.join(output_dir, output_filename)
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to CSV
        df.to_csv(output_path, index=False)
        print(f"✅ Saved CSV: {output_filename}")
        print(f"   Size: {os.path.getsize(output_path) / 1024:.1f}KB")
        
        return df, coin_name
        
    except Exception as e:
        print(f"❌ Error processing file: {e}")
        raise


def update_agent_config(coin_name: str) -> bool:
    """
    Update the COIN variable in rbi_agent_v2_simple.py.
    """
    agent_file = '/home/titus/moon-dev-ai-agents/src/agents/rbi_agent_v2_simple.py'
    
    try:
        with open(agent_file, 'r') as f:
            content = f.read()
        
        # Replace COIN = "..." with new coin
        old_pattern = r'COIN = "[A-Z]+"'
        new_value = f'COIN = "{coin_name}"'
        
        if re.search(old_pattern, content):
            new_content = re.sub(old_pattern, new_value, content)
            with open(agent_file, 'w') as f:
                f.write(new_content)
            print(f"✅ Updated COIN = \"{coin_name}\" in rbi_agent_v2_simple.py")
            return True
        else:
            print(f"⚠️  Warning: Could not find COIN variable in {agent_file}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating config: {e}")
        return False


def verify_data_quality(df: pd.DataFrame, coin_name: str) -> None:
    """Print data quality summary."""
    print(f"\n📈 Data Quality Summary ({coin_name}):")
    print(f"   Rows: {len(df)}")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"   Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
    print(f"   Avg volume: {df['volume'].mean():.0f}")
    
    # Check for missing values
    missing = df.isnull().sum().sum()
    if missing > 0:
        print(f"   ⚠️  Missing values: {missing}")
    else:
        print(f"   ✅ No missing values")


def main():
    """Main function."""
    print("=" * 60)
    print("🚀 Upload Coin Data for Backtesting")
    print("=" * 60)
    
    # Parse arguments
    if len(sys.argv) < 2:
        print("\n📝 Usage:")
        print("   python utils_upload_coin_data.py <feather_file>")
        print("\n📌 Example:")
        print("   python utils_upload_coin_data.py /home/titus/freqtrade/user_data/data/binance/SUI_USDT-5m.feather")
        sys.exit(1)
    
    feather_file = sys.argv[1]
    
    # Validate
    if not validate_file(feather_file):
        sys.exit(1)
    
    # Convert
    try:
        df, coin_name = feather_to_csv(feather_file)
    except Exception as e:
        sys.exit(1)
    
    # Quality check
    verify_data_quality(df, coin_name)
    
    # Ask to update config
    print(f"\n🔧 Configuration Options:")
    print(f"   1. Update COIN to '{coin_name}' in rbi_agent_v2_simple.py")
    print(f"   2. Keep current COIN setting")
    
    response = input("\nUpdate config? (y/n) [y]: ").strip().lower()
    
    if response != 'n':
        update_agent_config(coin_name)
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ SUCCESS! Coin data ready for backtesting")
    print("=" * 60)
    print(f"\n📊 CSV Location:")
    print(f"   /home/titus/moon-dev-ai-agents/src/data/{coin_name}_USDT-*.csv")
    print(f"\n🚀 To backtest:")
    print(f"   python src/agents/rbi_agent_v2_simple.py")
    print(f"\n💡 Note: COIN is set to '{coin_name}'")
    print()


if __name__ == "__main__":
    main()
