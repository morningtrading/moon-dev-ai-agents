#!/usr/bin/env python3
"""
🌙 RSI(25/85) Threshold Monitor
Built with love by Moon Dev 🚀

Monitors RSI levels across all configured symbols and alerts when 
they approach the buy (RSI < 25) or sell (RSI > 85) thresholds.

This script helps you anticipate when the RSI 25/85 strategy might trigger.
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import HYPERLIQUID_SYMBOLS
import nice_funcs_hyperliquid as hl
import pandas as pd
from datetime import datetime
from termcolor import cprint
import time

# Configuration
RSI_PERIOD = 14
RSI_OVERSOLD = 25
RSI_OVERBOUGHT = 85
WARNING_BUFFER = 5  # Alert when within 5 points of threshold

# Alert levels
RSI_VERY_CLOSE_BUY = RSI_OVERSOLD + WARNING_BUFFER  # 30
RSI_VERY_CLOSE_SELL = RSI_OVERBOUGHT - WARNING_BUFFER  # 80

TIMEFRAME = '15m'
LOOKBACK_BARS = 100
CHECK_INTERVAL_SECONDS = 300  # 5 minutes

def calculate_rsi(df, period=14):
    """Calculate RSI indicator"""
    try:
        if df is None or len(df) < period + 1:
            return None
        
        close = df['close']
        delta = close.diff()
        
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.iloc[-1]
        
    except Exception as e:
        return None

def get_rsi_status(rsi):
    """Get status color and emoji based on RSI level"""
    if rsi is None:
        return "white", "❓", "Unknown"
    
    if rsi < RSI_OVERSOLD:
        return "green", "🟢", "BUY SIGNAL"
    elif rsi < RSI_VERY_CLOSE_BUY:
        return "green", "🟡", f"Near Buy ({rsi:.1f}/{RSI_OVERSOLD})"
    elif rsi > RSI_OVERBOUGHT:
        return "yellow", "🔴", "SELL SIGNAL"
    elif rsi > RSI_VERY_CLOSE_SELL:
        return "yellow", "🟡", f"Near Sell ({rsi:.1f}/{RSI_OVERBOUGHT})"
    else:
        return "white", "⚪", "Neutral"

def display_header():
    """Display monitor header"""
    cprint("\n" + "="*90, "cyan")
    cprint("🌙 RSI(25/85) Threshold Monitor", "cyan", attrs=["bold"])
    cprint("="*90, "cyan")
    cprint(f"\n📊 Monitoring: {', '.join(HYPERLIQUID_SYMBOLS)}", "white")
    cprint(f"⏰ Check Interval: {CHECK_INTERVAL_SECONDS}s ({CHECK_INTERVAL_SECONDS//60} minutes)", "white")
    cprint(f"📈 Timeframe: {TIMEFRAME} bars | RSI Period: {RSI_PERIOD}", "white")
    cprint(f"\n🎯 Alert Levels:", "yellow")
    cprint(f"  🟢 BUY:  RSI < {RSI_OVERSOLD} (Extreme Oversold)", "green")
    cprint(f"  🟡 Warning: RSI < {RSI_VERY_CLOSE_BUY} (Approaching Buy)", "yellow")
    cprint(f"  ⚪ Neutral: RSI {RSI_VERY_CLOSE_BUY}-{RSI_VERY_CLOSE_SELL}", "white")
    cprint(f"  🟡 Warning: RSI > {RSI_VERY_CLOSE_SELL} (Approaching Sell)", "yellow")
    cprint(f"  🔴 SELL: RSI > {RSI_OVERBOUGHT} (Extreme Overbought)", "red")
    print()

def monitor_rsi():
    """Monitor RSI levels for all symbols"""
    try:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cprint(f"\n{'='*90}", "cyan")
        cprint(f"🔄 RSI Check at {timestamp}", "cyan", attrs=["bold"])
        cprint(f"{'='*90}", "cyan")
        
        results = []
        signals_found = False
        
        for symbol in HYPERLIQUID_SYMBOLS:
            try:
                # Fetch data
                df = hl.get_data(
                    symbol=symbol,
                    timeframe=TIMEFRAME,
                    bars=LOOKBACK_BARS,
                    add_indicators=False
                )
                
                if df is None or df.empty:
                    cprint(f"  {symbol}: No data", "red")
                    continue
                
                # Calculate RSI
                rsi = calculate_rsi(df, period=RSI_PERIOD)
                
                if rsi is None:
                    cprint(f"  {symbol}: RSI calculation failed", "red")
                    continue
                
                # Get current price
                current_price = df['close'].iloc[-1]
                
                # Get status
                color, emoji, status = get_rsi_status(rsi)
                
                # Store result
                results.append({
                    'symbol': symbol,
                    'rsi': rsi,
                    'price': current_price,
                    'status': status,
                    'color': color,
                    'emoji': emoji
                })
                
                # Check for signals
                if rsi < RSI_OVERSOLD or rsi > RSI_OVERBOUGHT:
                    signals_found = True
                
            except Exception as e:
                cprint(f"  {symbol}: Error - {str(e)}", "red")
        
        # Display results
        if results:
            cprint("\n📊 RSI Status:\n", "yellow", attrs=["bold"])
            
            # Header
            cprint(f"{'Symbol':<10} {'RSI':>8} {'Price':>15} {'Status':<25}", "white", attrs=["bold"])
            cprint("-"*90, "white")
            
            # Sort by RSI (lowest first to show buy signals first)
            results.sort(key=lambda x: x['rsi'])
            
            for result in results:
                status_str = f"{result['emoji']} {result['status']}"
                cprint(
                    f"{result['symbol']:<10} {result['rsi']:>8.2f} ${result['price']:>14,.4f} {status_str:<25}",
                    result['color']
                )
            
            # Alert if signals found
            if signals_found:
                cprint(f"\n{'='*90}", "red")
                cprint("🚨 SIGNAL DETECTED! RSI has crossed threshold!", "red", attrs=["bold", "blink"])
                cprint(f"{'='*90}\n", "red")
                
                # Show specific signals
                for result in results:
                    if result['rsi'] < RSI_OVERSOLD:
                        cprint(f"  🟢 {result['symbol']}: BUY SIGNAL (RSI={result['rsi']:.1f} < {RSI_OVERSOLD})", "green", attrs=["bold"])
                    elif result['rsi'] > RSI_OVERBOUGHT:
                        cprint(f"  🔴 {result['symbol']}: SELL SIGNAL (RSI={result['rsi']:.1f} > {RSI_OVERBOUGHT})", "yellow", attrs=["bold"])
            else:
                cprint("\n⏸️  No extreme RSI levels detected", "white")
                
                # Show closest to thresholds
                closest_buy = min([r for r in results], key=lambda x: abs(x['rsi'] - RSI_OVERSOLD))
                closest_sell = min([r for r in results], key=lambda x: abs(x['rsi'] - RSI_OVERBOUGHT))
                
                cprint(f"\n📍 Closest to thresholds:", "cyan")
                cprint(f"  Buy  ({RSI_OVERSOLD}): {closest_buy['symbol']} at RSI {closest_buy['rsi']:.1f} (distance: {abs(closest_buy['rsi'] - RSI_OVERSOLD):.1f})", "cyan")
                cprint(f"  Sell ({RSI_OVERBOUGHT}): {closest_sell['symbol']} at RSI {closest_sell['rsi']:.1f} (distance: {abs(closest_sell['rsi'] - RSI_OVERBOUGHT):.1f})", "cyan")
        
        return signals_found
        
    except Exception as e:
        cprint(f"❌ Error in monitor_rsi: {str(e)}", "red")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main monitoring loop"""
    display_header()
    
    cprint("🚀 Starting RSI Monitor...", "green", attrs=["bold"])
    cprint("Press Ctrl+C to stop\n", "white")
    
    cycle_count = 0
    
    try:
        while True:
            cycle_count += 1
            cprint(f"\n📈 Cycle #{cycle_count}", "cyan")
            
            # Monitor RSI
            signal_detected = monitor_rsi()
            
            # Sleep until next check
            if not signal_detected:
                next_check = datetime.now().timestamp() + CHECK_INTERVAL_SECONDS
                next_check_time = datetime.fromtimestamp(next_check).strftime('%H:%M:%S')
                cprint(f"\n💤 Sleeping {CHECK_INTERVAL_SECONDS}s... Next check at {next_check_time}", "white")
                time.sleep(CHECK_INTERVAL_SECONDS)
            else:
                # If signal detected, check more frequently (1 minute)
                cprint(f"\n⚡ Signal active - checking again in 60 seconds...", "yellow")
                time.sleep(60)
                
    except KeyboardInterrupt:
        cprint(f"\n\n⚠️  Monitor stopped by user", "yellow")
        cprint(f"Total cycles completed: {cycle_count}", "white")
    except Exception as e:
        cprint(f"\n\n❌ Fatal error: {str(e)}", "red")
        import traceback
        traceback.print_exc()
    finally:
        cprint(f"\n👋 RSI Monitor shutdown complete", "cyan")

if __name__ == "__main__":
    main()
