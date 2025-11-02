"""
🌙 Moon Dev's Strategy Agent
Handles all strategy-based trading decisions
"""

import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
import json
from termcolor import cprint
import anthropic
import importlib
import inspect
import time

# Import exchange manager for unified trading
try:
    from exchange_manager import ExchangeManager
    USE_EXCHANGE_MANAGER = True
except ImportError:
    import nice_funcs as n
    USE_EXCHANGE_MANAGER = False

# 🎯 Strategy Evaluation Prompt
STRATEGY_EVAL_PROMPT = """
You are Moon Dev's Strategy Validation Assistant 🌙

Analyze the following strategy signals and validate their recommendations:

Strategy Signals:
{strategy_signals}

Market Context:
{market_data}

Your task:
1. Evaluate each strategy signal's reasoning
2. Check if signals align with current market conditions
3. Look for confirmation/contradiction between different strategies
4. Consider risk factors

Respond in this format:
1. First line: EXECUTE or REJECT for each signal (e.g., "EXECUTE signal_1, REJECT signal_2")
2. Then explain your reasoning:
   - Signal analysis
   - Market alignment
   - Risk assessment
   - Confidence in each decision (0-100%)

Remember:
- Moon Dev prioritizes risk management! 🛡️
- Multiple confirming signals increase confidence
- Contradicting signals require deeper analysis
- Better to reject a signal than risk a bad trade
"""

class StrategyAgent:
    def __init__(self):
        """Initialize the Strategy Agent"""
        self.enabled_strategies = []
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_KEY"))

        # Initialize exchange manager if available
        if USE_EXCHANGE_MANAGER:
            self.em = ExchangeManager()
            cprint(f"✅ Strategy Agent using ExchangeManager for {EXCHANGE}", "green")
        else:
            self.em = None
            cprint("✅ Strategy Agent using direct nice_funcs", "green")
        
        if ENABLE_STRATEGIES:
            try:
                # Import strategies directly
                from strategies.custom.private_my_strategy import MyStrategy
                
                # Initialize strategies
                self.enabled_strategies.extend([
                    MyStrategy()
                ])
                
                print(f"✅ Loaded {len(self.enabled_strategies)} strategies!")
                for strategy in self.enabled_strategies:
                    print(f"  • {strategy.name}")
                    
            except Exception as e:
                print(f"⚠️ Error loading strategies: {e}")
        else:
            print("🤖 Strategy Agent is disabled in config.py")
        
        print(f"🤖 Moon Dev's Strategy Agent initialized with {len(self.enabled_strategies)} strategies!")

    def evaluate_signals(self, signals, market_data):
        """Have LLM evaluate strategy signals"""
        try:
            if not signals:
                return None
                
            # Format signals for prompt
            signals_str = json.dumps(signals, indent=2)
            
            message = self.client.messages.create(
                model=AI_MODEL,
                max_tokens=AI_MAX_TOKENS,
                temperature=AI_TEMPERATURE,
                messages=[{
                    "role": "user",
                    "content": STRATEGY_EVAL_PROMPT.format(
                        strategy_signals=signals_str,
                        market_data=market_data
                    )
                }]
            )
            
            response = message.content
            if isinstance(response, list):
                response = response[0].text if hasattr(response[0], 'text') else str(response[0])
            
            # Parse response
            lines = response.split('\n')
            decisions = lines[0].strip().split(',')
            reasoning = '\n'.join(lines[1:])
            
            print("🤖 Strategy Evaluation:")
            print(f"Decisions: {decisions}")
            print(f"Reasoning: {reasoning}")
            
            return {
                'decisions': decisions,
                'reasoning': reasoning
            }
            
        except Exception as e:
            print(f"❌ Error evaluating signals: {e}")
            return None

    def get_signals(self, token):
        """Get and evaluate signals from all enabled strategies"""
        try:
            # 1. Collect signals from all strategies
            signals = []
            print(f"\n🔍 Analyzing {token} with {len(self.enabled_strategies)} strategies...")
            
            for strategy in self.enabled_strategies:
                signal = strategy.generate_signals()
                if signal and signal['token'] == token:
                    signals.append({
                        'token': signal['token'],
                        'strategy_name': strategy.name,
                        'signal': signal['signal'],
                        'direction': signal['direction'],
                        'metadata': signal.get('metadata', {})
                    })
            
            if not signals:
                print(f"ℹ️ No strategy signals for {token}")
                return []
            
            print(f"\n📊 Raw Strategy Signals for {token}:")
            for signal in signals:
                print(f"  • {signal['strategy_name']}: {signal['direction']} ({signal['signal']}) for {signal['token']}")
            
            # 2. Get market data for context
            try:
                from data.ohlcv_collector import collect_token_data
                market_data = collect_token_data(token)
            except Exception as e:
                print(f"⚠️ Could not get market data: {e}")
                market_data = {}
            
            # 3. Have LLM evaluate the signals
            print("\n🤖 Getting LLM evaluation of signals...")
            evaluation = self.evaluate_signals(signals, market_data)
            
            if not evaluation:
                print("❌ Failed to get LLM evaluation")
                return []
            
            # 4. Filter signals based on LLM decisions
            approved_signals = []
            for signal, decision in zip(signals, evaluation['decisions']):
                if "EXECUTE" in decision.upper():
                    print(f"✅ LLM approved {signal['strategy_name']}'s {signal['direction']} signal")
                    approved_signals.append(signal)
                else:
                    print(f"❌ LLM rejected {signal['strategy_name']}'s {signal['direction']} signal")
            
            # 5. Print final approved signals
            if approved_signals:
                print(f"\n🎯 Final Approved Signals for {token}:")
                for signal in approved_signals:
                    print(f"  • {signal['strategy_name']}: {signal['direction']} ({signal['signal']})")
                
                # 6. Execute approved signals
                print("\n💫 Executing approved strategy signals...")
                self.execute_strategy_signals(approved_signals)
            else:
                print(f"\n⚠️ No signals approved by LLM for {token}")
            
            return approved_signals
            
        except Exception as e:
            print(f"❌ Error getting strategy signals: {e}")
            return []

    def combine_with_portfolio(self, signals, current_portfolio):
        """Combine strategy signals with current portfolio state"""
        try:
            final_allocations = current_portfolio.copy()
            
            for signal in signals:
                token = signal['token']
                strength = signal['signal']
                direction = signal['direction']
                
                if direction == 'BUY' and strength >= STRATEGY_MIN_CONFIDENCE:
                    print(f"🔵 Buy signal for {token} (strength: {strength})")
                    max_position = usd_size * (MAX_POSITION_PERCENTAGE / 100)
                    allocation = max_position * strength
                    final_allocations[token] = allocation
                elif direction == 'SELL' and strength >= STRATEGY_MIN_CONFIDENCE:
                    print(f"🔴 Sell signal for {token} (strength: {strength})")
                    final_allocations[token] = 0
            
            return final_allocations
            
        except Exception as e:
            print(f"❌ Error combining signals: {e}")
            return None 

    def execute_strategy_signals(self, approved_signals):
        """Execute trades based on approved strategy signals"""
        try:
            if not approved_signals:
                print("⚠️ No approved signals to execute")
                return

            print("\n🚀 Moon Dev executing strategy signals...")
            print(f"📝 Received {len(approved_signals)} signals to execute")
            
            for signal in approved_signals:
                try:
                    print(f"\n🔍 Processing signal: {signal}")  # Debug output
                    
                    token = signal.get('token')
                    if not token:
                        print("❌ Missing token in signal")
                        print(f"Signal data: {signal}")
                        continue
                        
                    strength = signal.get('signal', 0)
                    direction = signal.get('direction', 'NOTHING')
                    
                    # Skip USDC and other excluded tokens
                    if token in EXCLUDED_TOKENS:
                        print(f"💵 Skipping {token} (excluded token)")
                        continue
                    
                    print(f"\n🎯 Processing signal for {token}...")
                    
                    # Calculate position size based on signal strength
                    max_position = usd_size * (MAX_POSITION_PERCENTAGE / 100)
                    target_size = max_position * strength
                    
                    # Get current position value (using exchange manager if available)
                    if self.em:
                        current_position = self.em.get_token_balance_usd(token)
                    else:
                        current_position = n.get_token_balance_usd(token)

                    print(f"📊 Signal strength: {strength}")
                    print(f"🎯 Target position: ${target_size:.2f} USD")
                    print(f"📈 Current position: ${current_position:.2f} USD")

                    if direction == 'BUY':
                        if current_position < target_size:
                            print(f"✨ Executing BUY for {token}")
                            if self.em:
                                self.em.ai_entry(token, target_size)
                            else:
                                n.ai_entry(token, target_size)
                            print(f"✅ Entry complete for {token}")
                        else:
                            print(f"⏸️ Position already at or above target size")

                    elif direction == 'SELL':
                        if current_position > 0:
                            print(f"📉 Executing SELL for {token}")
                            if self.em:
                                self.em.chunk_kill(token)
                            else:
                                n.chunk_kill(token, max_usd_order_size, slippage)
                            print(f"✅ Exit complete for {token}")
                        else:
                            print(f"⏸️ No position to sell")
                    
                    time.sleep(2)  # Small delay between trades
                    
                except Exception as e:
                    print(f"❌ Error processing signal: {str(e)}")
                    print(f"Signal data: {signal}")
                    continue
                
        except Exception as e:
            print(f"❌ Error executing strategy signals: {str(e)}")
            print("🔧 Moon Dev suggests checking the logs and trying again!")
    
    def run_strategy_cycle(self):
        """Run one complete strategy evaluation cycle"""
        try:
            from datetime import datetime
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cprint(f"\n{'='*90}", "cyan")
            cprint(f"🔄 Strategy Cycle Started at {timestamp}", "cyan", attrs=['bold'])
            cprint(f"{'='*90}", "cyan")
            
            if not self.enabled_strategies:
                cprint("⚠️ No strategies loaded! Check ENABLE_STRATEGIES in config.py", "yellow")
                return
            
            cprint(f"\n📊 Active Strategies: {len(self.enabled_strategies)}", "white")
            for strategy in self.enabled_strategies:
                cprint(f"  • {strategy.name}", "cyan")
            
            # Collect signals from all strategies
            all_signals = []
            
            cprint(f"\n🔍 Collecting signals from all strategies...", "yellow")
            for strategy in self.enabled_strategies:
                try:
                    signal = strategy.generate_signals()
                    if signal:
                        all_signals.append({
                            'token': signal['token'],
                            'strategy_name': strategy.name,
                            'signal': signal['signal'],
                            'direction': signal['direction'],
                            'metadata': signal.get('metadata', {})
                        })
                        cprint(f"  ✅ {strategy.name}: {signal['direction']} {signal['token']} (confidence: {signal['signal']:.2f})", "green")
                    else:
                        cprint(f"  ⏸️  {strategy.name}: No signal", "white")
                except Exception as e:
                    cprint(f"  ❌ {strategy.name}: Error - {str(e)}", "red")
            
            # Process signals if any were generated
            if all_signals:
                cprint(f"\n📋 Total Signals Collected: {len(all_signals)}", "yellow", attrs=['bold'])
                
                # Group signals by token
                signals_by_token = {}
                for signal in all_signals:
                    token = signal['token']
                    if token not in signals_by_token:
                        signals_by_token[token] = []
                    signals_by_token[token].append(signal)
                
                # AI evaluation and execution for each token
                for token, signals in signals_by_token.items():
                    cprint(f"\n🎯 Evaluating {len(signals)} signal(s) for {token}", "cyan")
                    
                    # Get market data for context
                    try:
                        from data.ohlcv_collector import collect_token_data
                        market_data = collect_token_data(token)
                    except Exception as e:
                        cprint(f"⚠️ Could not get market data: {e}", "yellow")
                        market_data = {}
                    
                    # AI evaluation
                    evaluation = self.evaluate_signals(signals, market_data)
                    
                    if evaluation:
                        # Execute approved signals
                        approved_signals = []
                        for signal, decision in zip(signals, evaluation['decisions']):
                            if "EXECUTE" in decision.upper():
                                cprint(f"✅ AI approved: {signal['strategy_name']} {signal['direction']}", "green")
                                approved_signals.append(signal)
                            else:
                                cprint(f"❌ AI rejected: {signal['strategy_name']} {signal['direction']}", "red")
                        
                        if approved_signals:
                            self.execute_strategy_signals(approved_signals)
                        else:
                            cprint(f"⏸️  No signals approved for {token}", "white")
                    else:
                        cprint(f"❌ AI evaluation failed for {token}", "red")
            else:
                cprint(f"\n⏸️  No signals generated this cycle", "white")
            
            cprint(f"\n{'='*90}", "cyan")
            cprint(f"✅ Strategy Cycle Complete", "cyan", attrs=['bold'])
            cprint(f"{'='*90}\n", "cyan")
            
        except Exception as e:
            cprint(f"❌ Error in strategy cycle: {str(e)}", "red")
            import traceback
            traceback.print_exc()


def main():
    """Main function to run strategy agent continuously"""
    from datetime import datetime, timedelta
    
    cprint("\n" + "="*90, "cyan")
    cprint("🌙 Moon Dev's Strategy Agent - Multi-Strategy Trading System", "cyan", attrs=['bold'])
    cprint("="*90 + "\n", "cyan")
    
    try:
        # Initialize strategy agent
        agent = StrategyAgent()
        
        # Check interval from config (default 15 minutes)
        try:
            check_interval = SLEEP_BETWEEN_RUNS_MINUTES * 60  # Convert to seconds
        except:
            check_interval = 15 * 60  # Default 15 minutes
        
        cprint(f"⏰ Check Interval: {check_interval // 60} minutes", "white")
        cprint(f"🚀 Starting continuous strategy evaluation...", "green", attrs=['bold'])
        cprint(f"Press Ctrl+C to stop\n", "white")
        
        cycle_count = 0
        
        while True:
            cycle_count += 1
            cprint(f"\n📈 Cycle #{cycle_count}", "yellow")
            
            # Run strategy cycle
            agent.run_strategy_cycle()
            
            # Sleep until next cycle
            next_run = datetime.now() + timedelta(seconds=check_interval)
            cprint(f"💤 Sleeping {check_interval // 60} minutes... Next run at {next_run.strftime('%H:%M:%S')}", "white")
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        cprint(f"\n\n⚠️  Strategy Agent stopped by user", "yellow")
        cprint(f"Total cycles completed: {cycle_count}", "white")
    except Exception as e:
        cprint(f"\n\n❌ Fatal error: {str(e)}", "red")
        import traceback
        traceback.print_exc()
    finally:
        cprint(f"\n👋 Strategy Agent shutdown complete", "cyan")


if __name__ == "__main__":
    main()
