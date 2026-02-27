
import os
import sys
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import src.nice_funcs_hyperliquid as n

def test_buy_hype():
    print("🌙 Moon Dev Testing: Buy HYPE-USDC")
    
    # Load account
    try:
        account = n._get_account_from_env()
        print(f"✅ Account loaded: {account.address}")
    except Exception as e:
        print(f"❌ Failed to load account: {e}")
        return

    # Symbol to trade
    symbol = "HYPE"
    print(f"🔍 Checking for symbol: {symbol}")
    
    # Check if symbol exists and get decimals
    sz_dec, px_dec = n.get_sz_px_decimals(symbol)
    
    if sz_dec == 0 and px_dec == 0:
        print(f"❌ Symbol '{symbol}' not found on HyperLiquid Perps. Aborting.")
        # Try to fetch all symbols to see if it's under a different name
        try:
            info = n.get_market_info()
            if info:
                print(f"Items found matching 'HYPE': {[k for k in info.keys() if 'HYPE' in k]}")
        except:
            pass
        return

    print(f"✅ Symbol confirmed: {symbol}")
    
    # Amount: 10 EUR is approx $10.50 USD. 
    # Must be > $10. Let's do $12 to be safe and clear.
    amount_usd = 12
    print(f"\n🛒 Attempting to buy ${amount_usd} of {symbol} (approx 10 EUR)...")
    
    try:
        res = n.market_buy(symbol, amount_usd, account)
        print(f"Order Result: {res}")
    except Exception as e:
        print(f"❌ Error executing buy: {e}")

if __name__ == "__main__":
    test_buy_hype()
