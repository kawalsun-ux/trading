"""Stdlib backtester."""
import math

def run_backtest(prices, rule, fee=0.001, initial_cash=100000.0):
    """
    prices: list of floats
    rule: callable(i, prices, position) -> 'buy'|'sell'|'hold'
    returns dict with trades, equity curve, metrics
    """
    cash = initial_cash
    position = 0
    equity = [initial_cash]
    trades = []
    for i in range(1, len(prices)):
        action = rule(i, prices, position)
        p = prices[i]
        if action == 'buy' and position == 0:
            units = int(cash * (1 - fee) / p) if p > 0 else 0
            if units > 0:
                cost = units * p * (1 + fee)
                cash -= cost
                position = units
                trades.append(('buy', i, p, units))
        elif action == 'sell' and position > 0:
            proceeds = position * p * (1 - fee)
            cash += proceeds
            trades.append(('sell', i, p, position))
            position = 0
        equity.append(cash + position * p)
    final = cash + position * prices[-1]
    return {"trades": trades, "equity": equity, "final": final, "initial": initial_cash}