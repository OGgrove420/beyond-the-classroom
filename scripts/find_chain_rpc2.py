"""Probe more 4663 RPC candidates, with browser-like headers."""
import json, urllib.request

CANDIDATES = [
    "https://rpc.rainbow.me",
    "https://rpc.rainbow.info",
    "https://rainbowchainrpc.com",
    "https://rpc.rchchain.com",
    "https://robinhoodchain.rpc.thirdweb.com/4663",
    "https://4663.rpc.thirdweb.com",
]
HDRS = {"Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
        "Origin": "https://rainbow.me", "Referer": "https://rainbow.me/"}
for url in CANDIDATES:
    req = urllib.request.Request(url, data=json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "eth_chainId", "params": []}).encode(),
        headers=HDRS)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            print(url, '->', r.read().decode()[:150])
    except Exception as e:
        print(url, 'FAILED:', str(e)[:90])
