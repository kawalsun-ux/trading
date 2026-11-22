"""Multi-level circuit breakers (zero-dep, stdlib)."""


class CircuitBreaker:
    def __init__(self, name, threshold, cooldown=5):
        self.name = name
        self.threshold = threshold
        self.cooldown = cooldown
        self.state = "closed"
        self.failures = 0
        self.cooldown_left = 0

    def record_failure(self):
        self.failures += 1
        if self.failures >= self.threshold:
            self.state = "open"
            self.cooldown_left = self.cooldown

    def record_success(self):
        if self.state == "half_open":
            self.state = "closed"
            self.failures = 0

    def tick(self):
        if self.state == "open":
            self.cooldown_left -= 1
            if self.cooldown_left <= 0:
                self.state = "half_open"

    def allow(self):
        return self.state in ("closed", "half_open")


class BreakerStack:
    def __init__(self):
        self.breakers = {}

    def add(self, name, threshold, cooldown=5):
        self.breakers[name] = CircuitBreaker(name, threshold, cooldown)

    def record_failure(self, name):
        if name in self.breakers:
            self.breakers[name].record_failure()

    def record_success(self, name):
        if name in self.breakers:
            self.breakers[name].record_success()

    def tick(self):
        for b in self.breakers.values():
            b.tick()

    def all_allow(self):
        return all(b.allow() for b in self.breakers.values())

    def any_open(self):
        return any(b.state == "open" for b in self.breakers.values())