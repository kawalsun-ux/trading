"""Realized covariance/correlation/beta helpers (zero-dep, stdlib)."""

import math


def realized_covariance(x, y):
    n = min(len(x or []), len(y or []))
    if n < 2:
        return 0.0
    xs = [float(v) for v in (x or [])[:n]]
    ys = [float(v) for v in (y or [])[:n]]
    mx = sum(xs) / n
    my = sum(ys) / n
    return sum((xi - mx) * (yi - my) for xi, yi in zip(xs, ys)) / n


def realized_correlation(x, y):
    n = min(len(x or []), len(y or []))
    if n < 2:
        return 0.0
    xs = [float(v) for v in (x or [])[:n]]
    ys = [float(v) for v in (y or [])[:n]]
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(xs, ys))
    dx = math.sqrt(sum((xi - mx) ** 2 for xi in xs))
    dy = math.sqrt(sum((yi - my) ** 2 for yi in ys))
    if dx <= 0 or dy <= 0:
        return 0.0
    return num / (dx * dy)


def realized_beta(asset, market):
    cov = realized_covariance(asset, market)
    var_m = realized_covariance(market, market)
    if var_m <= 0:
        return 0.0
    return cov / var_m