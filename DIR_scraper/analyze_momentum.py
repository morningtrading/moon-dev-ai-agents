#!/usr/bin/env python3
"""
🌙 Moon Dev's Momentum Analyzer 📈

Analyzes trending coins to find the most promising based on price momentum
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Configuration
INPUT_FILE = Path("DIR_scraper/trending_coins_enriched.csv")
OUTPUT_FILE = Path("DIR_scraper/top_50_momentum_coins.csv")

def calculate_momentum_score(row):
    """
    Calculate momentum score based on multiple factors

    Scoring criteria:
    - 7d change: 40% weight (long-term trend)
    - 24h change: 30% weight (medium-term trend)
    - 1h change: 20% weight (short-term momentum)
    - Consistency bonus: 10% (all timeframes positive)
    """

    score = 0

    # Get price changes (handle NaN values)
    change_1h = row.get('price_change_1h_pct', 0) or 0
    change_24h = row.get('price_change_24h_pct', 0) or 0
    change_7d = row.get('price_change_7d_pct', 0) or 0

    # Base score from price changes (weighted)
    score += change_7d * 0.40   # 40% weight on 7d
    score += change_24h * 0.30  # 30% weight on 24h
    score += change_1h * 0.20   # 20% weight on 1h

    # Consistency bonus: all timeframes positive
    if change_1h > 0 and change_24h > 0 and change_7d > 0:
        # All positive - strong momentum
        consistency_bonus = (change_1h + change_24h + change_7d) * 0.10
        score += consistency_bonus

    # Acceleration bonus: 1h > 24h > 7d (momentum accelerating)
    if change_1h > change_24h and change_24h > 0:
        score += 5  # Acceleration bonus

    # Volume factor (higher volume = more reliable)
    volume_24h = row.get('volume_24h', 0) or 0
    if volume_24h > 1_000_000:  # At least $1M volume
        score += 2
    if volume_24h > 10_000_000:  # At least $10M volume
        score += 3
    if volume_24h > 100_000_000:  # At least $100M volume
        score += 5

    # Market cap factor (prefer mid-caps for growth potential)
    mcap = row.get('market_cap', 0) or 0
    if 10_000_000 < mcap < 500_000_000:  # $10M - $500M (high growth potential)
        score += 10
    elif 500_000_000 < mcap < 1_000_000_000:  # $500M - $1B (good potential)
        score += 5
    elif mcap > 5_000_000_000:  # Over $5B (established, lower risk)
        score += 3

    # Recent ATH bonus (near all-time high)
    try:
        price = row.get('price', 0) or 0
        ath = row.get('ath', 0) or 0
        if ath > 0 and price > 0:
            price_to_ath_ratio = (price / ath) * 100
            if price_to_ath_ratio > 90:  # Within 10% of ATH
                score += 15
            elif price_to_ath_ratio > 70:  # Within 30% of ATH
                score += 8
    except:
        pass

    return score

def categorize_momentum(row):
    """Categorize the type of momentum"""
    change_1h = row.get('price_change_1h_pct', 0) or 0
    change_24h = row.get('price_change_24h_pct', 0) or 0
    change_7d = row.get('price_change_7d_pct', 0) or 0

    if change_1h > 0 and change_24h > 0 and change_7d > 0:
        if change_1h > change_24h > change_7d:
            return "🚀 ACCELERATING"
        else:
            return "📈 STRONG UPTREND"
    elif change_24h > 0 and change_7d > 0:
        return "📊 UPTREND (recent dip)"
    elif change_7d > 0:
        return "⚡ RECOVERING"
    else:
        return "⚠️ MIXED"

def main():
    """Main analysis function"""
    print("🌙 Moon Dev's Momentum Analyzer 📈")
    print("="*60)

    # Load data
    if not INPUT_FILE.exists():
        print(f"❌ Input file not found: {INPUT_FILE}")
        return

    df = pd.read_csv(INPUT_FILE)
    print(f"📂 Loaded {len(df)} coins from {INPUT_FILE.name}")

    # Convert numeric columns
    numeric_cols = ['price', 'price_change_1h_pct', 'price_change_24h_pct', 'price_change_7d_pct',
                    'volume_24h', 'market_cap', 'high_24h', 'low_24h', 'ath']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Filter coins with complete price change data
    df_complete = df[
        df['price_change_1h_pct'].notna() &
        df['price_change_24h_pct'].notna() &
        df['price_change_7d_pct'].notna() &
        df['price'].notna() &
        df['volume_24h'].notna()
    ].copy()

    print(f"✅ {len(df_complete)} coins with complete data")

    # Calculate momentum score
    print("\n🔧 Calculating momentum scores...")
    df_complete['momentum_score'] = df_complete.apply(calculate_momentum_score, axis=1)
    df_complete['momentum_type'] = df_complete.apply(categorize_momentum, axis=1)

    # Sort by momentum score
    df_sorted = df_complete.sort_values('momentum_score', ascending=False)

    # Filter for positive momentum (at least one timeframe positive, or high score)
    # Use a more flexible filter since crypto is in a downtrend
    df_filtered = df_sorted[
        (df_sorted['price_change_7d_pct'] > 0) |  # 7d positive
        (df_sorted['price_change_24h_pct'] > 0) |  # or 24h positive
        (df_sorted['price_change_1h_pct'] > 2) |   # or strong 1h momentum
        (df_sorted['momentum_score'] > 0)           # or positive overall score
    ]

    print(f"📊 {len(df_filtered)} coins with positive momentum indicators")
    print(f"   • {len(df_sorted[df_sorted['price_change_7d_pct'] > 0])} coins with positive 7d")
    print(f"   • {len(df_sorted[df_sorted['price_change_24h_pct'] > 0])} coins with positive 24h")
    print(f"   • {len(df_sorted[df_sorted['price_change_1h_pct'] > 0])} coins with positive 1h")

    # Get top 50
    top_50 = df_filtered.head(50)

    print(f"\n✨ Selected Top {len(top_50)} Most Promising Coins")

    # Create output DataFrame with key columns
    output_columns = [
        'coin_name', 'symbol', 'price',
        'price_change_1h_pct', 'price_change_24h_pct', 'price_change_7d_pct',
        'volume_24h', 'market_cap', 'market_cap_rank',
        'momentum_score', 'momentum_type', 'category',
        'high_24h', 'low_24h', 'ath', 'ath_date',
        'circulating_supply', 'total_supply'
    ]

    top_50_output = top_50[output_columns].copy()

    # Save to CSV
    top_50_output.to_csv(OUTPUT_FILE, index=False)
    print(f"💾 Saved to: {OUTPUT_FILE.absolute()}")

    # Display top 20
    print(f"\n{'='*120}")
    print(f"🔥 TOP 20 MOST PROMISING COINS BY MOMENTUM")
    print(f"{'='*120}")
    print(f"{'#':<3} {'Coin':<25} {'Price':>12}  {'1h%':>7}  {'24h%':>7}  {'7d%':>7}  {'Score':>6}  {'Momentum Type':<20}  {'MCap':>10}")
    print(f"{'-'*3} {'-'*25} {'-'*12}  {'-'*7}  {'-'*7}  {'-'*7}  {'-'*6}  {'-'*20}  {'-'*10}")

    for idx, (_, row) in enumerate(top_50.head(20).iterrows(), 1):
        mcap = row['market_cap']
        mcap_str = f"${mcap/1e9:.2f}B" if mcap >= 1e9 else f"${mcap/1e6:.1f}M"

        price_str = f"${row['price']:.6f}" if row['price'] < 1 else f"${row['price']:.2f}"

        print(f"{idx:<3} {row['coin_name'][:25]:<25} {price_str:>12}  "
              f"{row['price_change_1h_pct']:>6.1f}%  "
              f"{row['price_change_24h_pct']:>6.1f}%  "
              f"{row['price_change_7d_pct']:>6.1f}%  "
              f"{row['momentum_score']:>6.1f}  "
              f"{row['momentum_type']:<20}  "
              f"{mcap_str:>10}")

    # Summary statistics
    print(f"\n{'='*120}")
    print(f"📊 MOMENTUM ANALYSIS SUMMARY")
    print(f"{'='*120}")

    print(f"\n🎯 Momentum Type Distribution:")
    momentum_counts = top_50['momentum_type'].value_counts()
    for momentum_type, count in momentum_counts.items():
        print(f"  {momentum_type}: {count} coins")

    print(f"\n📈 Average Statistics (Top 50):")
    print(f"  • Average 1h change:  {top_50['price_change_1h_pct'].mean():>6.2f}%")
    print(f"  • Average 24h change: {top_50['price_change_24h_pct'].mean():>6.2f}%")
    print(f"  • Average 7d change:  {top_50['price_change_7d_pct'].mean():>6.2f}%")
    print(f"  • Average momentum score: {top_50['momentum_score'].mean():>6.2f}")

    print(f"\n💰 Market Cap Distribution:")
    micro_cap = len(top_50[top_50['market_cap'] < 10_000_000])
    small_cap = len(top_50[(top_50['market_cap'] >= 10_000_000) & (top_50['market_cap'] < 100_000_000)])
    mid_cap = len(top_50[(top_50['market_cap'] >= 100_000_000) & (top_50['market_cap'] < 1_000_000_000)])
    large_cap = len(top_50[top_50['market_cap'] >= 1_000_000_000])

    print(f"  • Micro-cap (<$10M):      {micro_cap} coins")
    print(f"  • Small-cap ($10M-$100M): {small_cap} coins")
    print(f"  • Mid-cap ($100M-$1B):    {mid_cap} coins")
    print(f"  • Large-cap (>$1B):       {large_cap} coins")

    print(f"\n💎 High Growth Potential (Mid-caps with strong momentum):")
    high_potential = top_50[
        (top_50['market_cap'] >= 10_000_000) &
        (top_50['market_cap'] < 500_000_000) &
        (top_50['momentum_score'] > 20)
    ]

    print(f"  Found {len(high_potential)} high-potential coins:")
    for _, row in high_potential.head(10).iterrows():
        print(f"    • {row['coin_name']} ({row['symbol']}) - Score: {row['momentum_score']:.1f}, 7d: +{row['price_change_7d_pct']:.1f}%")

    print(f"\n✨ Analysis Complete!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Analysis cancelled")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
