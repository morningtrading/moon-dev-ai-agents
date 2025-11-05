#!/usr/bin/env python3
"""
🌙 Moon Dev's Hyperliquid Filter 🔄

Filters trending momentum coins to only include those tradeable on Hyperliquid
"""

import pandas as pd
from pathlib import Path

# Configuration
MOMENTUM_FILE = Path("DIR_scraper/top_50_momentum_coins.csv")
HYPERLIQUID_FILE = Path("src/data/hyperliquid_coins.csv")
OUTPUT_FILE = Path("DIR_scraper/hyperliquid_momentum_coins.csv")

def normalize_symbol(symbol):
    """Normalize symbol for matching (uppercase, remove special chars)"""
    if pd.isna(symbol):
        return ""
    return str(symbol).upper().strip()

def main():
    """Main filtering function"""
    print("🌙 Moon Dev's Hyperliquid Filter 🔄")
    print("="*80)

    # Load Hyperliquid coins
    if not HYPERLIQUID_FILE.exists():
        print(f"❌ Hyperliquid file not found: {HYPERLIQUID_FILE}")
        return

    df_hl = pd.read_csv(HYPERLIQUID_FILE)
    print(f"📂 Loaded {len(df_hl)} coins from Hyperliquid")

    # Create set of Hyperliquid symbols (normalized)
    hl_symbols = set(df_hl['symbol'].apply(normalize_symbol))
    print(f"🔑 Hyperliquid has {len(hl_symbols)} unique symbols")

    # Load momentum coins
    if not MOMENTUM_FILE.exists():
        print(f"❌ Momentum file not found: {MOMENTUM_FILE}")
        return

    df_momentum = pd.read_csv(MOMENTUM_FILE)
    print(f"📊 Loaded {len(df_momentum)} momentum coins")

    # Normalize momentum symbols
    df_momentum['symbol_normalized'] = df_momentum['symbol'].apply(normalize_symbol)

    # Filter for Hyperliquid availability
    print(f"\n🔍 Matching coins with Hyperliquid...")
    df_filtered = df_momentum[df_momentum['symbol_normalized'].isin(hl_symbols)].copy()

    print(f"✅ Found {len(df_filtered)} coins available on Hyperliquid!")
    print(f"❌ Filtered out {len(df_momentum) - len(df_filtered)} coins not on Hyperliquid")

    if len(df_filtered) == 0:
        print("\n⚠️ No matching coins found!")
        print("\nSample momentum symbols:", df_momentum['symbol'].head(10).tolist())
        print("Sample Hyperliquid symbols:", list(hl_symbols)[:10])
        return

    # Add Hyperliquid-specific data
    df_hl_lookup = df_hl.set_index('symbol')

    def get_hl_data(row):
        """Get Hyperliquid data for a coin"""
        symbol = normalize_symbol(row['symbol'])
        if symbol in df_hl_lookup.index:
            hl_row = df_hl_lookup.loc[symbol]
            return pd.Series({
                'hl_price': hl_row.get('price'),
                'hl_token_id': hl_row.get('token_id'),
                'hl_sz_decimals': hl_row.get('sz_decimals')
            })
        return pd.Series({'hl_price': None, 'hl_token_id': None, 'hl_sz_decimals': None})

    # Add Hyperliquid data
    df_filtered[['hl_price', 'hl_token_id', 'hl_sz_decimals']] = df_filtered.apply(get_hl_data, axis=1)

    # Drop normalized symbol column
    df_filtered = df_filtered.drop(columns=['symbol_normalized'])

    # Sort by momentum score
    df_filtered = df_filtered.sort_values('momentum_score', ascending=False)

    # Save to CSV
    df_filtered.to_csv(OUTPUT_FILE, index=False)
    print(f"💾 Saved to: {OUTPUT_FILE.absolute()}")

    # Display results
    print(f"\n{'='*120}")
    print(f"🔥 HYPERLIQUID-TRADEABLE MOMENTUM COINS")
    print(f"{'='*120}")
    print(f"{'#':<3} {'Coin':<25} {'Symbol':<6}  {'Price':>12}  {'1h%':>7}  {'24h%':>7}  {'7d%':>7}  {'Score':>6}  {'Momentum':<20}  {'MCap':>10}")
    print(f"{'-'*3} {'-'*25} {'-'*6}  {'-'*12}  {'-'*7}  {'-'*7}  {'-'*7}  {'-'*6}  {'-'*20}  {'-'*10}")

    for idx, (_, row) in enumerate(df_filtered.head(30).iterrows(), 1):
        mcap = row['market_cap']
        mcap_str = f"${mcap/1e9:.2f}B" if mcap >= 1e9 else f"${mcap/1e6:.1f}M"

        price_str = f"${row['price']:.6f}" if row['price'] < 1 else f"${row['price']:.2f}"

        print(f"{idx:<3} {row['coin_name'][:25]:<25} {row['symbol']:<6}  {price_str:>12}  "
              f"{row['price_change_1h_pct']:>6.1f}%  "
              f"{row['price_change_24h_pct']:>6.1f}%  "
              f"{row['price_change_7d_pct']:>6.1f}%  "
              f"{row['momentum_score']:>6.1f}  "
              f"{row['momentum_type'][:20]:<20}  "
              f"{mcap_str:>10}")

    # Statistics
    print(f"\n{'='*120}")
    print(f"📊 HYPERLIQUID FILTER SUMMARY")
    print(f"{'='*120}")

    print(f"\n🎯 Availability:")
    print(f"  • Total momentum coins analyzed: {len(df_momentum)}")
    print(f"  • Coins available on Hyperliquid: {len(df_filtered)}")
    print(f"  • Match rate: {len(df_filtered)/len(df_momentum)*100:.1f}%")

    print(f"\n📈 Filtered Coins Stats:")
    print(f"  • Average 1h change:  {df_filtered['price_change_1h_pct'].mean():>6.2f}%")
    print(f"  • Average 24h change: {df_filtered['price_change_24h_pct'].mean():>6.2f}%")
    print(f"  • Average 7d change:  {df_filtered['price_change_7d_pct'].mean():>6.2f}%")
    print(f"  • Average momentum score: {df_filtered['momentum_score'].mean():>6.2f}")

    # Count positive momentum
    positive_7d = len(df_filtered[df_filtered['price_change_7d_pct'] > 0])
    positive_24h = len(df_filtered[df_filtered['price_change_24h_pct'] > 0])
    positive_1h = len(df_filtered[df_filtered['price_change_1h_pct'] > 0])

    print(f"\n✅ Positive Momentum:")
    print(f"  • Coins with positive 1h:  {positive_1h}/{len(df_filtered)}")
    print(f"  • Coins with positive 24h: {positive_24h}/{len(df_filtered)}")
    print(f"  • Coins with positive 7d:  {positive_7d}/{len(df_filtered)}")

    # Market cap breakdown
    print(f"\n💰 Market Cap Distribution:")
    micro = len(df_filtered[df_filtered['market_cap'] < 10_000_000])
    small = len(df_filtered[(df_filtered['market_cap'] >= 10_000_000) & (df_filtered['market_cap'] < 100_000_000)])
    mid = len(df_filtered[(df_filtered['market_cap'] >= 100_000_000) & (df_filtered['market_cap'] < 1_000_000_000)])
    large = len(df_filtered[df_filtered['market_cap'] >= 1_000_000_000])

    print(f"  • Micro-cap (<$10M):      {micro} coins")
    print(f"  • Small-cap ($10M-$100M): {small} coins")
    print(f"  • Mid-cap ($100M-$1B):    {mid} coins")
    print(f"  • Large-cap (>$1B):       {large} coins")

    # Best performers
    print(f"\n🚀 BEST PERFORMERS (7d positive):")
    best_7d = df_filtered[df_filtered['price_change_7d_pct'] > 0].sort_values('price_change_7d_pct', ascending=False)
    if len(best_7d) > 0:
        for _, row in best_7d.head(5).iterrows():
            print(f"  • {row['coin_name']:25s} ({row['symbol']:6s}) - 7d: +{row['price_change_7d_pct']:.1f}% | Score: {row['momentum_score']:.1f}")
    else:
        print(f"  ⚠️ No coins with positive 7d momentum in Hyperliquid list")

    print(f"\n✨ Filtering Complete!")
    print(f"\n💡 TIP: These coins can be traded on Hyperliquid using nice_funcs_hl.py functions:")
    print(f"   • market_buy(symbol, size)")
    print(f"   • market_sell(symbol, size)")
    print(f"   • get_position(symbol)")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Filtering cancelled")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
