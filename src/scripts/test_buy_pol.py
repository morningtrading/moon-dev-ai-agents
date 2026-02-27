
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import src.nice_funcs_hyperliquid as n

def test_buy_pol():
    print("🌙 Moon Dev Testing: Buy POL-USDC")
    
    # Load account
    try:
        account = n._get_account_from_env()
        print(f"✅ Account loaded: {account.address}")
    except Exception as e:
        print(f"❌ Failed to load account: {e}")
        return

    # Check for POL symbol
    symbol = "POL"
    print(f"🔍 Checking for symbol: {symbol}")
    
    # Check if symbol exists and get decimals
    sz_dec, px_dec = n.get_sz_px_decimals(symbol)
    
    if sz_dec == 0 and px_dec == 0:
        print(f"⚠️  Symbol '{symbol}' not found or error fetching details.")
        print("🔍 Checking if 'MATIC' exists instead (HyperLiquid might still use old ticker)...")
        symbol = "MATIC"
        sz_dec, px_dec = n.get_sz_px_decimals(symbol)
        
        if sz_dec == 0 and px_dec == 0:
            print("❌ Neither POL nor MATIC found. Aborting.")
            return
        else:
            print(f"✅ Found 'MATIC' instead. Using MATIC.")

    print(f"✅ Symbol confirmed: {symbol}")
    
    # Helper to check balance
    try:
        n.get_balance(account)
    except:
        pass

    # Attempt buy
    amount_usd = 5
    print(f"\n🛒 Attempting to buy ${amount_usd} of {symbol}...")
    print("⚠️  NOTE: HyperLiquid has a minimum order value of $10.")
    print("⚠️  The market_buy function uses logic to automatically adjust < $10 orders to ~$11.")
    
    # Calling market_buy
    # n.market_buy handles the order placement and minimum size adjustment
    try:
        res = n.market_buy(symbol, amount_usd, account)
        print(f"Order Result: {res}")
    except Exception as e:
        print(f"❌ Error executing buy: {e}")

if __name__ == "__main__":
    test_buy_pol()
