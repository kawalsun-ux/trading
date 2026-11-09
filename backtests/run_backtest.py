"""Run a backtest for a named strategy (zero-dep)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit.backtest import run_backtest
from kit.report import summary
import importlib

STRATS = {
    "ma_crossover": "strategies.ma_crossover",
    "rsi_bb": "strategies.template",
    "momentum": "strategies.momentum",
    "mean_reversion": "strategies.mean_reversion",
    "breakout": "strategies.breakout",
    "pairs": "strategies.pairs",
    "scalp_micro": "strategies.ma_crossover",
    "arb_spread": "strategies.ma_crossover",
}

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", default="ma_crossover")
    ap.add_argument("--n", type=int, default=200)
    args = ap.parse_args()
    mod = importlib.import_module(STRATS.get(args.strategy, "strategies.ma_crossover"))
    rule = mod.make_rule()
    prices = [100 + i*0.1 + (i % 7 - 3)*0.5 for i in range(args.n)]
    res = run_backtest(prices, rule)
    s = summary(res)
    print(json.dumps({"strategy": args.strategy, "metrics": s}, indent=2))

if __name__ == "__main__":
    main()