"""Walk-forward optimization (zero-dep)."""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit.backtest import run_backtest
from kit.report import summary
import importlib

# keep yfinance optional; fallback to synthetic
def load_prices(ticker="SPY", start="2015-01-01", end="2024-12-31"):
    # stdlib-only: try Yahoo Finance via urllib, fallback to synthetic
    try:
        import json, urllib.request
        url = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=5y&interval=1d" % ticker
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            d = json.loads(r.read())
            closes = d["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            out = [float(c) for c in closes if c is not None]
            if out:
                return out
    except Exception:
        pass
    return [100 + i*0.1 + (i % 7 - 3)*0.5 for i in range(2000)]

PARAM_GRID = {
    "rsi_period": [10, 14],
    "rsi_oversold": [25, 30],
    "rsi_overbought": [70, 75],
}

def optimize(prices_train, mod):
    best = None
    keys = list(PARAM_GRID.keys())
    for combo in itertools.product(*PARAM_GRID.values()):
        params = dict(zip(keys, combo))
        try:
            rule = mod.make_rule(params)
            res = run_backtest(prices_train, rule)
            s = summary(res)
            sharpe = s.get("sharpe", 0) or 0
        except Exception:
            continue
        if best is None or sharpe > best[1]["sharpe"]:
            best = (params, s)
    return best

def walk_forward(prices, train=504, test=126, step=126):
    import strategies.template as tmpl
    out = []
    i = train
    n = len(prices)
    while i + test <= n:
        tr = prices[i-train:i]
        te = prices[i:i+test]
        bp, trs = optimize(tr, tmpl)
        rule = tmpl.make_rule(bp)
        tes = summary(run_backtest(te, rule))
        out.append({"train_sharpe": trs["sharpe"], "test_sharpe": tes["sharpe"],
                    "test_end": tes["final"], "params": bp})
        print(f"window {len(out)}: train_sharpe={trs['sharpe']:.3f} test_sharpe={tes['sharpe']:.3f}")
        i += step
    return out

if __name__ == "__main__":
    prices = load_prices()
    res = walk_forward(prices)
    os.makedirs("reports", exist_ok=True)
    with open("reports/walk_forward.json", "w") as f:
        json.dump(res, f, indent=2, default=str)
    print("saved reports/walk_forward.json")