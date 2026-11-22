"""Append-only run log for search accounting (zero-dep, stdlib)."""

import os
import json
import time
import subprocess


def _git_sha():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except Exception:
        pass
    return None


def log_run(path, record):
    """Append a JSON record to `path` (JSONL). Returns the record written."""
    rec = dict(record or {})
    rec.setdefault("ts", time.time())
    rec.setdefault("git_sha", _git_sha())
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def read_runs(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return out