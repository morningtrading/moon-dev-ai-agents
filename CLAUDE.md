# Moon Dev AI Agents - WARP Context

**Last Updated:** 2025-11-02

This file provides comprehensive context about the Moon Dev AI Trading Agents system for AI assistants.

---

## Project Overview

Moon Dev's experimental AI trading system with 48+ specialized agents for cryptocurrency trading across multiple exchanges (Hyperliquid, Solana/BirdEye, Aster, Extended).

**Key Characteristics:**
- Modular agent architecture (each agent < 800 lines)
- Multi-exchange support with unified API
- LLM provider abstraction (6 providers via ModelFactory)
- Risk-first trading approach
- Backtesting with RBI agent
- Educational/experimental project (no profit guarantees)

---

## Directory Structure

```
/home/titus/moon-dev-ai-agents/
├── src/
│   ├── agents/              # 48+ specialized AI agents
│   ├── models/              # LLM provider abstraction (ModelFactory)
│   ├── strategies/          # User-defined trading strategies
│   ├── scripts/             # Standalone utility scripts
│   ├── data/                # Agent outputs, memory, analysis results
│   ├── config.py            # Global configuration
│   ├── main.py              # Main orchestrator loop
│   ├── nice_funcs.py        # Core trading utilities (Solana/BirdEye)
│   ├── nice_funcs_hl.py     # Hyperliquid-specific functions
│   └── nice_funcs_extended.py # Extended Exchange functions
├── agent_manager.py         # CLI agent management tool
├── agent_config.yaml        # Agent configuration
├── .env                     # API keys and secrets (NEVER expose)
├── .claude/skills/          # Claude AI skill definitions
└── logs/                    # Agent log files
```

---

## Agent Management

**Agent Manager** (`agent_manager.py`): CLI tool for starting/stopping agents
**Agent Config** (`agent_config.yaml`): Defines which agents are enabled
**Logs Directory** (`logs/`): Contains runtime logs for each agent

**Current Running Agents** (as of last check):
- funding_agent.log
- grok_sentiment_agent.log
- liquidation_agent.log
- risk_agent.log (largest log - very active)
- trading_agent.log (largest log - very active)
- whale_agent.log

---

## Key Agents

**Trading Agents:**
- `trading_agent.py` - DUAL-MODE: Single model (~10s) or 6-model swarm consensus (~45-60s)
- `strategy_agent.py` - Executes strategies from src/strategies/
- `risk_agent.py` - **RUNS FIRST**, circuit breakers, risk management
- `copybot_agent.py` - Copies successful traders

**Market Analysis:**
- `sentiment_agent.py` / `grok_sentiment_agent.py` - Social sentiment analysis
- `whale_agent.py` - Tracks large wallet movements
- `funding_agent.py` - Monitors funding rates
- `liquidation_agent.py` - Tracks liquidation events

**Research & Backtesting:**
- `rbi_agent_pp_multi.py` - Parallel backtesting agent (18 threads, 20+ data sources)
- `rbi_agent.py` - Codes backtests from videos/PDFs/text using DeepSeek-R1

---

## Exchange Support

**Hyperliquid** (`nice_funcs_hl.py`):
- EVM-compatible perpetuals DEX
- Leverage up to 50x
- Functions: `market_buy()`, `market_sell()`, `get_position()`, `close_position()`

**Solana/BirdEye** (`nice_funcs.py`):
- Solana spot token data and trading
- 15,000+ tokens
- Functions: `token_overview()`, `token_price()`, `get_ohlcv_data()`

**Extended/Aster** (`nice_funcs_extended.py`):
- StarkNet-based perpetuals
- Leverage up to 20x
- Auto symbol conversion (BTC → BTC-USD)

---

## Configuration

**Trading Settings** (`src/config.py`):
- Position sizing, risk limits, monitored tokens
- AI model selection, temperature, max tokens
- Sleep intervals, agent activation

**Secrets** (`.env`):
- AI Provider Keys: ANTHROPIC_KEY, OPENAI_KEY, DEEPSEEK_KEY, GROQ_API_KEY, GEMINI_KEY, XAI_API_KEY
- Exchange Keys: HYPER_LIQUID_ETH_PRIVATE_KEY, X10_API_KEY, BIRDEYE_API_KEY
- Blockchain: SOLANA_PRIVATE_KEY, RPC_ENDPOINT

---

## LLM Provider Abstraction

**ModelFactory** (`src/models/`):
- Unified interface for multiple LLM providers
- Providers: Claude, GPT-4, DeepSeek, Groq, Gemini, Ollama
- Usage: `model = ModelFactory.create_model('anthropic')`

**Provider Strategy:**
- Claude Sonnet: Default, balanced
- Claude Haiku: Fast, cheap
- DeepSeek-R1: Deep reasoning, very cheap
- Groq: Ultra-fast inference
- Ollama: Local, no API costs

---

## Existing Dashboards

**Backtest Dashboard** (`src/scripts/backtestdashboard.py`):
- FastAPI web interface
- Views backtest results from `rbi_agent_pp_multi.py`
- Port: 8001
- Features: View stats CSV, organize backtest folders

**Agent Manager** (`agent_manager.py`):
- CLI tool for managing agents
- Start/stop agents, view status
- Check PIDs, monitor logs

---

## Development Rules (CRITICAL)

1. **Keep files under 800 lines** - split if longer
2. **NEVER move files** - can create new, but no moving without asking
3. **Use existing environment** - don't create new virtual environments
4. **Update requirements.txt** after any pip install: `pip freeze > requirements.txt`
5. **Use real data only** - never synthetic/fake data
6. **Minimal error handling** - user wants to see errors
7. **Never expose API keys** - don't show .env contents
8. **Use 'GEN_' prefix** - User prefers 'GEN_' before numbers in filenames (not numbers at start)

---

## Common Workflows

**Run single agent:**
```bash
python src/agents/trading_agent.py
```

**Run orchestrator:**
```bash
python src/main.py
```

**Switch exchange in agent:**
```python
EXCHANGE = "hyperliquid"  # or "birdeye", "extended"
if EXCHANGE == "hyperliquid":
    from src import nice_funcs_hl as nf
```

**Switch AI model:**
```python
model = ModelFactory.create_model('anthropic')  # or 'deepseek', 'groq', etc.
```

---

## Data Flow

```
Config/Input → Agent Init → API Data Fetch → Data Parsing →
LLM Analysis (ModelFactory) → Decision Output →
Result Storage (CSV/JSON in src/data/) → Optional Trade Execution
```

**Risk-First Flow:**
```
Main Orchestrator → Risk Agent (circuit breaker) →
Active Agents → ModelFactory → Exchange API → Blockchain/Market
```

---

## Philosophy

- **Experimental, educational project** - no guarantees of profitability
- **Never over-engineer** - always ship real trading systems
- **Fail fast** - minimal error handling to see issues immediately
- **Open source and free** - democratize AI agent development
- **No official token** - avoid scams claiming association

---

## Key Resources

**Claude Skills:** `.claude/skills/moon-dev-trading-agents/`
- SKILL.md - Main skill file
- AGENTS.md - Complete agent list
- WORKFLOWS.md - Practical workflows
- ARCHITECTURE.md - Deep architecture dive

**Documentation:** `docs/`
- CLAUDE.md - Project overview
- hyperliquid.md, extended_exchange.md - Exchange guides
- rbi_agent.md - Backtesting guide

---

## Git Info

**Branch:** main
**Python Version:** 3.10.9
**Environment:** User's choice (conda, venv, etc.) - commonly `tflow` for conda users

---

## Notes for AI Assistants

- Always activate environment before running commands
- Check `.env` exists and has required keys
- Respect the 800-line file limit
- Never move files without explicit permission
- Update requirements.txt after pip installs
- Use 'GEN_' prefix for generated files with numbers
- Read existing code patterns before suggesting changes
- Prioritize user's existing patterns over "best practices"

---

**Built with 🌙 by Moon Dev**

*This WARP file ensures AI assistants have full context about the Moon Dev trading system.*
