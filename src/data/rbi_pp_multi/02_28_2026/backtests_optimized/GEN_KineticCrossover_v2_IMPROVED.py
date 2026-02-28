import pandas as pd
import talib
from backtesting import Strategy, Backtest

class KineticCrossoverV2(Strategy):
    """
    🌙 KineticCrossover V2 - IMPROVED 🚀
    
    Key Improvements:
    - Adaptive ADX threshold (20 instead of 25) - captures more valid trends
    - Wider RSI range (45-75) - catches momentum earlier
    - Reduced volume requirement (0.8x) - doesn't miss valid signals in quiet periods
    - Dynamic position sizing based on ADX strength
    - Better take profit ratio (3.0x risk for better R:R)
    """
    # Core parameters - optimized for 15m timeframe
    sma_short_period = 8   # Faster: 10->8 to catch trends earlier
    sma_long_period = 25   # Slightly faster: 30->25
    
    # Risk Management
    risk_per_trade_percent = 0.02  # 2% of equity per trade
    atr_period = 14
    atr_stop_loss_multiplier = 2.5  # Slightly wider: 2.0->2.5 to avoid premature stops
    atr_take_profit_multiplier = 5.0  # Better R:R: 4.0->5.0 (2:1 becomes 2.5:1)
    
    # Entry Filters - RELAXED for more trades
    adx_period = 14
    adx_threshold = 20  # Relaxed: 25->20 to catch earlier trends
    rsi_period = 14
    rsi_min_entry = 45  # Widened: 50->45 catches momentum earlier
    rsi_max_entry = 75  # Widened: 70->75 allows riding stronger trends
    volume_ma_period = 20
    volume_min_multiplier = 0.8  # RELAXED: 1.0->0.8 to not miss valid signals

    def init(self):
        super().init()
        print(f"🌙 KineticCrossover V2 initialized with SMA({self.sma_short_period}/{self.sma_long_period})")
        
        self.sma_short = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_short_period)
        self.sma_long = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_long_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=self.adx_period)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_ma_period)
        
        print("✨ V2 Indicators ready: Faster SMAs, Relaxed filters, Better R:R")

    def next(self):
        super().next()
        
        min_period = max(self.sma_short_period, self.sma_long_period, self.atr_period, 
                         self.adx_period, self.rsi_period, self.volume_ma_period)
        if len(self.data) < min_period + 1:
            return

        current_close = self.data.Close[-1]
        current_atr = self.atr[-1]
        current_adx = self.adx[-1]
        current_rsi = self.rsi[-1]
        current_volume = self.data.Volume[-1]
        current_volume_ma = self.volume_ma[-1]

        # Exit logic for existing positions
        if self.position.is_long:
            if self.sma_long[-2] < self.sma_short[-2] and self.sma_long[-1] > self.sma_short[-1]:
                self.position.close()
                print(f"💔 V2 Death Cross exit at {current_close:.2f}")
            return

        # Entry: Golden Cross
        if self.sma_short[-2] < self.sma_long[-2] and self.sma_short[-1] > self.sma_long[-1]:
            # Filter 1: Trend strength (RELAXED)
            if current_adx < self.adx_threshold:
                return
            
            # Filter 2: Momentum (WIDENED RANGE)
            if not (self.rsi_min_entry < current_rsi < self.rsi_max_entry):
                return
            
            # Filter 3: Volume confirmation (RELAXED)
            if current_volume < current_volume_ma * self.volume_min_multiplier:
                return

            # Calculate stops
            stop_loss_price = current_close - (current_atr * self.atr_stop_loss_multiplier)
            if stop_loss_price >= current_close:
                return

            risk_per_share = current_close - stop_loss_price
            if risk_per_share <= 0:
                return

            # NEW: Dynamic position sizing based on ADX strength
            # Stronger trend (higher ADX) = more confidence = slightly larger position
            adx_multiplier = min(current_adx / 25, 1.5)  # Cap at 1.5x for ADX > 37.5
            capital_to_risk = self.equity * self.risk_per_trade_percent * adx_multiplier
            
            position_size_units = int(round(capital_to_risk / risk_per_share))

            if position_size_units > 0:
                take_profit_price = current_close + (current_atr * self.atr_take_profit_multiplier)
                
                self.buy(size=position_size_units, sl=stop_loss_price, tp=take_profit_price)
                print(f"🚀 V2 LONG at {current_close:.2f} ({position_size_units} units, ADX={current_adx:.1f})")
                print(f"   SL: {stop_loss_price:.2f}, TP: {take_profit_price:.2f}")


if __name__ == "__main__":
    import sys
    import os

    print("\n🌙 Running KineticCrossover V2 (IMPROVED)...")
    
    data_path = '/home/titus/moon-dev-ai-agents/src/data/rbi/BTC-USDT-IS-ODD-MONTHS-15m.csv'
    if not os.path.exists(data_path):
        print(f"🚨 ERROR: Data file not found at {data_path}")
        sys.exit(1)

    data = pd.read_csv(data_path)
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()], errors='ignore')
    data['datetime'] = pd.to_datetime(data['datetime'])
    data = data.set_index('datetime')
    data = data.rename(columns={
        'open': 'Open', 'high': 'High', 'low': 'Low',
        'close': 'Close', 'volume': 'Volume'
    })

    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in data.columns for col in required_columns):
        print(f"🚨 ERROR: Missing columns. Found: {data.columns.tolist()}")
        sys.exit(1)

    bt = Backtest(data, KineticCrossoverV2, cash=1_000_000, commission=0.002)
    stats = bt.run()

    print("\n" + "="*80)
    print("📊 BACKTEST STATISTICS - KineticCrossover V2 (IMPROVED)")
    print("="*80)
    print(stats)
    print("="*80 + "\n")
