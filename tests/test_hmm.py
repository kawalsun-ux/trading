"""HMM tests."""
import unittest, random

from utils.hmm import GaussianHMM, detect_regimes, regime_summary


class TestHMM(unittest.TestCase):
    def test_fit_predict(self):
        random.seed(1)
        returns = [random.gauss(0.001, 0.005) for _ in range(50)] + [random.gauss(-0.002, 0.02) for _ in range(50)]
        m, states, proba = detect_regimes(returns, n_states=2, seed=1)
        self.assertEqual(len(states), len(returns))
        self.assertEqual(len(proba), len(returns))
        self.assertEqual(len(proba[0]), 2)
        # two regimes detected
        self.assertEqual(len(set(states)), 2)

    def test_viterbi_new_data(self):
        random.seed(1)
        returns = [random.gauss(0.001, 0.005) for _ in range(50)] + [random.gauss(-0.002, 0.02) for _ in range(50)]
        m, states, proba = detect_regimes(returns, n_states=2, seed=1)
        new = [random.gauss(0.001, 0.005) for _ in range(5)]
        out = m.predict(new)
        self.assertEqual(len(out), 5)

    def test_predict_proba_sums(self):
        random.seed(2)
        returns = [random.gauss(0.0, 0.01) for _ in range(60)]
        m, states, proba = detect_regimes(returns, n_states=2, seed=2)
        for row in proba:
            self.assertAlmostEqual(sum(row), 1.0, places=6)

    def test_regime_summary(self):
        s = regime_summary([0, 0, 1, 1, 1])
        self.assertEqual(s[0], 2)
        self.assertEqual(s[1], 3)

    def test_too_short(self):
        m = GaussianHMM(n_states=2)
        m.fit([0.1, 0.2])
        # too short -> not fitted, but no crash
        self.assertEqual(m.predict([]), [])

    def test_n_states_3(self):
        random.seed(3)
        returns = [random.gauss(0.001, 0.005) for _ in range(40)] + [random.gauss(0.0, 0.01) for _ in range(40)] + [random.gauss(-0.002, 0.02) for _ in range(40)]
        m, states, proba = detect_regimes(returns, n_states=3, seed=3)
        self.assertEqual(len(set(states)), 3)


if __name__ == "__main__":
    unittest.main()