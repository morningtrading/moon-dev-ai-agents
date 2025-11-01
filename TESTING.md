# 🧪 Moon Dev Agent Testing Guide

## Overview

This guide covers testing individual agents and the full orchestrator for the HyperLiquid trading system.

## 🛡️ PRIORITY 1: Core Risk Management

### Risk Agent ✅ **WORKING**

**What it does**: Monitors portfolio value, tracks P&L, and can close positions if risk limits are breached.

**Test Command**:
```bash
python3 -m src.agents.risk_agent
```

**What to expect**:
- Shows your HyperLiquid portfolio value (~$929 from ATF, AI16Z, VIRTUAL)
- Logs all open positions with entry prices and PnL%
- Creates balance history in `src/data/portfolio_balance.csv`
- Runs in a loop, checking every 5 minutes
- **Stop with**: Ctrl+C

**Current Status**: ✅ Fixed and working with HyperLiquid main account address

---

## 🤖 PRIORITY 2: Trading Agents

### Trading Agent

**What it does**: Analyzes market data and generates BUY/SELL/DO NOTHING trading signals using AI models or AI swarm consensus.

**Configuration** (in `src/agents/trading_agent.py`):
- Line 84: `EXCHANGE = "HYPERLIQUID"` ✅ Already fixed
- Line 173-177: Update `SYMBOLS` list:
  ```python
  SYMBOLS = [
      'BTC',      # Bitcoin (add your tokens here)
      #'ETH',     # Ethereum (uncomment to enable)
      #'SOL',     # Solana
  ]
  ```
- Line 90: `USE_SWARM_MODE` - True for consensus (45-60s), False for fast (10s)
- Line 94: `LONG_ONLY` - True for long-only, False for long/short capability

**Test Command**:
```bash
python3 -m src.agents.trading_agent
```

**What to expect**:
- Fetches OHLCV data for configured symbols
- Generates trading signals (BUY/SELL/DO NOTHING)
- In swarm mode: queries 6 AI models for consensus
- Recommends position actions with confidence scores
- **May take 45-60 seconds in swarm mode per token**

**Known Issues**:
- May hang without proper exit condition (Ctrl+C)
- Requires configuration update for your specific trading style

---

## 📋 Recommended Testing Sequence

### Step 1: Verify Risk Agent ✅
```bash
python3 -m src.agents.risk_agent  # Run for 2-3 cycles, then Ctrl+C
```
✓ **Verify**: Shows your HyperLiquid portfolio correctly

### Step 2: Configure Trading Agent
Edit `src/agents/trading_agent.py`:
- Set `EXCHANGE = "HYPERLIQUID"` (already done)
- Update `SYMBOLS` list with tokens to trade
- Set `USE_SWARM_MODE = False` for faster testing
- Set `LONG_ONLY = True` for safer first test

### Step 3: Test Trading Agent
```bash
python3 -m src.agents.trading_agent  # Ctrl+C after first signal
```
✓ **Verify**: Generates trading signals for your configured symbols

### Step 4: Test Full Orchestrator
Edit `src/main.py`:
```python
ACTIVE_AGENTS = {
    'risk': True,      # ✅ Always on
    'trading': True,   # ✅ Turn on for testing
    'strategy': False, # Leave off for now
}
```

Run:
```bash
python3 -m src.main
```
✓ **Verify**: Both agents run in sequence without errors

---

## ✅ Testing Checklist

- [x] Risk Agent shows correct portfolio value
- [x] Risk Agent detects all open positions
- [ ] Trading Agent generates signals (with 1 symbol first)
- [ ] Main orchestrator runs both agents
- [ ] No hanging/timeout issues
- [ ] No unhandled exceptions
- [ ] All dependencies installed
- [ ] Environment variables configured
- [ ] Ready for live trading testing

---

## 🚀 Next Steps

After all agents are tested:

1. **Test Trading Agent** with 1 symbol first
2. **Set Position Size** appropriately 
3. **Start Small** (test with paper trading mindset)
4. **Monitor Logs** (check `src/data/` for agent outputs)
5. **Scale Up** (gradually add more tokens/agents)

---

**Last Updated**: 2025-10-31  
**System**: Moon Dev AI Trading System  
**Exchange**: HyperLiquid  
**Status**: Testing Phase - Risk Agent Working ✅