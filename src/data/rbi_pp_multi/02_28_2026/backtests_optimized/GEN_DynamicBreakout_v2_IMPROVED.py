import pandas as pd
import talib
from backtesting import Strategy, Backtest

class DynamicBreakoutV2(Strategy):
    """
    🌙 DynamicBreakout V2 - IMPROVED 🚀
    
    Original was barely functional (0 avg trades, -0.03% return).
    Complete redesign:
    - Dynamic Donchian Channel breakouts (20/10 periods)
    - ATR-based volatility filtering (only trade when ATR > threshold)
    - Volume confirmation with adaptive threshold
    - Trend alignment with EMA 40
    - Proper position sizing and risk management
    """
    # Donchian Channel parameters
    breakout_period = 20  # Look for highs/lows over 20 bars
    exit_period = 10      # Exit when price crosses opposite 10-period extreme
    
    # Risk Management
    risk_pct = 0.02  # 2% of equity per trade
    atr_period = 14
    atr_stop_multiplier = 2.5
    atr_take_profit_multiplier = 4.0
    
    # Filters
    atr_min_threshold_pct = 0.5  # Only trade if ATR > 0.5% of price (avoid dead markets)
    volume_ma_period = 20
    volume_min_multiplier = 1.0
    trend_ema_period = 40

    def init(self):
        print(f"🌙 DynamicBreakout V2: Donchian({self.breakout_period}/{self.exit_period}) + filters")
        
        # Donchian Channels
        self.high_channel = self.I(talib.MAX, self.data.High, timeperiod=self.breakout_period)
        self.low_channel = self.I(talib.MIN, self.data.Low, timeperiod=self.breakout_period)
        self.exit_high = self.I(talib.MAX, self.data.High, timeperiod=self.exit_period)
        self.exit_low = self.I(talib.MIN, self.data.Low, timeperiod=self.exit_period)
        
        # Filters
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_ma_period)
        self.trend_ema = self.I(talib.EMA, self.data.Close, timeperiod=self.trend_ema_period)
        
        print("🚀 V2 Ready: Dynamic breakouts with volatility & trend filters!")

    def next(self):
        min_period = max(self.breakout_period, self.atr_period, self.volume_ma_period, self.trend_ema_period)
        if len(self.data) < min_period + 1:
            return

        current_close = self.data.Close[-1]
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        current_atr = self.atr[-1]
        current_volume = self.data.Volume[-1]
        
        prev_high_channel = self.high_channel[-2]
        prev_low_channel = self.low_channel[-2]
        prev_exit_high = self.exit_high[-2]
        prev_exit_low = self.exit_low[-2]
        current_volume_ma = self.volume_ma[-1]
        current_trend_ema = self.trend_ema[-1]

        # Volatility filter: Skip if market is too quiet
        atr_pct = (current_atr / current_close) * 100
        if atr_pct < self.atr_min_threshold_pct:
            return

        # Exit management for existing positions
        if self.position.is_long:
            # Exit on opposite channel break
            if current_low < prev_exit_low:
                self.position.close()
                print(f"📉 V2 LONG Exit: Price broke below exit channel at {current_close:.2f}")
            return
        
        if self.position.is_short:
            # Exit on opposite channel break
            if current_high > prev_exit_high:
                self.position.close()
                print(f"📈 V2 SHORT Exit: Price broke above exit channel at {current_close:.2f}")
            return

        # Volume confirmation
        volume_confirmed = current_volume > (current_volume_ma * self.volume_min_multiplier)
        
        # LONG entry: Breakout above high channel + trend aligned
        if current_high > prev_high_channel and volume_confirmed and current_close > current_trend_ema:
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
                print(f"🚀 V2 LONG BREAKOUT @ {current_close:.2f} (ATR: {atr_pct:.2f}%)")
                print(f"   SL: {stop_loss_price:.2f}, TP: {take_profit_price:.2f}, Size: {position_size}")

        # SHORT entry: Breakdown below low channel + trend aligned
        elif current_low < prev_low_channel and volume_confirmed and current_close < current_trend_ema:
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
                print(f"🚀 V2 SHORT BREAKDOWN @ {current_close:.2f} (ATR: {atr_pct:.2f}%)")
                print(f"   SL: {stop_loss_price:.2f}, TP: {take_profit_price:.2f}, Size: {position_size}")


if __name__ == "__main__":
    import sys
    import os

    print("\n🌙 Running DynamicBreakout V2 (COMPLETE REDESIGN)...")
    
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

    bt = Backtest(data, DynamicBreakoutV2, cash=1_000_000, commission=0.002)
    stats = bt.run()

    print("\n" + "="*80)
    print("📊 BACKTEST STATISTICS - DynamicBreakout V2 (REDESIGNED)")
    print("="*80)
    print(stats)
    print("="*80 + "\n")
