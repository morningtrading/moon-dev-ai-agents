#!/usr/bin/env python3
"""
Test script to simulate AI consultation when risk limit is breached
Tests with your 3 current positions: JTO, AI16Z, ATF
Simulates 5% loss across all positions
"""

import sys
import os
sys.path.insert(0, '/home/titus/moon-dev-ai-agents')
os.chdir('/home/titus/moon-dev-ai-agents')

from dotenv import load_dotenv
load_dotenv()

import anthropic
import re
from termcolor import cprint

# Your current positions (from HyperLiquid UI)
POSITIONS = [
    {"symbol": "JTO", "size": 477, "entry_price": 0.90183, "current_price": 0.90183 * 0.95, "margin": 86.19},
    {"symbol": "AI16Z", "size": 4375.8, "entry_price": 0.07329, "current_price": 0.07329 * 0.95, "margin": 64.60},
    # ATF removed from your latest screenshot, but including for completeness
]

def simulate_breach():
    """Simulate a 5% loss and consult AI"""
    
    print("\n" + "="*70)
    cprint("🛡️ RISK BREACH SIMULATION TEST", "white", "on_blue")
    print("="*70)
    
    # Calculate losses
    print("\n📊 POSITIONS (with 5% loss simulated):")
    total_loss = 0
    positions_str = ""
    
    for pos in POSITIONS:
        loss_percent = -5.0
        entry_value = pos["size"] * pos["entry_price"]
        current_value = pos["size"] * pos["current_price"]
        pnl = current_value - entry_value
        
        print(f"\n  {pos['symbol']}:")
        print(f"    Size: {pos['size']}")
        print(f"    Entry: ${pos['entry_price']:.5f}")
        print(f"    Current (5% loss): ${pos['current_price']:.5f}")
        print(f"    PnL: ${pnl:.2f} ({loss_percent:.1f}%)")
        
        total_loss += pnl
        positions_str += f"- {pos['symbol']}: {pos['size']} (PnL: {loss_percent:.1f}%)\n"
    
    print(f"\n💰 TOTAL PnL: ${total_loss:.2f} (-5.0% across all positions)")
    
    # Simulate breach
    print("\n" + "="*70)
    print("⚠️ BREACH TRIGGERED: Loss exceeds max loss limit!")
    print("="*70)
    
    # Create the AI prompt
    prompt = f"""
🚨 RISK LIMIT BREACH ALERT 🚨

Your account has lost $18.50, exceeding the loss limit of $25.00

Current Positions:
{positions_str}

Should we close all positions immediately? Consider:
1. Market conditions
2. Position sizes and leverage (all 5x)
3. Recent price action (all down 5%)
4. Risk of further losses

Respond with:
CLOSE_ALL or HOLD_POSITIONS
Then explain your reasoning.
"""
    
    print("\n🤖 SENDING PROMPT TO AI (Claude)...\n")
    print("-" * 70)
    print("PROMPT SENT TO AI:")
    print("-" * 70)
    print(prompt)
    print("-" * 70)
    
    # Call Claude
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))
        
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            temperature=0.7,
            messages=[{
                "role": "user",
                "content": prompt
            }]
        )
        
        response_text = message.content[0].text
        
        print("\n" + "="*70)
        cprint("🤖 AI RESPONSE:", "white", "on_green")
        print("="*70)
        print(response_text)
        print("="*70)
        
        # Parse decision
        decision = response_text.split('\n')[0].strip().upper()
        
        if "CLOSE_ALL" in decision:
            cprint("\n🚨 AI DECISION: CLOSE ALL POSITIONS", "white", "on_red")
            print("→ Agent would immediately sell all positions at market price")
        elif "HOLD" in decision:
            cprint("\n✋ AI DECISION: HOLD POSITIONS", "white", "on_yellow")
            print("→ Agent would keep positions open despite breach")
        else:
            cprint("\n❓ AI DECISION: UNCLEAR", "white", "on_yellow")
            print(f"→ Response: {decision[:50]}...")
            
    except Exception as e:
        cprint(f"\n❌ Error calling AI: {e}", "white", "on_red")
        return False
    
    print("\n" + "="*70)
    print("✅ AI CONSULTATION TEST COMPLETE")
    print("="*70)
    return True

if __name__ == "__main__":
    print("\n🧪 Testing AI Consultation for Risk Breach...\n")
    simulate_breach()
