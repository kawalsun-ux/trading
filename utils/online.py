"""Online (streaming) estimators (zero-dep, stdlib)."""

import math
from collections import deque


class Welford:
    """Streaming mean & variance (Welford)."""
    __slots__ = ("_n", "_mean", "_m2")

    def __init__(self):
        self._n = 0
        self._mean = 0.0
        self._m2 = 0.0

    def update(self, x):
        self._n += 1
        delta = x - self._mean
        self._mean += delta / self._n
        delta2 = x - self._mean
        self._m2 += delta * delta2

    @property
    def n(self):
        return self._n

    @property
    def mean(self):
        return self._mean

    def variance(self, sample=True):
        if self._n < 2:
            return 0.0
        den = self._n - 1 if sample else self._n
        return self._m2 / den

    def std(self, sample=True):
        return math.sqrt(self.variance(sample))


class Ewma:
    """Exponentially weighted moving average (level)."""
    def __init__(self, alpha=0.1):
        self.alpha = alpha
        self._val = None

    def update(self, x):
        if self._val is None:
            self._val = float(x)
        else:
            self._val = self.alpha * float(x) + (1 - self.alpha) * self._val
        return self._val

    @property
    def value(self):
        return self._val


class EwmaVariance:
    """RiskMetrics-style EWMA variance."""
    def __init__(self, alpha=0.06, init=0.0):
        self.alpha = alpha
        self._var = float(init)

    def update(self, x):
        self._var = self.alpha * (x * x) + (1 - self.alpha) * self._var
        return self._var

    @property
    def variance(self):
        return self._var

    def std(self):
        return math.sqrt(self._var)


class RollingWindow:
    """Rolling mean & variance over a fixed window."""
    def __init__(self, size=20):
        self.size = max(1, int(size))
        self._buf = deque(maxlen=self.size)

    def update(self, x):
        self._buf.append(float(x))

    @property
    def n(self):
        return len(self._buf)

    @property
    def mean(self):
        if not self._buf:
            return 0.0
        return sum(self._buf) / len(self._buf)

    def variance(self, sample=True):
        n = len(self._buf)
        if n < 2:
            return 0.0
        m = self.mean
        var = sum((x - m) ** 2 for x in self._buf)
        den = n - 1 if sample else n
        return var / den

    def std(self, sample=True):
        return math.sqrt(self.variance(sample))