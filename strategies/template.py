"""Parameterized strategy template (RSI + Bollinger Bands mean reversion).

Tunable params exposed for walk-forward optimization:
  rsi_period, rsi_oversold, rsi_overbought,
  bb_period, bb_dev, stake
"""
import backtrader as bt

class RsiBbTemplate(bt.Strategy):
    params = (
        ("rsi_period", 14),
        ("rsi_oversold", 30),
        ("rsi_overbought", 70),
        ("bb_period", 20),
        ("bb_dev", 2.0),
        ("stake", 100),
    )

    def __init__(self):
        self.rsi = bt.indicators.RSI(self.data.close, period=self.p.rsi_period)
        self.bb = bt.indicators.BollingerBands(self.data.close, period=self.p.bb_period,
                                                devfactor=self.p.bb_dev)
        self.cross_up = bt.indicators.CrossOver(self.data.close, self.bb.lines.bot)
        self.cross_down = bt.indicators.CrossOver(self.data.close, self.bb.lines.top)

    def next(self):
        if not self.position:
            if self.rsi[0] < self.p.rsi_oversold or self.cross_up[0] > 0:
                self.buy(size=self.p.stake)
        else:
            if self.rsi[0] > self.p.rsi_overbought or self.cross_down[0] < 0:
                self.close()