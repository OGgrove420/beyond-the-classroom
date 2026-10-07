"""Confirm the working 4663 RPC and the treasury address balance."""
import json, urllib.request

RPC = "https://4663.rpc.thirdweb.com"
TREASURY = "0xEdd74f2C3277589CE0eCb747956a33fcD69e9082"

def rpc(method, params):
    req = urllib.request.Request(RPC, data=json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

print("chainId:", rpc("eth_chainId", []))
print("latest block:", int(rpc("eth_blockNumber", [])["result"], 16))
bal = rpc("eth_getBalance", [TREASURY, "latest"])
print("treasury balance wei:", int(bal["result"], 16))

# eth price source check (for sars valuation)
try:
    with urllib.request.urlopen("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd,zar", timeout=12) as r:
        print("coingecko:", r.read().decode()[:160])
except Exception as e:
    print("coingecko failed:", e)
