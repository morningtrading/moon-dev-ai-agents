#!/usr/bin/env python3
"""
🌙 Moon Dev's Trend Analysis Summary Display
Shows the summary of all analyzed coins with conclusions
"""

import pandas as pd
from pathlib import Path
from termcolor import colored, cprint

ANALYSIS_FILE = Path("src/data/trend_swarm_analysis.csv")

def display_summary():
    """Display summary of all analyzed coins"""
    if not ANALYSIS_FILE.exists():
        cprint("❌ No analysis file found!", "red")
        return
    
    df = pd.read_csv(ANALYSIS_FILE)
    
    if df.empty:
        cprint("📊 No coins analyzed yet", "yellow")
        return
    
    # Get most recent analysis for each coin
    df_latest = df.sort_values('timestamp').groupby('token_id').tail(1)
    
    cprint("\n" + "="*80, "cyan")
    cprint("📋 TREND COIN ANALYSIS SUMMARY", "cyan", attrs=["bold"])
    cprint("="*80 + "\n", "cyan")
    
    cprint(f"📊 Total Coins Analyzed: {len(df_latest)}", "white", attrs=["bold"])
    cprint(f"📈 BUY Signals: {len(df_latest[df_latest['overall_recommendation'] == 'BUY'])}", "green")
    cprint(f"📉 SELL Signals: {len(df_latest[df_latest['overall_recommendation'] == 'SELL'])}", "red")
    cprint(f"⏸️  DO NOTHING Signals: {len(df_latest[df_latest['overall_recommendation'] == 'DO NOTHING'])}", "white")
    
    print("\n" + "-"*80 + "\n")
    
    for idx, row in df_latest.iterrows():
        rec = row['overall_recommendation']
        conf = row['confidence_score']
        
        # Color based on recommendation
        if rec == "BUY":
            color = "green"
            icon = "🟢"
        elif rec == "SELL":
            color = "red"
            icon = "🔴"
        else:
            color = "white"
            icon = "⚪"
        
        cprint(f"{icon} {row['name']} ({row['symbol']})", color, attrs=["bold"])
        cprint(f"   Recommendation: {rec} (Confidence: {conf:.1f}%)", color)
        cprint(f"   Price: ${row['price']:.8f} | Market Cap: ${row['market_cap']:,.0f}", "white")
        cprint(f"   Technical: {row['technical_consensus']} (Buy:{row['technical_votes_buy']} Sell:{row['technical_votes_sell']} Nothing:{row['technical_votes_nothing']})", "yellow")
        cprint(f"   Fundamental: {row['fundamental_consensus']} (Buy:{row['fundamental_votes_buy']} Sell:{row['fundamental_votes_sell']} Nothing:{row['fundamental_votes_nothing']})", "cyan")
        print()
    
    print("-"*80)
    cprint(f"\n💾 Full analysis saved to: {ANALYSIS_FILE.absolute()}", "magenta")
    cprint(f"📊 Analyzed at: {df_latest['timestamp'].iloc[-1]}\n", "magenta")

if __name__ == "__main__":
    display_summary()
