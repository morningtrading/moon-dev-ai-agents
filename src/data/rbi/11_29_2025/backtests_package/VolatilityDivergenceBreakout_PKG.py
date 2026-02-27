import pandas as pd
import numpy as np
import talib
from backtesting import Strategy, Backtest

# Load data
data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
data = pd.read_csv(data_path)
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

class VolatilityDivergenceBreakout(Strategy):
    kc_multiplier = 1.8
    divergence_lookback = 30
    divergence_validity = 10
    
    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low

        # Indicators wrapped with self.I (talib)
        self.ema200 = self.I(talib.EMA, close, timeperiod=200)
        self.rsi = self.I(talib.RSI, close, timeperiod=14)
        self.bb_upper, self.bb_mid, self.bb_lower = self.I(talib.BBANDS, close, timeperiod=20, nbdevup=2, nbdevdn=2)
        self.ema20 = self.I(talib.EMA, close, timeperiod=20)
        self.atr20 = self.I(talib.ATR, high, low, close, timeperiod=20)

        # Keltner Channel derived from EMA and ATR
        self.kc_upper = self.ema20 + (self.atr20 * self.kc_multiplier)
        self.kc_lower = self.ema20 - (self.atr20 * self.kc_multiplier)

        # Bollinger Band width and its MA using talib via self.I
        self.bb_width = self.bb_upper - self.bb_lower
        self.bb_width_ma = self.I(talib.SMA, self.bb_width, timeperiod=20)

    def next(self):
        # Trend filter check
        if not (self.data.Close[-1] > self.ema200[-1] and (self.ema200[-1] > self.ema200[-2])):
            print("🌙 Trend filter not met — standing by. ✨")
            return
            
        # Detect RSI divergence (informational)
        self.detect_divergence()
        
        # Volatility expansion required
        if self.bb_width[-1] <= 1.2 * self.bb_width_ma[-1] or self.bb_width[-1] <= self.bb_width[-2]:
            print("🌙 Volatility expansion not sufficient yet — patience, stargazer. 🌌")
            return
        
        # Breakout condition
        if self.data.Close[-1] > self.kc_upper[-1]:
            atr_val = self.atr20[-1]
            stop_loss = min(
                self.data.Low[-1] - 0.5 * atr_val,
                self.kc_lower[-1] - 0.25 * atr_val
            )
            risk_per_unit = max(self.data.Close[-1] - stop_loss, 1e-8)
            position_size = int(round(1000000 / risk_per_unit))
            self.buy(size=position_size, sl=stop_loss)
            print(f"🌙 🚀 Going long at {self.data.Close[-1]} with size {position_size} and stop loss {stop_loss} 🌟")

        # Exit on correction
        if self.position and self.data.Close[-1] < self.kc_lower[-1]:
            self.position.close()
            print("✨ Exiting position due to correction below the lower Keltner band 🌑")

    def detect_divergence(self):
        # Simple bullish divergence detection within lookback window
        look = min(self.divergence_lookback, len(self.data.Close))
        if look < 5:
            return False

        found = False
        for offset in range(2, look):
            i = -offset
            prev = i - 2
            if self.data.Low[i] < self.data.Low[prev] and self.rsi[i] > self.rsi[prev]:
                print(f"🌟 Bullish RSI divergence detected between bars {len(self.data.Close)+prev} and {len(self.data.Close)+i} 👀")
                found = True
                break
        if not found:
            print("🌙 No bullish divergence spotted in the recent window. ✨")
        return found

bt = Backtest(data, VolatilityDivergenceBreakout, cash=1000000, commission=.002)
stats = bt.run()
print(stats)