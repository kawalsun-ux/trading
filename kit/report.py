"""Performance metrics (stdlib)."""
import math

def returns(equity):
    r = []
    for i in range(1, len(equity)):
        if equity[i-1] != 0:
            r.append((equity[i] - equity[i-1]) / equity[i-1])
    return r

def sharpe(equity, rf=0.0, periods_per_year=252):
    r = returns(equity)
    if not r:
        return 0.0
    mean = sum(r) / len(r)
    var = sum((x - mean) ** 2 for x in r) / len(r)
    sd = math.sqrt(var)
    if sd == 0:
        return 0.0
    return (mean - rf / periods_per_year) / sd * math.sqrt(periods_per_year)

def max_drawdown(equity):
    peak = equity[0]
    mdd = 0.0
    for v in equity:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak else 0.0
        if dd > mdd:
            mdd = dd
    return mdd

def win_rate(trades):
    # trades: list of (action, idx, price, units)
    buys = [t for t in trades if t[0] == 'buy']
    sells = [t for t in trades if t[0] == 'sell']
    wins = 0
    pairs = min(len(buys), len(sells))
    for i in range(pairs):
        if sells[i][2] > buys[i][2]:
            wins += 1
    return (wins / pairs) if pairs else 0.0

def summary(result):
    eq = result["equity"]
    tr = result["trades"]
    return {
        "initial": result["initial"],
        "final": result["final"],
        "return_pct": (result["final"] / result["initial"] - 1) * 100,
        "sharpe": sharpe(eq),
        "max_drawdown_pct": max_drawdown(eq) * 100,
        "num_trades": len(tr),
        "win_rate": win_rate(tr),
    }