#!/usr/bin/env python3
"""
🌙 Moon Dev's HyperLiquid Coins Fetcher 🔥

Fetches available perpetual coins from HyperLiquid and saves them with market data.
"""

import os
import sys
import requests
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
HYPERLIQUID_INFO_URL = "https://api.hyperliquid.xyz/info"
OUTPUT_FILE = Path("src/data/hyperliquid_coins.csv")

def get_meta_data():
    """Get metadata including all available coins/symbols from HyperLiquid"""
    print("🔍 Fetching HyperLiquid metadata...")
    
    headers = {'Content-Type': 'application/json'}
    data = {'type': 'meta'}
    
    try:
        response = requests.post(HYPERLIQUID_INFO_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching metadata: {str(e)}")
        return {}

def get_all_mids():
    """Get current prices for all coins"""
    print("💹 Fetching current prices...")
    
    headers = {'Content-Type': 'application/json'}
    data = {'type': 'allMids'}
    
    try:
        response = requests.post(HYPERLIQUID_INFO_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching prices: {str(e)}")
        return {}

def estimate_volume(price, open_interest_usd=None):
    """Estimate volume based on typical market conditions"""
    # HyperLiquid doesn't provide 24h volume in meta, so we'll estimate
    # Typical volume/OI ratio is 2-5x per day
    # For simplicity, we'll use a placeholder
    return 0  # Placeholder - actual volume would come from order book history

def fetch_hyperliquid_coins():
    """Main function to fetch HyperLiquid coins"""
    print("🌙 Moon Dev's HyperLiquid Coins Fetcher 🚀")
    print(f"⚙️ Configuration:")
    print(f"  • API Endpoint: {HYPERLIQUID_INFO_URL}")
    print(f"  • Output File: {OUTPUT_FILE.absolute()}\n")
    
    # Step 1: Get metadata (all coins)
    meta = get_meta_data()
    
    if not meta or 'universe' not in meta:
        print("❌ Could not fetch metadata!")
        return False
    
    universe = meta.get('universe', [])
    print(f"✅ Found {len(universe)} coins on HyperLiquid\n")
    
    # Step 2: Get current prices
    mids = get_all_mids()
    
    if not mids:
        print("❌ Could not fetch prices!")
        return False
    
    # Step 3: Build coin list with data
    coins = []
    
    for i, coin_meta in enumerate(universe):
        symbol = coin_meta.get('name', '')
        if not symbol:
            continue
        
        # Get current price
        price = float(mids.get(symbol, 0))
        
        # Note: HyperLiquid API doesn't provide 24h volume in metadata
        # Volume can be calculated from order book or order history
        
        print(f"[{i+1}/{len(universe)}] {symbol:8s} - Price: ${price:>15,.8f}")
        
        coins.append({
            'symbol': symbol,
            'name': coin_meta.get('displayName', symbol),
            'price': price,
            'token_id': symbol.lower(),
            'exchange': 'hyperliquid',
            'sz_decimals': coin_meta.get('szDecimals', 0),
            'discovered_at': datetime.now().isoformat()
        })
    
    if not coins:
        print("❌ No coins found!")
        return False
    
    # Step 4: Create DataFrame and save
    df = pd.DataFrame(coins)
    
    # Sort by symbol
    df = df.sort_values('symbol')
    
    # Create directory if needed
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n✨ HyperLiquid Coins Fetched!")
    print(f"📊 Found {len(df)} coins")
    print(f"💾 Saved to: {OUTPUT_FILE.absolute()}")
    print(f"\n🔥 Top 10 Coins:")
    for i, row in df.head(10).iterrows():
        print(f"  {i+1:2d}. {row['symbol']:8s} - Price: ${row['price']:>15,.8f}")
    
    return True

if __name__ == "__main__":
    try:
        fetch_hyperliquid_coins()
    except KeyboardInterrupt:
        print("\n👋 HyperLiquid coins fetch cancelled")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
