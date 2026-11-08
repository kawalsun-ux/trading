"""Trade log store (stdlib sqlite3)."""
import sqlite3, time, os

DB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "trades.db")

def init():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts REAL, action TEXT, token TEXT, price REAL, units REAL,
        status TEXT, note TEXT)""")
    con.commit()
    con.close()

def log_trade(action, token, price, units, status="filled", note=""):
    init()
    con = sqlite3.connect(DB)
    con.execute("INSERT INTO trades (ts, action, token, price, units, status, note) VALUES (?,?,?,?,?,?,?)",
                (time.time(), action, token, price, units, status, note))
    con.commit()
    con.close()

def recent(n=20):
    init()
    con = sqlite3.connect(DB)
    rows = con.execute("SELECT ts, action, token, price, units, status, note FROM trades ORDER BY id DESC LIMIT ?", (n,)).fetchall()
    con.close()
    return rows