"""Tamper-evident hash-chain audit log (zero-dep, stdlib)."""

import json
import hashlib
import os
import time


def _hash(prev, record):
    payload = json.dumps({"prev": prev, "record": record}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def append(path, record):
    """Append a record to a hash-chained JSONL log. Returns the hash."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    prev = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            lines = [l for l in f if l.strip()]
        if lines:
            try:
                last = json.loads(lines[-1])
                prev = last.get("hash")
            except json.JSONDecodeError:
                prev = None
    rec = dict(record or {})
    rec["ts"] = rec.get("ts", time.time())
    h = _hash(prev, rec)
    entry = {"prev": prev, "record": rec, "hash": h}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
    return h


def verify(path):
    """Verify the hash chain. Returns (ok, issues)."""
    if not os.path.exists(path):
        return True, []
    issues = []
    prev = None
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                issues.append(f"line {i}: invalid json")
                continue
            if entry.get("prev") != prev:
                issues.append(f"line {i}: prev mismatch")
            recomputed = _hash(entry.get("prev"), entry.get("record"))
            if recomputed != entry.get("hash"):
                issues.append(f"line {i}: hash mismatch")
            prev = entry.get("hash")
    return len(issues) == 0, issues