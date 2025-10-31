#!/usr/bin/env python3
"""
🔍 Test HyperLiquid Setup
Verify that your HyperLiquid account is properly configured
"""

import os
from dotenv import load_dotenv
from termcolor import cprint

load_dotenv()

print("\n" + "="*60)
print("🔍 HyperLiquid Setup Verification")
print("="*60)

# Check for private key
private_key = os.getenv('HYPER_LIQUID_ETH_PRIVATE_KEY')
print("\n1️⃣  Checking HYPER_LIQUID_ETH_PRIVATE_KEY...")
if not private_key:
    cprint("   ❌ Not set", "red")
elif private_key == "your_hyper_liquid_eth_private_key_here":
    cprint("   ⚠️  Still has placeholder value", "yellow")
else:
    cprint("   ✅ Set (value hidden)", "green")

# Try to load account
print("\n2️⃣  Testing account initialization...")
try:
    import eth_account
    if private_key and private_key != "your_hyper_liquid_eth_private_key_here":
        account = eth_account.Account.from_key(private_key)
        cprint(f"   ✅ Account loaded: {account.address}", "green")
    else:
        cprint("   ⚠️  Cannot test - private key not configured", "yellow")
except Exception as e:
    cprint(f"   ❌ Error: {str(e)}", "red")

# Check API connectivity
print("\n3️⃣  Testing HyperLiquid API connectivity...")
try:
    from hyperliquid.info import Info
    from hyperliquid.utils import constants
    
    info = Info(constants.MAINNET_API_URL, skip_ws=True)
    meta = info.meta_and_asset_ctxs()
    cprint(f"   ✅ Connected to HyperLiquid API", "green")
    cprint(f"   📊 Available assets: {len(meta[1])} trading pairs", "cyan")
except Exception as e:
    cprint(f"   ❌ Error: {str(e)}", "red")

print("\n" + "="*60)
print("\n📋 NEXT STEPS:")
print("   1. Get your HyperLiquid private key from your wallet")
print("   2. Update .env with: HYPER_LIQUID_ETH_PRIVATE_KEY=<your_key>")
print("   3. Public wallet address (for reference): 0x54Ff2efe9C3dF4e32A8c60628198419D68472B55")
print("   4. Run this script again to verify setup")
print("\n" + "="*60 + "\n")
