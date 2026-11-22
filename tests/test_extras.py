"""Extras (optional ML) graceful-degradation tests."""
import unittest

from extras import available
from extras.availability import report, missing
from extras.ml_models import is_available, train_classifier, predict, feature_importance, shap_values
from extras.hpo import is_available as hpo_avail, optimize
from extras.rl_execution import is_available as rl_avail, make_ppo


class TestExtras(unittest.TestCase):
    def test_availability(self):
        a = available()
        self.assertIsInstance(a, dict)
        self.assertIn("sklearn", a)

    def test_report(self):
        r = report()
        self.assertIn("Optional dependency availability", r)

    def test_missing_list(self):
        m = missing()
        self.assertIsInstance(m, list)

    def test_ml_models_degrade(self):
        # deps not installed in this env -> should be False and return None/error
        self.assertFalse(is_available())
        model, info = train_classifier([[1, 2], [3, 4]], [0, 1])
        self.assertIsNone(model)
        self.assertIsInstance(info, str)
        self.assertIsNone(predict(None, [[1, 2]]))
        self.assertIsNone(feature_importance(None))
        self.assertIsNone(shap_values(None, None))

    def test_hpo_degrade(self):
        self.assertFalse(hpo_avail())
        params, info = optimize(lambda t: 0.0, n_trials=1)
        self.assertIsNone(params)

    def test_rl_degrade(self):
        self.assertFalse(rl_avail())
        model, info = make_ppo(None)
        self.assertIsNone(model)


if __name__ == "__main__":
    unittest.main()