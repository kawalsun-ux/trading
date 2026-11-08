"""Zero-dep code generation helpers (ingested from api-anything codegen)."""
import keyword, re

def _words(name):
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name)
    spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", spaced)
    return [w for w in re.split(r"[^A-Za-z0-9]+", spaced) if w]

def snake(name):
    out = "_".join(w.lower() for w in _words(name)) or "op"
    if out[0].isdigit():
        out = "_" + out
    return out + "_" if keyword.iskeyword(out) else out

def pascal(name):
    out = "".join(w[:1].upper() + w[1:] for w in _words(name)) or "Op"
    return "_" + out if out[0].isdigit() else out

def unique(name, taken):
    candidate = name if name not in taken else name + "_"
    n = 2
    while candidate in taken:
        candidate, n = f"{name}_{n}", n + 1
    taken.add(candidate)
    return candidate

def safe_text(value):
    s = re.sub(r"[\x00-\x1f\x7f\x85\u2028\u2029]+", " ", str(value))
    s = re.sub(r"\s+", " ", s).strip()
    s = s.replace("\\", "\\\\")
    return re.sub(r'"(?=")', '\\"', s)