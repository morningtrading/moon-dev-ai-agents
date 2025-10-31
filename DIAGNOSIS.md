# 🔍 Risk Agent HyperLiquid Integration Diagnosis

## Problems Identified

### 1. **Wrong API Calls for HyperLiquid (Critical)**
- **Location**: `risk_agent.py:129` calls `n.get_token_balance_usd(config.USDC_ADDRESS)`
- **Issue**: Function tries to query Solana BirdEye API (`fetch_wallet_holdings_og`) when you have `EXCHANGE = 'hyperliquid'`
- **USDC Address being queried**: `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` (Solana token address)
- **Your wallet being queried**: `4wgfCBf2WwLSRKLef9iW7JXZ2AfkxUxGM4XcKpHm3Sin` (Solana wallet)

### 2. **Missing get_token_balance_usd() Function**
- **Function used**: Line 129 in `risk_agent.py` calls `n.get_token_balance_usd()`
- **Reality**: This function doesn't exist in `nice_funcs.py`
- **What exists instead**: `nice_funcs_hyperliquid.py` has `get_account_value()` and `get_all_positions()` but these aren't being called

### 3. **BirdEye API Authentication Error**
- **Error**: `Error code: 401 - invalid x-api-key`
- **Cause**: When Risk Agent calls Claude to analyze breach, it tries to fetch wallet holdings again
- **Location**: `risk_agent.py:464` calls `n.fetch_wallet_holdings_og(address)` in `handle_limit_breach()`
- **Result**: API call fails, triggers exception handler which defaults to closing all positions

### 4. **Empty MONITORED_TOKENS List**
- **Config**: `MONITORED_TOKENS = []` (line 18 in config.py)
- **Effect**: Risk Agent has no tokens to monitor, checks 0 tokens
- **Should be**: Using `HYPERLIQUID_SYMBOLS = ['BTC', 'ETH', 'SOL']` instead

### 5. **Position Closing Uses Wrong Exchange**
- **Location**: `risk_agent.py:407` calls `n.chunk_kill()` (Solana function)
- **Problem**: HyperLiquid uses `kill_switch()` instead
- **Reality**: When positions need closing, it fails silently because `chunk_kill` is Solana-specific

## Call Flow - Where It Breaks

```
risk_agent.run()
  ↓
get_portfolio_value()  ← WRONG EXCHANGE
  ├─ Tries: n.get_token_balance_usd(USDC_ADDRESS)  ✗ Function doesn't exist
  ├─ Falls back to: n.fetch_wallet_holdings_og()  ✗ Solana API
  └─ Result: $0.00 portfolio (actual HyperLiquid account ignored)

check_pnl_limits()
  ├─ Calculates: $0 - $0 = $0 PnL  ✗ Wrong data
  └─ Triggers: Balance < $50 threshold

handle_limit_breach()
  ├─ Calls: n.fetch_wallet_holdings_og()  ✗ Solana API again
  ├─ API fails: 401 authentication error
  ├─ Exception handler runs
  └─ Closes positions with: n.chunk_kill()  ✗ Solana function (doesn't work)
```

## HyperLiquid Functions Already Available

Located in `nice_funcs_hyperliquid.py`:
- ✅ `get_account_value(account)` - Total account value
- ✅ `get_balance(account)` - USDC balance
- ✅ `get_all_positions(account)` - All open positions
- ✅ `get_position(symbol, account)` - Specific position
- ✅ `kill_switch(symbol, account)` - Close position
- ✅ `ask_bid(symbol)` - Get current prices

Located in `exchange_manager.py`:
- ✅ `get_token_balance_usd()` method already routes correctly

## Solution Path

1. ✅ Add exchange detection to Risk Agent
2. ✅ Create wrapper function that uses correct exchange
3. ✅ Update portfolio value calculation to use HyperLiquid API when needed
4. ✅ Switch position closing to use `kill_switch()` for HyperLiquid
5. ✅ Update MONITORED_TOKENS to use HYPERLIQUID_SYMBOLS
6. ✅ Verify HYPER_LIQUID_ETH_PRIVATE_KEY exists in .env

## Key Difference: Solana vs HyperLiquid

| Aspect | Solana | HyperLiquid |
|--------|--------|-----------|
| Position source | BirdEye API wallet endpoint | HyperLiquid Info API (`user_state`) |
| Symbols | Token addresses (long strings) | Asset symbols (BTC, ETH, SOL) |
| Data in `assetPositions` | Token balances | Perpetual positions |
| Closing function | `chunk_kill()` | `kill_switch()` |
| Account init | Wallet address | Eth private key |
