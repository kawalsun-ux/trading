"""Hidden Markov Model (Gaussian, univariate) — zero-dep, stdlib.

Implements forward-backward, Viterbi, and Baum-Welch (EM) for a
K-state Gaussian HMM with scalar variance per state. Useful for market
regime detection (bull/bear/neutral) on a return series.
"""

import math
import random


class GaussianHMM:
    def __init__(self, n_states=2, n_iter=50, tol=1e-6, seed=None):
        self.n_states = max(1, int(n_states))
        self.n_iter = int(n_iter)
        self.tol = float(tol)
        self.seed = seed
        if seed is not None:
            random.seed(seed)
        self.pi = None   # initial probs
        self.A = None    # transition matrix KxK
        self.mu = None   # means
        self.var = None  # variances
        self.fitted = False

    def _init_params(self, X):
        K = self.n_states
        xs = [float(v) for v in X]
        n = len(xs)
        # quantile-based init for means
        sorted_xs = sorted(xs)
        self.mu = [sorted_xs[min(n - 1, int((k + 0.5) * n / K))] for k in range(K)]
        overall_var = sum((x - (sum(xs) / n)) ** 2 for x in xs) / max(1, n - 1)
        overall_var = max(overall_var, 1e-6)
        self.var = [overall_var] * K
        self.pi = [1.0 / K] * K
        # transition: high self-transition
        self.A = [[0.1 / (K - 1) if i != j else 0.9 for j in range(K)] for i in range(K)]
        # normalize rows
        for i in range(K):
            s = sum(self.A[i])
            self.A[i] = [a / s for a in self.A[i]]

    def _emit_prob(self, x, k):
        # Gaussian pdf
        var = max(self.var[k], 1e-12)
        sd = math.sqrt(var)
        diff = x - self.mu[k]
        return (1.0 / (sd * math.sqrt(2 * math.pi))) * math.exp(-0.5 * (diff / sd) ** 2)

    def _forward(self, X):
        K = self.n_states
        n = len(X)
        alpha = [[0.0] * K for _ in range(n)]
        scale = [0.0] * n
        # t=0
        for k in range(K):
            alpha[0][k] = self.pi[k] * self._emit_prob(X[0], k)
        scale[0] = sum(alpha[0])
        if scale[0] > 0:
            for k in range(K):
                alpha[0][k] /= scale[0]
        for t in range(1, n):
            for k in range(K):
                s = sum(alpha[t - 1][j] * self.A[j][k] for j in range(K))
                alpha[t][k] = s * self._emit_prob(X[t], k)
            scale[t] = sum(alpha[t])
            if scale[t] > 0:
                for k in range(K):
                    alpha[t][k] /= scale[t]
        return alpha, scale

    def _backward(self, X, scale):
        K = self.n_states
        n = len(X)
        beta = [[0.0] * K for _ in range(n)]
        for k in range(K):
            beta[n - 1][k] = 1.0
        if scale[n - 1] > 0:
            for k in range(K):
                beta[n - 1][k] /= scale[n - 1]
        for t in range(n - 2, -1, -1):
            for k in range(K):
                s = sum(self.A[k][j] * self._emit_prob(X[t + 1], j) * beta[t + 1][j] for j in range(K))
                beta[t][k] = s
            if scale[t] > 0:
                for k in range(K):
                    beta[t][k] /= scale[t]
        return beta

    def _e_step(self, X):
        K = self.n_states
        n = len(X)
        alpha, scale = self._forward(X)
        beta = self._backward(X, scale)
        # gamma
        gamma = [[0.0] * K for _ in range(n)]
        for t in range(n):
            for k in range(K):
                gamma[t][k] = alpha[t][k] * beta[t][k]
            s = sum(gamma[t])
            if s > 0:
                for k in range(K):
                    gamma[t][k] /= s
        # xi
        xi = [[[0.0] * K for _ in range(K)] for _ in range(n - 1)] if n > 1 else []
        for t in range(n - 1):
            denom = 0.0
            for i in range(K):
                for j in range(K):
                    val = alpha[t][i] * self.A[i][j] * self._emit_prob(X[t + 1], j) * beta[t + 1][j]
                    xi[t][i][j] = val
                    denom += val
            if denom > 0:
                for i in range(K):
                    for j in range(K):
                        xi[t][i][j] /= denom
        # log likelihood
        ll = sum(math.log(sc) if sc > 0 else -1e10 for sc in scale)
        return alpha, beta, gamma, xi, ll

    def _init_params_random(self, X, seed_offset=0):
        import random
        random.seed((self.seed if self.seed is not None else 0) + seed_offset)
        K = self.n_states
        xs = [float(v) for v in X]
        n = len(xs)
        # random means from data
        self.mu = [random.choice(xs) for _ in range(K)]
        overall_var = sum((x - (sum(xs) / n)) ** 2 for x in xs) / max(1, n - 1)
        overall_var = max(overall_var, 1e-6)
        self.var = [overall_var * (0.5 + random.random()) for _ in range(K)]
        self.pi = [1.0 / K] * K
        self.A = [[0.1 / (K - 1) if i != j else 0.9 for j in range(K)] for i in range(K)]
        for i in range(K):
            s = sum(self.A[i])
            self.A[i] = [a / s for a in self.A[i]]

    def fit(self, X, n_restarts=3):
        xs = [float(v) for v in X]
        if len(xs) < self.n_states + 1:
            return self
        best_ll = None
        best_params = None
        for r in range(n_restarts):
            # init
            if r == 0:
                self._init_params(xs)
            else:
                self._init_params_random(xs, seed_offset=r)
            prev_ll = None
            for it in range(self.n_iter):
                alpha, beta, gamma, xi, ll = self._e_step(xs)
                K = self.n_states
                n = len(xs)
                self.pi = [gamma[0][k] for k in range(K)]
                s = sum(self.pi)
                if s > 0:
                    self.pi = [p / s for p in self.pi]
                for i in range(K):
                    denom = sum(gamma[t][i] for t in range(n - 1))
                    if denom <= 0:
                        denom = 1.0
                    for j in range(K):
                        num = sum(xi[t][i][j] for t in range(n - 1)) if n > 1 else 0.0
                        self.A[i][j] = num / denom
                    s = sum(self.A[i])
                    if s > 0:
                        self.A[i] = [a / s for a in self.A[i]]
                for k in range(K):
                    denom = sum(gamma[t][k] for t in range(n))
                    if denom <= 0:
                        denom = 1.0
                    self.mu[k] = sum(gamma[t][k] * xs[t] for t in range(n)) / denom
                    var_num = sum(gamma[t][k] * (xs[t] - self.mu[k]) ** 2 for t in range(n))
                    self.var[k] = max(var_num / denom, 1e-6)
                if prev_ll is not None and abs(ll - prev_ll) < self.tol:
                    break
                prev_ll = ll
            if best_ll is None or ll > best_ll:
                best_ll = ll
                best_params = (list(self.pi), [row[:] for row in self.A],
                               list(self.mu), list(self.var))
        # restore best
        if best_params is not None:
            self.pi, self.A, self.mu, self.var = best_params
        self.fitted = True
        return self

    def predict(self, X):
        """Viterbi decoding."""
        xs = [float(v) for v in X]
        K = self.n_states
        n = len(xs)
        if n == 0:
            return []
        # delta and psi
        delta = [[0.0] * K for _ in range(n)]
        psi = [[0] * K for _ in range(n)]
        for k in range(K):
            delta[0][k] = math.log(self.pi[k] + 1e-300) + math.log(self._emit_prob(xs[0], k) + 1e-300)
        for t in range(1, n):
            for k in range(K):
                best = -float("inf")
                best_j = 0
                for j in range(K):
                    val = delta[t - 1][j] + math.log(self.A[j][k] + 1e-300)
                    if val > best:
                        best = val
                        best_j = j
                delta[t][k] = best + math.log(self._emit_prob(xs[t], k) + 1e-300)
                psi[t][k] = best_j
        # backtrack
        path = [0] * n
        path[n - 1] = max(range(K), key=lambda k: delta[n - 1][k])
        for t in range(n - 2, -1, -1):
            path[t] = psi[t + 1][path[t + 1]]
        return path

    def predict_proba(self, X):
        """Posterior state probabilities (gamma)."""
        xs = [float(v) for v in X]
        if not xs:
            return []
        alpha, beta, gamma, xi, ll = self._e_step(xs)
        return gamma

    def regime_labels(self, X):
        """Return list of most likely state index per observation."""
        return self.predict(X)

def detect_regimes(returns, n_states=2, n_iter=50, seed=42):
    model = GaussianHMM(n_states=n_states, n_iter=n_iter, seed=seed)
    model.fit(returns)
    states = model.predict(returns)
    proba = model.predict_proba(returns)
    return model, states, proba


def regime_summary(states):
    from collections import Counter
    return dict(Counter(states or []))
