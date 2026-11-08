"""Zero-dep text utilities (ingested from Herald-OS/hermes-agent shared patterns)."""
import re, math

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

def strip_ansi(s):
    return _ANSI_RE.sub("", s)

def fuzzy_score(query, text):
    """Simple fuzzy subsequence score (higher is better)."""
    q = query.lower()
    t = text.lower()
    if not q:
        return 1.0
    qi = 0
    score = 0
    consecutive = 0
    for ch in t:
        if qi < len(q) and ch == q[qi]:
            consecutive += 1
            score += 1 + consecutive * 0.5
            qi += 1
        else:
            consecutive = 0
    if qi < len(q):
        return 0.0
    # normalize by length
    return score / max(len(t), 1)

def fuzzy_rank(query, items):
    scored = [(fuzzy_score(query, str(x)), x) for x in items]
    scored.sort(key=lambda x: -x[0])
    return [x for _, x in scored if _ > 0] or [x for _, x in scored]

def parse_slash_command(line):
    line = line.strip()
    if not line.startswith("/"):
        return None
    parts = line[1:].split()
    if not parts:
        return None
    return {"command": parts[0], "args": parts[1:]}

def looks_like_slash_command(line):
    return line.strip().startswith("/")

def reconnect_backoff_delay_ms(attempt, base=1000, max_delay=30000):
    delay = base * (2 ** attempt)
    return min(delay, max_delay)