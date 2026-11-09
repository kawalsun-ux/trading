"""Apex Quant CLI (zero-dep)."""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from kit import connector, safety, pool, backtest, report, store, dashboard

def cmd_check(args):
    try:
        safety.run_all(args.token, set(args.known.split(",")), args.balance, args.required,
                      args.quote_ts, args.expected, args.actual)
        print("ALL CHECKS PASSED")
    except safety.SafetyError as e:
        print("BLOCKED:", e)

def cmd_backtest(args):
    import random
    prices = [100 + i*0.1 + (i % 7 - 3)*0.5 for i in range(200)]
    def rule(i, ps, pos):
        if i > 5 and ps[i] > ps[i-5] and not pos:
            return 'buy'
        if i > 5 and ps[i] < ps[i-5] and pos:
            return 'sell'
        return 'hold'
    res = backtest.run_backtest(prices, rule)
    print(json.dumps(report.summary(res), indent=2))

def cmd_dashboard(args):
    import random
    prices = [100 + i*0.1 + (i % 7 - 3)*0.5 for i in range(200)]
    html = dashboard.render("Demo", prices, entries=[20, 60], exits=[45, 90])
    out = args.out or "dashboard.html"
    with open(out, "w") as f:
        f.write(html)
    print("wrote", out)

def cmd_logdemo(args):
    store.log_trade("buy", "SOL", 100.0, 1.5, status="filled", note="demo")
    print(store.recent(5))

def main():
    p = argparse.ArgumentParser(prog="kit")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check"); 
    c.add_argument("--token", required=True); c.add_argument("--known", required=True)
    c.add_argument("--balance", type=float, required=True); c.add_argument("--required", type=float, required=True)
    c.add_argument("--quote-ts", type=float, required=True); c.add_argument("--expected", type=float, required=True)
    c.add_argument("--actual", type=float, required=True)
    c.set_defaults(func=cmd_check)
    b = sub.add_parser("backtest"); b.set_defaults(func=cmd_backtest)
    d = sub.add_parser("dashboard"); d.add_argument("--out", default="dashboard.html"); d.set_defaults(func=cmd_dashboard)
    l = sub.add_parser("logdemo"); l.set_defaults(func=cmd_logdemo)
    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()