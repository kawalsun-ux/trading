"""Walk-forward optimization for the template strategy."""
import sys, os, itertools, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import yfinance as yf
import backtrader as bt
from strategies.template import RsiBbTemplate

PARAM_GRID = {
    "rsi_period": [10, 14, 21],
    "rsi_oversold": [25, 30],
    "rsi_overbought": [70, 75],
    "bb_period": [15, 20, 30],
    "bb_dev": [1.5, 2.0, 2.5],
}

def _run(df, params, cash=100000.0):
    data = bt.feeds.PandasData(dataname=df)
    cerebro = bt.Cerebro()
    cerebro.adddata(data)
    cerebro.addstrategy(RsiBbTemplate, **params)
    cerebro.broker.setcash(cash)
    cerebro.broker.setcommission(commission=0.001)
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="dd")
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
    res = cerebro.run()[0]
    sharpe = res.analyzers.sharpe.get_analysis().get("sharperatio") or 0.0
    end_val = cerebro.broker.getvalue()
    dd = res.analyzers.dd.get_analysis().get("max", {}).get("drawdown", 0.0)
    ntrades = res.analyzers.trades.get_analysis().get("total", {}).get("total", 0)
    return {"sharpe": sharpe, "end": end_val, "dd": dd, "trades": ntrades}

def optimize(df_train):
    best = None
    for combo in itertools.product(*PARAM_GRID.values()):
        params = dict(zip(PARAM_GRID.keys(), combo))
        try:
            r = _run(df_train, params)
        except Exception:
            continue
        if best is None or r["sharpe"] > best[1]["sharpe"]:
            best = (params, r)
    return best

def walk_forward(df, train_days=504, test_days=126, step=126):
    out = []
    i = train_days
    n = len(df)
    while i + test_days <= n:
        train = df.iloc[i - train_days:i]
        test = df.iloc[i:i + test_days]
        best_params, train_res = optimize(train)
        test_res = _run(test, best_params)
        out.append({
            "train_end": train.index[-1].date(),
            "test_start": test.index[0].date(),
            "test_end": test.index[-1].date(),
            "params": best_params,
            "train_sharpe": train_res["sharpe"],
            "test_sharpe": test_res["sharpe"],
            "test_end_value": test_res["end"],
            "test_dd": test_res["dd"],
            "test_trades": test_res["trades"],
        })
        print(f"Window {len(out)}: train_sharpe={train_res['sharpe']:.3f} "
              f"test_sharpe={test_res['sharpe']:.3f} end={test_res['end']:.0f}")
        i += step
    return pd.DataFrame(out)

def main():
    ticker = "SPY"
    df = yf.download(ticker, start="2015-01-01", end="2024-12-31",
                     auto_adjust=True, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
    df = df.dropna()
    res = walk_forward(df)
    print("\n=== Summary ===")
    print(res[["train_sharpe", "test_sharpe", "test_end_value", "test_dd", "test_trades"]].describe())
    res.to_csv(os.path.join(os.path.dirname(__file__), "..", "reports", "walk_forward.csv"), index=False)
    print("Saved reports/walk_forward.csv")

if __name__ == "__main__":
    main()