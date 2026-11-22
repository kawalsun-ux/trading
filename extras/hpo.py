"""Optional hyperparameter optimization (guarded optuna import)."""

def _try_import(name):
    try:
        return __import__(name)
    except ImportError:
        return None


_optuna = _try_import("optuna")


def is_available():
    return _optuna is not None


def optimize(objective, n_trials=20, direction="maximize"):
    """Run an optuna study. objective(trial) -> float. Returns best params or None."""
    if _optuna is None:
        return None, "optuna not installed"
    try:
        study = _optuna.create_study(direction=direction)
        study.optimize(objective, n_trials=n_trials)
        return study.best_params, "ok"
    except Exception as e:
        return None, str(e)