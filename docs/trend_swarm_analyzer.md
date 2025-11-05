# 🌙 Moon Dev's Trend Coin AI Swarm Analyzer

**Multi-model AI consensus system for analyzing trending cryptocurrency opportunities**

---

## Overview

The Trend Coin AI Swarm Analyzer is a sophisticated multi-agent system that uses 4+ AI models to analyze trending cryptocurrencies through democratic consensus voting. Instead of relying on a single AI model's opinion, this system queries multiple LLMs simultaneously and aggregates their recommendations for more reliable trading signals.

**The AI Swarm includes:**
- DeepSeek (R1, V3) - Deep reasoning
- Grok (xAI) - Real-time insights
- Qwen (Alibaba) - Alternative perspective
- Gemini (Google) - Diverse analysis

---

## System Components

### 1. **AnalyseTrendCoin_agent.py** (Main Analyzer)

The core orchestrator that runs AI swarm analysis on trending coins.

**Features:**
- Multi-model consensus voting (4+ AI models)
- Dual analysis: Technical AND Fundamental
- Individual model vote tracking
- Confidence scoring based on agreement
- OHLCV data integration from CoinGecko
- Detailed results saved to CSV + JSON

**Analysis Flow:**
```
Token Data → Technical Analysis (Swarm Query)
          → Fundamental Analysis (Swarm Query)
          → Vote Counting
          → Consensus Building
          → Overall Recommendation
```

**Filtering:**
- Max Market Cap: $1B (configurable)
- Min 24h Volume: $100K
- Runs every 24 hours (configurable)

---

### 2. **GEN_fetch_trending_coins.py** (CoinGecko)

Fetches trending coins from CoinGecko API with smart filtering.

**Features:**
- Pulls top trending coins from CoinGecko
- Market data: price, volume, market cap, ATH date
- Auto-filters coins based on criteria
- Saves to `src/data/trending_coins.csv`

**Filters Applied:**
- Market cap < $500M (targets small/mid caps)
- ATH within last 1 year (active projects)
- Removes stale/dead coins

**Output:** CSV with ~10-50 trending coins ready for analysis

---

### 3. **GEN_fetch_hyperliquid_coins.py** (HyperLiquid)

Fetches available perpetual coins from HyperLiquid exchange.

**Features:**
- Lists all tradeable perpetuals on HyperLiquid
- Current prices for each coin
- Symbol metadata (display name, decimals)
- Saves to `src/data/hyperliquid_coins.csv`

**Use Case:** Get coins available for trading on HyperLiquid so you can cross-reference with trending analysis and execute trades.

**Output:** CSV with 50+ HyperLiquid coins and prices

---

### 4. **GEN_summary_trend_analysis.py** (Display)

Beautiful terminal display of analysis results.

**Features:**
- Color-coded recommendations (🟢 BUY, 🔴 SELL, ⚪ DO NOTHING)
- Shows both technical and fundamental votes
- Confidence scores
- Summary statistics (total coins, signal counts)
- Displays most recent analysis for each coin

**Output:** Formatted terminal display with all analyzed coins

---

## AI Swarm Consensus Mechanism

### How It Works

1. **Query Phase**: Each token is analyzed by 4+ AI models simultaneously
2. **Dual Analysis**: Each model provides BOTH technical AND fundamental analysis
3. **Vote Extraction**: System extracts BUY/SELL/DO NOTHING from each response
4. **Vote Counting**:
   - Technical votes: Model 1 (BUY), Model 2 (SELL), Model 3 (BUY), Model 4 (DO NOTHING)
   - Fundamental votes: Similar independent voting
5. **Consensus**: Majority wins (total BUY votes vs SELL votes)
6. **Confidence**: Percentage of models agreeing with consensus

### Example Voting

**Token: PEPE**

**Technical Analysis Votes:**
- DeepSeek: BUY
- Grok: BUY
- Qwen: DO NOTHING
- Gemini: BUY
- **Consensus: BUY (3/4)**

**Fundamental Analysis Votes:**
- DeepSeek: SELL
- Grok: DO NOTHING
- Qwen: SELL
- Gemini: DO NOTHING
- **Consensus: SELL (2/4)**

**Overall Recommendation:**
- Total BUY: 3
- Total SELL: 2
- **Final: BUY with 37.5% confidence (3/8 models)**

### Benefits of AI Swarm

✅ **Reduces bias** - No single model's opinion dominates
✅ **Increases reliability** - Consensus from diverse perspectives
✅ **Confidence scoring** - Know when models strongly agree
✅ **Transparent** - All individual votes saved
✅ **Cost-effective** - Uses cheaper models (DeepSeek, Groq) alongside premium ones

---

## Installation & Setup

### Prerequisites

```bash
# Activate your environment
conda activate tflow  # or your preferred environment

# Ensure dependencies are installed
pip install -r requirements.txt
```

### API Keys Required

Add to `.env` file:

```bash
# CoinGecko (for trending coins + OHLCV data)
COINGECKO_API_KEY=your_key_here

# AI Providers (swarm uses available models)
DEEPSEEK_KEY=your_key_here
XAI_API_KEY=your_key_here  # For Grok
GEMINI_KEY=your_key_here
# Optional: ANTHROPIC_KEY, OPENAI_KEY, GROQ_API_KEY
```

### File Structure

```
src/
├── agents/
│   ├── AnalyseTrendCoin_agent.py      # Main analyzer
│   ├── GEN_fetch_trending_coins.py    # Fetch from CoinGecko
│   ├── GEN_fetch_hyperliquid_coins.py # Fetch from HyperLiquid
│   ├── GEN_summary_trend_analysis.py  # Display results
│   └── swarm_agent.py                 # SwarmAgent class (dependency)
└── data/
    ├── trending_coins.csv             # Input: Trending coins
    ├── hyperliquid_coins.csv          # Input: HyperLiquid coins
    ├── trend_swarm_analysis.csv       # Output: Analysis summary
    └── trend_[token]_[timestamp].json # Output: Detailed results
```

---

## Usage

### Quick Start (Full Workflow)

```bash
# Step 1: Fetch trending coins from CoinGecko
python src/agents/GEN_fetch_trending_coins.py

# Step 2: (Optional) Fetch HyperLiquid coins for trading reference
python src/agents/GEN_fetch_hyperliquid_coins.py

# Step 3: Run AI Swarm analysis on trending coins
python src/agents/AnalyseTrendCoin_agent.py

# Step 4: View beautiful summary
python src/agents/GEN_summary_trend_analysis.py
```

### Individual Commands

#### Fetch Trending Coins
```bash
python src/agents/GEN_fetch_trending_coins.py
```

**Output:**
```
🌙 Moon Dev's Trending Coins Fetcher 🚀
⚙️ Configuration:
  • API Endpoint: https://api.coingecko.com/api/v3
  • Output File: /path/to/trending_coins.csv

🔥 Fetching trending coins from CoinGecko...
✅ Got 100 trending coins from API

📊 Fetching market data for coins (page 1)...

✨ Trending Coins Fetched!
📊 Fetched 100 coins from API
🔍 After filtering: 42 coins (removed 58)
   • Excluded coins with market cap >= $500M
   • Excluded coins with ATH older than 1 year
💾 Saved to: /path/to/trending_coins.csv

🔥 Top 10 Trending Coins:
   1. Pepe               (PEPE  ) - Market Cap: $412,345,678
   2. Bonk               (BONK  ) - Market Cap: $312,456,789
   ...
```

#### Fetch HyperLiquid Coins
```bash
python src/agents/GEN_fetch_hyperliquid_coins.py
```

**Output:**
```
🌙 Moon Dev's HyperLiquid Coins Fetcher 🚀
⚙️ Configuration:
  • API Endpoint: https://api.hyperliquid.xyz/info
  • Output File: /path/to/hyperliquid_coins.csv

🔍 Fetching HyperLiquid metadata...
✅ Found 52 coins on HyperLiquid

💹 Fetching current prices...
[1/52] BTC      - Price: $    50,123.45678900
[2/52] ETH      - Price: $     3,456.78901234
...

✨ HyperLiquid Coins Fetched!
📊 Found 52 coins
💾 Saved to: /path/to/hyperliquid_coins.csv
```

#### Run AI Swarm Analysis
```bash
python src/agents/AnalyseTrendCoin_agent.py
```

**Output:**
```
======================================================================
🌙 Moon Dev's Analyse Trend Coin Agent 🔥
Multi-Model AI Swarm for Token Analysis
======================================================================

⚙️ Configuration:
  • Tokens File: src/data/trending_coins.csv
  • Analysis Output: src/data/trend_swarm_analysis.csv
  • Max Market Cap: $1,000,000,000
  • Min 24h Volume: $100,000

🔥 Moon Dev's Trend Coin Swarm Analyzer Ready! 🔥

🔄 Starting Trend Coin Analysis Cycle!

📚 Loaded 42 tokens from src/data/trending_coins.csv

🔍 Analyzing: Pepe (PEPE)
📊 24h Volume: $412,345,678.90
💰 Market Cap: $312,456,789.00

🤖 Querying Swarm for Technical Analysis...
🤖 [DeepSeek] Analyzing...
🤖 [Grok] Analyzing...
🤖 [Qwen] Analyzing...
🤖 [Gemini] Analyzing...

📊 Technical Analysis:
   Votes: BUY=3 | SELL=0 | NOTHING=1
   Consensus: BUY
   Summary: Strong bullish momentum with increasing volume...

🤖 Querying Swarm for Fundamental Analysis...
🤖 [DeepSeek] Analyzing...
🤖 [Grok] Analyzing...
🤖 [Qwen] Analyzing...
🤖 [Gemini] Analyzing...

🔬 Fundamental Analysis:
   Votes: BUY=2 | SELL=1 | NOTHING=1
   Consensus: BUY
   Summary: Meme coin with strong community support...

✅ Analysis saved!
📊 Overall: BUY (Confidence: 62.5%)

... (continues for all tokens)

✨ Analysis cycle complete!
📊 Processed 42 tokens
💾 Results saved to src/data/trend_swarm_analysis.csv

⏳ Next round in 24 hours (at 14:30:45)
```

#### View Summary
```bash
python src/agents/GEN_summary_trend_analysis.py
```

**Output:**
```
================================================================================
📋 TREND COIN ANALYSIS SUMMARY
================================================================================

📊 Total Coins Analyzed: 42
📈 BUY Signals: 18
📉 SELL Signals: 5
⏸️  DO NOTHING Signals: 19

--------------------------------------------------------------------------------

🟢 Pepe (PEPE)
   Recommendation: BUY (Confidence: 62.5%)
   Price: $0.00001234 | Market Cap: $312,456,789
   Technical: BUY (Buy:3 Sell:0 Nothing:1)
   Fundamental: BUY (Buy:2 Sell:1 Nothing:1)

🔴 Shiba Inu (SHIB)
   Recommendation: SELL (Confidence: 75.0%)
   Price: $0.00002345 | Market Cap: $456,789,012
   Technical: SELL (Buy:0 Sell:3 Nothing:1)
   Fundamental: SELL (Buy:1 Sell:3 Nothing:0)

⚪ Dogecoin (DOGE)
   Recommendation: DO NOTHING (Confidence: 50.0%)
   Price: $0.12345678 | Market Cap: $234,567,890
   Technical: DO NOTHING (Buy:1 Sell:1 Nothing:2)
   Fundamental: DO NOTHING (Buy:1 Sell:0 Nothing:3)

... (continues for all coins)

--------------------------------------------------------------------------------
💾 Full analysis saved to: /path/to/trend_swarm_analysis.csv
📊 Analyzed at: 2025-11-03T14:30:45.123456
```

---

## Configuration

### AnalyseTrendCoin_agent.py

Edit configuration variables at top of file:

```python
# ⚙️ Configuration
HOURS_BETWEEN_RUNS = 24          # Run every 24 hours
PARALLEL_PROCESSES = 50          # Parallel analysis (future use)
MIN_VOLUME_USD = 100_000         # Skip coins below $100K volume
MAX_MARKET_CAP = 1000_000_000    # Skip coins above $1B market cap

# 📁 File Paths
TREND_FILE = Path("src/data/trending_coins.csv")
FALLBACK_FILE = Path("src/data/discovered_tokens.csv")
ANALYSIS_FILE = Path("src/data/trend_swarm_analysis.csv")
```

### GEN_fetch_trending_coins.py

Edit filters in the code:

```python
# Current filters (line ~131-138)
# Filter 1: Remove coins with market cap >= $500 million
df = df[df['market_cap'].notna() & (df['market_cap'] < 500_000_000)]

# Filter 2: Remove coins with ATH older than 1 year
one_year_ago = datetime.now() - timedelta(days=365)
df = df[df['ath_date'].notna()]
df['ath_date_parsed'] = pd.to_datetime(df['ath_date'], errors='coerce')
df = df[df['ath_date_parsed'] >= one_year_ago]
```

### Swarm Models

The swarm automatically uses available models based on API keys in `.env`:

**Active Models** (if keys present):
- DeepSeek (deepseek-chat, deepseek-reasoner)
- Grok (grok-beta)
- Qwen (qwen-plus)
- Gemini (gemini-pro)

**Optional Models:**
- Claude (anthropic - ANTHROPIC_KEY)
- GPT-4 (openai - OPENAI_KEY)
- Groq (groq - GROQ_API_KEY)

Models without API keys are automatically skipped.

---

## Output Files

### 1. trending_coins.csv

**Location:** `src/data/trending_coins.csv`

**Columns:**
- `token_id` - CoinGecko ID
- `name` - Token name
- `symbol` - Trading symbol
- `price` - Current price (USD)
- `market_cap` - Market capitalization
- `volume_24h` - 24-hour trading volume
- `market_cap_rank` - CoinGecko rank
- `trending_rank` - Trending position
- `ath_date` - All-time high date
- `discovered_at` - Timestamp when fetched

### 2. hyperliquid_coins.csv

**Location:** `src/data/hyperliquid_coins.csv`

**Columns:**
- `symbol` - Trading symbol (BTC, ETH, etc.)
- `name` - Display name
- `price` - Current price
- `token_id` - Lowercase symbol
- `exchange` - "hyperliquid"
- `sz_decimals` - Size decimals for orders
- `discovered_at` - Timestamp when fetched

### 3. trend_swarm_analysis.csv

**Location:** `src/data/trend_swarm_analysis.csv`

**Columns:**
- `timestamp` - Analysis timestamp
- `token_id` - CoinGecko ID
- `symbol` - Trading symbol
- `name` - Token name
- `price` - Price at analysis time
- `volume_24h` - 24h volume
- `market_cap` - Market cap
- `technical_consensus` - BUY/SELL/DO NOTHING
- `fundamental_consensus` - BUY/SELL/DO NOTHING
- `technical_votes_buy` - Count of BUY votes (technical)
- `technical_votes_sell` - Count of SELL votes (technical)
- `technical_votes_nothing` - Count of DO NOTHING votes (technical)
- `fundamental_votes_buy` - Count of BUY votes (fundamental)
- `fundamental_votes_sell` - Count of SELL votes (fundamental)
- `fundamental_votes_nothing` - Count of DO NOTHING votes (fundamental)
- `overall_recommendation` - Final recommendation
- `confidence_score` - Confidence percentage (0-100)

### 4. trend_[token]_[timestamp].json

**Location:** `src/data/trend_[token]_[timestamp].json`

**Structure:**
```json
{
  "timestamp": "2025-11-03T14:30:45.123456",
  "token": {
    "id": "pepe",
    "name": "Pepe",
    "symbol": "PEPE"
  },
  "market_data": {
    "price": 0.00001234,
    "volume_24h": 412345678.90,
    "market_cap": 312456789.00
  },
  "technical_analysis": {
    "responses": {
      "deepseek": {
        "success": true,
        "response": "Full technical analysis text...",
        "model": "deepseek-chat",
        "timestamp": "..."
      },
      "grok": { ... },
      "qwen": { ... },
      "gemini": { ... }
    },
    "consensus_summary": "Strong bullish momentum..."
  },
  "fundamental_analysis": {
    "responses": { ... },
    "consensus_summary": "Meme coin with strong community..."
  },
  "overall": {
    "recommendation": "BUY",
    "confidence": 0.625,
    "total_votes": {
      "buy": 5,
      "sell": 1
    }
  }
}
```

---

## Interpreting Results

### Confidence Scores

- **75-100%**: Strong consensus, high confidence
- **50-75%**: Moderate consensus, medium confidence
- **25-50%**: Weak consensus, low confidence
- **0-25%**: No clear consensus, very low confidence

### Recommendation Types

**🟢 BUY**: Majority of models recommend buying
- Look for high confidence (>60%)
- Check both technical and fundamental agree
- Review individual model reasoning in JSON files

**🔴 SELL**: Majority of models recommend selling
- May indicate overvalued or risky asset
- Check for fundamental concerns
- Consider exit strategies

**⚪ DO NOTHING**: Models split or recommend holding
- Insufficient signal strength
- Market uncertainty
- Wait for clearer opportunity

### Best Practices

1. **Filter by Confidence**: Focus on recommendations with >60% confidence
2. **Check Both Analyses**: Look for technical AND fundamental alignment
3. **Review Individual Votes**: Read detailed JSON for specific model reasoning
4. **Cross-reference HyperLiquid**: Ensure coin is tradeable on your exchange
5. **Monitor Volume**: Higher volume = more reliable signals
6. **Track Over Time**: Run daily and watch for consensus changes

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│         GEN_fetch_trending_coins.py                     │
│         (CoinGecko API → trending_coins.csv)           │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│         GEN_fetch_hyperliquid_coins.py                  │
│         (HyperLiquid API → hyperliquid_coins.csv)      │
└─────────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│         AnalyseTrendCoin_agent.py (MAIN)                │
│                                                          │
│  ┌────────────────────────────────────────────┐        │
│  │  For Each Token:                           │        │
│  │                                             │        │
│  │  1. Load Token Data                        │        │
│  │  2. Fetch OHLCV from CoinGecko             │        │
│  │                                             │        │
│  │  3. Technical Analysis Query               │        │
│  │     ├─► SwarmAgent.query()                 │        │
│  │     │   ├─► DeepSeek: BUY                  │        │
│  │     │   ├─► Grok: BUY                      │        │
│  │     │   ├─► Qwen: DO NOTHING               │        │
│  │     │   └─► Gemini: BUY                    │        │
│  │     └─► Consensus: BUY (3/4)               │        │
│  │                                             │        │
│  │  4. Fundamental Analysis Query             │        │
│  │     ├─► SwarmAgent.query()                 │        │
│  │     │   ├─► DeepSeek: SELL                 │        │
│  │     │   ├─► Grok: DO NOTHING               │        │
│  │     │   ├─► Qwen: SELL                     │        │
│  │     │   └─► Gemini: DO NOTHING             │        │
│  │     └─► Consensus: SELL (2/4)              │        │
│  │                                             │        │
│  │  5. Count Total Votes                      │        │
│  │     ├─► BUY: 3                             │        │
│  │     ├─► SELL: 2                            │        │
│  │     └─► Overall: BUY (37.5% confidence)    │        │
│  │                                             │        │
│  │  6. Save Results                           │        │
│  │     ├─► CSV (summary)                      │        │
│  │     └─► JSON (detailed)                    │        │
│  │                                             │        │
│  └────────────────────────────────────────────┘        │
└─────────────────┬───────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────┐
│         GEN_summary_trend_analysis.py                   │
│         (Display Results from CSV)                      │
└─────────────────────────────────────────────────────────┘
```

---

## Dependencies

**Core:**
- `pandas` - Data manipulation
- `requests` - API calls
- `termcolor` - Colored terminal output
- `python-dotenv` - Environment variables
- `numpy` - Statistical calculations

**Moon Dev Components:**
- `src.agents.swarm_agent.SwarmAgent` - Multi-model query engine
- `src.models.model_factory.ModelFactory` - LLM provider abstraction

**APIs:**
- CoinGecko API (trending coins, OHLCV data)
- HyperLiquid API (tradeable coins, prices)
- AI Provider APIs (DeepSeek, Grok, Qwen, Gemini)

---

## Cost Analysis

### Per Token Analysis

**API Calls:**
- 1x CoinGecko OHLCV (free tier: 50/min)
- 1x Technical Analysis Swarm (4 models)
- 1x Fundamental Analysis Swarm (4 models)

**AI Costs** (approximate per token):
- DeepSeek: ~$0.002 (2 queries)
- Grok: ~$0.02 (2 queries)
- Qwen: ~$0.01 (2 queries)
- Gemini: ~$0.01 (2 queries)
- **Total: ~$0.042 per token**

**For 50 Tokens:**
- Total Cost: ~$2.10
- Runtime: ~10-15 minutes
- Runs: Once per 24 hours
- Monthly Cost: ~$63

**Cost Optimization:**
- Use DeepSeek + Groq (very cheap) for bulk analysis
- Reserve premium models (Claude, GPT-4) for final decisions
- Adjust `HOURS_BETWEEN_RUNS` to reduce frequency

---

## Workflow Examples

### Daily Trending Analysis Routine

```bash
# Morning: Fetch fresh trending coins
python src/agents/GEN_fetch_trending_coins.py

# Midday: Run AI Swarm analysis
python src/agents/AnalyseTrendCoin_agent.py

# Afternoon: Review results
python src/agents/GEN_summary_trend_analysis.py

# Evening: Check detailed JSON for BUY signals
cat src/data/trend_*.json | grep -A 20 '"overall"'
```

### High-Confidence BUY Signals Only

```bash
# Run analysis
python src/agents/AnalyseTrendCoin_agent.py

# Filter for high-confidence BUYs in Python
python -c "
import pandas as pd
df = pd.read_csv('src/data/trend_swarm_analysis.csv')
buys = df[(df['overall_recommendation'] == 'BUY') & (df['confidence_score'] >= 60)]
print(buys[['name', 'symbol', 'confidence_score', 'price']])
"
```

### Cross-Reference with HyperLiquid

```bash
# Get HyperLiquid coins
python src/agents/GEN_fetch_hyperliquid_coins.py

# Get trending analysis
python src/agents/AnalyseTrendCoin_agent.py

# Find BUY signals available on HyperLiquid
python -c "
import pandas as pd
trend = pd.read_csv('src/data/trend_swarm_analysis.csv')
hl = pd.read_csv('src/data/hyperliquid_coins.csv')
buys = trend[(trend['overall_recommendation'] == 'BUY') & (trend['confidence_score'] >= 60)]
tradeable = buys[buys['symbol'].isin(hl['symbol'])]
print('🔥 BUY Signals on HyperLiquid:')
print(tradeable[['symbol', 'confidence_score', 'price']])
"
```

### Automated Cron Job (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add daily 9 AM analysis
0 9 * * * cd /path/to/moon-dev-ai-agents && /path/to/python src/agents/GEN_fetch_trending_coins.py && /path/to/python src/agents/AnalyseTrendCoin_agent.py
```

---

## Troubleshooting

### "No tokens file found"

**Problem:** `trending_coins.csv` doesn't exist

**Solution:**
```bash
python src/agents/GEN_fetch_trending_coins.py
```

### "API key not found"

**Problem:** Missing API keys in `.env`

**Solution:**
```bash
# Check .env has required keys
cat .env | grep -E "(COINGECKO|DEEPSEEK|XAI|GEMINI)"

# Add missing keys to .env
echo "COINGECKO_API_KEY=your_key" >> .env
```

### "No models available in swarm"

**Problem:** SwarmAgent has no active models

**Solution:**
```bash
# Check which AI provider keys are set
cat .env | grep -E "(ANTHROPIC|OPENAI|DEEPSEEK|XAI|GEMINI|GROQ)"

# Add at least one provider key
echo "DEEPSEEK_KEY=your_key" >> .env
```

### "CoinGecko rate limit exceeded"

**Problem:** Too many API calls to CoinGecko

**Solution:**
```bash
# Wait 60 seconds and retry
# Or get a CoinGecko Pro API key for higher limits
```

### "Empty analysis results"

**Problem:** All tokens filtered out

**Solution:**
```python
# Check filters in AnalyseTrendCoin_agent.py
MIN_VOLUME_USD = 100_000    # Lower if needed
MAX_MARKET_CAP = 1000_000_000  # Raise if needed
```

---

## Advanced Usage

### Custom Swarm Models

Edit `src/agents/swarm_agent.py` to customize models:

```python
# Add/remove models
self.active_models = ['deepseek', 'grok', 'qwen', 'gemini', 'claude']
```

### Custom Analysis Prompts

Edit prompts in `AnalyseTrendCoin_agent.py`:

```python
TECHNICAL_ANALYSIS_PROMPT = """
Your custom technical analysis prompt here...
Include: {name}, {symbol}, {price}, {volume_24h}, {market_cap}, {ohlcv_data}
Must end with: RECOMMENDATION: BUY/SELL/DO NOTHING
"""

FUNDAMENTAL_ANALYSIS_PROMPT = """
Your custom fundamental analysis prompt here...
"""
```

### Integration with Trading Agent

```python
# In your trading_agent.py
import pandas as pd

# Load analysis
df = pd.read_csv('src/data/trend_swarm_analysis.csv')

# Get high-confidence BUYs
buys = df[(df['overall_recommendation'] == 'BUY') &
          (df['confidence_score'] >= 70)]

# Execute trades
for _, row in buys.iterrows():
    symbol = row['symbol']
    execute_trade(symbol, 'BUY', confidence=row['confidence_score'])
```

---

## Development Notes

### File Naming Convention

- `GEN_` prefix for generated/utility scripts (Moon Dev standard)
- Main agent follows `[purpose]_agent.py` pattern

### Code Style

- Under 800 lines per file (Moon Dev rule)
- Colored terminal output via `termcolor`
- Minimal error handling (fail fast)
- Real data only, no synthetic/fake data

### Future Enhancements

**Planned Features:**
- [ ] Parallel token analysis (use `PARALLEL_PROCESSES`)
- [ ] Historical trend tracking (same token over time)
- [ ] Sentiment analysis integration
- [ ] On-chain metrics (whale movements, transaction volume)
- [ ] Auto-trading integration with risk agent approval
- [ ] Web dashboard for visualizing consensus votes
- [ ] Telegram/Discord notifications for high-confidence signals

---

## FAQ

**Q: How many AI models are in the swarm?**
A: Typically 4-6 models, depending on which API keys you have configured. The more models, the better the consensus.

**Q: Can I use this for live trading?**
A: This is an ANALYSIS tool. Always integrate with `risk_agent.py` before executing any trades. Never auto-trade without risk checks.

**Q: How often should I run the analysis?**
A: Default is every 24 hours. More frequent runs may hit CoinGecko rate limits. Consider 12-hour cycles for active trading.

**Q: What's the difference between technical and fundamental analysis?**
A: Technical focuses on price action, volume, momentum. Fundamental focuses on project viability, team, use case, market positioning.

**Q: Why do models sometimes disagree?**
A: Different models have different training data, reasoning capabilities, and perspectives. Disagreement is expected and healthy - it's why we use consensus voting.

**Q: Can I add more exchanges beyond HyperLiquid?**
A: Yes! Create similar fetcher scripts for other exchanges (Binance, Bybit, etc.) and cross-reference with trending analysis.

**Q: Is this profitable?**
A: This is an EXPERIMENTAL system for educational purposes. No guarantees of profitability. Always DYOR and manage risk.

---

## Credits

**Built with 🌙 by Moon Dev**

*AI Swarm consensus - because one AI's opinion is never enough!*

**Swarm Models:**
- DeepSeek (R1, V3)
- Grok (xAI)
- Qwen (Alibaba)
- Gemini (Google)

**Data Sources:**
- CoinGecko API
- HyperLiquid API

**System:**
- SwarmAgent multi-model orchestrator
- ModelFactory LLM abstraction
- Moon Dev AI Agents framework

---

## License

Part of Moon Dev AI Agents - Open source for educational and experimental use.

**Disclaimer:** This system is for educational and research purposes only. Cryptocurrency trading involves substantial risk. Never trade with money you cannot afford to lose. Always conduct your own research and consult with financial advisors before making investment decisions.

---

**🌙 Happy Trading with AI Swarm Consensus! 🔥**
