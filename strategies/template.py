"""RSI + Bollinger Bands template (zero-dep)."""
PARAMS = {"rsi_period": 14, "rsi_oversold": 30, "rsi_overbought": 70,
          "bb_period": 20, "bb_dev": 2.0, "stake": 100}

def _rsi(prices, period):
    if len(prices) < period+1: return 50.0
    gains, losses = [], []
    for i in range(1, period+1):
        d = prices[-i] - prices[-i-1]
        (gains if d > 0 else losses).append(abs(d))
    ag = sum(gains)/period if gains else 0
    al = sum(losses)/period if losses else 0
    if al == 0: return 100.0
    return 100 - (100/(1+ag/al))

def make_rule(params=None):
    p = dict(PARAMS)
    if params: p.update(params)
    rp, bbp, dev = p["rsi_period"], p["bb_period"], p["bb_dev"]
    def rule(i, prices, position):
        if i < max(rp, bbp): return "hold"
        rsi = _rsi(prices[:i+1], rp)
        window = prices[i-bbp+1:i+1]
        mean = sum(window)/len(window)
        std = (sum((x-mean)**2 for x in window)/len(window))**0.5
        lower = mean - dev*std
        upper = mean + dev*std
        if not position and (rsi < p["rsi_oversold"] or prices[i] < lower):
            return "buy"
        if position and (rsi > p["rsi_overbought"] or prices[i] > upper):
            return "sell"
        return "hold"
    return rule