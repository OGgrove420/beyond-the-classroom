"""thirdweb rpc needs no browser headers? test variations: empty payload got 403
on second call — maybe rate limit or UA. retry with UA + single call per run."""
import json, urllib.request, time

RPC = "https://4663.rpc.thirdweb.com"
TREASURY = "0xEdd74f2C3277589CE0eCb747956a33fcD69e9082"

def rpc(method, params):
    req = urllib.request.Request(RPC, data=json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())

for attempt in range(3):
    try:
        print("chainId:", rpc("eth_chainId", []))
        print("block:", int(rpc("eth_blockNumber", [])["result"], 16))
        bal = rpc("eth_getBalance", [TREASURY, "latest"])
        print("treasury wei:", int(bal["result"], 16))
        break
    except Exception as e:
        print("attempt", attempt, "failed:", str(e)[:100])
        time.sleep(3)

try:
    with urllib.request.urlopen("https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd,zar", timeout=12) as r:
        print("coingecko:", r.read().decode()[:160])
except Exception as e:
    print("coingecko failed:", str(e)[:100])
