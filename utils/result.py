"""Result object: a dict with attribute access (ingested from api-anything)."""

class Result(dict):
    """A call's answer as a dict with attribute access. Missing keys read as None."""

    @property
    def ok(self):
        return self.get("ok") is True

    @property
    def klass(self):
        return self.get("class")

    @property
    def reason(self):
        return self.get("reason")

    @property
    def data(self):
        return self.get("data")

    @property
    def pending(self):
        return self.get("class") == "pending"

    @property
    def job(self):
        return self.get("job")

    def raise_for_status(self):
        if self.ok:
            return self
        raise ValueError(f"{self.klass}: {self.reason}")