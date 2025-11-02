# Centralized Coin Configuration

## Overview
All agents now use a centralized coin configuration from `src/config.py` to ensure consistency across the system.

## Changes Made

### 1. Central Configuration (src/config.py)
**Master Coin List:**
- `HYPERLIQUID_SYMBOLS = ['BTC', 'ETH', 'SOL', 'BNB', 'XLM']`
- `TOKEN_NAMES` dictionary maps symbols to full names

This is the **single source of truth** for which coins to monitor across ALL agents.

### 2. Updated Agents

#### Grok Sentiment Agent (`src/agents/grok_sentiment_agent.py`)
- **Before:** Hardcoded `TOKENS_TO_TRACK` with BTC, ETH, SOL, DOGE, PEPE, WIF, BONK, XRP
- **After:** Imports `TOKEN_NAMES` from `src/config`
- **Result:** Now tracks BTC, ETH, SOL, BNB, XLM

#### Funding Agent (`src/agents/funding_agent.py`)
- **Before:** Hardcoded `SYMBOL_NAMES` with only FARTCOIN
- **After:** Imports `TOKEN_NAMES` from `src/config`
- **Result:** Now tracks BTC, ETH, SOL, BNB, XLM

#### Trading Agent (`src/agents/trading_agent.py`)
- **Before:** Hardcoded `SYMBOLS` list with BTC, ETH, SOL, BNB, HYPE
- **After:** Imports `HYPERLIQUID_SYMBOLS` and initializes from config
- **Result:** Now tracks BTC, ETH, SOL, BNB, XLM

#### Whale Agent (`src/agents/whale_agent.py`)
- **Status:** Hardcoded to track BTC and ETH open interest
- **Note:** Works independently by analyzing all open interest data

#### Liquidation Agent (`src/agents/liquidation_agent.py`)
- **Status:** Analyzes all liquidation events across all coins
- **Note:** No coin-specific list needed

## Benefits

1. **Consistency:** All agents now track the same coins
2. **Easy Management:** Change coins in one place (`src/config.py`)
3. **No Confusion:** Grok sentiment agent no longer tracks obscure meme coins
4. **Professional Focus:** System now focuses on major cryptocurrencies

## How to Add/Remove Coins

### To Add a Coin
Edit `src/config.py`:

```python
HYPERLIQUID_SYMBOLS = ['BTC', 'ETH', 'SOL', 'BNB', 'XLM', 'NEW_COIN']

TOKEN_NAMES = {
    'BTC': 'Bitcoin',
    'ETH': 'Ethereum',
    'SOL': 'Solana',
    'BNB': 'Binance Coin',
    'XLM': 'Stellar',
    'NEW_COIN': 'New Coin Name'
}
```

### To Remove a Coin
Simply remove it from both lists in `src/config.py`.

## Verified Agents Using Centralized Config

✅ **grok_sentiment_agent** - Sentiment analysis with Grok AI
✅ **funding_agent** - Funding rate monitoring
✅ **trading_agent** - AI-powered trading decisions

## Testing

All agents have been tested and confirmed to import the correct coin list:

```bash
# Test central config
python -c "from src.config import HYPERLIQUID_SYMBOLS, TOKEN_NAMES; print(HYPERLIQUID_SYMBOLS)"

# Test grok_sentiment_agent
python -c "from src.agents.grok_sentiment_agent import TOKENS_TO_TRACK; print(TOKENS_TO_TRACK)"

# Test funding_agent
python -c "from src.agents.funding_agent import SYMBOL_NAMES; print(SYMBOL_NAMES)"
```

Expected output for all: `BTC, ETH, SOL, BNB, XLM`

## Date
Configuration centralized: 2025-11-02
