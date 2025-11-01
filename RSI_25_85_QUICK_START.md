# 🚀 RSI(25/85) Trading Agent - Quick Start Guide

## 📋 Prerequisites

1. **Hyperliquid Account Setup:**
   - Create account at https://app.hyperliquid.xyz
   - Get your private key (testnet for paper trading, mainnet for real)
   - Fund account with USDC

2. **Environment Variables:**
   Edit `.env` file and add:
   ```bash
   HYPER_LIQUID_ETH_PRIVATE_KEY=your_private_key_here
   ```

3. **Python Dependencies:**
   All dependencies should already be installed from `requirements.txt`

---

## 🎯 Quick Start (Paper Trading)

### Step 1: Verify Configuration

The agent is already configured for paper trading by default:
```python
PAPER_TRADING = True  # No real trades, just logging
```

Located in: `/home/titus/moon-dev-ai-agents/src/agents/rsi_2585_agent.py`

### Step 2: Run the Agent

```bash
cd /home/titus/moon-dev-ai-agents
python src/agents/rsi_2585_agent.py
```

### Step 3: Monitor Output

The agent will:
- ✅ Connect to Hyperliquid
- ✅ Display account balance
- ✅ Check RSI for all 4 pairs every 5 minutes
- ✅ Log buy/sell signals (paper mode = no execution)
- ✅ Save logs to `src/data/rsi_2585_agent/trades_YYYYMMDD.log`

### Step 4: Stop the Agent

Press `Ctrl+C` to stop gracefully

---

## 📊 What the Agent Does

### Trading Logic:

1. **Every 5 minutes:**
   - Fetches 15m OHLCV data for BCH, BNB, PENDLE, QTUM
   - Calculates RSI(14) for each pair
   - Checks for buy/sell signals

2. **Buy Signal (RSI < 25):**
   - No existing position → Execute BUY
   - Has position → Hold

3. **Sell Signal (RSI > 85):**
   - Has position → Execute SELL
   - No position → Do nothing

4. **Hold Signal (25 < RSI < 85):**
   - Keep current position unchanged

### Position Sizing:
- **$25 per trade** (start small)
- **Max 5% of account** per position
- Equal weight across 4 pairs

---

## 🔄 Switching to Live Trading

⚠️ **CAUTION: Real money at risk!**

### Step 1: Test Paper Trading First

Run paper trading for **at least 2 weeks** to verify:
- Agent runs without errors
- Signals match your expectations
- Account connectivity is stable

### Step 2: Start with Micro Capital

Before going live:
1. Fund Hyperliquid account with **small amount** ($100-500)
2. Confirm position sizing is appropriate
3. Set stop losses and alerts

### Step 3: Enable Live Trading

Edit `src/agents/rsi_2585_agent.py`:
```python
PAPER_TRADING = False  # Enable live trading
```

The agent will warn you and give 10 seconds to cancel.

### Step 4: Monitor Closely

For first few days:
- Check performance hourly
- Compare live vs backtest results
- Watch for execution issues (slippage, fills)
- Track actual returns vs expected (+22.84%)

---

## 📈 Expected Performance

Based on triple-validated backtesting:

| Pair | Expected 3-Month Return | Trade Frequency |
|------|------------------------|-----------------|
| BCH | **+47.52%** 🔥 | ~2 trades/week |
| BNB | **+22.89%** | ~2 trades/week |
| PENDLE | **+14.25%** | ~2 trades/week |
| QTUM | **+6.69%** | ~1 trade/week |
| **Portfolio** | **+22.84%** | ~7 trades/week total |

**Note:** Live performance typically achieves 50-70% of backtest returns due to:
- Slippage
- Execution timing differences
- Market condition changes
- Exchange fees

**Realistic expectation: +11-16% over 3 months**

---

## ⚙️ Configuration Options

Edit these values in `src/agents/rsi_2585_agent.py`:

### Trading Pairs
```python
TRADING_PAIRS = [
    'BCH',      # Remove pairs you don't want
    'BNB',
    'PENDLE',
    'QTUM',
]
```

### RSI Parameters
```python
RSI_PERIOD = 14       # RSI calculation period
RSI_OVERSOLD = 25     # Buy threshold
RSI_OVERBOUGHT = 85   # Sell threshold
```

### Position Sizing
```python
POSITION_SIZE_USD = 25           # USD per trade
MAX_POSITION_PERCENTAGE = 5      # Max % of account per position
```

### Timing
```python
SLEEP_BETWEEN_CHECKS = 300  # Seconds between checks (300 = 5 min)
TIMEFRAME = '15m'           # Bar timeframe (15m, 1H, etc.)
```

---

## 📁 Log Files

### Location:
`/home/titus/moon-dev-ai-agents/src/data/rsi_2585_agent/`

### Files Created:
- `trades_YYYYMMDD.log` - Daily trading log
- Includes: timestamps, signals, RSI values, positions, PnL

### Example Log Entry:
```
[2025-11-01 14:30:15] 🔄 Trading Cycle Started
[2025-11-01 14:30:16] 💼 Account Status: Balance=$1000.00
[2025-11-01 14:30:17]   BCH: Price=$382.45, RSI=22.3, Position=No position
[2025-11-01 14:30:17]   🎯 BCH: BUY Signal - RSI(22.3) < 25 (oversold)
[2025-11-01 14:30:17]   📝 PAPER: Would BUY BCH for $25
```

---

## 🛡️ Risk Management

### Built-in Safeguards:

1. **Conservative Position Sizing:**
   - Only 5% of account per pair
   - Total max exposure: 20% (4 pairs × 5%)

2. **Mean-Reversion Strategy:**
   - Buys dips, sells strength
   - Not chasing trends = lower risk

3. **Paper Trading Default:**
   - Must manually enable live trading
   - 10-second warning before live execution

### Recommended Additional Safeguards:

1. **Manual Stop Loss:**
   - Monitor positions daily
   - Close if down >10% per pair
   - Close all if portfolio down >20%

2. **Time-Based Review:**
   - Week 1-2: Paper trade only
   - Week 3-4: Live with $100-500
   - Month 2+: Scale up gradually

3. **Performance Tracking:**
   - Compare live vs backtest weekly
   - If significantly underperforming → pause and analyze
   - If matching expectations → continue

---

## 📊 Monitoring Dashboard (Coming Soon)

A monitoring dashboard script will be created to show:
- Real-time PnL per pair
- RSI values and signals
- Win rate and trade stats
- Performance vs backtest comparison

Check: `src/agents/rsi_2585_monitor.py` (to be created)

---

## 🐛 Troubleshooting

### Agent won't start:
- Check `.env` has `HYPER_LIQUID_ETH_PRIVATE_KEY`
- Verify Hyperliquid API is accessible
- Check Python dependencies are installed

### No signals generating:
- Check if pairs have sufficient data (100+ bars)
- Verify timeframe is correct (15m)
- Check Hyperliquid supports all 4 pairs

### Unexpected behavior:
- Review logs in `src/data/rsi_2585_agent/`
- Compare RSI calculations manually
- Test in paper mode first

---

## 📞 Support

- **Project:** Moon Dev AI Trading Agents
- **Documentation:** `/home/titus/moon-dev-ai-agents/FINAL_STRATEGY_RSI_25_85.md`
- **Discord:** Join for community support
- **GitHub:** Report issues

---

## ⚠️ Disclaimer

**Risk Warning:**
- Cryptocurrency trading carries substantial risk of loss
- Past backtest performance does not guarantee future results
- Only trade with capital you can afford to lose
- Start small and scale gradually
- This is experimental software - use at your own risk

**Paper Trading Recommended:**
- Test for minimum 2 weeks before live trading
- Verify all functionality works as expected
- Compare results with backtest expectations

---

## ✅ Checklist for Going Live

Before enabling live trading:

- [ ] Paper traded for 2+ weeks
- [ ] Verified signals are correct
- [ ] No errors or crashes observed
- [ ] Reviewed all log files
- [ ] Compared paper results vs backtest
- [ ] Funded Hyperliquid account (start small: $100-500)
- [ ] Set up account value alerts
- [ ] Confirmed position sizing is appropriate
- [ ] Have plan to monitor daily for first week
- [ ] Understand and accept the risks

**Only proceed if ALL boxes are checked!**

---

🌙 Built with Moon Dev AI Trading Agents
🚀 Ready to deploy your validated strategy!
