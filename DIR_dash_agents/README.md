# 🌙 Moon Dev Agent Control Center Dashboard

**Real-time monitoring and control dashboard for Moon Dev's AI trading agent system.**

---

## 🎯 Features

### 📊 Dashboard Panels

1. **Agent Status Grid** - View all 48+ agents, their status (running/stopped), PIDs, and uptime
2. **Master Control Panel** - Start/stop all agents with one click
3. **Live Log Viewer** - Tail agent logs in real-time with color-coded levels
4. **Trading Overview** - Current balance, positions, P&L, and risk status
5. **Recent Alerts** - Stream of important events (whale, liquidation, sentiment, funding, errors)
6. **System Info** - Python version, environment, system uptime, active exchange

### ⚡ Real-Time Updates

- Agent status updates every 3 seconds
- Log viewer refreshes every 3 seconds
- Alerts poll every 5 seconds
- Trading metrics update every 5 seconds
- System info updates every 10 seconds

### 🎛️ Agent Control

- Start/stop individual agents with confirmation dialogs
- Bulk operations: "Start All Enabled" and "Stop All"
- View live logs for any agent
- Agent warnings for trading/risk agents

---

## 🚀 Quick Start

### Installation

```bash
# Activate your environment (e.g., conda activate tflow)
cd /home/titus/moon-dev-ai-agents

# Install dependencies (if not already installed)
pip install fastapi uvicorn[standard] jinja2 aiofiles python-multipart
```

### Run Dashboard

```bash
# Method 1: Direct Python
python DIR_dash_agents/app.py

# Method 2: Using startup script
./DIR_dash_agents/start_dashboard.sh
```

### Access Dashboard

Open browser to: **http://localhost:8002**

---

## 🏗️ Architecture

**Backend:** FastAPI (Python)
- Port: 8002 (avoids conflict with backtestdashboard.py on 8001)
- Integrates with `agent_manager.py` for agent control
- Reads `agent_config.yaml` for agent configuration
- Tails log files from `logs/` directory
- Parses trading data from `src/data/` directories

**Frontend:** HTML + CSS + Vanilla JavaScript
- AJAX polling for real-time updates
- Dark theme UI optimized for trading
- Responsive grid layout
- Toast notifications for actions

---

## 📁 Directory Structure

```
DIR_dash_agents/
├── app.py                  # FastAPI backend application
├── templates/
│   └── index.html          # Main dashboard HTML template
├── static/
│   ├── style.css           # Dashboard styling
│   └── script.js           # Real-time updates and interactions
├── start_dashboard.sh      # Convenience startup script
└── README.md               # This file
```

---

## 🔧 Configuration

Dashboard reads from:
- `agent_config.yaml` - Agent definitions and enabled status
- `.agent_pids/` - Agent process IDs
- `logs/` - Agent log files
- `src/data/` - Trading metrics and agent outputs

No additional configuration needed!

---

## 🎨 UI Color Scheme

- **Running:** Green (#00ff88)
- **Stopped:** Gray (#6c757d)
- **Error:** Red (#ff4757)
- **Warning:** Yellow (#ffd93d)
- **Info:** Blue (#5f9dff)
- **Background:** Dark (#1a1a2e, #16213e)

---

## 🐛 Troubleshooting

**Dashboard won't start:**
- Check port 8002 is not in use: `lsof -i :8002`
- Verify dependencies installed: `pip list | grep fastapi`

**Agents not showing:**
- Ensure `agent_config.yaml` exists in project root
- Check `.agent_pids/` directory exists

**Logs not displaying:**
- Verify `logs/` directory exists with agent log files
- Check file permissions

**Trading metrics empty:**
- Ensure trading agents have run at least once
- Check `src/data/` contains agent output files

---

## 🔗 Integration

Works alongside existing tools:
- ✅ `agent_manager.py` - Uses same AgentManager class
- ✅ `agent_config.yaml` - Reads same configuration
- ✅ `backtestdashboard.py` - Runs on different port (8001 vs 8002)
- ✅ All existing agents - No modifications needed

---

## 📜 API Endpoints

- `GET /` - Main dashboard page
- `GET /api/agents/status` - Agent status JSON
- `POST /api/agents/{name}/start` - Start agent
- `POST /api/agents/{name}/stop` - Stop agent
- `POST /api/agents/start-all` - Start all enabled
- `POST /api/agents/stop-all` - Stop all running
- `GET /api/logs/{name}` - Agent log tail
- `GET /api/alerts` - Recent alert stream
- `GET /api/trading/overview` - Trading metrics
- `GET /api/system/info` - System information

---

**Built with 🌙 by Moon Dev**

*Real-time control center for AI trading agents.*
