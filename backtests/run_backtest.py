"""Run a backtest for the MA crossover strategy."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import backtrader as bt
import yfinance as yf
import pandas as pd
from strategies.ma_crossover import MACrossover

def main():
    ticker = "SPY"
    start, end = "2018-01-01", "2024-12-31"
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.dropna()
    data = bt.feeds.PandasData(dataname=df)

    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(MACrossover)
    cerebro.broker.setcash(100000.0)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addsizer(bt.sizers.FixedSize, stake=100)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="dd")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")

    print(f"Start value: {cerebro.broker.getvalue():.2f}")
    results = cerebro.run()
    strat = results[0]
    print(f"End value:   {cerebro.broker.getvalue():.2f}")
    print(f"Sharpe:      {strat.analyzers.sharpe.get_analysis().get('sharperatio')}")
    dd = strat.analyzers.dd.get_analysis()
    print(f"Max DD:      {dd.get('max', {}).get('drawdown'):.2f}%")
    tr = strat.analyzers.trades.get_analysis()
    print(f"Trades:      {tr.get('total', {}).get('total', 0)}")

if __name__ == "__main__":
    main()