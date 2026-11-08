"""The 4 safety checks before any trade is signed."""
import time

class SafetyError(Exception):
    pass

def check_right_token(token_mint, known_mints):
    """Right token: not a copycat with the same name."""
    if token_mint not in known_mints:
        raise SafetyError(f"Unknown token mint: {token_mint}")
    return True

def check_balance(balance, required):
    """Enough balance: funds actually there."""
    if balance < required:
        raise SafetyError(f"Insufficient balance: {balance} < {required}")
    return True

def check_fresh_quote(quote_ts, max_age_sec=10):
    """Fresh quote: price isn't stale."""
    age = time.time() - quote_ts
    if age > max_age_sec:
        raise SafetyError(f"Stale quote: age {age:.1f}s > {max_age_sec}s")
    return True

def check_slippage(expected_price, actual_price, max_slippage_pct=0.01):
    """Max slippage: price can't run away."""
    if expected_price <= 0:
        raise SafetyError("Invalid expected price")
    slip = abs(actual_price - expected_price) / expected_price
    if slip > max_slippage_pct:
        raise SafetyError(f"Slippage {slip:.4%} > {max_slippage_pct:.2%}")
    return True

def run_all(token_mint, known_mints, balance, required, quote_ts, expected_price,
            actual_price, max_age_sec=10, max_slippage_pct=0.01):
    check_right_token(token_mint, known_mints)
    check_balance(balance, required)
    check_fresh_quote(quote_ts, max_age_sec)
    check_slippage(expected_price, actual_price, max_slippage_pct)
    return True