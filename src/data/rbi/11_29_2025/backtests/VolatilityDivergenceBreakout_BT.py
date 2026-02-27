import pandas as pd
import numpy as np
import talib
from backtesting import Strategy, Backtest
from backtesting.lib import crossover

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
        self.ema200 = self.I(talib.EMA, self.data.Close, timeperiod=200)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        self.bb_upper, self.bb_mid, self.bb_lower = self.I(talib.BBANDS, self.data.Close, timeperiod=20, nbdevup=2, nbdevdn=2)
        self.kc_upper, self.kc_mid, self.kc_lower = self.keltner_channel()

    def keltner_channel(self):
        ema20 = talib.EMA(self.data.Close, timeperiod=20)
        atr20 = talib.ATR(self.data.High, self.data.Low, self.data.Close, timeperiod=20)
        kc_upper = ema20 + (atr20 * self.kc_multiplier)
        kc_lower = ema20 - (atr20 * self.kc_multiplier)
        return kc_upper, ema20, kc_lower

    def next(self):
        # Trend filter check
        if not (self.data.Close[-1] > self.ema200[-1] and (self.ema200[-1] > self.ema200[-2])):
            return
            
        # Detect RSI divergence
        self.detect_divergence()
        
        # Volatility expansion required
        bb_width = self.bb_upper - self.bb_lower
        bb_width_ma = talib.SMA(bb_width, timeperiod=20)
        if bb_width[-1] <= 1.2 * bb_width_ma[-1] or bb_width[-1] <= bb_width[-2]:
            return
        
        # Breakout condition
        if self.data.Close[-1] > self.kc_upper[-1]:
            stop_loss = min(self.data.Low[-1] - 0.5 * talib.ATR(self.data.High, self.data.Low, self.data.Close, timeperiod=20)[-1],
                            self.kc_lower[-1] - 0.25 * talib.ATR(self.data.High, self.data.Low, self.data.Close, timeperiod=20)[-1])
            position_size = int(round(1000000 / (self.data.Close[-1] - stop_loss)))
            self.buy(size=position_size,
                     sl=stop_loss)
            print(f"🌙 🚀 Going long at {self.data.Close[-1]} with size {position_size} and stop loss {stop_loss} 🌟")

        # Exit on correction
        if self.position and self.data.Close[-1] < self.kc_lower[-1]:
            self.position.close()
            print("✨ Exiting position due to correction below the lower Keltner band 🌑")

    def detect_divergence(self):
        lows = talib.MIN(self.data.Low, timeperiod=self.divergence_lookback)
        rsi_lows = self.rsi[-self.divergence_lookback:]
        for i in range(self.divergence_lookback - 2, len(lows) - 2):
            if lows[i] < lows[i - 2] and rsi_lows[i] > rsi_lows[i - 2]:
                print(f"🌟 Bullish divergence detected between bars {i-2} and {i} 👀")

bt = Backtest(data, VolatilityDivergenceBreakout, cash=1000000, commission=.002)
stats = bt.run()
print(stats)