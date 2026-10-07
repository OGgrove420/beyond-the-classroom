"""Find a Robinhood Chain (4663) RPC endpoint that works from this box."""
import json, urllib.request, urllib.error

CANDIDATES = [
    "https://rpc.rainbow.me",
    "https://rpc.robinhoodchain.com",
    "https://rpc.robinhood.com",
    "https://chain.robinhood.com",
    "https://rpc-rainbow.rainbow.me",
]
for url in CANDIDATES:
    req = urllib.request.Request(url, data=json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []}).encode(),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            print(url, '->', r.read().decode()[:120])
    except Exception as e:
        print(url, 'FAILED:', str(e)[:80])
