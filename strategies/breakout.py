"""Breakout strategy (zero-dep)."""
PARAMS = {"period": 20, "stake": 100}

def make_rule(params=None):
    p = dict(PARAMS)
    if params: p.update(params)
    per = p["period"]
    def rule(i, prices, position):
        if i < per: return "hold"
        hi = max(prices[i-per:i])
        lo = min(prices[i-per:i])
        if not position and prices[i] > hi: return "buy"
        if position and prices[i] < lo: return "sell"
        return "hold"
    return rule