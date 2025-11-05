#!/usr/bin/env python3
"""
🌙 Moon Dev's Coin Data Enricher 💰

Takes scraped coin IDs and enriches with price, market cap, volume from CoinGecko API
"""

import os
import pandas as pd
import requests
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configuration
INPUT_FILE = Path("DIR_scraper/trending_coins_data.csv")
OUTPUT_FILE = Path("DIR_scraper/trending_coins_enriched.csv")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

def fetch_coin_market_data(coin_ids, batch_size=250):
    """Fetch market data for multiple coins at once"""
    all_data = []

    print(f"📊 Fetching market data for {len(coin_ids)} coins...")

    # Split into batches
    for i in range(0, len(coin_ids), batch_size):
        batch = coin_ids[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(coin_ids) + batch_size - 1) // batch_size

        print(f"\n  📦 Batch {batch_num}/{total_batches} ({len(batch)} coins)")

        url = f"{COINGECKO_BASE_URL}/coins/markets"

        params = {
            'vs_currency': 'usd',
            'ids': ','.join(batch),
            'order': 'market_cap_desc',
            'per_page': batch_size,
            'page': 1,
            'sparkline': False,
            'price_change_percentage': '1h,24h,7d',
            'x_cg_demo_api_key': COINGECKO_API_KEY if COINGECKO_API_KEY else ''
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            all_data.extend(data)
            print(f"  ✓ Got data for {len(data)} coins")

            # Rate limiting
            time.sleep(1.5)

        except Exception as e:
            print(f"  ❌ Error fetching batch: {str(e)}")
            continue

    return all_data

def parse_volume_and_mcap(text):
    """Convert text like '$5.2M' or '$1.3B' to numbers"""
    if not text or text == 'N/A' or text == '':
        return None

    try:
        # Remove $ and spaces
        text = text.replace('$', '').replace(',', '').strip()

        multiplier = 1
        if 'B' in text:
            multiplier = 1_000_000_000
            text = text.replace('B', '')
        elif 'M' in text:
            multiplier = 1_000_000
            text = text.replace('M', '')
        elif 'K' in text:
            multiplier = 1_000
            text = text.replace('K', '')

        return float(text) * multiplier
    except:
        return None

def main():
    """Main enrichment function"""
    print("🌙 Moon Dev's Coin Data Enricher 🚀")

    # Load the scraped data
    if not INPUT_FILE.exists():
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)
    print(f"📂 Loaded {len(df)} coins from {INPUT_FILE}")

    # Get all coin IDs
    coin_ids = df['coin_id'].dropna().unique().tolist()
    print(f"🔑 Found {len(coin_ids)} unique coin IDs")

    # Fetch market data
    market_data = fetch_coin_market_data(coin_ids)

    if not market_data:
        print("❌ No market data retrieved!")
        return

    # Create a lookup dictionary
    market_lookup = {coin['id']: coin for coin in market_data}

    print(f"\n💾 Got market data for {len(market_lookup)} coins")

    # Enrich the DataFrame
    print("\n🔧 Enriching data...")

    enriched_rows = []

    for _, row in df.iterrows():
        coin_id = row['coin_id']

        if pd.notna(coin_id) and coin_id in market_lookup:
            coin_data = market_lookup[coin_id]

            enriched_row = row.to_dict()
            enriched_row.update({
                'price': coin_data.get('current_price'),
                'market_cap': coin_data.get('market_cap'),
                'volume_24h': coin_data.get('total_volume'),
                'price_change_1h_pct': coin_data.get('price_change_percentage_1h_in_currency'),
                'price_change_24h_pct': coin_data.get('price_change_percentage_24h'),
                'price_change_7d_pct': coin_data.get('price_change_percentage_7d_in_currency'),
                'market_cap_rank': coin_data.get('market_cap_rank'),
                'high_24h': coin_data.get('high_24h'),
                'low_24h': coin_data.get('low_24h'),
                'circulating_supply': coin_data.get('circulating_supply'),
                'total_supply': coin_data.get('total_supply'),
                'ath': coin_data.get('ath'),
                'ath_date': coin_data.get('ath_date'),
                'atl': coin_data.get('atl'),
                'atl_date': coin_data.get('atl_date'),
            })

            enriched_rows.append(enriched_row)
        else:
            # Keep original row if no market data
            enriched_rows.append(row.to_dict())

    # Create enriched DataFrame
    df_enriched = pd.DataFrame(enriched_rows)

    # Sort by market cap (descending)
    df_enriched = df_enriched.sort_values('market_cap', ascending=False, na_position='last')

    # Save to CSV
    df_enriched.to_csv(OUTPUT_FILE, index=False)

    print(f"\n✨ Enrichment Complete!")
    print(f"💾 Saved to: {OUTPUT_FILE.absolute()}")

    # Summary statistics
    print(f"\n📈 Summary:")
    print(f"  • Total coins: {len(df_enriched)}")
    print(f"  • Coins with price: {df_enriched['price'].notna().sum()}")
    print(f"  • Coins with market cap: {df_enriched['market_cap'].notna().sum()}")
    print(f"  • Coins with volume: {df_enriched['volume_24h'].notna().sum()}")

    # Filter coins with complete data
    complete_data = df_enriched[
        df_enriched['price'].notna() &
        df_enriched['market_cap'].notna() &
        df_enriched['volume_24h'].notna()
    ]

    print(f"  • Coins with complete data: {len(complete_data)}")

    # Show top 10
    print(f"\n🔥 Top 10 by Market Cap:")
    print(f"  {'Coin Name':<25s} {'Symbol':<6s}   {'Price':>12s}   {'1h %':>7s}  {'24h %':>7s}  {'7d %':>7s}   {'Market Cap':>10s}   {'Volume 24h':>10s}")
    print(f"  {'-'*25} {'-'*6}   {'-'*12}   {'-'*7}  {'-'*7}  {'-'*7}   {'-'*10}   {'-'*10}")

    for _, row in complete_data.head(10).iterrows():
        mcap = row['market_cap']
        vol = row['volume_24h']
        price_change_1h = row.get('price_change_1h_pct', 0) or 0
        price_change_24h = row.get('price_change_24h_pct', 0) or 0
        price_change_7d = row.get('price_change_7d_pct', 0) or 0

        mcap_str = f"${mcap/1e9:.2f}B" if mcap >= 1e9 else f"${mcap/1e6:.2f}M"
        vol_str = f"${vol/1e9:.2f}B" if vol >= 1e9 else f"${vol/1e6:.2f}M"

        print(f"  {row['coin_name']:<25s} {row['symbol']:<6s}   ${row['price']:>11.6f}   {price_change_1h:>6.1f}%  {price_change_24h:>6.1f}%  {price_change_7d:>6.1f}%   {mcap_str:>10s}   {vol_str:>10s}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Enrichment cancelled")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
