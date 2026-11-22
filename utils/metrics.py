"""Backtest credibility metrics (zero-dep, stdlib)."""

import math


def deflated_sharpe(sharpe, n_trials, skew=0.0, kurtosis=0.0, n_obs=252):
    """Deflated Sharpe Ratio (Bailey & Lopez de Prado).

    Adjusts the observed Sharpe for multiple testing, skew, and kurtosis.
    Returns an approximate DSR (probability that true Sharpe > 0).
    """
    if n_obs <= 1:
        return 0.0
    # expected max Sharpe under null (Euler-Mascheroni approx)
    import math as _m
    euler = 0.5772156649
    if n_trials > 1:
        emax = (1 - euler) * _norm_ppf(1 - 1.0 / n_trials) + euler * _norm_ppf(1 - 1.0 / (n_trials * math.e))
    else:
        emax = 0.0
    # variance of Sharpe estimator
    var_sr = (1.0 + (kurtosis / 4.0) - skew * sharpe / 2.0 + (sharpe ** 2) / 4.0) / (n_obs - 1)
    if var_sr <= 0:
        return 0.0
    sd_sr = math.sqrt(var_sr)
    # DSR = Phi((SR - Emax) / sd_sr) adjusted by skew/kurt (simplified)
    z = (sharpe - emax) / sd_sr if sd_sr > 0 else 0.0
    return _norm_cdf(z)


def _norm_cdf(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_ppf(p):
    # Abramowitz & Stegun approximation
    if p <= 0:
        return -6.0
    if p >= 1:
        return 6.0
    if p < 0.5:
        return -_norm_ppf(1 - p)
    # rational approximation
    t = math.sqrt(-2.0 * math.log(1 - p))
    c0, c1, c2 = 2.515517, 0.802853, 0.010328
    d1, d2, d3 = 1.432788, 0.189269, 0.001308
    return t - (c0 + c1 * t + c2 * t * t) / (1 + d1 * t + d2 * t * t + d3 * t * t * t)


def sharpe_ci(sharpe, n_obs, z=1.96):
    """Approximate confidence interval for Sharpe ratio."""
    if n_obs <= 1:
        return (sharpe, sharpe)
    se = 1.0 / math.sqrt(n_obs)
    return (sharpe - z * se, sharpe + z * se)


def rademacher_bound(n_trials, n_obs):
    """Simplified Rademacher complexity bound (placeholder scale)."""
    if n_obs <= 0:
        return 0.0
    return math.sqrt(2.0 * math.log(max(1, n_trials)) / n_obs)