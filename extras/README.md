# Extras (optional ML layer)

These modules are **not** part of the zero-dependency core. They import optional
third-party packages only when available and degrade gracefully otherwise.

## Install
```bash
pip install scikit-learn xgboost lightgbm optuna shap \
    stable-baselines3 gymnasium scipy numpy pandas
```

## Modules
- `availability.py` — dependency report (`python -m extras.availability`).
- `ml_models.py` — classifier training/prediction/feature importance/SHAP.
- `hpo.py` — Optuna hyperparameter optimization wrapper.
- `rl_execution.py` — PPO execution helper (stable-baselines3).

## Usage
```python
from extras.ml_models import is_available, train_classifier
if is_available():
    model, info = train_classifier(X, y, kind="logistic")
```

Nothing in `engines/`, `utils/`, `risk/`, `monitoring/`, `backtests/`, `data/`,
`execution/` imports from `extras/`, so the core stays stdlib-only.