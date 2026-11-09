"""MA crossover strategy (zero-dep, stdlib)."""
PARAMS = {"fast": 10, "slow": 30, "stake": 100}

def make_rule(params=None):
    p = dict(PARAMS); 
    if params: p.update(params)
    fast, slow = p["fast"], p["slow"]
    def rule(i, prices, position):
        if i < slow:
            return "hold"
        fast_ma = sum(prices[i-fast+1:i+1]) / fast
        slow_ma = sum(prices[i-slow+1:i+1]) / slow
        prev_fast = sum(prices[i-fast:i]) / fast
        prev_slow = sum(prices[i-slow:i]) / slow
        if not position and prev_fast <= prev_slow and fast_ma > slow_ma:
            return "buy"
        if position and prev_fast >= prev_slow and fast_ma < slow_ma:
            return "sell"
        return "hold"
    return rule