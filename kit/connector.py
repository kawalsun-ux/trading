"""Solana connector (stdlib only, urllib)."""
import json, urllib.request, time

DEFAULT_RPC = "https://api.mainnet-beta.solana.com"

def rpc(method, params=None, rpc_url=DEFAULT_RPC, timeout=15):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []}
    req = urllib.request.Request(rpc_url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def get_balance(pubkey, rpc_url=DEFAULT_RPC):
    res = rpc("getBalance", [pubkey], rpc_url=rpc_url)
    lamports = res.get("result", {}).get("value", 0)
    return lamports / 1e9

def get_slot(rpc_url=DEFAULT_RPC):
    return rpc("getSlot", [], rpc_url=rpc_url).get("result")

def get_token_accounts(pubkey, rpc_url=DEFAULT_RPC):
    res = rpc("getTokenAccountsByOwner", [pubkey, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                                          {"encoding": "jsonParsed"}], rpc_url=rpc_url)
    return res.get("result", {}).get("value", [])

def mock_balance(pubkey):
    return 1.2345  # SOL, for test mode