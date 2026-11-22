"""Dependency availability reporting for extras."""

try:
    from extras import available as _avail
except ImportError:  # pragma: no cover - direct-path execution
    from __init__ import available as _avail


def report():
    a = _avail()
    lines = ["Optional dependency availability:"]
    for k in sorted(a):
        lines.append(f"  {k:22s} {'OK' if a[k] else 'MISSING'}")
    return "\n".join(lines)


def missing():
    a = _avail()
    return [k for k, v in a.items() if not v]


if __name__ == "__main__":
    print(report())