"""Functional trading research & execution pipeline (zero-dep)."""
import sys, os, time, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from kit import safety, backtest, report, store, dashboard, pool

def main():
    print("=" * 60)
    print("TRADING RESEARCH & EXECUTION PIPELINE (test mode)")
    print("=" * 60)

    # 1. Safety check on a mock trade
    print("\n[1] Safety checks (4 checks before any trade)")
    token = "So11111111111111111111111111111111111111112"
    known = {token}
    balance, required = 5.0, 1.0
    quote_ts = time.time()
    expected, actual = 100.0, 100.3
    try:
        safety.run_all(token, known, balance, required, quote_ts, expected, actual)
        print("    ALL 4 CHECKS PASSED -> trade may be signed")
        store.log_trade("buy", "SOL", actual, 1.0, status="filled", note="safety passed")
    except safety.SafetyError as e:
        print("    BLOCKED:", e)
        store.log_trade("buy", "SOL", actual, 1.0, status="rejected", note=str(e))

    # 2. Backtest on past data
    print("\n[2] Backtest on past data (MA crossover)")
    prices = [100 + i*0.1 + (i % 7 - 3)*0.5 for i in range(200)]
    def rule(i, ps, pos):
        if i > 5 and ps[i] > ps[i-5] and not pos: return 'buy'
        if i > 5 and ps[i] < ps[i-5] and pos: return 'sell'
        return 'hold'
    res = backtest.run_backtest(prices, rule)
    s = report.summary(res)
    print("    " + json.dumps(s, indent=2).replace("\n", "\n    "))

    # 3. Dashboard
    print("\n[3] Generate dashboard")
    entries = [i for i, t in enumerate(res["trades"]) if t[0] == 'buy']
    # map trade indices to price indices
    e_idx = [t[1] for t in res["trades"] if t[0] == 'buy']
    x_idx = [t[1] for t in res["trades"] if t[0] == 'sell']
    html = dashboard.render("Trading Research Dashboard", prices, entries=e_idx, exits=x_idx)
    out = os.path.join(os.path.dirname(__file__), "reports", "dashboard.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w") as f:
        f.write(html)
    print(f"    wrote {out}")

    print("\n" + "=" * 60)
    print("RECENT TRADE LOG")
    print("=" * 60)
    for row in store.recent(10):
        print(" ", row)
    print("\nDone. Test mode only — no real money used.")

if __name__ == "__main__":
    main()