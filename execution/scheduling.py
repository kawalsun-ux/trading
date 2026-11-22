"""Execution scheduling helpers (zero-dep, stdlib)."""


def twap(total_size, slices):
    """Split total_size into `slices` equal child orders."""
    if not isinstance(slices, int) or isinstance(slices, bool) or slices < 1:
        raise ValueError("slices must be a positive integer")
    out = []
    allocated = 0.0
    for i in range(1, slices + 1):
        target = (total_size * i) / slices
        out.append(target - allocated)
        allocated = target
    return out


def pov(total_size, interval_volumes, rate):
    """POV: trade `rate` * each interval's volume, capped by remaining size."""
    r = max(0.0, rate)
    out = []
    remaining = total_size
    for vol in (interval_volumes or []):
        if remaining <= 0:
            out.append(0.0)
            continue
        slice_size = min(remaining, r * float(vol))
        out.append(slice_size)
        remaining -= slice_size
    return out