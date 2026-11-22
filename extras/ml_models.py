"""Optional ML model wrappers (guarded imports)."""

def _try_import(name):
    try:
        return __import__(name)
    except ImportError:
        return None


_sklearn = _try_import("sklearn")
_xgb = _try_import("xgboost")
_lgb = _try_import("lightgbm")
_shap = _try_import("shap")
_np = _try_import("numpy")


def is_available():
    return _sklearn is not None


def train_classifier(X, y, kind="logistic"):
    """Train a classifier. Returns (model, info) or (None, error)."""
    if _sklearn is None:
        return None, "scikit-learn not installed"
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    if kind == "logistic":
        m = LogisticRegression(max_iter=1000)
    elif kind == "rf":
        m = RandomForestClassifier(n_estimators=100)
    elif kind == "xgb" and _xgb is not None:
        m = _xgb.XGBClassifier(n_estimators=100, use_label_encoder=False,
                               eval_metric="logloss")
    elif kind == "lgb" and _lgb is not None:
        m = _lgb.LGBMClassifier(n_estimators=100)
    else:
        return None, f"unknown or unavailable kind: {kind}"
    try:
        m.fit(X, y)
    except Exception as e:
        return None, str(e)
    return m, "ok"


def predict(model, X):
    if model is None:
        return None
    try:
        return model.predict(X).tolist() if hasattr(model, "predict") else None
    except Exception:
        return None


def feature_importance(model, X=None):
    """Return feature importances if available, else None."""
    if model is None:
        return None
    if hasattr(model, "feature_importances_"):
        return list(model.feature_importances_)
    if hasattr(model, "coef_"):
        try:
            return [abs(float(v)) for v in model.coef_.ravel()]
        except Exception:
            return None
    return None


def shap_values(model, X):
    if _shap is None or model is None:
        return None
    try:
        explainer = _shap.Explainer(model, X)
        return explainer(X).values
    except Exception:
        return None