"""Simple moving-average crossover strategy for backtrader."""
import backtrader as bt

class MACrossover(bt.Strategy):
    params = (("fast", 10), ("slow", 30), ("stake", 100))

    def __init__(self):
        self.fast_ma = bt.indicators.SMA(self.data.close, period=self.p.fast)
        self.slow_ma = bt.indicators.SMA(self.data.close, period=self.p.slow)
        self.crossover = bt.indicators.CrossOver(self.fast_ma, self.slow_ma)

    def next(self):
        if not self.position:
            if self.crossover > 0:
                self.buy(size=self.p.stake)
        elif self.crossover < 0:
            self.close()