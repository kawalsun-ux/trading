"""Paper trading (zero-dep, uses live_adapter)."""
from execution.live_adapter import LiveAdapter

def demo():
    ad = LiveAdapter(sandbox=True)
    print("mode:", ad.mode())
    print("price:", ad.price("BTCUSDT"))
    print("order:", ad.place_order("BTCUSDT", "buy", 0.001))

if __name__ == "__main__":
    demo()