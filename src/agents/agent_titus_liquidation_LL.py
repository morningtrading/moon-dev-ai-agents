"""
🌊 Titus Liquidation Agent LL
Built with love by Moon Dev 🚀

A simplified liquidation analysis agent that sends liquidation data to AI
and gets trend analysis: BUY/SELL signal with strength rating.

Now with SWARM support - queries multiple AI models for consensus!

Based on Moon Dev's Liquidation Agent
"""

import os
import pandas as pd
import time
from datetime import datetime, timedelta
from termcolor import colored, cprint
from dotenv import load_dotenv
import openai
from pathlib import Path
import sys

# Add parent directory to path so we can import from src
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.api import MoonDevAPI
import traceback

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# ═══════════════════════════════════════════════════════════════════════════════
# 🎛️ CONFIGURATION - Adjust these settings as needed
# ═══════════════════════════════════════════════════════════════════════════════

# How often to check liquidations (in minutes)
CHECK_INTERVAL_MINUTES = 5

# Number of liquidation rows to fetch each time
LIQUIDATION_ROWS = 10000

# Enable/Disable Swarm Mode - Uses multiple AI models for consensus
USE_SWARM = True  # Set to True to use SwarmAgent, False for single AI

# Model Selection (only used if USE_SWARM is False)
# Options:
# - "deepseek-chat" (DeepSeek V3 - fast & cheap)
# - "deepseek-reasoner" (DeepSeek R1 - reasoning model)
# - "gpt-4" (OpenAI GPT-4)
# - "gpt-3.5-turbo" (OpenAI GPT-3.5)
AI_MODEL = "deepseek-chat"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

# AI Response Settings
AI_MAX_TOKENS = 200
AI_TEMPERATURE = 0.3

# ═══════════════════════════════════════════════════════════════════════════════
# 🤖 AI ANALYSIS PROMPT
# ═══════════════════════════════════════════════════════════════════════════════

TREND_ANALYSIS_PROMPT = """You are an expert crypto market analyst specializing in liquidation data analysis.

Analyze the following liquidation data and determine the market trend:

{liquidation_table}

ANALYSIS GUIDELINES:
- Large LONG liquidations indicate longs are being stopped out → often signals a SHORT trend or bearish pressure
- Large SHORT liquidations indicate shorts are being stopped out → often signals a LONG/BUY trend or bullish pressure
- Compare the ratio of long vs short liquidations across different timeframes
- Look at the trend progression from 4hr → 1hr → 15min to see if momentum is building

You MUST respond in EXACTLY this format (4 lines only):

Line 1: SIGNAL: [BUY or SELL or NEUTRAL]
Line 2: STRENGTH: [WEAK, MODERATE, STRONG, or VERY STRONG]
Line 3: CONFIDENCE: [0-100]%
Line 4: REASON: [One sentence explaining why]

Example response:
SIGNAL: BUY
STRENGTH: STRONG
CONFIDENCE: 75%
REASON: Short liquidations significantly exceed longs across all timeframes, indicating shorts are being squeezed.
"""


class TitusLiquidationAgent:
    """Titus Liquidation Analysis Agent 🌊"""
    
    def __init__(self):
        """Initialize the Titus Liquidation Agent"""
        print("\n" + "═" * 60)
        print("🌊 Titus Liquidation Agent LL Starting Up...")
        print("═" * 60)
        
        load_dotenv()
        
        # Initialize Swarm Agent if enabled
        self.swarm = None
        if USE_SWARM:
            try:
                from src.agents.swarm_agent import SwarmAgent
                self.swarm = SwarmAgent()
                print(f"🐝 Swarm Mode ENABLED - Using multiple AI models for consensus")
            except Exception as e:
                print(f"⚠️ Could not initialize SwarmAgent: {e}")
                print(f"📌 Falling back to single AI mode")
                self._init_ai_client()
        else:
            # Initialize single AI client
            self._init_ai_client()
        
        # Initialize Moon Dev API
        self.api = MoonDevAPI()
        
        print(f"✅ Agent initialized successfully!")
        print(f"📊 Fetching {LIQUIDATION_ROWS} liquidation events per cycle")
        print(f"⏱️ Check interval: {CHECK_INTERVAL_MINUTES} minutes")
        print("═" * 60 + "\n")
        
    def _init_ai_client(self):
        """Initialize the appropriate AI client"""
        if "deepseek" in AI_MODEL.lower():
            deepseek_key = os.getenv("DEEPSEEK_KEY")
            if not deepseek_key:
                raise ValueError("🚨 DEEPSEEK_KEY not found in environment variables!")
            self.client = openai.OpenAI(
                api_key=deepseek_key,
                base_url=DEEPSEEK_BASE_URL
            )
            self.client_type = "deepseek"
            print(f"🚀 Using DeepSeek model: {AI_MODEL}")
        else:
            openai_key = os.getenv("OPENAI_KEY")
            if not openai_key:
                raise ValueError("🚨 OPENAI_KEY not found in environment variables!")
            self.client = openai.OpenAI(api_key=openai_key)
            self.client_type = "openai"
            print(f"🤖 Using OpenAI model: {AI_MODEL}")
            
    def _get_liquidation_data(self):
        """Fetch and process liquidation data"""
        try:
            print("\n🔍 Fetching fresh liquidation data...")
            df = self.api.get_liquidation_data(limit=LIQUIDATION_ROWS)
            
            if df is None or df.empty:
                print("❌ No liquidation data received")
                return None
                
            # Convert timestamp to datetime
            if 'order_trade_time' in df.columns:
                df['datetime'] = pd.to_datetime(df['order_trade_time'], unit='ms')
            elif 'datetime' not in df.columns:
                print("❌ No timestamp column found")
                return None
                
            # Find USD value column
            if 'usd_size' in df.columns:
                usd_col = 'usd_size'
            elif 'usd_value' in df.columns:
                usd_col = 'usd_value'
            else:
                print(f"❌ No USD column found. Columns: {df.columns.tolist()}")
                return None
                
            df[usd_col] = pd.to_numeric(df[usd_col], errors='coerce')
            
            current_time = datetime.utcnow()
            
            # Calculate time windows
            fifteen_min = current_time - timedelta(minutes=15)
            one_hour = current_time - timedelta(hours=1)
            four_hours = current_time - timedelta(hours=4)
            
            # Separate long and short liquidations
            longs = df[df['side'] == 'SELL']  # SELL side = long liquidation
            shorts = df[df['side'] == 'BUY']   # BUY side = short liquidation
            
            # Calculate totals for each time window
            data = {
                '15min_longs': longs[longs['datetime'] >= fifteen_min][usd_col].sum(),
                '15min_shorts': shorts[shorts['datetime'] >= fifteen_min][usd_col].sum(),
                '15min_long_events': len(longs[longs['datetime'] >= fifteen_min]),
                '15min_short_events': len(shorts[shorts['datetime'] >= fifteen_min]),
                '1hr_longs': longs[longs['datetime'] >= one_hour][usd_col].sum(),
                '1hr_shorts': shorts[shorts['datetime'] >= one_hour][usd_col].sum(),
                '1hr_long_events': len(longs[longs['datetime'] >= one_hour]),
                '1hr_short_events': len(shorts[shorts['datetime'] >= one_hour]),
                '4hr_longs': longs[longs['datetime'] >= four_hours][usd_col].sum(),
                '4hr_shorts': shorts[shorts['datetime'] >= four_hours][usd_col].sum(),
                '4hr_long_events': len(longs[longs['datetime'] >= four_hours]),
                '4hr_short_events': len(shorts[shorts['datetime'] >= four_hours]),
            }
            
            return data
            
        except Exception as e:
            print(f"❌ Error fetching liquidation data: {str(e)}")
            traceback.print_exc()
            return None
            
    def _format_liquidation_table(self, data):
        """Format liquidation data into a nice table string"""
        table = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                🌙 Moon Dev's Liquidation Party 💦                    ║
╠══════════════════════════════════════════════════════════════════════╣
║  Last 15min LONGS:  ${data['15min_longs']:>12,.2f} ({data['15min_long_events']:>4} events)              ║
║  Last 15min SHORTS: ${data['15min_shorts']:>12,.2f} ({data['15min_short_events']:>4} events)              ║
║  Last 1hr LONGS:    ${data['1hr_longs']:>12,.2f} ({data['1hr_long_events']:>4} events)              ║
║  Last 1hr SHORTS:   ${data['1hr_shorts']:>12,.2f} ({data['1hr_short_events']:>4} events)              ║
║  Last 4hrs LONGS:   ${data['4hr_longs']:>12,.2f} ({data['4hr_long_events']:>4} events)              ║
║  Last 4hrs SHORTS:  ${data['4hr_shorts']:>12,.2f} ({data['4hr_short_events']:>4} events)              ║
╚══════════════════════════════════════════════════════════════════════╝
"""
        return table
        
    def _analyze_with_ai(self, liquidation_table):
        """Send liquidation data to AI and get trend analysis"""
        try:
            prompt = TREND_ANALYSIS_PROMPT.format(liquidation_table=liquidation_table)
            
            # Use Swarm if available
            if self.swarm:
                print("\n🐝 Sending data to AI SWARM for multi-model analysis...")
                
                system_prompt = "You are an expert crypto market analyst specializing in liquidation data. Always respond in the exact format requested."
                
                # Query the swarm
                swarm_result = self.swarm.query(prompt, system_prompt)
                
                # Display consensus summary
                if swarm_result.get("consensus_summary"):
                    print("\n" + "═" * 60)
                    cprint("🧠 SWARM CONSENSUS SUMMARY", "magenta", attrs=['bold'])
                    print("═" * 60)
                    cprint(swarm_result["consensus_summary"], "white")
                    print("═" * 60)
                
                # Parse individual responses to find the most common signal
                return self._parse_swarm_responses(swarm_result)
            else:
                # Single AI mode
                print("\n🤖 Sending data to AI for analysis...")
                
                response = self.client.chat.completions.create(
                    model=AI_MODEL,
                    messages=[
                        {"role": "system", "content": "You are an expert crypto market analyst. Always respond in the exact format requested."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=AI_MAX_TOKENS,
                    temperature=AI_TEMPERATURE
                )
                
                response_text = response.choices[0].message.content.strip()
                return self._parse_ai_response(response_text)
            
        except Exception as e:
            print(f"❌ Error in AI analysis: {str(e)}")
            traceback.print_exc()
            return None
    
    def _parse_swarm_responses(self, swarm_result):
        """Parse swarm responses and find consensus signal"""
        try:
            signals = []
            strengths = []
            confidences = []
            reasons = []
            individual_results = []  # Store each AI's result
            
            # Parse each successful response
            for provider, data in swarm_result.get("responses", {}).items():
                if data.get("success") and data.get("response"):
                    parsed = self._parse_ai_response(data["response"])
                    if parsed and parsed.get("signal") in ["BUY", "SELL", "NEUTRAL"]:
                        signals.append(parsed["signal"])
                        strengths.append(parsed.get("strength", "UNKNOWN"))
                        confidences.append(parsed.get("confidence", 50))
                        reasons.append(f"{provider}: {parsed.get('reason', 'No reason')}")
                        
                        # Store individual result for display
                        individual_results.append({
                            'provider': provider.upper(),
                            'signal': parsed["signal"],
                            'strength': parsed.get("strength", "UNKNOWN"),
                            'confidence': parsed.get("confidence", 50),
                            'reason': parsed.get("reason", "No reason")
                        })
            
            if not signals:
                return {
                    'signal': 'NEUTRAL',
                    'strength': 'UNKNOWN',
                    'confidence': 50,
                    'reason': 'No valid responses from swarm',
                    'swarm_consensus': swarm_result.get("consensus_summary", ""),
                    'individual_results': []
                }
            
            # Find majority signal
            from collections import Counter
            signal_counts = Counter(signals)
            majority_signal = signal_counts.most_common(1)[0][0]
            signal_agreement = signal_counts[majority_signal] / len(signals) * 100
            
            # Calculate confidence based on ONLY the winning signal's AIs
            # Then weight by agreement percentage
            winning_confidences = []
            winning_strengths = []
            for i, sig in enumerate(signals):
                if sig == majority_signal:
                    winning_confidences.append(confidences[i])
                    winning_strengths.append(strengths[i])
            
            # Average confidence of winning AIs, weighted by agreement
            avg_winning_confidence = sum(winning_confidences) / len(winning_confidences) if winning_confidences else 50
            weighted_confidence = int((signal_agreement / 100) * avg_winning_confidence)
            
            # Most common strength among winning AIs
            strength_counts = Counter(winning_strengths)
            majority_strength = strength_counts.most_common(1)[0][0] if winning_strengths else "UNKNOWN"
            
            return {
                'signal': majority_signal,
                'strength': majority_strength,
                'confidence': weighted_confidence,
                'reason': f"Swarm consensus ({signal_agreement:.0f}% agreement)",
                'swarm_consensus': swarm_result.get("consensus_summary", ""),
                'individual_signals': dict(signal_counts),
                'model_count': len(signals),
                'individual_results': individual_results  # Add individual results
            }
            
        except Exception as e:
            print(f"❌ Error parsing swarm responses: {str(e)}")
            traceback.print_exc()
            return None
            
    def _parse_ai_response(self, response_text):
        """Parse the AI response into structured data"""
        try:
            lines = [line.strip() for line in response_text.split('\n') if line.strip()]
            
            result = {
                'signal': 'NEUTRAL',
                'strength': 'UNKNOWN',
                'confidence': 50,
                'reason': 'Could not parse AI response',
                'raw_response': response_text
            }
            
            for line in lines:
                line_upper = line.upper()
                if line_upper.startswith('SIGNAL:'):
                    signal = line.split(':', 1)[1].strip().upper()
                    if signal in ['BUY', 'SELL', 'NEUTRAL']:
                        result['signal'] = signal
                elif line_upper.startswith('STRENGTH:'):
                    result['strength'] = line.split(':', 1)[1].strip().upper()
                elif line_upper.startswith('CONFIDENCE:'):
                    conf_str = line.split(':', 1)[1].strip()
                    # Extract number from string like "75%" or "75"
                    import re
                    match = re.search(r'(\d+)', conf_str)
                    if match:
                        result['confidence'] = int(match.group(1))
                elif line_upper.startswith('REASON:'):
                    result['reason'] = line.split(':', 1)[1].strip()
                    
            return result
            
        except Exception as e:
            print(f"❌ Error parsing AI response: {str(e)}")
            return {
                'signal': 'NEUTRAL',
                'strength': 'UNKNOWN',
                'confidence': 50,
                'reason': f'Parse error: {str(e)}',
                'raw_response': response_text
            }
            
    def _display_analysis(self, data, analysis):
        """Display the liquidation data and AI analysis"""
        # Display liquidation table
        table = self._format_liquidation_table(data)
        print(table)
        
        # Display AI analysis
        if analysis:
            # Color code based on signal
            if analysis['signal'] == 'BUY':
                signal_color = 'green'
                emoji = '🟢'
            elif analysis['signal'] == 'SELL':
                signal_color = 'red'
                emoji = '🔴'
            else:
                signal_color = 'yellow'
                emoji = '🟡'
            
            # Check if this is a swarm result
            is_swarm = 'swarm_consensus' in analysis or 'individual_signals' in analysis
            
            # Show individual AI results first if swarm
            if is_swarm and 'individual_results' in analysis and analysis['individual_results']:
                print("\n" + "╔" + "═" * 60 + "╗")
                print("║" + "       🤖 INDIVIDUAL AI RESPONSES 🤖       ".center(60) + "║")
                print("╠" + "═" * 60 + "╣")
                
                for result in analysis['individual_results']:
                    # Get emoji for this AI's signal
                    if result['signal'] == 'BUY':
                        ai_emoji = '🟢'
                    elif result['signal'] == 'SELL':
                        ai_emoji = '🔴'
                    else:
                        ai_emoji = '🟡'
                    
                    ai_line = f"  {ai_emoji} {result['provider']}: {result['signal']} ({result['strength']}) {result['confidence']}%"
                    print(f"║{ai_line:<59}║")
                
                print("╚" + "═" * 60 + "╝")
            
            print("\n" + "╔" + "═" * 60 + "╗")
            if is_swarm:
                print("║" + "       🐝 SWARM AI TREND ANALYSIS 🐝       ".center(60) + "║")
            else:
                print("║" + "          🤖 AI TREND ANALYSIS 🤖          ".center(60) + "║")
            print("╠" + "═" * 60 + "╣")
            
            signal_line = f"  {emoji} SIGNAL: {analysis['signal']}"
            print(f"║{signal_line:<59}║")
            
            strength_line = f"  💪 STRENGTH: {analysis['strength']}"
            print(f"║{strength_line:<59}║")
            
            confidence_line = f"  📊 CONFIDENCE: {analysis['confidence']}%"
            print(f"║{confidence_line:<59}║")
            
            # Show swarm-specific info
            if is_swarm and 'individual_signals' in analysis:
                print("╠" + "═" * 60 + "╣")
                models_line = f"  🤖 MODELS QUERIED: {analysis.get('model_count', 'N/A')}"
                print(f"║{models_line:<59}║")
                
                signals = analysis.get('individual_signals', {})
                votes_line = f"  📊 VOTES: BUY={signals.get('BUY', 0)} | SELL={signals.get('SELL', 0)} | NEUTRAL={signals.get('NEUTRAL', 0)}"
                print(f"║{votes_line:<59}║")
            
            print("╠" + "═" * 60 + "╣")
            
            # Wrap reason text
            reason = analysis['reason']
            reason_lines = [reason[i:i+56] for i in range(0, len(reason), 56)]
            for line in reason_lines:
                print(f"║  {line:<57}║")
                
            print("╚" + "═" * 60 + "╝")
            
            # Also print with color to terminal
            if is_swarm:
                cprint(f"\n🐝 SWARM: {emoji} {analysis['signal']} | Strength: {analysis['strength']} | Confidence: {analysis['confidence']}%", 
                       signal_color, attrs=['bold'])
            else:
                cprint(f"\n{emoji} {analysis['signal']} | Strength: {analysis['strength']} | Confidence: {analysis['confidence']}%", 
                       signal_color, attrs=['bold'])
        else:
            print("\n⚠️ Could not get AI analysis")
            
    def run_cycle(self):
        """Run one analysis cycle"""
        try:
            # Get liquidation data
            data = self._get_liquidation_data()
            
            if data is None:
                print("❌ Could not fetch liquidation data")
                return
                
            # Format table for AI
            table = self._format_liquidation_table(data)
            
            # Get AI analysis
            analysis = self._analyze_with_ai(table)
            
            # Display results
            self._display_analysis(data, analysis)
            
        except Exception as e:
            print(f"❌ Error in analysis cycle: {str(e)}")
            traceback.print_exc()
            
    def run(self):
        """Run the agent continuously"""
        print("\n🌊 Starting Titus Liquidation Agent...\n")
        
        while True:
            try:
                self.run_cycle()
                
                print(f"\n💤 Sleeping for {CHECK_INTERVAL_MINUTES} minutes...")
                print(f"⏰ Next check at: {(datetime.now() + timedelta(minutes=CHECK_INTERVAL_MINUTES)).strftime('%H:%M:%S')}")
                time.sleep(CHECK_INTERVAL_MINUTES * 60)
                
            except KeyboardInterrupt:
                print("\n\n👋 Titus Liquidation Agent shutting down gracefully...")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {str(e)}")
                traceback.print_exc()
                time.sleep(60)


if __name__ == "__main__":
    agent = TitusLiquidationAgent()
    agent.run()
