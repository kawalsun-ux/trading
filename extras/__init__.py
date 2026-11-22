"""Optional ML extras for Apex Quant (zero-dep core; heavy deps guarded).

These modules are NOT part of the zero-dependency core. They import optional
third-party packages (scikit-learn, xgboost, lightgbm, optuna, shap,
stable-baselines3, gymnasium, scipy) only when available, and degrade
gracefully otherwise. Install extras with:

    pip install scikit-learn xgboost lightgbm optuna shap \
        stable-baselines3 gymnasium scipy

Nothing in `engines/`, `utils/`, `risk/`, `monitoring/`, or `backtests/`
imports from this package, so the core stays stdlib-only.
"""

__all__ = ["availability", "ml_models", "hpo", "rl_execution"]


def available():
    """Return dict of optional dependency -> bool."""
    out = {}
    for name in ("sklearn", "xgboost", "lightgbm", "optuna", "shap",
                 "stable_baselines3", "gymnasium", "scipy", "numpy", "pandas"):
        try:
            __import__(name)
            out[name] = True
        except ImportError:
            out[name] = False
    return out