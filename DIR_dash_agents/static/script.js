// ============================================================================
// Moon Dev Agent Control Center Dashboard - JavaScript
// Real-time updates and agent control
// ============================================================================

// Global state
let currentLogAgent = null;
let refreshIntervals = {};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function formatUptime(seconds) {
    if (seconds === 0) return '0s';
    
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    let parts = [];
    if (days > 0) parts.push(`${days}d`);
    if (hours > 0) parts.push(`${hours}h`);
    if (minutes > 0) parts.push(`${minutes}m`);
    if (secs > 0 && days === 0) parts.push(`${secs}s`);
    
    return parts.join(' ') || '0s';
}

function formatTimestamp(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString();
}

function showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    const container = document.getElementById('toast-container');
    container.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => container.removeChild(toast), 300);
    }, 3000);
}

function showConfirmModal(title, message, onConfirm) {
    const modal = document.getElementById('confirm-modal');
    document.getElementById('modal-title').textContent = title;
    document.getElementById('modal-message').textContent = message;
    
    modal.classList.add('active');
    
    const confirmBtn = document.getElementById('modal-confirm');
    const cancelBtn = document.getElementById('modal-cancel');
    
    const handleConfirm = () => {
        modal.classList.remove('active');
        onConfirm();
        cleanup();
    };
    
    const handleCancel = () => {
        modal.classList.remove('active');
        cleanup();
    };
    
    const cleanup = () => {
        confirmBtn.removeEventListener('click', handleConfirm);
        cancelBtn.removeEventListener('click', handleCancel);
    };
    
    confirmBtn.addEventListener('click', handleConfirm);
    cancelBtn.addEventListener('click', handleCancel);
}

// ============================================================================
// DATA FETCHING
// ============================================================================

async function fetchAgentStatus() {
    try {
        const response = await fetch('/api/agents/status');
        const data = await response.json();
        updateAgentCards(data.agents);
    } catch (error) {
        console.error('Error fetching agent status:', error);
    }
}

async function fetchLogs(agentName) {
    try {
        const response = await fetch(`/api/logs/${agentName}`);
        const data = await response.json();
        updateLogViewer(agentName, data.lines);
    } catch (error) {
        console.error('Error fetching logs:', error);
    }
}

async function fetchAlerts() {
    try {
        const response = await fetch('/api/alerts');
        const data = await response.json();
        updateAlerts(data.alerts);
    } catch (error) {
        console.error('Error fetching alerts:', error);
    }
}

async function fetchTradingOverview() {
    try {
        const response = await fetch('/api/trading/overview');
        const data = await response.json();
        updateTradingMetrics(data);
    } catch (error) {
        console.error('Error fetching trading overview:', error);
    }
}

async function fetchSystemInfo() {
    try {
        const response = await fetch('/api/system/info');
        const data = await response.json();
        updateSystemInfo(data);
    } catch (error) {
        console.error('Error fetching system info:', error);
    }
}

// ============================================================================
// UI UPDATE FUNCTIONS
// ============================================================================

function updateAgentCards(agents) {
    const container = document.getElementById('agents-container');
    
    if (!agents || agents.length === 0) {
        container.innerHTML = '<div class="loading">No agents found</div>';
        return;
    }
    
    container.innerHTML = '';
    
    agents.forEach(agent => {
        const card = document.createElement('div');
        card.className = 'agent-card';
        
        const statusClass = agent.running ? 'running' : 'stopped';
        const uptimeText = agent.running ? formatUptime(agent.uptime_seconds) : 'Stopped';
        
        card.innerHTML = `
            <div class="agent-header">
                <span class="agent-name" onclick="viewLogs('${agent.name}')">${agent.name}</span>
                <span class="status-badge ${statusClass}"></span>
            </div>
            <div class="agent-description">${agent.description}</div>
            <div class="agent-info">
                ${agent.running ? `PID: ${agent.pid} | Uptime: ${uptimeText}` : 'Not running'}
            </div>
            <div class="agent-buttons">
                <button class="btn btn-start" onclick="startAgent('${agent.name}')" 
                        ${agent.running ? 'disabled' : ''}>
                    Start
                </button>
                <button class="btn btn-stop" onclick="stopAgent('${agent.name}')" 
                        ${!agent.running ? 'disabled' : ''}>
                    Stop
                </button>
            </div>
        `;
        
        container.appendChild(card);
    });
    
    // Update log tabs
    updateLogTabs(agents);
}

function updateLogTabs(agents) {
    const tabsContainer = document.getElementById('log-tabs');
    const runningAgents = agents.filter(a => a.running);
    
    if (runningAgents.length === 0) {
        tabsContainer.innerHTML = '<div style="color: var(--text-secondary);">No running agents</div>';
        return;
    }
    
    tabsContainer.innerHTML = '';
    
    runningAgents.forEach(agent => {
        const tab = document.createElement('div');
        tab.className = 'log-tab';
        if (agent.name === currentLogAgent) {
            tab.classList.add('active');
        }
        tab.textContent = agent.name;
        tab.onclick = () => viewLogs(agent.name);
        tabsContainer.appendChild(tab);
    });
}

function updateLogViewer(agentName, lines) {
    const content = document.getElementById('log-content');
    
    if (!lines || lines.length === 0) {
        content.innerHTML = '<div class="log-placeholder">No logs available</div>';
        return;
    }
    
    content.innerHTML = '';
    
    lines.forEach(line => {
        const div = document.createElement('div');
        div.className = 'log-line';
        div.textContent = line;
        content.appendChild(div);
    });
    
    // Auto-scroll to bottom
    content.scrollTop = content.scrollHeight;
}

function updateAlerts(alerts) {
    const container = document.getElementById('alerts-container');
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = '<div class="no-alerts">No recent alerts</div>';
        return;
    }
    
    container.innerHTML = '';
    
    alerts.forEach(alert => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert-item ${alert.type}`;
        
        alertDiv.innerHTML = `
            <div class="alert-header">
                <span class="alert-type">${alert.type}</span>
                <span class="alert-time">${formatTimestamp(alert.timestamp)}</span>
            </div>
            <div class="alert-message">${alert.message}</div>
        `;
        
        container.appendChild(alertDiv);
    });
}

function updateTradingMetrics(metrics) {
    document.getElementById('balance').textContent = 
        metrics.balance ? `$${metrics.balance.toFixed(2)}` : '$0.00';
    
    document.getElementById('positions').textContent = metrics.positions_count || '0';
    
    const pnlElement = document.getElementById('pnl');
    const pnl = metrics.pnl_today || 0;
    pnlElement.textContent = `$${pnl.toFixed(2)}`;
    pnlElement.className = 'metric-value ' + (pnl >= 0 ? 'positive' : 'negative');
    
    document.getElementById('risk-status').textContent = metrics.risk_status || 'Unknown';
}

function updateSystemInfo(info) {
    document.getElementById('python-version').textContent = info.python_version || '-';
    document.getElementById('system-uptime').textContent = 
        info.uptime_seconds ? formatUptime(info.uptime_seconds) : '-';
    document.getElementById('active-agents').textContent = 
        `${info.running_agents || 0} / ${info.active_agents || 0}`;
    document.getElementById('exchange').textContent = info.exchange || '-';
}

// ============================================================================
// AGENT CONTROL FUNCTIONS
// ============================================================================

async function startAgent(agentName) {
    try {
        const response = await fetch(`/api/agents/${agentName}/start`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showNotification(`Started ${agentName}`, 'success');
            fetchAgentStatus();
        } else {
            showNotification(`Failed to start ${agentName}: ${data.message}`, 'error');
        }
    } catch (error) {
        showNotification(`Error starting ${agentName}`, 'error');
        console.error('Error:', error);
    }
}

async function stopAgent(agentName) {
    showConfirmModal(
        'Stop Agent',
        `Are you sure you want to stop ${agentName}?`,
        async () => {
            try {
                const response = await fetch(`/api/agents/${agentName}/stop`, {
                    method: 'POST'
                });
                const data = await response.json();
                
                if (data.success) {
                    showNotification(`Stopped ${agentName}`, 'success');
                    fetchAgentStatus();
                } else {
                    showNotification(`Failed to stop ${agentName}: ${data.message}`, 'error');
                }
            } catch (error) {
                showNotification(`Error stopping ${agentName}`, 'error');
                console.error('Error:', error);
            }
        }
    );
}

async function startAllAgents() {
    showConfirmModal(
        'Start All Enabled Agents',
        'This will start all agents that are marked as enabled. Continue?',
        async () => {
            try {
                const response = await fetch('/api/agents/start-all', {
                    method: 'POST'
                });
                const data = await response.json();
                
                showNotification(data.message, data.success ? 'success' : 'error');
                fetchAgentStatus();
            } catch (error) {
                showNotification('Error starting all agents', 'error');
                console.error('Error:', error);
            }
        }
    );
}

async function stopAllAgents() {
    showConfirmModal(
        'Stop All Agents',
        '⚠️ This will stop ALL running agents! Are you sure?',
        async () => {
            try {
                const response = await fetch('/api/agents/stop-all', {
                    method: 'POST'
                });
                const data = await response.json();
                
                showNotification(data.message, data.success ? 'success' : 'error');
                fetchAgentStatus();
            } catch (error) {
                showNotification('Error stopping all agents', 'error');
                console.error('Error:', error);
            }
        }
    );
}

function viewLogs(agentName) {
    currentLogAgent = agentName;
    fetchLogs(agentName);
    
    // Update tab active state
    document.querySelectorAll('.log-tab').forEach(tab => {
        if (tab.textContent === agentName) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
}

function refreshAll() {
    showNotification('Refreshing all data...', 'info');
    fetchAgentStatus();
    if (currentLogAgent) {
        fetchLogs(currentLogAgent);
    }
    fetchAlerts();
    fetchTradingOverview();
    fetchSystemInfo();
}

// ============================================================================
// SOUND SETTINGS
// ============================================================================

async function loadSoundSettings() {
    try {
        const response = await fetch('/api/settings/mp3-sounds');
        const data = await response.json();
        const toggle = document.getElementById('sound-toggle');
        if (toggle) {
            toggle.checked = data.enabled;
        }
    } catch (error) {
        console.error('Error loading sound settings:', error);
    }
}

async function toggleSounds() {
    const toggle = document.getElementById('sound-toggle');
    try {
        const response = await fetch('/api/settings/mp3-sounds/toggle', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            toggle.checked = data.enabled;
        } else {
            showNotification(data.message, 'error');
            // Revert toggle on error
            toggle.checked = !toggle.checked;
        }
    } catch (error) {
        showNotification('Error toggling sounds', 'error');
        console.error('Error:', error);
        // Revert toggle on error
        toggle.checked = !toggle.checked;
    }
}

// ============================================================================
// INITIALIZATION
// ============================================================================

function startPolling() {
    // Initial fetch
    fetchAgentStatus();
    fetchAlerts();
    fetchTradingOverview();
    fetchSystemInfo();
    
    // Set up intervals
    refreshIntervals.agents = setInterval(fetchAgentStatus, 3000);  // 3 seconds
    refreshIntervals.alerts = setInterval(fetchAlerts, 5000);       // 5 seconds
    refreshIntervals.trading = setInterval(fetchTradingOverview, 5000);  // 5 seconds
    refreshIntervals.system = setInterval(fetchSystemInfo, 10000);  // 10 seconds
    
    // Poll logs if viewing one
    refreshIntervals.logs = setInterval(() => {
        if (currentLogAgent) {
            fetchLogs(currentLogAgent);
        }
    }, 3000);  // 3 seconds
}

// Start when page loads
document.addEventListener('DOMContentLoaded', () => {
    console.log('🌙 Moon Dev Agent Control Center - Initializing...');
    loadSoundSettings();
    startPolling();
    console.log('✅ Dashboard ready!');
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    Object.values(refreshIntervals).forEach(interval => clearInterval(interval));
});
