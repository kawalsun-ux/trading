"""Pairs trading (spread z-score) strategy (zero-dep)."""
PARAMS = {"period": 20, "z_entry": 2.0, "z_exit": 0.5, "stake": 100}

def make_rule(params=None):
    p = dict(PARAMS)
    if params: p.update(params)
    per = p["period"]
    def rule(i, prices, position):
        if i < per: return "hold"
        window = prices[i-per:i]
        mean = sum(window)/len(window)
        var = sum((x-mean)**2 for x in window)/len(window)
        std = var**0.5
        if std == 0: return "hold"
        z = (prices[i]-mean)/std
        if not position and z < -p["z_entry"]: return "buy"
        if position and z > p["z_exit"]: return "sell"
        return "hold"
    return rule