"""Order lifecycle state machine (zero-dep, stdlib)."""

STATES = ("NEW", "ACKED", "PARTIAL", "FILLED", "CANCELED", "REJECTED")
TRANSITIONS = {
    "NEW": ("ACKED", "REJECTED"),
    "ACKED": ("PARTIAL", "FILLED", "CANCELED", "REJECTED"),
    "PARTIAL": ("PARTIAL", "FILLED", "CANCELED", "REJECTED"),
    "FILLED": (),
    "CANCELED": (),
    "REJECTED": (),
}


class Order:
    def __init__(self, order_id, side, qty, price=None, idempotency_key=None):
        self.order_id = order_id
        self.side = side
        self.qty = qty
        self.price = price
        self.filled_qty = 0.0
        self.state = "NEW"
        self.idempotency_key = idempotency_key or order_id
        self.history = [("NEW", None)]

    def transition(self, new_state, event=None):
        if new_state not in STATES:
            raise ValueError(f"unknown state {new_state}")
        if new_state not in TRANSITIONS.get(self.state, ()):
            raise ValueError(f"invalid transition {self.state} -> {new_state}")
        self.state = new_state
        self.history.append((new_state, event))
        return self

    def apply_fill(self, qty):
        if self.state in ("FILLED", "CANCELED", "REJECTED"):
            return self
        self.filled_qty += float(qty)
        if self.filled_qty >= self.qty - 1e-9:
            self.transition("FILLED", {"filled": self.filled_qty})
        else:
            if self.state == "NEW":
                self.transition("ACKED", {"filled": self.filled_qty})
            self.transition("PARTIAL", {"filled": self.filled_qty})
        return self

    def cancel(self):
        if self.state in ("FILLED", "CANCELED", "REJECTED"):
            return self
        if self.state == "NEW":
            self.transition("ACKED", {"cancel": True})
        self.transition("CANCELED", {"cancel": True})
        return self

    def reject(self, reason=None):
        if self.state in ("FILLED", "CANCELED", "REJECTED"):
            return self
        if self.state == "NEW":
            self.transition("ACKED", {"reject": reason})
        self.transition("REJECTED", {"reject": reason})
        return self


def reconcile(local_orders, broker_orders):
    """Compare local vs broker order states. Returns list of mismatches."""
    mismatches = []
    broker_map = {o.get("order_id"): o for o in (broker_orders or [])}
    for lo in (local_orders or []):
        oid = lo.get("order_id") if isinstance(lo, dict) else getattr(lo, "order_id", None)
        bo = broker_map.get(oid)
        if bo is None:
            mismatches.append({"order_id": oid, "issue": "missing-at-broker"})
            continue
        ls = lo.get("state") if isinstance(lo, dict) else getattr(lo, "state", None)
        bs = bo.get("state") if isinstance(bo, dict) else getattr(bo, "state", None)
        if ls != bs:
            mismatches.append({"order_id": oid, "issue": "state-mismatch",
                              "local": ls, "broker": bs})
    return mismatches