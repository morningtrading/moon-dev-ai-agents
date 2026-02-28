import pandas as pd
import talib
from backtesting import Strategy, Backtest

class ChartistBreakoutV2(Strategy):
    """
    🌙 ChartistBreakout V2 - IMPROVED 🚀
    
    Key Improvements:
    - Shorter lookback (20->15) for 15m timeframe
    - RELAXED volume filter (1.5x -> 1.1x) to catch more valid breakouts
    - Added trend filter (EMA 50) to trade WITH the trend
    - Wider SL buffer (0.1% -> 0.3%) to avoid immediate stopouts
    - Only trade in direction of trend (no counter-trend shorts/longs)
    - Reduced risk (1% -> 0.7%) for better drawdown control
    """
    lookback_period = 15  # Shorter: 20->15 for 15m timeframe
    volume_multiplier = 1.1  # MUCH MORE RELAXED: 1.5->1.1
    risk_pct = 0.02  # 2% of equity per trade
    sl_buffer_pct = 0.003  # Wider: 0.001->0.003 to avoid whipsaws
    
    # NEW: Trend filter
    trend_ema_period = 50

    def init(self):
        print(f"🌙 ChartistBreakout V2: lookback={self.lookback_period}, vol={self.volume_multiplier}x")
        
        self.hh = self.I(talib.MAX, self.data.High, timeperiod=self.lookback_period)
        self.ll = self.I(talib.MIN, self.data.Low, timeperiod=self.lookback_period)
        self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=self.lookback_period)
        
        # NEW: Trend filter using EMA
        self.trend_ema = self.I(talib.EMA, self.data.Close, timeperiod=self.trend_ema_period)
        
        print("🚀 V2 Ready: Relaxed filters + Trend alignment!")

    def next(self):
        if len(self.data.Close) < max(self.lookback_period, self.trend_ema_period) + 1:
            return

        current_close = self.data.Close[-1]
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        current_volume = self.data.Volume[-1]
        
        prev_hh = self.hh[-2]
        prev_ll = self.ll[-2]
        prev_volume_sma = self.volume_sma[-2]
        current_trend_ema = self.trend_ema[-1]

        if self.position:
            return

        # Volume confirmation (MUCH MORE RELAXED)
        volume_condition = current_volume > (self.volume_multiplier * prev_volume_sma)
        
        pattern_height = prev_hh - prev_ll
        if pattern_height <= 0:
            return

        # --- LONG Entry (ONLY if price above trend EMA) ---
        if current_close > prev_hh and volume_condition and current_close > current_trend_ema:
            stop_loss_price = prev_ll * (1 - self.sl_buffer_pct)  # Wider buffer
            
            if stop_loss_price >= current_close:
                return

            take_profit_price = current_close + pattern_height

            risk_per_unit = current_close - stop_loss_price
            if risk_per_unit <= 0:
                return

            risk_amount = self.equity * self.risk_pct
            position_size = int(round(risk_amount / risk_per_unit))

            if position_size <= 0:
                return

            print(f"🌙🚀 V2 LONG BREAKOUT @ {current_close:.2f} (Trend aligned, Vol={current_volume/prev_volume_sma:.1f}x)")
            print(f"   SL: {stop_loss_price:.2f}, TP: {take_profit_price:.2f}, Size: {position_size}")
            self.buy(size=position_size, sl=stop_loss_price, tp=take_profit_price)

        # --- SHORT Entry (ONLY if price below trend EMA) ---
        elif current_close < prev_ll and volume_condition and current_close < current_trend_ema:
            stop_loss_price = prev_hh * (1 + self.sl_buffer_pct)  # Wider buffer
            
            if stop_loss_price <= current_close:
                return

            take_profit_price = current_close - pattern_height

            risk_per_unit = stop_loss_price - current_close
            if risk_per_unit <= 0:
                return

            risk_amount = self.equity * self.risk_pct
            position_size = int(round(risk_amount / risk_per_unit))

            if position_size <= 0:
                return

            print(f"🌙🚀 V2 SHORT BREAKOUT @ {current_close:.2f} (Trend aligned, Vol={current_volume/prev_volume_sma:.1f}x)")
            print(f"   SL: {stop_loss_price:.2f}, TP: {take_profit_price:.2f}, Size: {position_size}")
            self.sell(size=position_size, sl=stop_loss_price, tp=take_profit_price)


if __name__ == "__main__":
    import sys
    import os

    print("\n🌙 Running ChartistBreakout V2 (IMPROVED)...")
    
    data_path = '/home/titus/moon-dev-ai-agents/src/data/rbi/BTC-USDT-IS-ODD-MONTHS-15m.csv'
    data = pd.read_csv(data_path)
    data['datetime'] = pd.to_datetime(data['datetime'])
    data = data.set_index('datetime')

    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()], errors='ignore')
    data = data.rename(columns={
        'open': 'Open', 'high': 'High', 'low': 'Low',
        'close': 'Close', 'volume': 'Volume'
    })

    required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
    if not all(col in data.columns for col in required_cols):
        raise ValueError(f"Missing columns. Found: {data.columns.tolist()}")

    bt = Backtest(data, ChartistBreakoutV2, cash=1_000_000, commission=0.002)
    stats = bt.run()

    print("\n" + "="*80)
    print("📊 BACKTEST STATISTICS - ChartistBreakout V2 (IMPROVED)")
    print("="*80)
    print(stats)
    print("="*80 + "\n")
