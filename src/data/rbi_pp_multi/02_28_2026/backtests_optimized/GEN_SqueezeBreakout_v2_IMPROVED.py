import pandas as pd
import talib
from backtesting import Strategy, Backtest

class SqueezeBreakoutV2(Strategy):
    """
    🌙 SqueezeBreakout V2 - IMPROVED 🚀
    
    Original: -0.78% return, 20.4% win rate, 3.5 avg trades
    
    Improvements:
    - Proper Bollinger Band squeeze detection
    - Keltner Channel for volatility confirmation
    - Momentum indicator (RSI) for direction
    - Volume surge confirmation
    - Better position sizing and risk management
    - Optimized for 15m timeframe
    """
    # Bollinger Bands parameters
    bb_period = 20
    bb_std = 2.0
    
    # Keltner Channel parameters (for squeeze detection)
    kc_period = 20
    kc_atr_mult = 1.5
    
    # Squeeze and breakout detection
    squeeze_threshold = 0.02  # BB must be within 2% of KC for squeeze
    momentum_period = 12      # Fast momentum indicator
    
    # Risk Management
    risk_pct = 0.02  # 2% of equity per trade
    atr_period = 14
    atr_stop_multiplier = 2.0
    atr_take_profit_multiplier = 3.5
    
    # Filters
    volume_ma_period = 20
    volume_surge_multiplier = 1.2  # Need 20% volume surge for breakout
    min_rsi_momentum = 50  # RSI must show directional bias

    def init(self):
        print(f"🌙 SqueezeBreakout V2: BB({self.bb_period}) + KC({self.kc_period}) squeeze detection")
        
        # Bollinger Bands
        self.bb_upper = self.I(talib.BBANDS, self.data.Close, timeperiod=self.bb_period, 
                               nbdevup=self.bb_std, nbdevdn=self.bb_std, matype=0)[0]
        self.bb_middle = self.I(talib.BBANDS, self.data.Close, timeperiod=self.bb_period, 
                                nbdevup=self.bb_std, nbdevdn=self.bb_std, matype=0)[1]
        self.bb_lower = self.I(talib.BBANDS, self.data.Close, timeperiod=self.bb_period, 
                               nbdevup=self.bb_std, nbdevdn=self.bb_std, matype=0)[2]
        
        # Keltner Channel (using EMA + ATR)
        self.kc_middle = self.I(talib.EMA, self.data.Close, timeperiod=self.kc_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        # Momentum and volume
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.momentum_period)
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_ma_period)
        
        print("🚀 V2 Ready: Squeeze detection with momentum & volume confirmation!")

    def next(self):
        min_period = max(self.bb_period, self.kc_period, self.atr_period, 
                        self.momentum_period, self.volume_ma_period)
        if len(self.data) < min_period + 1:
            return

        current_close = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        
        # Calculate Keltner Channel dynamically
        kc_upper = self.kc_middle[-1] + (self.atr[-1] * self.kc_atr_mult)
        kc_lower = self.kc_middle[-1] - (self.atr[-1] * self.kc_atr_mult)
        
        bb_upper = self.bb_upper[-1]
        bb_lower = self.bb_lower[-1]
        bb_middle = self.bb_middle[-1]
        
        current_rsi = self.rsi[-1]
        current_volume_ma = self.volume_ma[-1]
        current_atr = self.atr[-1]

        # Detect squeeze: BB inside KC
        bb_width = bb_upper - bb_lower
        kc_width = kc_upper - kc_lower
        
        # Squeeze is active when BB is significantly inside KC
        is_squeezed = bb_width < kc_width * (1 + self.squeeze_threshold)
        
        # If in a position, let SL/TP handle exits
        if self.position:
            return

        # Only look for breakouts if squeeze was active recently (check last 3 bars)
        was_recently_squeezed = False
        for i in range(1, 4):
            if len(self.data) < min_period + i:
                continue
            bb_w = self.bb_upper[-i] - self.bb_lower[-i]
            kc_u = self.kc_middle[-i] + (self.atr[-i] * self.kc_atr_mult)
            kc_l = self.kc_middle[-i] - (self.atr[-i] * self.kc_atr_mult)
            kc_w = kc_u - kc_l
            if bb_w < kc_w * (1 + self.squeeze_threshold):
                was_recently_squeezed = True
                break
        
        if not was_recently_squeezed:
            return

        # Volume surge confirmation
        volume_surge = current_volume > (current_volume_ma * self.volume_surge_multiplier)
        if not volume_surge:
            return

        # LONG breakout: Price breaks above BB middle + bullish RSI momentum
        if current_close > bb_middle and current_rsi > self.min_rsi_momentum:
            stop_loss_price = current_close - (current_atr * self.atr_stop_multiplier)
            if stop_loss_price >= current_close:
                return
            
            risk_per_share = current_close - stop_loss_price
            if risk_per_share <= 0:
                return
            
            capital_to_risk = self.equity * self.risk_pct
            position_size = int(round(capital_to_risk / risk_per_share))
            
            if position_size > 0:
                take_profit_price = current_close + (current_atr * self.atr_take_profit_multiplier)
                self.buy(size=position_size, sl=stop_loss_price, tp=take_profit_price)
                print(f"🚀 V2 SQUEEZE BREAKOUT LONG @ {current_close:.2f}")
                print(f"   RSI: {current_rsi:.1f}, Vol: {current_volume/current_volume_ma:.1f}x")
                print(f"   SL: {stop_loss_price:.2f}, TP: {take_profit_price:.2f}")

        # SHORT breakdown: Price breaks below BB middle + bearish RSI momentum
        elif current_close < bb_middle and current_rsi < (100 - self.min_rsi_momentum):
            stop_loss_price = current_close + (current_atr * self.atr_stop_multiplier)
            if stop_loss_price <= current_close:
                return
            
            risk_per_share = stop_loss_price - current_close
            if risk_per_share <= 0:
                return
            
            capital_to_risk = self.equity * self.risk_pct
            position_size = int(round(capital_to_risk / risk_per_share))
            
            if position_size > 0:
                take_profit_price = current_close - (current_atr * self.atr_take_profit_multiplier)
                self.sell(size=position_size, sl=stop_loss_price, tp=take_profit_price)
                print(f"🚀 V2 SQUEEZE BREAKDOWN SHORT @ {current_close:.2f}")
                print(f"   RSI: {current_rsi:.1f}, Vol: {current_volume/current_volume_ma:.1f}x")
                print(f"   SL: {stop_loss_price:.2f}, TP: {take_profit_price:.2f}")


if __name__ == "__main__":
    import sys
    import os

    print("\n🌙 Running SqueezeBreakout V2 (IMPROVED)...")
    
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

    bt = Backtest(data, SqueezeBreakoutV2, cash=1_000_000, commission=0.002)
    stats = bt.run()

    print("\n" + "="*80)
    print("📊 BACKTEST STATISTICS - SqueezeBreakout V2 (IMPROVED)")
    print("="*80)
    print(stats)
    print("="*80 + "\n")
