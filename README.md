# 🤖 AI AGENTS FOR TRADING

<p align="center">
  <a href="https://www.moondev.com/"><img src="moondev.png" width="300" alt="Moon Dev"></a>
</p>

## 🎯 Vision
ai agents are clearly the future and the entire workforce will be replaced or atleast using ai agents. while i am a quant and building agents for algo trading i will be contributing to all different types of ai agent flows and placing all of the agents here for free, 100% open sourced because i believe code is the great equalizer and we have never seen a regime shift like this so i need to get this code to the people

feel free to join [our discord](https://discord.gg/8UPuVZ53bh) if you beleive ai agents will be integrated into the workforce

## Video Updates & Training

⭐️ [first full concise documentation video (watch here)](https://youtu.be/RlqzkSgDKDc)

⭐️ [second full walkthrough video(watch here)](https://youtu.be/tjY24JR8Cso?si=Za-PQ2L79US6cu2T)

⭐️ [third full walkthrough w/ big updates, new models, new agents(watch here)](https://youtu.be/qZv6IFIkk6I)

⭐️ [forth full walkthrough w/ new agents & ai models](https://youtu.be/D0VRQj0tuCI)


📀 follow all updates here on youtube in this playlist: https://www.youtube.com/playlist?list=PLXrNVMjRZUJg4M4uz52iGd1LhXXGVbIFz

---

## 🤖 All Available Agents

**⚠️ For live trading agents: Only use these AFTER thoroughly backtesting your strategies!**

### Backtesting & Research Agents
- **RBI Agent** (`rbi_agent.py`): Uses AI (GPT-5, DeepSeek, Gemini, etc.) to research trading strategies based on YouTube videos, PDFs, or text you provide, then codes out the backtest automatically
- **RBI Parallel Agent** (`rbi_agent_pp_multi.py`): Parallel version with up to 18 threads, auto debug/optimize loop, continuous monitoring mode. Currently uses Gemini 2.5 Flash for all pipeline stages (Research → Backtest → Package → Debug → Optimize)
- **Research Agent** (`research_agent.py`): Fills the ideas.txt file so the RBI agent can run forever
- **Websearch Agent** (`websearch_agent.py`): This agent searches the web, in my use case for trading strategy resources and then uses other ai's to split the website ideas into strategy files i can have my  `rbi_agent_pp_multi.py` process and build out backtests

### Live Trading Agents
- **Trading Agent** (`trading_agent.py`): **DUAL-MODE AI trading system** - Toggle between single model (fast ~10s) or swarm mode (6-model consensus ~45-60s). Swarm mode queries Claude 4.5, GPT-5, Gemini 2.5, Grok-4, DeepSeek, and DeepSeek-R1 local for majority vote trading decisions. Configure via `USE_SWARM_MODE` in config.py
- **Strategy Agent** (`strategy_agent.py`): Manages and executes trading strategies placed in the strategies folder
- **Risk Agent** (`risk_agent.py`): Monitors and manages portfolio risk, enforcing position limits and PnL thresholds
- **Copy Agent** (`copy_agent.py`): Monitors copy bot for potential trades
- **Swarm Agent** (`swarm_agent.py`): Queries 6 AI models in parallel (Claude 4.5, GPT-5, Gemini 2.5, Grok-4, DeepSeek, DeepSeek-R1 local), generates AI consensus summary, returns clean JSON with model mapping for easy parsing 🐝

### Market Analysis Agents
- **Whale Agent** (`whale_agent.py`): Monitors whale activity and announces when a whale enters the market
- **Sentiment Agent** (`sentiment_agent.py`): Analyzes Twitter sentiment for crypto tokens with voice announcements
- **Chart Agent** (`chartanalysis_agent.py`): Looks at any crypto chart and analyzes it with AI to make a buy/sell/nothing recommendation
- **Funding Agent** (`funding_agent.py`): Monitors funding rates across exchanges and uses AI to analyze opportunities, providing voice alerts for extreme funding situations with technical context 🌙
- **Liquidation Agent** (`liquidation_agent.py`): Tracks liquidation events with configurable time windows (15min/1hr/4hr), providing AI analysis and voice alerts for significant liquidation spikes 💦
- **Listing Arbitrage Agent** (`listingarb_agent.py`): Identifies promising Solana tokens on CoinGecko before they reach major exchanges like Binance and Coinbase, using parallel AI analysis for technical and fundamental insights
- **Funding Arbitrage Agent** (`fundingarb_agent.py`): Tracks the funding rate on HyperLiquid to find funding rate arbitrage opportunities between HL and Solana
- **New or Top Tokens Agent** (`new_or_top_agent.py`): Looks at the new tokens and the top tokens from CoinGecko API

### Solana-Specific Agents
- **Sniper Agent** (`sniper_agent.py`): Watches for new Solana token launches, analyzes them, and maybe snipes
- **TX Agent** (`tx_agent.py`): Watches transactions made by your copy list and prints them out with optional auto tab open
- **Solana Agent** (`solana_agent.py`): Looks at the sniper agent and the TX agent to select which memes may be interesting

### Content Creation Agents
- **Chat Agent** (`chat_agent.py`): Monitors YouTube live stream chat, moderates & responds to known questions. Absolute fire.
- **Twitter Agent** (`tweet_agent.py`): Takes in text and creates tweets using DeepSeek or other models
- **Video Agent** (`video_agent.py`): 🎬 Parallel AI video generation using OpenAI's Sora 2 API - create videos directly from text prompts with 9 concurrent workers, configurable resolutions (720p/1080p), durations (4/8/12s), and aspect ratios (9:16 for TikTok/Reels, 16:9 for YouTube, 1:1 for Instagram). [See full docs](docs/video_agent.md)
- **Clips Agent** (`clips_agent.py`): Helps clip long videos into shorter ones so you can upload to your YouTube and get paid. More info: https://discord.gg/XAw8US9aHT
- **Real-Time Clips Agent** (`realtime_clips_agent.py`): Makes real-time clips of streamers using OBS
- **Phone Agent** (`phone_agent.py`): An AI agent that can take phone calls for you

### Specialized Agents
- **Prompt Agent** (`prompt_agent.py`): 🎯 Interactive prompt enhancement tool that transforms basic prompts into professional, production-ready prompts using best practices from Parahelp & Cursor. Stays open in terminal, continuously ready to enhance your prompts with expert design principles (role-based prompting, structured formatting, explicit thinking order). Auto-saves and copies enhanced prompts. Perfect for improving prompts for any AI task. [See full docs](docs/prompt_agent.md)
- **Focus Agent** (`focus_agent.py`): Randomly samples audio during coding sessions to maintain productivity, providing focus scores and voice alerts when focus drops (~$10/month, perfect for voice-to-code workflows)
- **Million Agent** (`million_agent.py`): Uses million context window from Gemini to pull in a knowledge base
- **TikTok Agent** (`tiktok_agent.py`): Scrolls TikTok and gets screenshots of the video + comments to extract consumer data to feed into algos. Sometimes called social arbitrage
- **Compliance Agent** (`compliance_agent.py`): Analyzes TikTok ads for Facebook advertising compliance, extracting frames and transcribing audio to check against FB guidelines
- **Housecoin Agent** (`housecoin_agent.py`): DCA (dollar cost average) agent with AI confirmation layer using Grok-4 for the thesis: 1 House = 1 Housecoin 🏠
- **Polymarket Agent** (`polymarket_agent.py`): Connects to the live trades feed via WebSocket and analyzes with the swarm agent to see which markets could be interesting to trade


## ⚠️ Critical Disclaimers

*There is no token associated with this project and there never will be. any token launched is not affiliated with this project, moon dev will never dm you. be careful. don't send funds anywhere*

**PLEASE READ CAREFULLY:**

1. This is an experimental research project, NOT a trading system
2. There are NO plug-and-play solutions for guaranteed profits
3. We do NOT provide trading strategies
4. Success depends entirely on YOUR:
   - Trading strategy
   - Risk management
   - Market research
   - Testing and validation
   - Overall trading approach

5. NO AI agent can guarantee profitable trading
6. You MUST develop and validate your own trading approach
7. Trading involves substantial risk of loss
8. Past performance does not indicate future results

**⚠️ IMPORTANT: This is an experimental project. There are NO guarantees of profitability. Trading involves substantial risk of loss.**

## 👂 Looking for Updates?
Project updates will be posted in Discord, join here: [discord.gg/8UPuVZ53bh](https://discord.gg/8UPuVZ53bh)

## 🔗 Links
- Free Algo Trading Roadmap: [moondev.com](https://moondev.com)
- Algo Trading Education: [algotradecamp.com](https://algotradecamp.com)
- Business Contact [moon@algotradecamp.com](mailto:moon@algotradecamp.com)

---

## 🚀 Quick Start Guide - RBI Backtesting Agent

**Why Start with Backtesting?**

Before running ANY trading algorithm or AI agent with real money, you MUST backtest your strategies. Backtesting shows you how a strategy would have performed on historical data. The RBI (Research-Based Inference) Agent automates this entire process for you.

**What is the RBI Agent?**

The RBI Agent takes your trading ideas (from YouTube videos, PDFs, or plain text) and:
1. 🧠 Uses AI to understand the trading strategy
2. 💻 Codes a complete backtest using the `backtesting.py` library
3. 📊 Tests across 20+ different market data sources
4. ✅ Only saves strategies that pass a 1% return threshold
5. 🎯 Tries to optimize strategies to hit a 50% target return

**Python Version:** 3.10.9 was used during development

### Step 1: ⭐ Star & Fork the Repo
- Click the star button to save it to your GitHub favorites
- Fork to your GitHub account to get your own copy
- This lets you make changes and track updates

### Step 2: 💻 Clone to Your Machine
```bash
git clone https://github.com/YOUR_USERNAME/moon-dev-ai-agents-for-trading.git
cd moon-dev-ai-agents-for-trading
```

**Recommended IDEs:**
- [Cursor](https://www.cursor.com/) - AI-enabled coding
- [Windsurfer](https://codeium.com/) - AI-enabled coding

### Step 3: 🔑 Set Up Environment Variables

The RBI Agent needs API keys to function. Create a `.env` file in the root directory:

```bash
# Copy the example file
cp .env.example .env
```

**Required API Keys for RBI Agent:**

```bash
# AI Model APIs (you need at least ONE of these)
ANTHROPIC_KEY=your_anthropic_api_key_here          # Claude models (recommended)
OPENAI_KEY=your_openai_api_key_here                # GPT models
DEEPSEEK_KEY=your_deepseek_api_key_here            # DeepSeek models (cheap!)
GROQ_API_KEY=your_groq_api_key_here                # Groq (fast inference)
GEMINI_KEY=your_gemini_api_key_here                # Google Gemini
XAI_API_KEY=your_xai_api_key_here                  # Grok models
OPENROUTER_API_KEY=your_openrouter_api_key_here    # OpenRouter (200+ models!)

# Market Data APIs (for downloading price data)
BIRDEYE_API_KEY=your_birdeye_api_key_here          # Solana token data
COINGECKO_API_KEY=your_coingecko_api_key_here      # Crypto market data
```

**Where to Get API Keys:**
- **Anthropic Claude**: https://console.anthropic.com/
- **OpenAI GPT**: https://platform.openai.com/api-keys
- **DeepSeek**: https://platform.deepseek.com/ (very cheap, great for backtesting)
- **Groq**: https://console.groq.com/
- **Google Gemini**: https://aistudio.google.com/app/apikey
- **xAI Grok**: https://console.x.ai/
- **OpenRouter**: https://openrouter.ai/keys (access 200+ models including Qwen, GLM, and more!)
- **BirdEye**: https://birdeye.so/ (Solana data)
- **CoinGecko**: https://www.coingecko.com/en/api

⚠️ **Never commit or share your `.env` file! It's in .gitignore for your safety.**

### Step 4: 📦 Install Dependencies

Using conda (recommended):
```bash
conda create -n tflow python=3.10.9
conda activate tflow
pip install -r requirements.txt
```

Or using pip/venv directly:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Key Dependencies:** `backtesting`, `pandas_ta`, `talib`, `openai`, `anthropic`, `google-generativeai`, `groq`, `termcolor`, `python-dotenv`

### Step 5: 🧪 Run Your First Backtest

**Option A: Single Strategy Test (Parallel Agent)**

Create an ideas file (one strategy per line):

```bash
echo "RSI mean reversion: Buy when RSI(14) < 30, sell when RSI(14) > 70, with 2x ATR stop loss" > my_ideas.txt
```

Then run with your custom ideas file:
```bash
python src/agents/rbi_agent_pp_multi.py --ideas-file my_ideas.txt
```

Or run with the default ideas file:
```bash
python src/agents/rbi_agent_pp_multi.py
```

**Option B: Single-Threaded Agent**

Add ideas to `src/data/rbi/ideas.txt` (one per line), then:
```bash
python src/agents/rbi_agent.py
```

**Option C: File-Based Mode (pairs with Websearch Agent)**

Set `STRATEGIES_FROM_FILES = True` in `rbi_agent_pp_multi.py` and point `STRATEGIES_FOLDER` to a directory of `.md`/`.txt` strategy files. The agent auto-detects new files every second.

### Step 6: 📊 Understanding Results

The agent will:
- Process your strategy idea
- Generate backtest code
- Test across 20+ market datasets (BTC, ETH, SOL, etc.)
- Show results in a table with:
  - Return %
  - Buy & Hold %
  - Max Drawdown
  - Sharpe Ratio
  - Sortino Ratio
  - Number of Trades

**Only strategies returning > 1% are saved to the CSV.**

Results are saved to:
- `src/data/rbi_pp_multi/backtest_stats.csv` - All passing backtests
- `src/data/rbi_pp_multi/user_folders/` - Organized by run name

### Step 7: 🔍 Analyze Backtest Code

Find your strategy files in:
```
src/data/rbi_pp_multi/10_25_2025_09_08/
```

Each successful backtest has:
- **Python file**: The actual backtest code you can review and modify
- **Results**: Performance metrics

**Read the code!** This is how you learn what works and what doesn't.

---

## 🎯 Configuration - RBI Agent

All settings are in `src/agents/rbi_agent_pp_multi.py`:

```python
# 🎯 PROFIT TARGET CONFIGURATION
TARGET_RETURN = 15  # Target return in % (AI tries to optimize to this)
SAVE_IF_OVER_RETURN = 1.0  # Save backtest to CSV if return > this %
```

**How it works:**
- AI tries to optimize strategies to hit the **target return %**
- ANY backtest returning **> 1%** gets saved to CSV
- This way you can review all decent strategies, not just perfect ones

**Pipeline per strategy:** Research AI → Backtest AI → Package AI → Execute → Debug Loop (up to 10 attempts) → Optimize Loop (up to 10 attempts)

**Other Settings:**
```python
MAX_PARALLEL_THREADS = 18  # Number of parallel threads (adjust based on your CPU)
MAX_DEBUG_ITERATIONS = 10  # How many times to try fixing errors
MAX_OPTIMIZATION_ITERATIONS = 10  # How many times to try optimizing
CONDA_ENV = "tflow"  # Conda environment for backtest execution
EXECUTION_TIMEOUT = 300  # 5 minutes max per backtest execution
```

**AI Model Configuration (all configurable per pipeline stage):**
```python
# Currently using Gemini 2.5 Flash for all stages (fast and cheap)
# Available types: "claude", "openai", "deepseek", "groq", "gemini", "xai", "openrouter", "ollama"
RESEARCH_CONFIG = {"type": "gemini", "name": "gemini-2.5-flash"}
BACKTEST_CONFIG = {"type": "gemini", "name": "gemini-2.5-flash"}
DEBUG_CONFIG    = {"type": "gemini", "name": "gemini-2.5-flash"}
PACKAGE_CONFIG  = {"type": "gemini", "name": "gemini-2.5-flash"}
OPTIMIZE_CONFIG = {"type": "gemini", "name": "gemini-2.5-flash"}
```

---

## 📚 Advanced: Data & Custom Sources

**Default Data:** `src/data/rbi/BTC-USDT-COMPLETE-15m.csv` — 3.85 years of BTC 15-minute candles with 100% coverage and no gaps.

Additional data files available in `src/data/rbi/`:
- `BNB-USDT-2022-BEAR-15m.csv` — Bear market period
- `SOL-USDT-2022-BEAR-15m.csv` — Bear market period
- `BTC-USDT-WALK-FORWARD-15m.csv` — Walk-forward testing

To add custom data, place CSV files with columns `datetime, open, high, low, close, volume` in `src/data/rbi/` and update the data path in the backtest prompt.


---

## 🚀 Strategy Improvements & Multi-Symbol Backtesting

### Overview

We've dramatically improved 6 RBI-generated strategies and created an enhanced backtesting framework to test them across 95+ different symbols (stocks, forex, crypto, commodities, indices).

**Location:** `src/data/rbi_pp_multi/02_28_2026/backtests_optimized/`

### 📊 Original Performance Issues

| Strategy | Avg Return | Sharpe | MaxDD | Trades | Win Rate | Main Problem |
|----------|-----------|--------|--------|--------|----------|-------------|
| **ChartistBreakout** | -8.99% | -2.85 | -10.74% | 39.2 | 58.2% | Volume filter too strict (1.5x) |
| **VelocityConfirmation** | **-11.91%** | **-7.75** | -12.51% | 39.0 | **18.4%** | **Catastrophic over-filtering** |
| **GeneticArchitect** | -3.83% | -1.70 | -5.62% | 9.9 | 33.3% | SMAs too slow for 15m |
| **KineticCrossover** | -0.33% | -0.39 | -1.04% | 1.7 | 46.3% | Best but over-filtered |
| **SqueezeBreakout** | -0.78% | -1.73 | -1.05% | 3.5 | 20.4% | Barely functional |
| **DynamicBreakout** | -0.03% | -0.98 | -0.07% | **0.0** | 25.0% | **Completely broken** |

**Average Return Across All Strategies: -4.3%** ❌

### ✨ V2 Improvements (All with 2% Risk Per Trade)

#### 1. **KineticCrossover V2**
**Critical Fixes:**
- ✅ ADX threshold: 25 → 20 (catch earlier trends)
- ✅ RSI range: 50-70 → 45-75 (wider momentum window)
- ✅ Volume filter: 1.0x → 0.8x (don't miss quiet signals)
- ✅ Dynamic sizing: position scales with ADX strength
- ✅ Better R:R: 4.0x → 5.0x TP multiplier
- ✅ Slightly wider SL: 2.0 → 2.5 ATR (fewer whipsaws)
- ✅ Faster SMAs: 10/30 → 8/25 (better for 15m)

**Expected: -0.33% → +2-5% return**

#### 2. **ChartistBreakout V2**
**Critical Fixes:**
- ✅ **CRITICAL: Volume 1.5x → 1.1x** (catch 3x more breakouts!)
- ✅ Lookback: 20 → 15 periods (fits 15m better)
- ✅ **NEW: EMA 50 trend filter** (only trade WITH trend)
- ✅ SL buffer: 0.1% → 0.3% (avoid whipsaws)

**Expected: -8.99% → +1-4% return, 58% → 65%+ win rate**

#### 3. **VelocityConfirmation V2** 🔥 **MOST CRITICAL FIX**
**Catastrophic Issues Fixed:**
- ✅ **CRITICAL: SMA 20/100 → 12/40** (from 25 hours to 5 hours on 15m!)
- ✅ **CRITICAL: Trailing stop 3.0 → 1.8 ATR** (was giving back ALL profits!)
- ✅ ADX: 25 → 22 (relaxed)
- ✅ RSI: 55 → 50 (relaxed)
- ✅ Volume: 1.0x → 0.9x (relaxed)
- ✅ Take profit: 2.0x → 2.5x (better R:R)

**Expected: -11.91% → +3-8% return, 18% → 45%+ win rate**

#### 4. **GeneticArchitect V2**
**Critical Fixes:**
- ✅ **Trend SMA: 100 → 50** (25h → 12.5h on 15m)
- ✅ Core SMAs faster: 10/30 → 8/24
- ✅ RSI bands: 70/30 → 75/25 (more trades)
- ✅ **Take profit: 1.5x → 2.5x** (much better R:R!)
- ✅ **NEW: Volatility-based sizing** (reduce in extreme vol)

**Expected: -3.83% → +2-6% return**

#### 5. **DynamicBreakout V2** 🆕 **COMPLETE REDESIGN**
**Original was completely broken (0 trades). Complete rebuild:**
- ✅ **NEW: Donchian Channel breakouts (20/10)**
- ✅ **NEW: ATR volatility filter** (avoid dead markets)
- ✅ **NEW: Volume confirmation**
- ✅ **NEW: EMA 40 trend alignment**
- ✅ **NEW: Proper risk management**
- ✅ **NEW: Dynamic exit on 10-period channel**

**Expected: -0.03% → +2-5% return**

#### 6. **SqueezeBreakout V2**
**Critical Fixes:**
- ✅ **NEW: Bollinger Band squeeze detection**
- ✅ **NEW: Keltner Channel confirmation**
- ✅ **NEW: Volume surge filter (1.2x)**
- ✅ **NEW: RSI momentum for direction**
- ✅ **NEW: Recent squeeze history check**
- ✅ Better R:R: 3.5x TP multiplier

**Expected: -0.78% → +1-4% return**

### 🎯 Key Improvement Themes

#### 1. **Timeframe Optimization** (CRITICAL)
**Problem:** SMA(100) on 15m = 25 hours = useless
**Fix:** All long-period indicators reduced by 50%+
- SMA 100 → 50 (VelocityConfirmation, GeneticArchitect)
- SMA 20 → 12 (VelocityConfirmation)
- Lookback 20 → 15 (ChartistBreakout)

#### 2. **Over-Filtering Fixed**
**Problem:** Too many filters = no trades or terrible win rates
**Fix:** RELAXED all entry requirements:
- ADX: 25 → 20/22 (easier entry)
- RSI: Widened ranges by 5-10 points
- Volume: 1.0-1.5x → 0.8-1.1x (much more relaxed)

#### 3. **Risk-Reward Improved**
**Problem:** Most had 2:1 or worse R:R
**Fix:** Improved take profit levels:
- 1.5x → 2.5x (GeneticArchitect)
- 2.0x → 2.5x (VelocityConfirmation)
- 4.0x → 5.0x (KineticCrossover)

#### 4. **Trailing Stops Fixed**
**Problem:** 3.0 ATR trailing stop gave back all profits
**Fix:** 3.0 → 1.8 ATR (VelocityConfirmation)

#### 5. **Trend Alignment Added**
**Problem:** Counter-trend trades killed performance
**Fix:** Added EMA/SMA trend filters:
- ChartistBreakout: EMA 50
- DynamicBreakout: EMA 40
- All strategies: Only trade WITH the trend

### 📊 Enhanced Backtest Framework

**Script:** `src/scripts/backtest_all_type_of15m.py`

**Features:**

#### Real-Time Progress Display
```bash
[1/665] KineticCrossover x BTCUSD (12450bars/365d, FULL) -> +2.3% (15T, 60%WR, MaxW:4/L:2)
[2/665] ChartistBreakout x ETHUSD (12450bars/365d, FULL) -> 0.0% (NO TRADES)
[3/665] VelocityConfirmation x ARKK (8320bars/243d, IS-ODD) -> +4.1% (22T, 45%WR, MaxW:5/L:3)
```

**Progress shows:**
- Bar count & time span (e.g., `12450bars/365d`)
- Data type (IS-ODD, OOS-EVEN, FULL)
- Return % with trade count
- Win rate
- Max consecutive wins/losses (`MaxW:4/L:2`)

#### Enhanced 0.0% Explanations
- `0.0% (NO TRADES)` - Strategy didn't trigger
- `0.0% (5T, ALL LOSSES! MaxL:5)` - Lost all 5 trades
- `0.0% (10T, 50%WR, MaxW:3/L:4)` - Breakeven but rough streak

#### Comprehensive Strategy Scoring

**Scoring System (0-100):**
- **PnL (30%)** - Most important: profitability
- **Sharpe Ratio (25%)** - Risk-adjusted returns
- **Win Rate (20%)** - Consistency
- **Max Drawdown (15%)** - Capital protection
- **Max Consecutive Losses (10%)** - Psychology & risk

**Example Output:**
```
🏆 COMPREHENSIVE STRATEGY SCORING (Best = 100)
Scoring: PnL(30%) + Sharpe(25%) + WinRate(20%) + MaxDD(15%) + ConsecLoss(10%)

Rank  Strategy                   Score    PnL  Sharpe WinRate  MaxDD  MaxCL
🥇 1   KineticCrossoverV2          82.3   3.50%   1.85    58.5%  -4.20%   3.2
🥈 2   GeneticArchitectV2          78.9   2.80%   1.62    55.0%  -5.80%   3.8
🥉 3   ChartistBreakoutV2          71.5   2.10%   1.20    62.0%  -6.50%   4.5
```

**Score Interpretation:**
- **90-100**: 🌟 Excellent - Deploy with confidence
- **70-89**: ✅ Good - Solid performer
- **50-69**: ⚠️ Moderate - Use with caution
- **30-49**: ⚠️ Poor - Needs improvement
- **0-29**: ❌ Failing - Do not deploy

#### Max Consecutive Losses Tracking

**Why This Matters:**
- **Psychology**: Can you survive 8 losses in a row?
- **Risk Management**: MaxL × risk_per_trade = potential drawdown
- **Strategy Validation**: MaxL > 10 = systemic issues

**Example Risk Calculation:**
```
Strategy: VelocityConfirmation
MaxL: 8 consecutive losses
Risk per trade: 2%
Potential drawdown: ~16%
```

⚠️ **If you see MaxL:15, that's a red flag** even if profitable overall!

### 🚀 Running the Enhanced Backtest

```bash
cd src/scripts
conda run -n tflow python backtest_all_type_of15m.py
```

**What it does:**
1. Tests 6-7 strategies across 95 symbols
2. Shows real-time progress with detailed metrics
3. Generates comprehensive CSV with all results
4. Outputs final strategy scoring and rankings

**Results saved to:** `src/data/multi_symbol_backtest/GEN_95_symbol_results.csv`

### 📈 Expected Results

**Target Performance:**
- **Original Avg:** -4.3% return
- **V2 Target:** +2% to +5% average return
- **Win Rate:** 30-45% → 45-60%
- **Max Consecutive Losses:** < 6 for most strategies

**Most Dramatic Improvement:**
- VelocityConfirmation: -11.91% → +3-8%, Win rate 18% → 45%+

### 📚 Documentation

**Full improvement analysis:** `src/data/rbi_pp_multi/02_28_2026/IMPROVEMENTS_SUMMARY.md`

**Strategy files:**
- `GEN_KineticCrossover_v2_IMPROVED.py`
- `GEN_ChartistBreakout_v2_IMPROVED.py`
- `GEN_VelocityConfirmation_v2_IMPROVED.py`
- `GEN_GeneticArchitect_v2_IMPROVED.py`
- `GEN_DynamicBreakout_v2_IMPROVED.py`
- `GEN_SqueezeBreakout_v2_IMPROVED.py`

### 💡 Moon Dev's Improvement Philosophy

1. **Fix the biggest losers first** (VelocityConfirmation -11.91%)
2. **Relax over-filtering** (let good trades through)
3. **Match timeframes properly** (15m needs fast indicators)
4. **Improve R:R ratios** (better take profits)
5. **Add trend filters** (don't fight the trend)
6. **Real data only** (no synthetic improvements)
7. **Track psychology** (consecutive losses matter!)

---

## 🗺️ ROADMAP

### Completed
- [x] **HyperLiquid Perps Integration** ✅
- [x] **Swarm Consensus Trading** ✅ (6-model parallel: Claude 4.5, GPT-5, Gemini 2.5, Grok-4, DeepSeek, DeepSeek-R1)
- [x] **RBI Parallel Backtesting** ✅ (18 threads, auto debug/optimize)
- [x] **OpenRouter Integration** ✅ (200+ models)
- [x] **Aster Integration** ✅
- [x] **Extended Exchange (X10)** ✅
- [x] **Multi-Data Testing** ✅ (25+ data sources)

### Coming Soon
- [ ] **Polymarket Integration** - Prediction market trading
- [ ] **Base Chain Integration** - L2 network support
- [ ] **HyperLiquid Spot Trading** - Spot market support
- [ ] **Trending Agent** - Spots leaders on HyperLiquid
- [ ] **Position Sizing Agent** - Volume/liquidation-based sizing
- [ ] **Regime Agents** - Adaptive strategy switching
- [ ] **Polymarket Sweeper Agent** - Follow successful prediction traders

### Future Ideas
- [ ] **Lighter Integration**
- [ ] **Pacifica Integration**
- [ ] **Hibachi Integration**
- [ ] **HyperEVM Support**

---

*Built with love by Moon Dev - Pioneering the future of AI-powered trading*

## 📜 Detailed Disclaimer
The content presented is for educational and informational purposes only and does not constitute financial advice. All trading involves risk and may not be suitable for all investors. You should carefully consider your investment objectives, level of experience, and risk appetite before investing.

Past performance is not indicative of future results. There is no guarantee that any trading strategy or algorithm discussed will result in profits or will not incur losses.

**CFTC Disclaimer:** Commodity Futures Trading Commission (CFTC) regulations require disclosure of the risks associated with trading commodities and derivatives. There is a substantial risk of loss in trading and investing.

I am not a licensed financial advisor or a registered broker-dealer. Content & code is based on personal research perspectives and should not be relied upon as a guarantee of success in trading.
