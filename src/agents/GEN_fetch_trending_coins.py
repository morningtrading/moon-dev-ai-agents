#!/usr/bin/env python3
"""
🌙 Moon Dev's Trending Coins Fetcher 🔥

Fetches trending coins from CoinGecko and saves them to a CSV file for analysis
"""

import os
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
OUTPUT_FILE = Path("src/data/trending_coins.csv")

def get_trending_coins():
    """Fetch trending coins from CoinGecko"""
    print("🔥 Fetching trending coins from CoinGecko...")
    
    url = f"{COINGECKO_BASE_URL}/search/trending"
    
    params = {
        'x_cg_demo_api_key': COINGECKO_API_KEY if COINGECKO_API_KEY else ''
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract coins from response
        coins = data.get('coins', [])
        print(f"✅ Got {len(coins)} trending coins from API")
        
        return coins
    except Exception as e:
        print(f"❌ Error fetching trending coins: {str(e)}")
        return []

def get_market_data(coin_ids, page=1):
    """Fetch market data for coins"""
    print(f"\n📊 Fetching market data for coins (page {page})...")
    
    url = f"{COINGECKO_BASE_URL}/coins/markets"
    
    params = {
        'vs_currency': 'usd',
        'ids': ','.join(coin_ids),
        'order': 'market_cap_desc',
        'per_page': 250,
        'page': page,
        'sparkline': False,
        'x_cg_demo_api_key': COINGECKO_API_KEY if COINGECKO_API_KEY else ''
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching market data: {str(e)}")
        return []

def fetch_trending():
    """Main function to fetch trending coins"""
    print("🌙 Moon Dev's Trending Coins Fetcher 🚀")
    print(f"⚙️ Configuration:")
    print(f"  • API Endpoint: {COINGECKO_BASE_URL}")
    print(f"  • Output File: {OUTPUT_FILE.absolute()}")
    
    if not COINGECKO_API_KEY:
        print("⚠️ Warning: COINGECKO_API_KEY not set, using public endpoint")
    
    # Step 1: Get trending coins list
    trending = get_trending_coins()
    
    if not trending:
        print("❌ No trending coins found!")
        return False
    
    # Extract coin IDs from trending response
    coin_ids = [coin['item']['id'] for coin in trending[:100]]  # Get top 100
    print(f"📝 Found trending coin IDs: {', '.join(coin_ids[:10])}... (and {len(coin_ids)-10} more)")
    
    # Step 2: Fetch market data for these coins
    all_market_data = []
    
    # Fetch in batches of 250 (API limit per request)
    for i in range(0, len(coin_ids), 250):
        batch_ids = coin_ids[i:i+250]
        page = (i // 250) + 1
        
        market_data = get_market_data(batch_ids, page=page)
        all_market_data.extend(market_data)
        
        time.sleep(1)  # Rate limiting
    
    if not all_market_data:
        print("❌ No market data retrieved!")
        return False
    
    # Step 3: Create DataFrame
    tokens = []
    for coin in all_market_data:
        tokens.append({
            'token_id': coin.get('id', ''),
            'name': coin.get('name', 'Unknown'),
            'symbol': coin.get('symbol', 'UNKNOWN').upper(),
            'price': coin.get('current_price', 0),
            'market_cap': coin.get('market_cap'),
            'volume_24h': coin.get('total_volume'),
            'market_cap_rank': coin.get('market_cap_rank'),
            'trending_rank': coin_ids.index(coin.get('id')) + 1 if coin.get('id') in coin_ids else 999,
            'ath_date': coin.get('ath_date'),
            'discovered_at': datetime.now().isoformat()
        })
    
    df = pd.DataFrame(tokens)
    
    # Store original count before filtering
    total_before_filter = len(df)
    
    # Filter 1: Remove coins with market cap >= $500 million
    df = df[df['market_cap'].notna() & (df['market_cap'] < 500_000_000)]
    
    # Filter 2: Remove coins with ATH older than 1 year
    one_year_ago = pd.Timestamp.now(tz='UTC') - timedelta(days=365)
    df = df[df['ath_date'].notna()]
    df['ath_date_parsed'] = pd.to_datetime(df['ath_date'], errors='coerce')
    df = df[df['ath_date_parsed'] >= one_year_ago]
    
    # Drop the temporary parsed column
    df = df.drop(columns=['ath_date_parsed'])
    
    # Calculate how many were filtered out
    filtered_count = total_before_filter - len(df)
    
    # Sort by trending rank
    df = df.sort_values('trending_rank')
    
    # Create directory if needed
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n✨ Trending Coins Fetched!")
    print(f"📊 Fetched {total_before_filter} coins from API")
    print(f"🔍 After filtering: {len(df)} coins (removed {filtered_count})")
    print(f"   • Excluded coins with market cap >= $500M")
    print(f"   • Excluded coins with ATH older than 1 year")
    print(f"💾 Saved to: {OUTPUT_FILE.absolute()}")
    print(f"\n🔥 Top 10 Trending Coins:")
    for i, row in df.head(10).iterrows():
        print(f"  {row['trending_rank']:2d}. {row['name']:20s} ({row['symbol']:6s}) - Market Cap: ${row['market_cap']:,.0f}" if row['market_cap'] else f"  {row['trending_rank']:2d}. {row['name']:20s} ({row['symbol']:6s}) - Market Cap: N/A")
    
    return True

if __name__ == "__main__":
    try:
        fetch_trending()
    except KeyboardInterrupt:
        print("\n👋 Trending coins fetch cancelled")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
