# 🌙 Moon Dev Agent Manager Guide

## Overview

The Agent Manager is a centralized control system for managing all Moon Dev AI agents. It provides:
- ✅ Start/stop/restart agents
- 📊 Real-time status monitoring
- 📝 Centralized logging
- 🎛️ Interactive menu interface
- ⚙️ Easy enable/disable configuration

## Quick Start

### 1. Interactive Menu (Recommended)
```bash
python agent_manager.py
```

This opens an interactive menu where you can:
1. View status of all agents
2. Start all enabled agents
3. Stop all running agents
4. Start/stop specific agents
5. Enable/disable agents
6. View logs
7. And more!

### 2. Command Line Interface

**Check status:**
```bash
python agent_manager.py status
```

**Start agents:**
```bash
python agent_manager.py start all              # Start all enabled agents
python agent_manager.py start liquidation_agent # Start specific agent
```

**Stop agents:**
```bash
python agent_manager.py stop all               # Stop all running agents
python agent_manager.py stop liquidation_agent  # Stop specific agent
```

**Restart agent:**
```bash
python agent_manager.py restart liquidation_agent
```

**View logs:**
```bash
python agent_manager.py logs liquidation_agent     # Last 50 lines
python agent_manager.py logs liquidation_agent 100 # Last 100 lines
```

**Enable/disable agents:**
```bash
python agent_manager.py enable liquidation_agent
python agent_manager.py disable liquidation_agent
```

## Configuration

Edit `agent_config.yaml` to enable/disable agents:

```yaml
agents:
  liquidation_agent:
    enabled: true  # Change to false to disable
    description: "Monitors liquidation events"
    script: "src/agents/liquidation_agent.py"
```

## Status Output

The status command shows:
- ● **Green dot** = Running
- ○ **Yellow dot** = Enabled but not running  
- ○ **White dot** = Disabled

Example:
```
● liquidation_agent        PID: 96150  Uptime: 5m  RAM: 172.1MB
○ whale_agent              Enabled (not running)
○ sentiment_agent          Disabled
```

## File Structure

```
moon-dev-ai-agents/
├── agent_manager.py          # Main manager script
├── agent_config.yaml         # Configuration file
├── logs/                     # Centralized logs
│   ├── liquidation_agent.log
│   └── whale_agent.log
└── .agent_pids/             # PID tracking
    └── liquidation_agent.pid
```

## Common Workflows

### Starting Multiple Agents

**Option 1: Enable in config, then start all**
```bash
# Edit agent_config.yaml and set enabled: true for desired agents
python agent_manager.py start all
```

**Option 2: Start individually**
```bash
python agent_manager.py enable liquidation_agent
python agent_manager.py enable whale_agent
python agent_manager.py start liquidation_agent
python agent_manager.py start whale_agent
```

### Monitoring Running Agents

**Check status:**
```bash
python agent_manager.py status
```

**View live logs:**
```bash
tail -f logs/liquidation_agent.log
```

### Safe Shutdown

**Stop all agents before system shutdown:**
```bash
python agent_manager.py stop all
```

## Tips

1. **Always check status first** to see what's running
2. **Use enable/disable** to control which agents start with `start all`
3. **Check logs** if an agent fails to start
4. **Enable warnings** - Trading agents show confirmation prompts
5. **Monitor memory** - Status shows RAM usage per agent

## Available Agents

### Market Analysis (Safe)
- `liquidation_agent` - Liquidation monitoring
- `whale_agent` - Whale wallet tracking
- `sentiment_agent` - Twitter sentiment analysis
- `funding_agent` - Funding rate monitoring
- `chartanalysis_agent` - Chart analysis

### Trading Agents (⚠️ Use with caution!)
- `trading_agent` - Live trading with AI
- `risk_agent` - Portfolio risk management
- `strategy_agent` - Strategy execution

### Research & Content
- `research_agent` - Strategy research
- `websearch_agent` - Web scraping for strategies
- `chat_agent` - YouTube chat moderation
- `tweet_agent` - Twitter posting

### Specialized
- `sniper_agent` - Token launch sniping
- `polymarket_agent` - Prediction markets
- `housecoin_agent` - DCA with AI confirmation
- And more...

## Troubleshooting

**Agent won't start:**
```bash
# Check the logs
python agent_manager.py logs <agent_name>

# Check if script exists
ls -la src/agents/<agent_name>.py
```

**Stale PID file:**
```bash
# The manager auto-cleans stale PIDs
python agent_manager.py status
```

**Permission denied:**
```bash
chmod +x agent_manager.py
```

## Advanced Usage

### Custom Python Path
Edit `agent_config.yaml`:
```yaml
settings:
  python_path: "/your/custom/path"
```

### Auto-restart (Coming soon)
```yaml
settings:
  auto_restart: true
  max_restarts: 3
```

## Support

- Discord: https://discord.gg/8UPuVZ53bh
- YouTube: Moon Dev channel
- Issues: GitHub repository

---

**🌙 Built by Moon Dev - Democratizing AI agent development**
