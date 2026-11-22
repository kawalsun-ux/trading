"""Optional RL execution helpers (guarded stable-baselines3/gymnasium)."""

def _try_import(name):
    try:
        return __import__(name)
    except ImportError:
        return None


_sb3 = _try_import("stable_baselines3")
_gym = _try_import("gymnasium")


def is_available():
    return _sb3 is not None and _gym is not None


def make_ppo(env):
    if not is_available():
        return None, "stable-baselines3/gymnasium not installed"
    try:
        model = _sb3.PPO("MlpPolicy", env, verbose=0)
        return model, "ok"
    except Exception as e:
        return None, str(e)