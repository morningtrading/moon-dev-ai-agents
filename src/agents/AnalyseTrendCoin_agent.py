#!/usr/bin/env python3
"""
🌙 Moon Dev's Analyse Trend Coin Agent 🔥

Uses AI Swarm (6+ models) to analyze trending coins with multi-model consensus.
- Technical Analysis from swarm
- Fundamental Analysis from swarm
- Consensus recommendations
- Individual model votes saved

Better than dual-agent with diverse AI perspectives!
"""

import os
import sys
import pandas as pd
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time
from pathlib import Path
from termcolor import colored, cprint
from dotenv import load_dotenv
import requests
import numpy as np
import concurrent.futures

# Add project root to path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

# Import SwarmAgent
from src.agents.swarm_agent import SwarmAgent

# Load environment variables
load_dotenv()

# 🤖 CoinGecko API Settings
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# 📁 File Paths
TREND_FILE = Path("src/data/trending_coins.csv")
FALLBACK_FILE = Path("src/data/discovered_tokens.csv")
TOKENS_FILE = TREND_FILE if TREND_FILE.exists() else FALLBACK_FILE
ANALYSIS_FILE = Path("src/data/trend_swarm_analysis.csv")
DETAILED_FILE = Path("src/data/trend_swarm_detailed.json")

# ⚙️ Configuration
HOURS_BETWEEN_RUNS = 24
PARALLEL_PROCESSES = 50
MIN_VOLUME_USD = 100_000
MAX_MARKET_CAP = 1000_000_000

# 🤖 Analysis Prompts
TECHNICAL_ANALYSIS_PROMPT = """
Analyze this token from a TECHNICAL perspective:

📊 Token Information:
• Name: {name} ({symbol})
• Current Price: ${price:,.8f}
• 24h Volume: ${volume_24h:,.2f}
• Market Cap: ${market_cap:,.2f}

{ohlcv_data}

Provide a concise technical analysis focusing on:
1. Price momentum and trends
2. Volume patterns
3. Support/resistance levels (if OHLCV available)
4. Technical strength (0-100 score)
5. Trading opportunity assessment

IMPORTANT: End with one of these:
RECOMMENDATION: BUY
RECOMMENDATION: SELL
RECOMMENDATION: DO NOTHING
"""

FUNDAMENTAL_ANALYSIS_PROMPT = """
Analyze this token from a FUNDAMENTAL perspective:

📊 Token Information:
• Name: {name} ({symbol})
• Current Price: ${price:,.8f}
• 24h Volume: ${volume_24h:,.2f}
• Market Cap: ${market_cap:,.2f}

Provide a concise fundamental analysis focusing on:
1. Project viability and innovation
2. Market positioning and competitive advantage
3. Growth potential in current market conditions
4. Risk factors (regulatory, technical, market)
5. Fundamental strength (0-100 score)

IMPORTANT: End with one of these:
RECOMMENDATION: BUY
RECOMMENDATION: SELL
RECOMMENDATION: DO NOTHING
"""

class SwarmAnalyzer:
    """Analyzes tokens using AI Swarm consensus"""
    
    def __init__(self):
        print_banner()
        self.swarm = SwarmAgent()
        self.analysis_log = self._load_analysis_log()
        cprint("🔥 Moon Dev's Trend Coin Swarm Analyzer Ready! 🔥", "white", "on_green", attrs=["bold"])
        
    def _load_analysis_log(self) -> pd.DataFrame:
        """Load or create analysis log"""
        if ANALYSIS_FILE.exists():
            df = pd.read_csv(ANALYSIS_FILE)
            print(f"\n📈 Loaded analysis log with {len(df)} previous analyses")
            return df
        else:
            df = pd.DataFrame(columns=[
                'timestamp', 'token_id', 'symbol', 'name',
                'price', 'volume_24h', 'market_cap',
                'technical_consensus', 'fundamental_consensus',
                'technical_votes_buy', 'technical_votes_sell', 'technical_votes_nothing',
                'fundamental_votes_buy', 'fundamental_votes_sell', 'fundamental_votes_nothing',
                'overall_recommendation', 'confidence_score'
            ])
            df.to_csv(ANALYSIS_FILE, index=False)
            print("\n📝 Created new analysis log")
            return df
    
    def load_tokens(self) -> pd.DataFrame:
        """Load tokens from CSV"""
        if not TOKENS_FILE.exists():
            raise FileNotFoundError(f"❌ No tokens file found at {TOKENS_FILE}")
        
        df = pd.read_csv(TOKENS_FILE)
        print(f"\n📚 Loaded {len(df)} tokens from {TOKENS_FILE}")
        return df
    
    def get_ohlcv_data(self, token_id: str) -> str:
        """Get OHLCV data for the past 14 days"""
        try:
            url = f"{COINGECKO_BASE_URL}/coins/{token_id}/ohlc"
            params = {
                'vs_currency': 'usd',
                'days': '14',
                'x_cg_demo_api_key': COINGECKO_API_KEY if COINGECKO_API_KEY else ''
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                return "❌ OHLCV data not available"
            
            ohlcv_data = response.json()
            
            if not ohlcv_data or len(ohlcv_data) < 2:
                return "❌ No OHLCV data returned"
            
            # Format OHLCV data
            formatted = "📊 OHLCV Data (4h intervals, past 14 days):\n"
            formatted += "Timestamp | Open | High | Low | Close\n"
            formatted += "-" * 50 + "\n"
            
            try:
                for entry in ohlcv_data[-10:]:
                    timestamp = datetime.fromtimestamp(entry[0]/1000).strftime('%Y-%m-%d %H:%M')
                    formatted += f"{timestamp} | ${entry[1]:.8f} | ${entry[2]:.8f} | ${entry[3]:.8f} | ${entry[4]:.8f}\n"
                
                prices = np.array([float(entry[4]) for entry in ohlcv_data])
                stats = f"""
📈 Price Statistics:
• Highest: ${np.max(prices):,.8f}
• Lowest: ${np.min(prices):,.8f}
• Average: ${np.mean(prices):,.8f}
• Volatility: {np.std(prices)/np.mean(prices)*100:.2f}%
• Change: {((prices[-1]/prices[0])-1)*100:,.2f}% over period
"""
                return formatted + stats
            except:
                return "❌ Error processing OHLCV data"
                
        except Exception as e:
            return f"❌ Error fetching OHLCV: {str(e)}"
    
    def extract_recommendation(self, response: str) -> str:
        """Extract BUY/SELL/DO NOTHING from response"""
        if "BUY" in response.upper():
            return "BUY"
        elif "SELL" in response.upper():
            return "SELL"
        else:
            return "DO NOTHING"
    
    def count_recommendations(self, responses: Dict) -> tuple:
        """Count votes for each recommendation"""
        votes = {"BUY": 0, "SELL": 0, "DO NOTHING": 0}
        
        for provider, data in responses.items():
            if data.get("success"):
                rec = self.extract_recommendation(data.get("response", ""))
                votes[rec] += 1
        
        return votes["BUY"], votes["SELL"], votes["DO NOTHING"]
    
    def analyze_token(self, token_data: Dict):
        """Analyze a token using swarm consensus"""
        try:
            name = token_data.get('name', 'Unknown')
            symbol = token_data.get('symbol', 'UNKNOWN')
            token_id = token_data.get('token_id', '')
            
            try:
                volume = float(token_data.get('volume_24h', 0))
                price = float(token_data.get('price', 0))
                market_cap = float(token_data.get('market_cap', 0))
            except (TypeError, ValueError):
                return
            
            print(f"\n🔍 Analyzing: {name} ({symbol})")
            print(f"📊 24h Volume: ${volume:,.2f}")
            print(f"💰 Market Cap: ${market_cap:,.2f}")
            
            # Skip if market cap too high
            if market_cap > MAX_MARKET_CAP:
                print(f"⏭️ Skipping - Market cap above maximum (${MAX_MARKET_CAP:,.0f})")
                return
            
            # Skip if volume too low
            if volume < MIN_VOLUME_USD:
                print(f"⏭️ Skipping - Volume below minimum (${MIN_VOLUME_USD:,.2f})")
                return
            
            # Get OHLCV data
            ohlcv_data = self.get_ohlcv_data(token_id)
            
            # Technical Analysis from Swarm
            print("\n🤖 Querying Swarm for Technical Analysis...")
            tech_prompt = TECHNICAL_ANALYSIS_PROMPT.format(
                name=name, symbol=symbol, price=price,
                volume_24h=volume, market_cap=market_cap,
                ohlcv_data=ohlcv_data
            )
            
            tech_result = self.swarm.query(tech_prompt)
            tech_votes_buy, tech_votes_sell, tech_votes_nothing = self.count_recommendations(
                tech_result.get("responses", {})
            )
            tech_consensus = tech_result.get("consensus_summary", "No consensus")
            tech_rec = self.extract_recommendation(tech_consensus)
            
            print(f"📊 Technical Analysis:")
            print(f"   Votes: BUY={tech_votes_buy} | SELL={tech_votes_sell} | NOTHING={tech_votes_nothing}")
            print(f"   Consensus: {tech_rec}")
            cprint(f"   Summary: {tech_consensus[:200]}...", "green")
            
            # Fundamental Analysis from Swarm
            print("\n🤖 Querying Swarm for Fundamental Analysis...")
            fund_prompt = FUNDAMENTAL_ANALYSIS_PROMPT.format(
                name=name, symbol=symbol, price=price,
                volume_24h=volume, market_cap=market_cap
            )
            
            fund_result = self.swarm.query(fund_prompt)
            fund_votes_buy, fund_votes_sell, fund_votes_nothing = self.count_recommendations(
                fund_result.get("responses", {})
            )
            fund_consensus = fund_result.get("consensus_summary", "No consensus")
            fund_rec = self.extract_recommendation(fund_consensus)
            
            print(f"\n🔬 Fundamental Analysis:")
            print(f"   Votes: BUY={fund_votes_buy} | SELL={fund_votes_sell} | NOTHING={fund_votes_nothing}")
            print(f"   Consensus: {fund_rec}")
            cprint(f"   Summary: {fund_consensus[:200]}...", "cyan")
            
            # Overall recommendation
            total_buy = tech_votes_buy + fund_votes_buy
            total_sell = tech_votes_sell + fund_votes_sell
            total_models = len(self.swarm.active_models) * 2  # tech + fund
            
            if total_buy > total_sell:
                overall_rec = "BUY"
            elif total_sell > total_buy:
                overall_rec = "SELL"
            else:
                overall_rec = "DO NOTHING"
            
            confidence = max(total_buy, total_sell) / max(total_models, 1) if total_models > 0 else 0
            
            # Save analysis
            self.analysis_log = pd.concat([
                self.analysis_log,
                pd.DataFrame([{
                    'timestamp': datetime.now().isoformat(),
                    'token_id': token_id,
                    'symbol': symbol,
                    'name': name,
                    'price': price,
                    'volume_24h': volume,
                    'market_cap': market_cap,
                    'technical_consensus': tech_rec,
                    'fundamental_consensus': fund_rec,
                    'technical_votes_buy': tech_votes_buy,
                    'technical_votes_sell': tech_votes_sell,
                    'technical_votes_nothing': tech_votes_nothing,
                    'fundamental_votes_buy': fund_votes_buy,
                    'fundamental_votes_sell': fund_votes_sell,
                    'fundamental_votes_nothing': fund_votes_nothing,
                    'overall_recommendation': overall_rec,
                    'confidence_score': round(confidence * 100, 2)
                }])
            ], ignore_index=True)
            
            self.analysis_log.to_csv(ANALYSIS_FILE, index=False)
            
            # Save detailed results
            detailed_result = {
                'timestamp': datetime.now().isoformat(),
                'token': {'id': token_id, 'name': name, 'symbol': symbol},
                'market_data': {'price': price, 'volume_24h': volume, 'market_cap': market_cap},
                'technical_analysis': tech_result,
                'fundamental_analysis': fund_result,
                'overall': {
                    'recommendation': overall_rec,
                    'confidence': confidence,
                    'total_votes': {'buy': total_buy, 'sell': total_sell}
                }
            }
            
            detailed_file = DETAILED_FILE.parent / f"trend_{token_id}_{datetime.now().timestamp()}.json"
            with open(detailed_file, 'w') as f:
                json.dump(detailed_result, f, indent=2)
            
            print(f"\n✅ Analysis saved!")
            print(f"📊 Overall: {overall_rec} (Confidence: {confidence*100:.1f}%)")
            
        except Exception as e:
            print(f"⚠️ Error analyzing {token_data.get('name', 'Unknown')}: {str(e)}")
    
    def run_analysis_cycle(self):
        """Run one complete analysis cycle"""
        try:
            print("\n🔄 Starting Trend Coin Analysis Cycle!")
            
            # Load tokens
            tokens_df = self.load_tokens()
            
            # Sort by market cap
            tokens_df = tokens_df.sort_values('market_cap', ascending=False)
            
            # Analyze each token
            for _, token_data in tokens_df.iterrows():
                self.analyze_token(token_data.to_dict())
                time.sleep(2)  # Rate limiting
            
            print("\n✨ Analysis cycle complete!")
            print(f"📊 Processed {len(tokens_df)} tokens")
            print(f"💾 Results saved to {ANALYSIS_FILE}")
            
        except Exception as e:
            print(f"❌ Error in analysis cycle: {str(e)}")

def print_banner():
    """Print welcome banner"""
    cprint("\n" + "="*70, "cyan")
    cprint("🌙 Moon Dev's Analyse Trend Coin Agent 🔥", "cyan", attrs=["bold"])
    cprint("Multi-Model AI Swarm for Token Analysis", "cyan")
    cprint("="*70 + "\n", "cyan")
def main():
    """Main entry point"""
    print_banner()
    cprint("⚙️ Configuration:", "yellow")
    cprint(f"  • Tokens File: {TOKENS_FILE}", "yellow")
    cprint(f"  • Analysis Output: {ANALYSIS_FILE}", "yellow")
    cprint(f"  • Max Market Cap: ${MAX_MARKET_CAP:,.0f}", "yellow")
    cprint(f"  • Min 24h Volume: ${MIN_VOLUME_USD:,.0f}\n", "yellow")
    
    analyzer = SwarmAnalyzer()
    
    try:
        round_number = 1
        while True:
            print_section(f"🎯 Round {round_number} 🎯")
            analyzer.run_analysis_cycle()
            
            next_round = datetime.now() + timedelta(hours=HOURS_BETWEEN_RUNS)
            cprint(f"\n⏳ Next round in {HOURS_BETWEEN_RUNS} hours (at {next_round.strftime('%H:%M:%S')})",
                  "magenta")
            time.sleep(HOURS_BETWEEN_RUNS * 3600)
            round_number += 1
            
    except KeyboardInterrupt:
        cprint("\n👋 Trend Coin Analyzer shutting down...", "magenta")
    except Exception as e:
        cprint(f"\n❌ Error: {str(e)}", "red")

def print_section(title: str):
    """Print section header"""
    cprint(f"\n{'='*60}", "blue")
    cprint(f"  {title}", "blue", attrs=["bold"])
    cprint(f"{'='*60}\n", "blue")

if __name__ == "__main__":
    main()
