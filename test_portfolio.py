#!/usr/bin/env python3
"""Quick test of portfolio value"""
import sys
import os
sys.path.insert(0, '/home/titus/moon-dev-ai-agents')
os.chdir('/home/titus/moon-dev-ai-agents')

from dotenv import load_dotenv
load_dotenv()

from src.nice_funcs import get_hyperliquid_portfolio_value

print("Testing portfolio value...\n")
value = get_hyperliquid_portfolio_value()
print(f"\n\nFinal portfolio value: ${value:,.2f}")
