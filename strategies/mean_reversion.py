"""Mean reversion strategy (RSI-based, zero-dep)."""
PARAMS = {"rsi_period": 14, "oversold": 30, "overbought": 70, "stake": 100}

def _rsi(prices, period):
    if len(prices) < period + 1: return 50.0
    gains, losses = [], []
    for i in range(1, period+1):
        d = prices[-i] - prices[-i-1]
        (gains if d > 0 else losses).append(abs(d))
    ag = sum(gains)/period if gains else 0
    al = sum(losses)/period if losses else 0
    if al == 0: return 100.0
    rs = ag/al
    return 100 - (100/(1+rs))

def make_rule(params=None):
    p = dict(PARAMS)
    if params: p.update(params)
    def rule(i, prices, position):
        if i < p["rsi_period"]+1: return "hold"
        rsi = _rsi(prices[:i+1], p["rsi_period"])
        if not position and rsi < p["oversold"]: return "buy"
        if position and rsi > p["overbought"]: return "sell"
        return "hold"
    return rule