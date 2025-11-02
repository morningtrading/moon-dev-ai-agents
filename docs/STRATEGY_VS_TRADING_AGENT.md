# Strategy Agent vs Trading Agent - Complete Comparison

**Moon Dev AI Agents - System Architecture Analysis**

---

## 🎯 TL;DR - Quick Summary

| Feature | Strategy Agent | Trading Agent |
|---------|---------------|---------------|
| **Purpose** | Execute multi-strategy trading signals | AI-driven discretionary trading |
| **Decision Making** | Strategy logic + AI validation | Pure AI analysis (6-model swarm) |
| **Cycle Time** | 15 minutes | 15 minutes |
| **Signals** | From loaded strategy classes | From market data analysis |
| **Validation** | Claude validates strategy signals | Swarm consensus validates trades |
| **Strategies** | Multiple (RSI 25/85 + more) | None (AI decides everything) |
| **Best For** | Rule-based, backtested systems | Discretionary AI trading |
| **Complexity** | High (multi-strategy orchestration) | Medium (data → AI → trade) |

---

## 📋 Detailed Comparison

### 1. Core Purpose

**Strategy Agent:**
- **Role:** Systematic strategy executor
- **Function:** Load multiple strategy classes, collect signals, validate with AI, execute approved trades
- **Philosophy:** "Let backtested strategies make decisions, AI validates them"
- **Use Case:** When you have proven strategies (like RSI 25/85) that you trust

**Trading Agent:**
- **Role:** AI discretionary trader
- **Function:** Collect market data, ask AI swarm to analyze, execute consensus recommendations
- **Philosophy:** "Let AI analyze raw data and make all decisions"
- **Use Case:** When you want AI to discover patterns without predefined rules

---

### 2. Decision Making Process

**Strategy Agent Flow:**
```
1. Load strategies (MyStrategy, ExampleStrategy, etc.)
2. Each strategy generates signals (BUY/SELL/None)
3. Aggregate signals by token
4. Get market data for context
5. AI (Claude) validates signals
6. Execute only approved signals
```

**Trading Agent Flow:**
```
1. Collect OHLCV data for all tokens
2. Format data for AI consumption
3. Query 6-model swarm (or single model)
4. Calculate consensus vote
5. Execute majority decision if confidence > 80%
```

---

### 3. AI Usage

**Strategy Agent:**
- **Model:** Claude (Anthropic)
- **Role:** Validator/Filter
- **Question:** "Should I execute this strategy's signal?"
- **Input:** Strategy signal + reasoning + market data
- **Output:** EXECUTE or REJECT + reasoning
- **Prompt Focus:** Risk assessment, signal quality, market alignment

**Trading Agent:**
- **Mode 1 - Swarm:** 6 models vote (Claude, GPT-5, Qwen3, Grok-4, DeepSeek x2)
- **Mode 2 - Single:** One fast model (configurable)
- **Role:** Decision Maker
- **Question:** "What should I do with this token?"
- **Input:** Raw OHLCV data + indicators
- **Output:** BUY, SELL, or NOTHING + confidence %
- **Prompt Focus:** Technical analysis, market conditions, action selection

---

### 4. Strategy Integration

**Strategy Agent:**
```python
# Has built-in strategy loader
from strategies.custom.private_my_strategy import MyStrategy

self.enabled_strategies = [
    MyStrategy()  # RSI 25/85
    # Add more strategies here
]

# Each strategy implements:
- generate_signals() → Returns signal dict
- analyze() → Performs indicator calculations
```

**Trading Agent:**
```python
# No built-in strategies
# Can receive optional strategy signals:
def run_trading_cycle(self, strategy_signals=None):
    if strategy_signals and token in strategy_signals:
        data['strategy_signals'] = strategy_signals[token]
    
# But doesn't require them - AI analyzes raw data
```

**Key Difference:**
- Strategy Agent: Strategies are **required** (primary signal source)
- Trading Agent: Strategies are **optional** (supplementary context for AI)

---

### 5. Signal Sources

**Strategy Agent:**
| Source | Type | Example |
|--------|------|---------|
| RSI Strategy | Technical | RSI < 25 → BUY |
| MACD Strategy | Technical | Bullish crossover → BUY |
| Custom Strategy | Any logic | Your algorithm → BUY/SELL |
| AI Validation | Filter | Approves/rejects above signals |

**Trading Agent:**
| Source | Type | Example |
|--------|------|---------|
| Claude Sonnet | AI analysis | Swarm vote: BUY |
| GPT-5 | AI analysis | Swarm vote: BUY |
| Grok-4 | AI analysis | Swarm vote: SELL |
| Qwen3 | AI analysis | Swarm vote: BUY |
| DeepSeek Chat | AI analysis | Swarm vote: BUY |
| DeepSeek-R1 | AI analysis | Swarm vote: BUY |
| **Consensus** | **Vote** | **5/6 = BUY at 83% confidence** |

---

### 6. Code Architecture

**Strategy Agent:**
```python
class StrategyAgent:
    def __init__(self):
        # Load all strategies
        self.enabled_strategies = [MyStrategy(), ...]
        self.client = anthropic.Anthropic()
        
    def run_strategy_cycle(self):
        # 1. Collect signals from all strategies
        signals = []
        for strategy in self.enabled_strategies:
            signal = strategy.generate_signals()
            if signal:
                signals.append(signal)
        
        # 2. Group by token
        grouped = self.group_signals_by_token(signals)
        
        # 3. AI validates each token's signals
        for token, token_signals in grouped.items():
            evaluation = self.evaluate_signals(token_signals, market_data)
            
            if evaluation['decision'] == 'EXECUTE':
                self.execute_trade(token, token_signals)
        
        time.sleep(15 * 60)  # 15 minutes
```

**Trading Agent:**
```python
class TradingAgent:
    def __init__(self):
        if USE_SWARM_MODE:
            self.swarm = SwarmAgent()  # 6 models
        else:
            self.model = model_factory.get_model(AI_MODEL_TYPE)
    
    def run_trading_cycle(self):
        # 1. Collect market data
        market_data = collect_all_tokens(SYMBOLS, TIMEFRAME)
        
        # 2. Analyze each token
        for token, data in market_data.items():
            # Swarm mode: 6 models vote
            if USE_SWARM_MODE:
                swarm_result = self.swarm.query(data)
                action, confidence = self._calculate_consensus(swarm_result)
            # Single mode: one model decides
            else:
                response = self.model.generate_response(data)
                action, confidence = self._parse_response(response)
            
            # 3. Execute if confidence > threshold
            if confidence >= MIN_SWARM_CONFIDENCE:
                self.execute_action(token, action)
        
        time.sleep(15 * 60)  # 15 minutes
```

---

### 7. Execution Logic

**Strategy Agent:**
```python
# Only executes APPROVED strategy signals
if evaluation['decision'] == 'EXECUTE':
    # Use ExchangeManager for unified execution
    if signal['direction'] == 'BUY':
        self.em.market_buy(token, position_size)
    elif signal['direction'] == 'SELL':
        self.em.market_sell(token, position_size)
```

**Trading Agent:**
```python
# Executes based on AI decision + current position state
if action == 'BUY':
    if no_position:
        open_position(token, size)
    else:
        hold_position(token)  # Keep existing
        
elif action == 'SELL':
    if has_position:
        close_position(token)
    elif not LONG_ONLY:
        open_short(token, size)
    else:
        do_nothing()  # Can't short in LONG_ONLY
        
elif action == 'NOTHING':
    maintain_current_state(token)
```

---

### 8. Configuration

**Strategy Agent:**
```python
# File: src/agents/strategy_agent.py
ENABLE_STRATEGIES = True  # From config.py
STRATEGY_MIN_CONFIDENCE = 0.7  # Min 70% to execute
SLEEP_BETWEEN_RUNS_MINUTES = 15
HYPERLIQUID_SYMBOLS = ['BTC', 'ETH', 'SOL', 'BNB', 'XLM']

# Strategies loaded at runtime:
self.enabled_strategies.extend([
    MyStrategy()  # RSI 25/85
])
```

**Trading Agent:**
```python
# File: src/agents/trading_agent.py (lines 66-183)
EXCHANGE = "HYPERLIQUID"  # or ASTER, SOLANA
USE_SWARM_MODE = True  # 6-model consensus
LONG_ONLY = True  # No shorting
MIN_SWARM_CONFIDENCE = 80  # Only trade if 80%+ agree
MAX_POSITION_PERCENTAGE = 10  # 10% of balance per position
LEVERAGE = 3  # 3x leverage
STOP_LOSS_PERCENTAGE = 2.0
TAKE_PROFIT_PERCENTAGE = 4.0
SLEEP_BETWEEN_RUNS_MINUTES = 15
SYMBOLS = HYPERLIQUID_SYMBOLS  # Loaded from config
```

---

### 9. Monitoring & Tracking

**Strategy Agent:**
```python
# Logs:
✅ Loaded 1 strategies!
  • 🌙 RSI(25/85) Mean-Reversion Strategy

🔍 🌙 RSI(25/85) analyzing 5 symbols...
  BTC: RSI 43.1 (Neutral)
  ETH: RSI 41.3 (Neutral)
  XLM: RSI 27.8 (⚠️ Approaching buy threshold!)

📊 Raw Strategy Signals for BTC:
  • RSI Strategy: No signal (neutral)

🤖 Getting LLM evaluation of signals...
✅ No signals to evaluate this cycle

💤 Sleeping 15 minutes... Next run at 22:42:58
```

**Trading Agent:**
```python
# Logs:
🌊 Analyzing BTC with SWARM (6 AI models voting)

🤖 Active Swarm Models:
   - claude: claude-sonnet-4.5
   - openai: gpt-5
   - ollama_qwen: qwen3-8b
   - xai: grok-4-fast-reasoning
   - deepseek: deepseek-chat
   - ollama_deepseek: deepseek-r1

📊 MARKET DATA RECEIVED FOR BTC
✅ DataFrame received: 72 bars
📅 Date range: 2025-01-30 to 2025-02-02

🌊 Swarm Consensus:
  Buy: 5 votes
  Sell: 0 votes
  Do Nothing: 1 votes

🌊 Swarm Consensus: BUY with 83% agreement

📈 BUY signal with no position
💰 Opening position at MAX_POSITION_PERCENTAGE
✅ Position opened successfully!
```

---

### 10. When to Use Which Agent

**Use Strategy Agent When:**
- ✅ You have backtested strategies you trust
- ✅ You want rule-based, reproducible trading
- ✅ You need multiple strategies working together
- ✅ You want AI as a safety filter (not decision maker)
- ✅ You prefer systematic over discretionary trading
- ✅ You want to add/remove strategies easily (plug-and-play)

**Use Trading Agent When:**
- ✅ You want AI to make all decisions
- ✅ You trust machine learning pattern recognition
- ✅ You want 6-model consensus for confidence
- ✅ You don't have specific strategies yet
- ✅ You prefer discretionary over systematic
- ✅ You want AI to adapt to changing markets

---

### 11. Can They Work Together?

**Yes! Two Ways:**

**Option 1: Sequential (Recommended)**
```
1. Strategy Agent runs, generates signals
2. Trading Agent receives strategy signals as input
3. Trading Agent's swarm considers both:
   - Market data (OHLCV)
   - Strategy signals (as context)
4. Swarm makes final decision
```

**Option 2: Parallel (Advanced)**
```
1. Both agents run independently
2. Different token allocations:
   - Strategy Agent: BTC, ETH (systematic)
   - Trading Agent: SOL, BNB, XLM (discretionary)
3. Risk agent monitors total exposure
```

**Currently:** They run **independently** (not integrated)

---

### 12. Integration Possibilities

**To integrate strategy_agent → trading_agent:**

```python
# In trading_agent.py, line 1093:
def run_trading_cycle(self, strategy_signals=None):
    # Already accepts optional strategy signals!
    
    if strategy_signals and token in strategy_signals:
        cprint(f"📊 Including strategy signals in analysis", "cyan")
        data['strategy_signals'] = strategy_signals[token]
```

**To enable:**
1. Run strategy_agent first
2. Collect approved signals
3. Pass to trading_agent as `strategy_signals` parameter
4. Trading agent's swarm sees both market data + strategy signals
5. Swarm makes final decision with full context

---

## 13. Current System State

**What's Running:**
```bash
Agent               Status    Purpose
─────────────────────────────────────────────────
strategy_agent      ✅        Execute RSI 25/85 strategy
trading_agent       ✅        AI swarm discretionary trading
funding_agent       ✅        Monitor funding rates
grok_sentiment_agent ✅       Track social sentiment
risk_agent          ✅        Portfolio risk management
whale_agent         ✅        Whale transaction alerts
liquidation_agent   ✅        Liquidation monitoring
```

**Current Setup:**
- Both agents track **same 5 coins**: BTC, ETH, SOL, BNB, XLM
- Both run **independently** (no integration)
- Both execute trades on **Hyperliquid**
- Both use **15-minute cycles**

---

## 14. Recommendations

### For Your Use Case:

**Keep Both Running Because:**

1. **Strategy Agent (RSI 25/85)**
   - ✅ Proven strategy (+22.84% backtested)
   - ✅ Waits for extreme conditions (patient)
   - ✅ AI validates before execution (safe)
   - ✅ Systematic, rule-based approach

2. **Trading Agent (AI Swarm)**
   - ✅ 6-model consensus (robust)
   - ✅ Analyzes market conditions AI can see
   - ✅ May catch opportunities strategy misses
   - ✅ Discretionary, adaptive approach

**To avoid conflicts:**
- Set `MAX_POSITION_PERCENTAGE` conservatively (10% each agent)
- Monitor total portfolio exposure with risk_agent
- Consider giving each agent different token allocations

**Example Safe Allocation:**
```python
# Strategy Agent: 50% of portfolio
MAX_POSITION_PERCENTAGE = 10  # per position
Tokens: BTC, ETH

# Trading Agent: 50% of portfolio  
MAX_POSITION_PERCENTAGE = 10  # per position
Tokens: SOL, BNB, XLM
```

---

## 15. Summary Table

| Aspect | Strategy Agent | Trading Agent |
|--------|---------------|---------------|
| **Signal Source** | Strategy classes | AI analysis |
| **AI Role** | Validator | Decision maker |
| **Models Used** | Claude (1 model) | Swarm (6 models) or Single |
| **Backtesting** | Required (strategies) | Not applicable |
| **Adaptability** | Low (rule-based) | High (AI learns) |
| **Transparency** | High (clear rules) | Medium (AI reasoning) |
| **Customization** | High (add strategies) | Medium (config) |
| **Risk** | Lower (validated rules) | Higher (AI mistakes) |
| **Speed** | Fast (rules + validation) | Slower (6 models) |
| **Best For** | Systematic traders | Discretionary traders |
| **Complexity** | High (multi-strategy) | Medium (swarm voting) |
| **Current State** | ✅ Running (RSI 25/85) | ✅ Running (swarm mode) |

---

## 16. File Locations

**Strategy Agent:**
```
src/agents/strategy_agent.py          # Main orchestrator
src/strategies/base_strategy.py       # Strategy interface
src/strategies/custom/
  ├── private_my_strategy.py          # RSI 25/85
  └── [add more strategies here]
```

**Trading Agent:**
```
src/agents/trading_agent.py           # Complete standalone agent
src/agents/swarm_agent.py             # 6-model swarm implementation
src/models/model_factory.py           # AI model loader
```

**Shared:**
```
src/config.py                          # HYPERLIQUID_SYMBOLS, TOKEN_NAMES
src/exchange_manager.py                # Unified trading interface
agent_config.yaml                      # Agent enable/disable
```

---

## 17. Key Takeaway

**They solve different problems:**

- **Strategy Agent:** "I have a proven strategy, help me execute it safely"
- **Trading Agent:** "I have market data, help me find profitable trades"

**Both are valuable!**

Use strategy_agent for **systematic** strategies you've backtested.  
Use trading_agent for **discretionary** AI-driven opportunities.

Running both gives you:
- ✅ Systematic coverage (strategy agent)
- ✅ Discretionary opportunities (trading agent)
- ✅ Diversified decision-making approaches
- ✅ Redundancy (if one misses, other may catch)

Just manage position sizing carefully so they don't over-allocate!

---

**🌙 Built with Moon Dev AI Agents**  
**📅 Last Updated: 2025-11-02**
