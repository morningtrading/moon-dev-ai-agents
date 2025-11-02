#!/usr/bin/env python3
"""
🌙 Moon Dev's Grok Sentiment Agent
Built with love by Moon Dev 🚀

Uses Grok's real-time X (Twitter) access to analyze crypto sentiment.
No scraping, no API limits, just pure AI-powered sentiment analysis!

Grok has built-in access to X posts and can analyze sentiment in real-time.
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from termcolor import colored, cprint
from dotenv import load_dotenv
import openai
import pandas as pd
import re

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.models.model_factory import model_factory
from src.agents.base_agent import BaseAgent
from src.config import HYPERLIQUID_SYMBOLS, TOKEN_NAMES

# Configuration
CHECK_INTERVAL_MINUTES = 15  # Check sentiment every 15 minutes

# 🌙 Tokens to track - imported from centralized config
# This ensures all agents (trading, sentiment, funding, whale, liquidation) track the same coins
TOKENS_TO_TRACK = TOKEN_NAMES  # Uses the master coin list from config.py

# Sentiment thresholds for alerts
SENTIMENT_EXTREME_THRESHOLD = 0.6  # Alert if abs(sentiment) > 0.6
SENTIMENT_VERY_EXTREME_THRESHOLD = 0.8  # Very strong alert

# Voice settings
VOICE_MODEL = "tts-1"
VOICE_NAME = "nova"  # Options: alloy, echo, fable, onyx, nova, shimmer
VOICE_SPEED = 1.0

# Grok Sentiment Analysis Prompt
GROK_SENTIMENT_PROMPT = """You have real-time access to X (Twitter). Analyze current sentiment for {token_name} ({token_symbol}).

Your task:
1. Look at recent X posts about {token_name}
2. Analyze the overall sentiment and emotion
3. Consider: FOMO, FUD, panic, euphoria, neutral discussion

Respond ONLY with valid JSON (no markdown, no explanation):
{{
    "sentiment_score": <float between -1.0 and 1.0>,
    "reasoning": "<1-2 sentence explanation>",
    "confidence": <integer 0-100>,
    "market_mood": "<one word: fear/greed/neutral/panic/euphoria>",
    "volume": "<high/medium/low based on post frequency>"
}}

Scale:
-1.0 = Extreme Fear/Panic (everyone selling, FUD everywhere)
-0.6 = Strong Fear (mostly negative posts)
-0.3 = Mild Fear (somewhat negative)
 0.0 = Neutral (balanced or quiet)
+0.3 = Mild Greed (somewhat positive)
+0.6 = Strong Greed (mostly bullish posts)
+1.0 = Extreme Greed/Euphoria (FOMO, "moon" everywhere)

IMPORTANT: Return ONLY the JSON object, nothing else."""

class GrokSentimentAgent(BaseAgent):
    """Grok-powered sentiment analyzer using real-time X data"""
    
    def __init__(self):
        """Initialize Grok Sentiment Agent"""
        super().__init__('grok_sentiment')
        
        load_dotenv()
        
        # Initialize Grok
        try:
            self.grok = model_factory.get_model("xai", "grok-2-latest")
            if not self.grok:
                raise ValueError("Failed to initialize Grok model")
            cprint("✅ Grok model initialized with X access!", "green")
        except Exception as e:
            cprint(f"❌ Error initializing Grok: {e}", "red")
            raise
        
        # Initialize OpenAI for voice
        openai_key = os.getenv("OPENAI_KEY")
        if not openai_key:
            cprint("⚠️ OPENAI_KEY not found - voice alerts disabled", "yellow")
            self.voice_enabled = False
        else:
            openai.api_key = openai_key
            self.voice_enabled = True
        
        # Create directories
        self.audio_dir = project_root / "src" / "audio"
        self.data_dir = project_root / "src" / "data" / "grok_sentiment"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize history file
        self.history_file = self.data_dir / "sentiment_history.csv"
        self.load_history()
        
        cprint("🤖 Grok Sentiment Agent initialized!", "cyan", attrs=['bold'])
        cprint(f"📊 Tracking: {', '.join(TOKENS_TO_TRACK.keys())}", "cyan")
        cprint(f"⏰ Check interval: {CHECK_INTERVAL_MINUTES} minutes", "cyan")
        
    def load_history(self):
        """Load or create sentiment history"""
        if self.history_file.exists():
            self.history = pd.read_csv(self.history_file)
            self.history['timestamp'] = pd.to_datetime(self.history['timestamp'])
            
            # Keep only last 7 days
            cutoff = datetime.now() - timedelta(days=7)
            self.history = self.history[self.history['timestamp'] > cutoff]
            
            cprint(f"📈 Loaded {len(self.history)} historical sentiment records", "green")
        else:
            self.history = pd.DataFrame(columns=[
                'timestamp', 'token', 'sentiment_score', 'reasoning', 
                'confidence', 'market_mood', 'volume'
            ])
            cprint("📝 Created new sentiment history", "yellow")
    
    def save_history(self):
        """Save sentiment history to CSV"""
        try:
            self.history.to_csv(self.history_file, index=False)
        except Exception as e:
            cprint(f"❌ Error saving history: {e}", "red")
    
    def analyze_token_sentiment(self, token_symbol, token_name):
        """Get sentiment for a specific token using Grok"""
        try:
            cprint(f"\n🔍 Analyzing {token_name} ({token_symbol}) sentiment with Grok...", "cyan")
            
            prompt = GROK_SENTIMENT_PROMPT.format(
                token_name=token_name,
                token_symbol=token_symbol
            )
            
            response = self.grok.generate_response(
                system_prompt="You are a crypto sentiment analyst with real-time X access. Respond with JSON only.",
                user_content=prompt,
                temperature=0.3,  # Lower temperature for more consistent JSON
                max_tokens=200
            )
            
            # Extract JSON from response
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Try to parse JSON
            try:
                # Remove markdown code blocks if present
                response_text = re.sub(r'```json\s*|\s*```', '', response_text)
                response_text = response_text.strip()
                
                sentiment_data = json.loads(response_text)
                
                # Validate required fields
                required_fields = ['sentiment_score', 'reasoning', 'confidence', 'market_mood']
                if not all(field in sentiment_data for field in required_fields):
                    raise ValueError(f"Missing required fields in response")
                
                # Clamp sentiment score to valid range
                sentiment_data['sentiment_score'] = max(-1.0, min(1.0, float(sentiment_data['sentiment_score'])))
                sentiment_data['confidence'] = max(0, min(100, int(sentiment_data['confidence'])))
                
                return sentiment_data
                
            except json.JSONDecodeError as e:
                cprint(f"❌ Failed to parse JSON response: {e}", "red")
                cprint(f"Response was: {response_text[:200]}", "yellow")
                return None
                
        except Exception as e:
            cprint(f"❌ Error analyzing {token_symbol}: {e}", "red")
            return None
    
    def format_sentiment_display(self, token, data):
        """Format sentiment data for display"""
        score = data['sentiment_score']
        mood = data['market_mood'].upper()
        confidence = data['confidence']
        reasoning = data['reasoning']
        volume = data.get('volume', 'unknown').upper()
        
        # Determine color based on sentiment
        if score > 0.6:
            color = "red"
            emoji = "🔥"
            label = "EXTREME GREED"
        elif score > 0.3:
            color = "yellow"
            emoji = "📈"
            label = "BULLISH"
        elif score > -0.3:
            color = "white"
            emoji = "😴"
            label = "NEUTRAL"
        elif score > -0.6:
            color = "cyan"
            emoji = "📉"
            label = "BEARISH"
        else:
            color = "green"
            emoji = "💚"
            label = "EXTREME FEAR"
        
        print("\n" + "═" * 70)
        cprint(f"  {emoji} {token} SENTIMENT: {label} {emoji}", color, attrs=['bold'])
        print("═" * 70)
        cprint(f"  Score: {score:+.2f} | Mood: {mood} | Volume: {volume}", "white")
        cprint(f"  Confidence: {confidence}%", "white")
        cprint(f"  {reasoning}", color)
        print("═" * 70)
        
        return score, mood
    
    def check_for_alert(self, token, score, mood, reasoning):
        """Check if sentiment warrants an alert"""
        abs_score = abs(score)
        
        if abs_score >= SENTIMENT_VERY_EXTREME_THRESHOLD:
            # Very extreme sentiment
            if score > 0:
                message = (f"ayo moon dev seven seven seven! "
                          f"EXTREME GREED detected on {token}! "
                          f"Sentiment score {score:.2f}. "
                          f"{reasoning} "
                          f"Everyone is euphoric - potential top!")
            else:
                message = (f"ayo moon dev seven seven seven! "
                          f"EXTREME FEAR detected on {token}! "
                          f"Sentiment score {score:.2f}. "
                          f"{reasoning} "
                          f"Everyone is panicking - potential bottom!")
            
            self.announce(message, important=True)
            return True
            
        elif abs_score >= SENTIMENT_EXTREME_THRESHOLD:
            # Extreme sentiment
            if score > 0:
                message = f"{token} showing strong greed. Sentiment {score:.2f}. {reasoning}"
            else:
                message = f"{token} showing strong fear. Sentiment {score:.2f}. {reasoning}"
            
            self.announce(message, important=False)
            return True
        
        return False
    
    def announce(self, message, important=False):
        """Announce via text and optionally voice"""
        # TODO: TTS disabled - uncomment to re-enable OpenAI voice generation
        cprint(f"\n🗣️ {message}", "yellow", attrs=['bold'])
        
        # Play MP3 notification sound for important messages
        if important:
            try:
                from src import config
                import subprocess
                from pathlib import Path
                
                if not config.PLAY_MP3_AGENT_SOUNDS:
                    return
                
                notification_file = Path("src/audio/notifications/alert.mp3")
                if notification_file.exists():
                    for i in range(config.MP3_REPEAT_COUNT):
                        subprocess.run(['mpg123', '-q', str(notification_file)], 
                                     check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                pass
        return
        
        # if not self.voice_enabled or not important:
        #     return
        # 
        # try:
        #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        #     audio_file = self.audio_dir / f"grok_sentiment_{timestamp}.mp3"
        #     
        #     response = openai.audio.speech.create(
        #         model=VOICE_MODEL,
        #         voice=VOICE_NAME,
        #         speed=VOICE_SPEED,
        #         input=message
        #     )
        #     
        #     response.stream_to_file(audio_file)
        #     
        #     # Play audio
        #     os.system(f"afplay {audio_file} 2>/dev/null || aplay {audio_file} 2>/dev/null")
        #     
        #     # Clean up after playing
        #     time.sleep(1)
        #     audio_file.unlink(missing_ok=True)
        #     
        # except Exception as e:
        #     cprint(f"⚠️ Voice alert failed: {e}", "yellow")
    
    def save_sentiment(self, token, data):
        """Save sentiment data to history"""
        try:
            new_row = pd.DataFrame([{
                'timestamp': datetime.now(),
                'token': token,
                'sentiment_score': data['sentiment_score'],
                'reasoning': data['reasoning'],
                'confidence': data['confidence'],
                'market_mood': data['market_mood'],
                'volume': data.get('volume', 'unknown')
            }])
            
            self.history = pd.concat([self.history, new_row], ignore_index=True)
            self.save_history()
            
        except Exception as e:
            cprint(f"❌ Error saving sentiment: {e}", "red")
    
    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        print("\n" + "="*70)
        cprint("🤖 Grok Sentiment Analysis Cycle", "cyan", attrs=['bold'])
        print("="*70)
        
        for token_symbol, token_name in TOKENS_TO_TRACK.items():
            sentiment_data = self.analyze_token_sentiment(token_symbol, token_name)
            
            if sentiment_data:
                score, mood = self.format_sentiment_display(token_symbol, sentiment_data)
                self.check_for_alert(token_symbol, score, mood, sentiment_data['reasoning'])
                self.save_sentiment(token_symbol, sentiment_data)
            else:
                cprint(f"⚠️ Failed to get sentiment for {token_symbol}", "yellow")
            
            # Small delay between tokens to avoid rate limits
            time.sleep(2)
    
    def run(self):
        """Run continuous monitoring"""
        cprint("\n🚀 Starting Grok Sentiment Monitoring...\n", "green", attrs=['bold'])
        
        while True:
            try:
                self.run_monitoring_cycle()
                
                next_run = datetime.now() + timedelta(minutes=CHECK_INTERVAL_MINUTES)
                cprint(f"\n😴 Sleeping until {next_run.strftime('%H:%M:%S')}", "cyan")
                time.sleep(CHECK_INTERVAL_MINUTES * 60)
                
            except KeyboardInterrupt:
                cprint("\n👋 Grok Sentiment Agent shutting down...", "yellow")
                break
            except Exception as e:
                cprint(f"\n❌ Error in monitoring cycle: {e}", "red")
                time.sleep(60)

if __name__ == "__main__":
    agent = GrokSentimentAgent()
    agent.run()
