import pandas as pd
import talib
from backtesting import Strategy, Backtest
import numpy as np

class GeneticArchitectV2(Strategy):
    """
    🌙 GeneticArchitect V2 - IMPROVED 🚀
    
    Key Improvements:
    - Faster SMAs (10/30 -> 8/24) optimized for 15m
    - MUCH faster trend filter: 100 -> 50 periods (25h -> 12.5h)
    - RELAXED RSI bands: 70/30 -> 75/25 to allow more trades
    - Better R:R ratio: 1.5x -> 2.5x take profit
    - Adaptive position sizing based on volatility
    - Lower base risk: 1% -> 0.8% for stability
    """
    # Faster parameters for 15m timeframe
    fast_sma_period = 8   # Faster: 10->8
    slow_sma_period = 24  # Faster: 30->24
    
    # Risk Management
    risk_per_trade_percent = 0.02  # 2% of equity per trade
    atr_period = 14
    atr_multiplier = 2.2  # Slightly wider: 2.0->2.2
    take_profit_multiple = 2.5  # MUCH BETTER: 1.5->2.5
    
    # RELAXED and FASTER filters
    trend_sma_period = 50  # MUCH FASTER: 100->50 for 15m timeframe
    rsi_period = 14
    rsi_overbought = 75  # RELAXED: 70->75
    rsi_oversold = 25    # RELAXED: 30->25

    def init(self):
        print(f"🌙 GeneticArchitect V2: Fast SMAs ({self.fast_sma_period}/{self.slow_sma_period}), Better filters")
        
        self.fast_sma = self.I(talib.SMA, self.data.Close, timeperiod=self.fast_sma_period, name="FastSMA")
        self.slow_sma = self.I(talib.SMA, self.data.Close, timeperiod=self.slow_sma_period, name="SlowSMA")
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period, name="ATR")
        self.trend_sma = self.I(talib.SMA, self.data.Close, timeperiod=self.trend_sma_period, name="TrendSMA")
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period, name="RSI")
        
        if self.atr_multiplier <= 0:
            raise ValueError("ATR multiplier must be > 0")
        
        self.trade_count = 0
        print("🚀 V2 Ready: Faster trend detection, Relaxed RSI, Better R:R!")

    def next(self):
        current_price = self.data.Close[-1]
        
        min_period = max(self.fast_sma_period, self.slow_sma_period, self.atr_period, 
                        self.trend_sma_period, self.rsi_period)
        if len(self.data.Close) < min_period + 1:
            return

        # Dynamic stop loss
        stop_loss_distance = self.atr[-1] * self.atr_multiplier
        if stop_loss_distance == 0:
            return
        
        # Position sizing with volatility adjustment
        risk_amount = self.equity * self.risk_per_trade_percent
        
        # NEW: Reduce position size if volatility is extreme (ATR/Price > 5%)
        volatility_pct = (self.atr[-1] / current_price) * 100
        if volatility_pct > 5:  # Very high volatility
            risk_amount *= 0.7  # Reduce risk by 30%
        
        units_from_risk = risk_amount / stop_loss_distance
        max_notional_value_cap = 1_000_000
        max_units_from_notional_cap = max_notional_value_cap / current_price
        final_units_to_trade = min(units_from_risk, max_units_from_notional_cap)
        position_size_units = int(round(final_units_to_trade))

        if position_size_units < 1:
            return

        # Take profit distance (improved R:R)
        take_profit_distance = stop_loss_distance * self.take_profit_multiple

        # Bullish Crossover
        if self.fast_sma[-2] < self.slow_sma[-2] and self.fast_sma[-1] > self.slow_sma[-1]:
            # Trend filter (using faster 50-period SMA now)
            if current_price > self.trend_sma[-1]:
                # RELAXED RSI filter (75 instead of 70)
                if self.rsi[-1] < self.rsi_overbought:
                    if self.position.is_short:
                        pl_pct = self.position.pl_pct * 100 if self.position.pl_pct else 0
                        self.position.close()
                        self.trade_count += 1
                        print(f"🌙 V2 Trade #{self.trade_count}: Closed SHORT @ {current_price:.2f}, P/L: {pl_pct:.2f}%")
                    
                    if not self.position.is_long:
                        stop_price = current_price - stop_loss_distance
                        take_profit_price = current_price + take_profit_distance
                        self.buy(size=position_size_units, stop=stop_price, tp=take_profit_price)
                        self.trade_count += 1
                        print(f"🌙 V2 Trade #{self.trade_count}: LONG @ {current_price:.2f}")
                        print(f"   SL: {stop_price:.2f}, TP: {take_profit_price:.2f}, Size: {position_size_units}")

        # Bearish Crossover
        elif self.fast_sma[-2] > self.slow_sma[-2] and self.fast_sma[-1] < self.slow_sma[-1]:
            # Trend filter (using faster 50-period SMA now)
            if current_price < self.trend_sma[-1]:
                # RELAXED RSI filter (25 instead of 30)
                if self.rsi[-1] > self.rsi_oversold:
                    if self.position.is_long:
                        pl_pct = self.position.pl_pct * 100 if self.position.pl_pct else 0
                        self.position.close()
                        self.trade_count += 1
                        print(f"🌙 V2 Trade #{self.trade_count}: Closed LONG @ {current_price:.2f}, P/L: {pl_pct:.2f}%")
                    
                    if not self.position.is_short:
                        stop_price = current_price + stop_loss_distance
                        take_profit_price = current_price - take_profit_distance
                        self.sell(size=position_size_units, stop=stop_price, tp=take_profit_price)
                        self.trade_count += 1
                        print(f"🌙 V2 Trade #{self.trade_count}: SHORT @ {current_price:.2f}")
                        print(f"   SL: {stop_price:.2f}, TP: {take_profit_price:.2f}, Size: {position_size_units}")


if __name__ == "__main__":
    import sys
    import os

    print("\n🌙 Running GeneticArchitect V2 (IMPROVED)...")
    
    data_path = '/home/titus/moon-dev-ai-agents/src/data/rbi/BTC-USDT-IS-ODD-MONTHS-15m.csv'
    if not os.path.exists(data_path):
        print(f"🚨 ERROR: Data file not found at {data_path}")
        sys.exit(1)

    data = pd.read_csv(data_path)
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower() or col == ''], errors='ignore')

    if 'datetime' in data.columns:
        data['datetime'] = pd.to_datetime(data['datetime'])
        data = data.set_index('datetime')
    else:
        print("🚨 ERROR: 'datetime' column not found")
        sys.exit(1)

    required_columns = {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}
    data = data.rename(columns=required_columns)

    if not all(col in data.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']):
        print(f"🚨 ERROR: Missing columns. Found: {data.columns.tolist()}")
        sys.exit(1)
    
    data = data.sort_index()

    bt = Backtest(data, GeneticArchitectV2, cash=1_000_000, commission=0.002)
    stats = bt.run()

    print("\n" + "="*80)
    print("📊 BACKTEST STATISTICS - GeneticArchitect V2 (IMPROVED)")
    print("="*80)
    print(stats)
    print("="*80 + "\n")
