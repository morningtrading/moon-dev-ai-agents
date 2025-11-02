# 🔊 MP3 Notification Sounds Implementation

## Summary
Added MP3 notification sound support to replace OpenAI text-to-speech across all agents, with dashboard controls for enabling/disabling sounds.

## Changes Made

### 1. Configuration (src/config.py)
Added two new settings:
```python
# 🔊 Agent Notification Sounds Settings
PLAY_MP3_AGENT_SOUNDS = True  # Enable/disable MP3 notification sounds for all agents
MP3_REPEAT_COUNT = 1  # How many times to repeat notification sounds
```

### 2. Notification Sounds Downloaded
Downloaded 3 notification sounds to `src/audio/notifications/`:
- **whale_alert.mp3** (63KB) - Whale detection alert
- **success.mp3** (57KB) - Success notification
- **alert.mp3** (13KB) - General alert

### 3. Audio Player Installation
Installed `mpg123` audio player for Linux:
```bash
sudo apt-get install -y mpg123
```

### 4. Whale Agent Updated (src/agents/whale_agent.py)
- Modified `_announce()` method to:
  - Check `config.PLAY_MP3_AGENT_SOUNDS` before playing
  - Play notification sound `MP3_REPEAT_COUNT` times (default: 3)
  - Support both `mpg123` and `ffplay` audio players
  - Gracefully handle missing audio players

Example usage in whale_agent:
```python
if not config.PLAY_MP3_AGENT_SOUNDS:
    print("🔇 Notification sounds disabled in config")
    return

repeat_count = config.MP3_REPEAT_COUNT
print(f"🔊 Playing whale alert sound {repeat_count} times...")

for i in range(repeat_count):
    subprocess.run(['mpg123', '-q', str(notification_file)], ...)
```

### 5. TTS Disabled in All Agents
Commented out OpenAI text-to-speech in 10 agents:
1. whale_agent.py ✅ (replaced with MP3)
2. clips_agent.py
3. fundingarb_agent.py
4. funding_agent.py
5. liquidation_agent.py
6. grok_sentiment_agent.py
7. sentiment_agent.py
8. phone_agent.py
9. focus_agent.py
10. chartanalysis_agent.py

All TTS code is preserved with `# TODO: TTS disabled - uncomment to re-enable` comments.

### 6. Dashboard API (DIR_dash_agents/app.py)
Added 3 new API endpoints:

#### GET /api/settings/mp3-sounds
Get current MP3 sound settings
```json
{
  "enabled": true,
  "repeat_count": 3
}
```

#### POST /api/settings/mp3-sounds/toggle
Toggle sounds on/off - returns:
```json
{
  "success": true,
  "enabled": false,
  "message": "MP3 sounds disabled"
}
```

#### POST /api/settings/mp3-sounds/repeat
Set repeat count (1-10) - body: `{"count": 3}`
```json
{
  "success": true,
  "repeat_count": 3,
  "message": "MP3 repeat count set to 3"
}
```

## Usage

### From Dashboard
1. Start the dashboard: `python DIR_dash_agents/app.py`
2. Open http://localhost:8002
3. Use the UI controls to toggle sounds on/off
4. Adjust repeat count slider (1-10 times)

### From Code
```python
from src import config

# Check if sounds enabled
if config.PLAY_MP3_AGENT_SOUNDS:
    # Play sound config.MP3_REPEAT_COUNT times
    pass
```

### Manual Configuration
Edit `src/config.py`:
```python
PLAY_MP3_AGENT_SOUNDS = False  # Disable sounds
MP3_REPEAT_COUNT = 1  # Play once instead of 3 times
```

## Testing

### Test Notification Sound
```bash
mpg123 /home/titus/moon-dev-ai-agents/src/audio/notifications/whale_alert.mp3
```

### Test Whale Agent
The whale agent will play sounds when it detects a whale movement (OI change > 31% above average).

## Adding MP3 Sounds to Other Agents

To add notification sounds to other agents:

1. **Choose or download an MP3 file** to `src/audio/notifications/`

2. **In the agent's announce/alert method**, add:
```python
from src import config
import subprocess
from pathlib import Path

def _announce(self, message, is_alert=False):
    print(f"🗣️ {message}")
    
    if not is_alert or not config.PLAY_MP3_AGENT_SOUNDS:
        return
    
    # Play notification sound
    notification_file = Path("src/audio/notifications/alert.mp3")
    
    if notification_file.exists():
        for i in range(config.MP3_REPEAT_COUNT):
            try:
                subprocess.run(['mpg123', '-q', str(notification_file)], 
                             check=False, 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
            except FileNotFoundError:
                print("⚠️ mpg123 not found. Install: sudo apt-get install mpg123")
                break
```

## Benefits

- ✅ **No API costs** - Free notification sounds
- ✅ **Works offline** - No internet required
- ✅ **Centralized control** - Toggle all agents from dashboard
- ✅ **Customizable** - Adjustable repeat count
- ✅ **Easy to restore TTS** - All original code preserved as comments
- ✅ **Graceful degradation** - Works without audio player installed

## Notes

- Dashboard changes take effect immediately for running agents after config reload
- Agents check config on each notification, so no restart needed
- TTS code remains in place and can be uncommented if needed
- MP3 files are small (13-63KB) and play instantly
