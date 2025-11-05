import pandas as pd
import numpy as np
import talib
from backtesting import Strategy, Backtest

class MitigativeBreaker(Strategy):
    ema_period = 21  # 🌙 Optimized: Slightly adjusted from 20 to 21 for better trend alignment
    ema_long_period = 200  # 🌙 New: Added longer EMA for overall trend filter to avoid counter-trend trades
    atr_period = 14
    swing_period = 3  # 🌙 Optimized: Increased from 2 to 3 for stronger pivot confirmation (left/right bars)
    risk_pct = 0.01  # 1% risk per trade - kept for risk management
    breaker_zone_mult = 0.25  # 🌙 Optimized: Tightened from 0.5 to 0.25 ATR for more precise retest zones
    rr_ratio = 3  # 🌙 Optimized: Increased from 2 to 3 for higher reward potential while maintaining RR
    vol_sma_period = 20  # 🌙 New: Volume SMA for filtering high-volume swings only
    min_body_mult = 0.5  # 🌙 New: Minimum body size relative to ATR for rejection candle confirmation

    def init(self):
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
        self.ema_long = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_long_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.vol_sma = self.I(talib.SMA, self.data.Volume, timeperiod=self.vol_sma_period)
        
        self.potential_breaker_low = None
        self.potential_breaker_high = None
        self.broken_low_level = None
        self.waiting_long_reversal = False
        self.broken_high_level = None
        self.waiting_short_reversal = False
        self.breaker_long_level = None
        self.breaker_long_active = False
        self.breaker_short_level = None
        self.breaker_short_active = False

    def next(self):
        # 🌙 Minimum bars check: Ensure enough data for all indicators and pivot confirmation
        min_bars = max(self.ema_period, self.ema_long_period, self.vol_sma_period, self.atr_period) + 2 * self.swing_period + 1
        if len(self.data) < min_bars:
            return

        current_close = self.data.Close[-1]
        current_open = self.data.Open[-1]
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        current_atr = self.atr[-1]
        current_ema = self.ema[-1]
        current_ema_long = self.ema_long[-1]

        # 🌙 Improved swing detection: Proper pivot high/low with left/right bars and volume filter
        # Detect confirmed pivots with lag for stronger signals
        if len(self.data) >= 2 * self.swing_period + 1:
            pivot_idx = - (self.swing_period + 1)
            left_start = pivot_idx - self.swing_period
            left_end = pivot_idx
            right_start = pivot_idx + 1
            right_end = pivot_idx + self.swing_period + 1

            # Ensure valid indices (skip if not enough history)
            if left_start < -len(self.data):
                return

            # Pivot low detection
            pivot_low = self.data.Low[pivot_idx]
            is_pivot_low = True
            # Check left bars
            for i in range(left_start, left_end):
                if pivot_low >= self.data.Low[i]:
                    is_pivot_low = False
                    break
            # Check right bars
            if is_pivot_low:
                for i in range(right_start, right_end):
                    if i < 0 and pivot_low >= self.data.Low[i]:  # Ensure i is valid negative index
                        is_pivot_low = False
                        break
            # Volume filter for quality
            if is_pivot_low and self.data.Volume[pivot_idx] > self.vol_sma[pivot_idx]:
                self.potential_breaker_low = pivot_low
                print(f"✨ Potential bearish OB (demand zone) at low: {self.potential_breaker_low}, Vol filter passed")

            # Pivot high detection
            pivot_high = self.data.High[pivot_idx]
            is_pivot_high = True
            # Check left bars
            for i in range(left_start, left_end):
                if pivot_high <= self.data.High[i]:
                    is_pivot_high = False
                    break
            # Check right bars
            if is_pivot_high:
                for i in range(right_start, right_end):
                    if i < 0 and pivot_high <= self.data.High[i]:  # Ensure i is valid negative index
                        is_pivot_high = False
                        break
            # Volume filter for quality
            if is_pivot_high and self.data.Volume[pivot_idx] > self.vol_sma[pivot_idx]:
                self.potential_breaker_high = pivot_high
                print(f"✨ Potential bullish OB (supply zone) at high: {self.potential_breaker_high}, Vol filter passed")

        # 🌙 Detect break of potential breaker low
        if self.potential_breaker_low is not None:
            if current_low < self.potential_breaker_low:  # Broken below
                print(f"🚨 Bearish OB broken at {self.potential_breaker_low}")
                self.broken_low_level = self.potential_breaker_low
                self.waiting_long_reversal = True
                self.potential_breaker_low = None

        # 🌙 Detect break of potential breaker high
        if self.potential_breaker_high is not None:
            if current_high > self.potential_breaker_high:  # Broken above
                print(f"🚨 Bullish OB broken at {self.potential_breaker_high}")
                self.broken_high_level = self.potential_breaker_high
                self.waiting_short_reversal = True
                self.potential_breaker_high = None

        # 🌙 Check for reversal after break (allows delay beyond same bar for more realistic setups)
        if self.waiting_long_reversal and self.broken_low_level is not None:
            if (current_close > current_ema and self.data.Close[-2] <= self.ema[-2] and
                current_close > current_ema_long):  # Added long EMA trend filter
                self.breaker_long_level = self.broken_low_level
                self.breaker_long_active = True
                self.waiting_long_reversal = False
                print(f"🌙 Long breaker block activated at {self.breaker_long_level} after failure and reversal!")
        
        if self.waiting_short_reversal and self.broken_high_level is not None:
            if (current_close < current_ema and self.data.Close[-2] >= self.ema[-2] and
                current_close < current_ema_long):  # Added long EMA trend filter
                self.breaker_short_level = self.broken_high_level
                self.breaker_short_active = True
                self.waiting_short_reversal = False
                print(f"🌙 Short breaker block activated at {self.breaker_short_level} after failure and reversal!")

        # 🌙 Entry logic with enhanced filters
        if not self.position:
            # Bullish entry on return to long breaker with trend and body confirmation
            if (self.breaker_long_active and current_close > current_ema and current_close > current_ema_long):
                breaker = self.breaker_long_level
                zone_low = breaker - self.breaker_zone_mult * current_atr
                zone_high = breaker + self.breaker_zone_mult * current_atr
                # Touch zone with strong bullish rejection candle
                body = (current_close - current_open) / current_atr
                if (current_low <= zone_high and current_low >= zone_low and
                    current_close > current_open and current_close > zone_high and body > self.min_body_mult):
                    sl = breaker - current_atr  # 🌙 Optimized: Tighter SL based on breaker level - ATR
                    entry = current_close
                    stop_distance = entry - sl
                    risk_amount = self.equity * self.risk_pct
                    position_size = int(round(risk_amount / stop_distance))
                    tp = entry + self.rr_ratio * stop_distance
                    self.buy(size=position_size, sl=sl, tp=tp)
                    print(f"🚀 MOON DEV LONG ENTRY: Price {entry:.2f}, Breaker {breaker:.2f}, Size {position_size}, SL {sl:.2f}, TP {tp:.2f}")
                    self.breaker_long_active = False
                    self.breaker_long_level = None  # Clean up

            # Bearish entry on return to short breaker with trend and body confirmation
            if (self.breaker_short_active and current_close < current_ema and current_close < current_ema_long):
                breaker = self.breaker_short_level
                zone_low = breaker - self.breaker_zone_mult * current_atr
                zone_high = breaker + self.breaker_zone_mult * current_atr
                # Touch zone with strong bearish rejection candle
                body = (current_open - current_close) / current_atr
                if (current_high >= zone_low and current_high <= zone_high and
                    current_close < current_open and current_close < zone_low and body > self.min_body_mult):
                    sl = breaker + current_atr  # 🌙 Optimized: Tighter SL based on breaker level + ATR
                    entry = current_close
                    stop_distance = sl - entry
                    risk_amount = self.equity * self.risk_pct
                    position_size = int(round(risk_amount / stop_distance))
                    tp = entry - self.rr_ratio * stop_distance
                    self.sell(size=position_size, sl=sl, tp=tp)
                    print(f"🚀 MOON DEV SHORT ENTRY: Price {entry:.2f}, Breaker {breaker:.2f}, Size {position_size}, SL {sl:.2f}, TP {tp:.2f}")
                    self.breaker_short_active = False
                    self.breaker_short_level = None  # Clean up

        # 🌙 Invalidation: Tightened threshold for quicker exits on invalidation
        if self.position and self.breaker_long_level is not None:
            # For long position, invalidate if closes below breaker
            if self.position.is_long and current_close < self.breaker_long_level - 0.5 * current_atr:
                self.position.close()
                print(f"⚠️ Long position invalidated: Closed below breaker {self.breaker_long_level:.2f}")
        if self.position and self.breaker_short_level is not None:
            # For short position, invalidate if closes above breaker
            if self.position.is_short and current_close > self.breaker_short_level + 0.5 * current_atr:
                self.position.close()
                print(f"⚠️ Short position invalidated: Closed above breaker {self.breaker_short_level:.2f}")

# 🌙 MOON DEV'S BACKTEST RUNNER 🚀
if __name__ == "__main__":
    import sys
    import os
    from backtesting import Backtest
    import pandas as pd

    # 🌙 Run standard backtest and print stats (REQUIRED for parsing!)
    print("\n🌙 Running initial backtest for stats extraction...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '../../../rbi/BTC-USD-15m.csv')
    data = pd.read_csv(data_path)
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data = data.set_index(pd.to_datetime(data['datetime']))
    data.index.name = 'Datetime'

    bt = Backtest(data, MitigativeBreaker, cash=1_000_000, commission=0.002)
    stats = bt.run()

    # 🌙 CRITICAL: Print full stats for Moon Dev's parser!
    print("\n" + "="*80)
    print("📊 BACKTEST STATISTICS (Moon Dev's Format)")
    print("="*80)
    print(stats)
    print(stats._strategy)
    print("="*80 + "\n")

    print("🌙 Multi-data testing skipped - module not available. Standard backtest complete! ✨")