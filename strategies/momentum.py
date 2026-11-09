"""Momentum strategy (zero-dep)."""
PARAMS = {"lookback": 20, "threshold": 0.02, "stake": 100}

def make_rule(params=None):
    p = dict(PARAMS)
    if params: p.update(params)
    lb, thr = p["lookback"], p["threshold"]
    def rule(i, prices, position):
        if i < lb + 1: return "hold"
        mom = (prices[i] - prices[i-lb]) / prices[i-lb] if prices[i-lb] else 0
        if not position and mom > thr: return "buy"
        if position and mom < -thr: return "sell"
        return "hold"
    return rule