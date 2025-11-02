#!/usr/bin/env python3
"""
🌙 Moon Dev Agent Control Center Dashboard
FastAPI backend for real-time agent monitoring and control
"""

import os
import sys
import yaml
import time
import psutil
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

# Import AgentManager from parent directory
from agent_manager import AgentManager
# Import config to read/write MP3 settings
import src.config as config

# ============================================================================
# CONFIGURATION
# ============================================================================

PORT = 8002
HOST = "0.0.0.0"
PROJECT_ROOT = Path(__file__).parent.parent
TEMPLATES_DIR = Path(__file__).parent / "templates"
STATIC_DIR = Path(__file__).parent / "static"
LOGS_DIR = PROJECT_ROOT / "logs"
DATA_DIR = PROJECT_ROOT / "src" / "data"
CONFIG_FILE = PROJECT_ROOT / "agent_config.yaml"

# ============================================================================
# INITIALIZE FASTAPI
# ============================================================================

app = FastAPI(title="Moon Dev Agent Control Center")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize AgentManager
agent_manager = AgentManager(config_file=str(CONFIG_FILE))

# Alert cache for recent alerts
alert_cache = deque(maxlen=50)  # Keep last 50 alerts

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def read_agent_config() -> Dict:
    """Read agent configuration from YAML file"""
    try:
        with open(CONFIG_FILE, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error reading config: {e}")
        return {"agents": {}, "settings": {}}


def get_agent_status(agent_name: str) -> Dict:
    """Get status of a specific agent"""
    config = read_agent_config()
    agent_config = config.get('agents', {}).get(agent_name, {})
    
    # Get PID and check if running
    pid = agent_manager.get_agent_pid(agent_name)
    is_running = pid is not None
    
    # Get uptime if running
    uptime_seconds = 0
    if is_running and pid:
        try:
            process = psutil.Process(pid)
            create_time = process.create_time()
            uptime_seconds = time.time() - create_time
        except:
            uptime_seconds = 0
    
    # Get last activity from log file
    last_activity = get_last_log_timestamp(agent_name)
    
    return {
        "name": agent_name,
        "enabled": agent_config.get('enabled', False),
        "description": agent_config.get('description', ''),
        "running": is_running,
        "pid": pid,
        "uptime_seconds": int(uptime_seconds),
        "last_activity": last_activity,
        "warning": agent_config.get('warning'),
        "script": agent_config.get('script', '')
    }


def get_last_log_timestamp(agent_name: str) -> Optional[str]:
    """Get timestamp of last log entry"""
    log_file = LOGS_DIR / f"{agent_name}.log"
    if not log_file.exists():
        return None
    
    try:
        # Read last few lines
        with open(log_file, 'r') as f:
            lines = f.readlines()
            if lines:
                # Try to extract timestamp from last line
                last_line = lines[-1].strip()
                if last_line:
                    return datetime.now().isoformat()  # Simplified
    except Exception as e:
        return None
    
    return None


def tail_log_file(log_path: Path, lines: int = 50) -> List[str]:
    """Read last N lines from log file"""
    if not log_path.exists():
        return []
    
    try:
        with open(log_path, 'r') as f:
            all_lines = f.readlines()
            return [line.rstrip() for line in all_lines[-lines:]]
    except Exception as e:
        return [f"Error reading log: {e}"]


def parse_alerts_from_logs() -> List[Dict]:
    """Scan log files for important events/alerts"""
    alerts = []
    
    # Keywords to look for
    alert_keywords = {
        'whale': 'whale',
        'liquidation': 'liquidation',
        'sentiment': 'sentiment',
        'funding': 'funding',
        'error': 'ERROR',
        'warning': 'WARNING',
        'critical': 'CRITICAL'
    }
    
    if not LOGS_DIR.exists():
        return alerts
    
    # Scan recent log files
    for log_file in LOGS_DIR.glob("*.log"):
        agent_name = log_file.stem
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Check last 20 lines for alerts
                for line in lines[-20:]:
                    line_lower = line.lower()
                    for alert_type, keyword in alert_keywords.items():
                        if keyword.lower() in line_lower:
                            alerts.append({
                                "type": alert_type,
                                "agent": agent_name,
                                "message": line.strip()[:200],  # Truncate long messages
                                "timestamp": datetime.now().isoformat()
                            })
                            break
        except Exception:
            continue
    
    # Sort by timestamp (most recent first)
    alerts.sort(key=lambda x: x['timestamp'], reverse=True)
    return alerts[:10]  # Return last 10 alerts


def get_trading_metrics() -> Dict:
    """Read trading metrics from Hyperliquid"""
    metrics = {
        "balance": 0,
        "positions_count": 0,
        "pnl_today": 0,
        "risk_status": "Unknown"
    }
    
    try:
        # Import Hyperliquid functions
        import src.nice_funcs_hyperliquid as hl
        
        # Get account from environment
        account = hl._get_account_from_env()
        
        # Get account balance
        try:
            balance = hl.get_account_value(account)
            metrics["balance"] = round(balance, 2)
        except Exception as e:
            print(f"Error getting balance: {e}")
        
        # Get positions for configured symbols
        from src.config import HYPERLIQUID_SYMBOLS
        positions_count = 0
        total_pnl = 0
        
        for symbol in HYPERLIQUID_SYMBOLS:
            try:
                position = hl.get_position(symbol, account)
                if position and position.get('position_amount', 0) != 0:
                    positions_count += 1
                    # Add unrealized PnL
                    pnl = position.get('pnl', 0)
                    total_pnl += pnl
            except:
                continue
        
        metrics["positions_count"] = positions_count
        metrics["pnl_today"] = round(total_pnl, 2)
        
        # Determine risk status based on PnL
        if total_pnl < -50:
            metrics["risk_status"] = "High Risk"
        elif total_pnl < -20:
            metrics["risk_status"] = "Medium Risk"
        elif total_pnl < 0:
            metrics["risk_status"] = "Low Risk"
        else:
            metrics["risk_status"] = "Healthy"
            
    except Exception as e:
        print(f"Error getting trading metrics: {e}")
    
    return metrics


def get_system_info() -> Dict:
    """Get system information"""
    # Get Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    # Get system uptime
    boot_time = psutil.boot_time()
    uptime_seconds = time.time() - boot_time
    
    # Count active agents
    config = read_agent_config()
    active_count = sum(1 for agent in config.get('agents', {}).values() 
                      if agent.get('enabled', False))
    
    # Get running count
    running_count = sum(1 for name in config.get('agents', {}).keys() 
                       if agent_manager.get_agent_pid(name) is not None)
    
    # Try to detect exchange from config or trading agent
    exchange = "Unknown"
    try:
        trading_agent_path = PROJECT_ROOT / "src" / "agents" / "trading_agent.py"
        if trading_agent_path.exists():
            with open(trading_agent_path, 'r') as f:
                content = f.read()
                # Look for EXCHANGE = "..." pattern
                match = re.search(r'EXCHANGE\s*=\s*["\']([^"\']+)["\']', content)
                if match:
                    exchange = match.group(1)
    except:
        pass
    
    return {
        "python_version": python_version,
        "uptime_seconds": int(uptime_seconds),
        "active_agents": active_count,
        "running_agents": running_count,
        "exchange": exchange
    }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Render main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    config = read_agent_config()
    agents = config.get('agents', {})
    
    status_list = []
    for agent_name, agent_config in agents.items():
        # Skip agents hidden from dashboard
        if not agent_config.get('show_in_dashboard', True):
            continue
        
        status = get_agent_status(agent_name)
        status_list.append(status)
    
    # Sort by name
    status_list.sort(key=lambda x: x['name'])
    
    return JSONResponse(content={"agents": status_list})


@app.post("/api/agents/{agent_name}/start")
async def start_agent(agent_name: str):
    """Start a specific agent"""
    try:
        success = agent_manager.start_agent(agent_name)
        if success:
            return JSONResponse(content={
                "success": True,
                "message": f"Agent {agent_name} started successfully"
            })
        else:
            return JSONResponse(content={
                "success": False,
                "message": f"Failed to start {agent_name}"
            }, status_code=500)
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": f"Error starting {agent_name}: {str(e)}"
        }, status_code=500)


@app.post("/api/agents/{agent_name}/stop")
async def stop_agent(agent_name: str):
    """Stop a specific agent"""
    try:
        success = agent_manager.stop_agent(agent_name)
        if success:
            return JSONResponse(content={
                "success": True,
                "message": f"Agent {agent_name} stopped successfully"
            })
        else:
            return JSONResponse(content={
                "success": False,
                "message": f"Failed to stop {agent_name}"
            }, status_code=500)
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": f"Error stopping {agent_name}: {str(e)}"
        }, status_code=500)


@app.post("/api/agents/start-all")
async def start_all_agents():
    """Start all enabled agents"""
    config = read_agent_config()
    agents = config.get('agents', {})
    
    started = []
    failed = []
    
    for agent_name, agent_config in agents.items():
        if agent_config.get('enabled', False):
            try:
                success = agent_manager.start_agent(agent_name)
                if success:
                    started.append(agent_name)
                else:
                    failed.append(agent_name)
            except Exception as e:
                failed.append(agent_name)
    
    return JSONResponse(content={
        "success": len(failed) == 0,
        "started": started,
        "failed": failed,
        "message": f"Started {len(started)} agents, {len(failed)} failed"
    })


@app.post("/api/agents/stop-all")
async def stop_all_agents():
    """Stop all running agents"""
    config = read_agent_config()
    agents = config.get('agents', {})
    
    stopped = []
    failed = []
    
    for agent_name in agents.keys():
        if agent_manager.get_agent_pid(agent_name) is not None:
            try:
                success = agent_manager.stop_agent(agent_name)
                if success:
                    stopped.append(agent_name)
                else:
                    failed.append(agent_name)
            except Exception as e:
                failed.append(agent_name)
    
    return JSONResponse(content={
        "success": len(failed) == 0,
        "stopped": stopped,
        "failed": failed,
        "message": f"Stopped {len(stopped)} agents, {len(failed)} failed"
    })


@app.get("/api/logs/{agent_name}")
async def get_agent_logs(agent_name: str, lines: int = 50):
    """Get last N lines from agent log file"""
    log_file = LOGS_DIR / f"{agent_name}.log"
    
    if not log_file.exists():
        return JSONResponse(content={
            "agent": agent_name,
            "lines": [f"No log file found for {agent_name}"]
        })
    
    log_lines = tail_log_file(log_file, lines)
    
    return JSONResponse(content={
        "agent": agent_name,
        "lines": log_lines
    })


@app.get("/api/alerts")
async def get_alerts():
    """Get recent alerts from log files"""
    alerts = parse_alerts_from_logs()
    return JSONResponse(content={"alerts": alerts})


@app.get("/api/settings/mp3-sounds")
async def get_mp3_sound_settings():
    """Get current MP3 notification sound settings"""
    return JSONResponse(content={
        "enabled": config.PLAY_MP3_AGENT_SOUNDS,
        "repeat_count": config.MP3_REPEAT_COUNT
    })


@app.post("/api/settings/mp3-sounds/toggle")
async def toggle_mp3_sounds():
    """Toggle MP3 notification sounds on/off"""
    try:
        # Toggle the setting
        new_value = not config.PLAY_MP3_AGENT_SOUNDS
        
        # Update config file
        config_path = PROJECT_ROOT / "src" / "config.py"
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Replace the PLAY_MP3_AGENT_SOUNDS value
        content = re.sub(
            r'PLAY_MP3_AGENT_SOUNDS\s*=\s*(True|False)',
            f'PLAY_MP3_AGENT_SOUNDS = {new_value}',
            content
        )
        
        with open(config_path, 'w') as f:
            f.write(content)
        
        # Reload config module
        import importlib
        importlib.reload(config)
        
        return JSONResponse(content={
            "success": True,
            "enabled": new_value,
            "message": f"MP3 sounds {'enabled' if new_value else 'disabled'}"
        })
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": f"Error toggling MP3 sounds: {str(e)}"
        }, status_code=500)


@app.post("/api/settings/mp3-sounds/repeat")
async def set_mp3_repeat_count(count: int):
    """Set MP3 notification repeat count"""
    try:
        if count < 1 or count > 10:
            return JSONResponse(content={
                "success": False,
                "message": "Repeat count must be between 1 and 10"
            }, status_code=400)
        
        # Update config file
        config_path = PROJECT_ROOT / "src" / "config.py"
        with open(config_path, 'r') as f:
            content = f.read()
        
        # Replace the MP3_REPEAT_COUNT value
        content = re.sub(
            r'MP3_REPEAT_COUNT\s*=\s*\d+',
            f'MP3_REPEAT_COUNT = {count}',
            content
        )
        
        with open(config_path, 'w') as f:
            f.write(content)
        
        # Reload config module
        import importlib
        importlib.reload(config)
        
        return JSONResponse(content={
            "success": True,
            "repeat_count": count,
            "message": f"MP3 repeat count set to {count}"
        })
    except Exception as e:
        return JSONResponse(content={
            "success": False,
            "message": f"Error setting repeat count: {str(e)}"
        }, status_code=500)


@app.get("/api/trading/overview")
async def get_trading_overview():
    """Get trading metrics overview"""
    metrics = get_trading_metrics()
    return JSONResponse(content=metrics)


@app.get("/api/system/info")
async def get_system_information():
    """Get system information"""
    info = get_system_info()
    return JSONResponse(content=info)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print(f"🌙 Moon Dev Agent Control Center")
    print(f"Starting dashboard on http://{HOST}:{PORT}")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Press Ctrl+C to stop\n")
    
    uvicorn.run(app, host=HOST, port=PORT)
