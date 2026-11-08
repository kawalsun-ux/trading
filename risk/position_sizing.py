"""Position sizing helpers."""
def fixed_fraction(capital: float, risk_pct: float, entry: float, stop: float) -> float:
    risk_capital = capital * risk_pct
    per_unit_risk = abs(entry - stop)
    if per_unit_risk <= 0:
        return 0.0
    return risk_capital / per_unit_risk

def kelly(win_rate: float, avg_win: float, avg_loss: float) -> float:
    if avg_loss == 0:
        return 0.0
    b = avg_win / abs(avg_loss)
    q = 1 - win_rate
    f = (b * win_rate - q) / b
    return max(0.0, min(f, 1.0))