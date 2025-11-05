#!/usr/bin/env python3
"""
🌙 Moon Dev's Token Discovery Agent 🚀

Discovers tokens from CoinGecko and creates discovered_tokens.csv for the Listing Arbitrage Agent
"""

import os
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
COINGECKO_BASE_URL = "https://pro-api.coingecko.com/api/v3"
OUTPUT_FILE = Path("src/data/discovered_tokens.csv")

# Criteria for token discovery
MIN_MARKET_CAP = 100_000       # $100k minimum
MAX_MARKET_CAP = 10_000_000    # $10M maximum
MIN_VOLUME_24H = 100_000       # $100k minimum volume
MAX_TOKENS = 100               # Limit results

def get_headers():
    """Get API headers with CoinGecko key"""
    return {
        "x-cg-pro-api-key": COINGECKO_API_KEY,
        "Content-Type": "application/json"
    }

def fetch_tokens_by_criteria(page=1, per_page=250):
    """Fetch tokens that meet criteria from CoinGecko"""
    print(f"\n📊 Fetching tokens from CoinGecko (page {page})...")
    
    url = f"{COINGECKO_BASE_URL}/coins/markets"
    
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': per_page,
        'page': page,
        'sparkline': False
    }
    
    headers = get_headers()
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Error fetching tokens: {str(e)}")
        return []

def filter_tokens(tokens):
    """Filter tokens based on criteria"""
    print(f"\n🔍 Filtering {len(tokens)} tokens...")
    
    filtered = []
    
    for token in tokens:
        try:
            # Get required fields
            token_id = token.get('id', '')
            name = token.get('name', 'Unknown')
            symbol = token.get('symbol', 'UNKNOWN').upper()
            market_cap = token.get('market_cap')
            volume_24h = token.get('total_volume')
            price = token.get('current_price', 0)
            
            # Skip if missing critical data
            if not token_id or market_cap is None or volume_24h is None:
                continue
            
            # Apply filters
            if market_cap < MIN_MARKET_CAP or market_cap > MAX_MARKET_CAP:
                continue
            if volume_24h < MIN_VOLUME_24H:
                continue
            
            # Add to filtered list
            filtered.append({
                'token_id': token_id,
                'name': name,
                'symbol': symbol,
                'price': price,
                'market_cap': market_cap,
                'volume_24h': volume_24h,
                'discovered_at': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"⚠️ Error processing token: {str(e)}")
            continue
    
    return filtered

def discover_tokens():
    """Main discovery process"""
    print("🌙 Moon Dev's Token Discovery Agent Starting Up! 🚀")
    print(f"⚙️ Configuration:")
    print(f"  • Min Market Cap: ${MIN_MARKET_CAP:,.0f}")
    print(f"  • Max Market Cap: ${MAX_MARKET_CAP:,.0f}")
    print(f"  • Min 24h Volume: ${MIN_VOLUME_24H:,.0f}")
    print(f"  • Max Tokens: {MAX_TOKENS}")
    
    if not COINGECKO_API_KEY:
        print("❌ Error: COINGECKO_API_KEY not found in environment variables!")
        return False
    
    all_tokens = []
    page = 1
    
    # Fetch multiple pages to get enough candidates
    while len(all_tokens) < MAX_TOKENS * 2:
        tokens = fetch_tokens_by_criteria(page=page, per_page=250)
        
        if not tokens:
            print("ℹ️ No more tokens to fetch")
            break
        
        filtered = filter_tokens(tokens)
        all_tokens.extend(filtered)
        
        print(f"✅ Found {len(filtered)} matching tokens on page {page}")
        print(f"📊 Total so far: {len(all_tokens)}")
        
        if len(all_tokens) >= MAX_TOKENS:
            break
        
        page += 1
        time.sleep(1)  # Rate limiting
    
    # Sort by market cap descending
    all_tokens.sort(key=lambda x: x['market_cap'], reverse=True)
    
    # Keep only top MAX_TOKENS
    all_tokens = all_tokens[:MAX_TOKENS]
    
    if not all_tokens:
        print("❌ No tokens found matching criteria!")
        return False
    
    # Create DataFrame and save
    df = pd.DataFrame(all_tokens)
    
    # Create directory if needed
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n✨ Discovery Complete!")
    print(f"📊 Found {len(df)} tokens matching criteria")
    print(f"💾 Saved to: {OUTPUT_FILE.absolute()}")
    print(f"\n📈 Top 5 tokens by market cap:")
    for i, row in df.head(5).iterrows():
        print(f"  {i+1}. {row['name']} ({row['symbol']})")
        print(f"     Market Cap: ${row['market_cap']:,.0f}")
        print(f"     24h Volume: ${row['volume_24h']:,.0f}")
    
    return True

if __name__ == "__main__":
    try:
        discover_tokens()
    except KeyboardInterrupt:
        print("\n👋 Token discovery cancelled")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
