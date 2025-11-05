import talib
from backtesting import Strategy, Backtest
import pandas as pd
import sys
import os

class ConfluenceSweep(Strategy):
    n = 15  # 🌙 OPTIMIZED: Reduced swing period from 20 to 15 for more responsive swing detection, capturing fresher support/resistance levels without excessive noise
    rsi_period = 10  # 🌙 OPTIMIZED: Shortened RSI period from 14 to 10 for faster momentum signals, improving entry timing in volatile crypto markets
    atr_period = 10  # 🌙 OPTIMIZED: Reduced ATR period from 14 to 10 to better adapt to short-term volatility on 15m timeframe
    vol_mult = 2.5  # 🌙 OPTIMIZED: Increased volume spike multiplier from 2.0 to 2.5 for even stronger volume confirmation, filtering out weaker sweeps
    confluence_threshold = 3  # 🌙 OPTIMIZED: Lowered threshold from 4 to 3 (now out of 5 factors) to increase trade frequency while maintaining quality, addressing low trade count contributing to negative returns
    risk_percent = 0.01  # 🌙 OPTIMIZED: Increased risk per trade from 0.5% to 1% to allow larger position sizes and higher potential returns, balanced with improved filters
    rr_ratio = 4  # 🌙 OPTIMIZED: Further increased reward:risk from 3:1 to 4:1 to target larger profitable moves in trending conditions
    max_pending_bars = 5  # 🌙 OPTIMIZED: Reduced pending confirmation window from 10 to 5 bars for quicker entries, reducing opportunity cost in fast-moving markets
    buffer_mult = 0.2  # 🌙 OPTIMIZED: Further tightened stop buffer from 0.3 to 0.2 ATR for tighter risk control, minimizing losses on false breakouts

    def init(self):
        # 🌙 OPTIMIZED: Switched to talib.MAX/MIN for efficiency and accuracy in swing detection
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=self.n)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.n)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.obv = self.I(talib.OBV, self.data.Close, self.data.Volume)
        self.avg_vol = self.I(talib.SMA, self.data.Volume, timeperiod=self.n)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        # 🌙 OPTIMIZED: Added EMA200 trend filter to only trade in favorable market regimes (long above EMA, short below), avoids counter-trend trades in choppy/ranging markets
        self.ema200 = self.I(talib.EMA, self.data.Close, timeperiod=200)
        
        # 🌙 NEW: Added ADX for trend strength filter to avoid ranging markets, only trade when ADX > 20 indicating sufficient trend momentum
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
        
        # 🌙 NEW: Added OBV SMA for better volume flow confirmation, replacing simple comparison to detect sustained accumulation/distribution
        self.obv_sma = self.I(talib.SMA, self.obv, timeperiod=5)
        
        self.pending_long = False
        self.pending_short = False
        self.sweep_index_long = 0
        self.sweep_index_short = 0

    def next(self):
        if len(self.data) < max(self.n, self.rsi_period, self.atr_period, 200, 14, 5) + 10:  # 🌙 OPTIMIZED: Updated buffer to cover all indicators including ADX and OBV SMA for proper initialization
            return

        # Reset pending if too old
        if self.pending_long and (len(self.data) - self.sweep_index_long > self.max_pending_bars):
            self.pending_long = False
            print("🌙 Long pending expired 🔄")
        if self.pending_short and (len(self.data) - self.sweep_index_short > self.max_pending_bars):
            self.pending_short = False
            print("🌙 Short pending expired 🔄")

        current_idx = len(self.data)
        # Long sweep detection
        if not self.position and not self.pending_long and not self.pending_short:
            support = self.swing_low[-2]
            if pd.isna(support) or pd.isna(self.rsi[-1]) or pd.isna(self.atr[-1]) or pd.isna(self.ema200[-1]) or pd.isna(self.adx[-1]) or pd.isna(self.obv_sma[-1]):
                return

            # 🌙 OPTIMIZED: Added trend filter - only long if price above EMA200 for uptrend confirmation
            if self.data.Close[-1] <= self.ema200[-1]:
                return

            # 🌙 NEW: Added ADX trend strength filter to ensure sufficient market momentum, avoiding choppy conditions
            if self.adx[-1] < 20:
                return

            # Confluence count (now 5 factors for better signal quality)
            confluence = 0
            volume_spike = self.data.Volume[-1] > self.avg_vol[-1] * self.vol_mult
            if volume_spike:
                confluence += 1
            # 🌙 OPTIMIZED: Further tightened RSI oversold from <30 to <25 for stronger momentum reversal signals
            rsi_oversold = self.rsi[-1] < 25
            if rsi_oversold:
                confluence += 1
            # 🌙 OPTIMIZED: Improved OBV confirmation using SMA crossover instead of single bar for sustained volume flow detection
            obv_accumulating = self.obv[-1] > self.obv_sma[-1]
            if obv_accumulating:
                confluence += 1
            # 🌙 OPTIMIZED: Tightened near_level proximity from 1% to 0.5% to focus on precise touches of support
            near_level = abs(self.data.Close[-1] - support) / self.data.Close[-1] < 0.005
            if near_level:
                confluence += 1
            # 🌙 NEW: Added bullish candle filter for long setups to confirm reversal momentum at sweep
            bullish_candle = self.data.Close[-1] > self.data.Open[-1]
            if bullish_candle:
                confluence += 1

            sweep_long = (self.data.Low[-1] < support and 
                          self.data.Close[-1] > support and 
                          confluence >= self.confluence_threshold)

            if sweep_long:
                self.pending_long = True
                self.sweep_index_long = current_idx
                self.sweep_high = self.data.High[-1]
                self.stop_price_long = self.data.Low[-1] - (self.atr[-1] * self.buffer_mult)
                print(f"🌙 Potential LONG sweep at support {support:.2f}, confluence {confluence}, price {self.data.Close[-1]:.2f} ✨")

        # Short sweep detection
        if not self.position and not self.pending_short and not self.pending_long:
            resistance = self.swing_high[-2]
            if pd.isna(resistance) or pd.isna(self.rsi[-1]) or pd.isna(self.atr[-1]) or pd.isna(self.ema200[-1]) or pd.isna(self.adx[-1]) or pd.isna(self.obv_sma[-1]):
                return

            # 🌙 OPTIMIZED: Added trend filter - only short if price below EMA200 for downtrend confirmation
            if self.data.Close[-1] >= self.ema200[-1]:
                return

            # 🌙 NEW: Added ADX trend strength filter to ensure sufficient market momentum, avoiding choppy conditions
            if self.adx[-1] < 20:
                return

            # Confluence count (now 5 factors for better signal quality)
            confluence = 0
            volume_spike = self.data.Volume[-1] > self.avg_vol[-1] * self.vol_mult
            if volume_spike:
                confluence += 1
            # 🌙 OPTIMIZED: Further tightened RSI overbought from >70 to >75 for stronger momentum reversal signals
            rsi_overbought = self.rsi[-1] > 75
            if rsi_overbought:
                confluence += 1
            # 🌙 OPTIMIZED: Improved OBV confirmation using SMA crossover instead of single bar for sustained volume flow detection
            obv_distributing = self.obv[-1] < self.obv_sma[-1]
            if obv_distributing:
                confluence += 1
            # 🌙 OPTIMIZED: Tightened near_level proximity from 1% to 0.5% to focus on precise touches of resistance
            near_level = abs(self.data.Close[-1] - resistance) / self.data.Close[-1] < 0.005
            if near_level:
                confluence += 1
            # 🌙 NEW: Added bearish candle filter for short setups to confirm reversal momentum at sweep
            bearish_candle = self.data.Close[-1] < self.data.Open[-1]
            if bearish_candle:
                confluence += 1

            sweep_short = (self.data.High[-1] > resistance and 
                           self.data.Close[-1] < resistance and 
                           confluence >= self.confluence_threshold)

            if sweep_short:
                self.pending_short = True
                self.sweep_index_short = current_idx
                self.sweep_low = self.data.Low[-1]
                self.stop_price_short = self.data.High[-1] + (self.atr[-1] * self.buffer_mult)
                print(f"🌙 Potential SHORT sweep at resistance {resistance:.2f}, confluence {confluence}, price {self.data.Close[-1]:.2f} ✨")

        # Long entry confirmation
        if self.pending_long and self.data.High[-1] > self.sweep_high:
            entry_approx = self.data.Close[-1]
            sl = self.stop_price_long
            sl_dist = entry_approx - sl
            if sl_dist > 0:
                sl_pct = sl_dist / entry_approx
                size_pct = self.risk_percent / sl_pct
                if size_pct > 1.0:
                    size_pct = 1.0
                tp = entry_approx + (self.rr_ratio * sl_dist)
                self.buy(size=size_pct, sl=sl, tp=tp)
                print(f"🚀 CONFLUENCESWEEP LONG ENTRY at {entry_approx:.2f}, SL {sl:.2f}, TP {tp:.2f}, size {size_pct:.4f} (fraction) 🌙")
            self.pending_long = False

        # Short entry confirmation
        if self.pending_short and self.data.Low[-1] < self.sweep_low:
            entry_approx = self.data.Close[-1]
            sl = self.stop_price_short
            sl_dist = sl - entry_approx
            if sl_dist > 0:
                sl_pct = sl_dist / entry_approx
                size_pct = self.risk_percent / sl_pct
                if size_pct > 1.0:
                    size_pct = 1.0
                tp = entry_approx - (self.rr_ratio * sl_dist)
                self.sell(size=size_pct, sl=sl, tp=tp)
                print(f"🩸 CONFLUENCESWEEP SHORT ENTRY at {entry_approx:.2f}, SL {sl:.2f}, TP {tp:.2f}, size {size_pct:.4f} (fraction) 🌙")
            self.pending_short = False

# 🌙 MOON DEV'S BACKTESTING SCRIPT 🚀
if __name__ == "__main__":
    print("\n🌙 Running initial backtest for stats extraction...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, '..', '..', '..', '..', 'data', 'rbi', 'BTC-USD-15m.csv')
    data = pd.read_csv(data_path)
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data = data.set_index(pd.to_datetime(data['datetime']))

    bt = Backtest(data, ConfluenceSweep, cash=1_000_000, commission=0.002, finalize_trades=True)
    stats = bt.run()

    # 🌙 CRITICAL: Print full stats for Moon Dev's parser!
    print("\n" + "="*80)
    print("📊 BACKTEST STATISTICS (Moon Dev's Format)")
    print("="*80)
    print(stats)
    print("="*80 + "\n")