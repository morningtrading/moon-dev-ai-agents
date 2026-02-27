# 🚀 Quick Start Guide - Titus Start Agents

## What is `titus_start_agents.sh`?

An optimized bash script that automates the entire setup process for moon-dev-ai-agents including:
- ✅ Creating conda environments (tflow + moon312)
- ✅ Installing all dependencies
- ✅ Validating configuration
- ✅ Displaying next steps

## Installation

The script is already in the project root:
```bash
/home/titus/moon-dev-ai-agents/titus_start_agents.sh
```

## Usage

### Option 1: Full Setup (First Time)
```bash
cd /home/titus/moon-dev-ai-agents
bash titus_start_agents.sh
```

**What it does:**
1. Checks prerequisites (conda, pip)
2. Creates `tflow` environment (Python 3.10.9)
3. Creates `moon312` environment (Python 3.12)
4. Installs all required packages:
   - pandas, numpy
   - backtesting.py, ta-lib
   - anthropic, deepseek
   - openai, dotenv, termcolor
   - pyarrow
5. Validates agent script exists
6. Validates API keys in .env

**Output:**
```
╔════════════════════════════════════════════════════════════════╗
║     🚀 Titus Start Agents - Setup & Launch                     ║
╚════════════════════════════════════════════════════════════════╝

✅ Step 1/6: Prerequisites validated
✅ Step 2/6: Working directory: /home/titus/moon-dev-ai-agents
✅ Step 3/6: tflow environment ready
✅ Step 4/6: moon312 environment ready
✅ Step 5/6: Agent script found
✅ Step 6/6: Environment configuration valid

✅ Setup Complete!

📊 Environments Ready:
   • tflow (Python 3.10.9) - Backtesting with talib
   • moon312 (Python 3.12) - Agent runtime

🚀 Next Steps:
   1. Switch coin (if needed)...
   2. Start backtesting...
   3. Or use utilities...
```

### Option 2: Quick Start (If Already Setup)
```bash
bash titus_start_agents.sh --quick-start
```

**What it does:**
- Skips all setup
- Immediately runs the backtesting agent
- Useful for repeated runs

### Option 3: Help
```bash
bash titus_start_agents.sh --help
```

## Environments Created

### tflow (Python 3.10.9)
- **Purpose**: Backtesting with talib library
- **Packages**: pandas, numpy, backtesting.py, ta-lib, anthropic, deepseek
- **Usage**: `conda run -n tflow python src/agents/rbi_agent_v2_simple.py`

### moon312 (Python 3.12)
- **Purpose**: Agent runtime (future use)
- **Note**: Currently not actively used in the workflow

## Common Tasks

### Run Backtesting Agent
```bash
conda run -n tflow python src/agents/rbi_agent_v2_simple.py
```

### Switch to Different Coin
1. Edit `src/agents/rbi_agent_v2_simple.py` line 24:
   ```python
   COIN = "SUI"  # Change to BNB, BTC, etc
   ```
2. Run agent normally

### Upload New Coin Data
```bash
python utils_upload_coin_data.py /path/to/coin.feather
```

### Manually Activate Environment
```bash
conda activate tflow
python src/agents/rbi_agent_v2_simple.py
```

## Troubleshooting

### Issue: "conda not found"
**Solution**: Install Miniconda from https://docs.conda.io/projects/miniconda/en/latest/

### Issue: "ANTHROPIC_KEY not found in .env"
**Solution**: 
1. Create/update `.env` file in project root
2. Add: `ANTHROPIC_KEY=sk-ant-api03-...`
3. Add: `DEEPSEEK_KEY=sk-...`

### Issue: "Environment already exists"
**Solution**: Script will skip creation and just install packages. To recreate:
```bash
conda env remove -n tflow -y
bash titus_start_agents.sh
```

### Issue: "ta-lib installation fails"
**Solution**: This is normal on some systems. Script will warn but continue. Install manually:
```bash
conda install -n tflow -c conda-forge ta-lib -y
```

## Performance Tips

### First Run
- Takes 5-10 minutes (downloading and installing all packages)
- Creates ~2-3 GB of environments

### Subsequent Runs  
- Fast (~30 seconds) as environments already exist
- Use `--quick-start` to skip validation

### Reduce Setup Time
```bash
# Skip full setup, just validate
conda env list | grep tflow  # Check if exists
conda run -n tflow python src/agents/rbi_agent_v2_simple.py
```

## What Happens Under the Hood

```bash
# Step 1: Validate
conda --version
pip --version

# Step 2: Create tflow (if not exists)
conda create -n tflow python=3.10.9 -y

# Step 3: Install packages
conda activate tflow
pip install pandas numpy backtesting ta-lib anthropic deepseek python-dotenv termcolor openai pyarrow

# Step 4: Create moon312 (if not exists)
conda create -n moon312 python=3.12 -y

# Step 5-6: Validate configuration
ls -f src/agents/rbi_agent_v2_simple.py
grep ANTHROPIC_KEY .env
grep DEEPSEEK_KEY .env
```

## Script Structure

| Function | Purpose |
|----------|---------|
| `log_info()` | Print blue info messages |
| `log_success()` | Print green success messages |
| `log_warning()` | Print yellow warnings |
| `log_error()` | Print red errors |
| `check_command()` | Verify conda/pip exist |
| `env_exists()` | Check if conda env exists |
| `main()` | Execute 6-step setup |

## Next Actions

After setup completes, you can:

1. **Run backtesting**: Start generating and testing strategies
2. **Upload coin data**: Convert feather files to CSV format
3. **Monitor results**: Check generated backtests and metrics
4. **Deploy**: Move successful strategies to paper trading

## References

- 📖 [RBI Agent v2 Simple README](RBI_AGENT_V2_SIMPLE_README.md)
- 🔧 [Upload Coin Data Utility](utils_upload_coin_data.py)
- 📊 [Backtest Results](src/data/rbi_v2/)
- 🎯 [Strategy Selection Guide](STRATEGY_DEPLOYMENT.md)

---

**Last Updated**: November 30, 2025  
**Status**: ✅ Production Ready
