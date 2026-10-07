"""Payments engine for beyond-the-classroom: crypto (live) + payfast (dormant until keys).

crypto rail (Robinhood Chain 4663, native ETH to treasury):
  - POST /api/pay/intent  {tier} -> order id, amount ZAR, ETH amount, treasury, chain
  - POST /api/pay/confirm {order_id, tx_hash} -> verifies tx on-chain, records
    the SARS snapshot: date-time (UTC+2), ETH value, ETH price at payment,
    ZAR value at payment.
  - GET  /api/pay/status?id=<order_id> -> order incl. sars record

payfast rail: signature + hosted checkout are built; returns 503 "pending
merchant keys" until PAYFAST_MERCHANT_ID/KEY/PASSPHRASE exist in env.
ITN webhook endpoint included, ready to activate.
"""
import hashlib, hmac, json, os, re, time, urllib.parse, urllib.request, uuid
from datetime import datetime, timezone, timedelta

# treasury (holder's dedicated wallet) and chain
TREASURY = os.environ.get("BTC_TREASURY", "0xEdd74f2C3277589CE0eCb747956a33fcD69e9082")
CHAIN_ID = 4663
CHAIN_NAME = "Robinhood Chain"
RPC_URL = os.environ.get("BTC_CHAIN_RPC", "https://4663.rpc.thirdweb.com")

# fiat reference rate if coingecko zar is unavailable
FALLBACK_ZAR = 18.50

SAST = timezone(timedelta(hours=2))  # south africa standard time (UTC+2)

# in-memory order store (serverless-warm; also mirrored to supabase when keyed)
ORDERS = {}

TIERS_CACHE = {"rates": None, "ts": 0}


def _site():
    here = os.path.dirname(__file__)
    return json.load(open(os.path.join(here, "..", "data", "site.json")))


def tier_by_id(tid):
    for t in _site()["tiers"]:
        if t["id"] == tid:
            return t
    return None


# ---------------- rates ----------------

def eth_rates():
    """{eth_usd, usd_zar, eth_zar} — coingecko with 10-min cache + fallback."""
    now = time.time()
    if TIERS_CACHE["rates"] and now - TIERS_CACHE["ts"] < 600:
        return TIERS_CACHE["rates"]
    rates = None
    try:
        url = ("https://api.coingecko.com/api/v3/simple/price"
               "?ids=ethereum&vs_currencies=usd,zar")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as r:
            d = json.loads(r.read().decode())
            rates = {"eth_usd": d["ethereum"]["usd"],
                     "usd_zar": d["ethereum"]["zar"] / d["ethereum"]["usd"],
                     "eth_zar": d["ethereum"]["zar"]}
    except Exception:
        pass
    if not rates or not rates.get("eth_zar"):
        rates = {"eth_usd": 2600.0, "usd_zar": FALLBACK_ZAR,
                 "eth_zar": 2600.0 * FALLBACK_ZAR}
    rates["fallback"] = bool(TIERS_CACHE["rates"] is None)
    TIERS_CACHE["rates"] = rates
    TIERS_CACHE["ts"] = now
    return rates


def quote_zar_to_eth(zar_amount):
    r = eth_rates()
    eth = zar_amount / r["eth_zar"]
    return {"eth": round(eth, 8), "eth_zar": r["eth_zar"], "rates": r}


# ---------------- orders ----------------

def new_order(tier_id, method):
    t = tier_by_id(tier_id)
    if not t:
        return None, "unknown tier"
    if t["price"] <= 0:
        return None, "tier is free — no payment needed"
    oid = str(uuid.uuid4())[:12]
    q = quote_zar_to_eth(t["price"])
    order = {
        "id": oid, "tier": tier_id, "method": method,
        "amount_zar": t["price"], "status": "pending",
        "eth_amount": q["eth"], "eth_zar_at_quote": q["eth_zar"],
        "treasury": TREASURY, "chain_id": CHAIN_ID, "chain": CHAIN_NAME,
        "created_at": datetime.now(SAST).isoformat(),
    }
    ORDERS[oid] = order
    return order, None


# ---------------- on-chain verification (crypto rail) ----------------

def _rpc(method, params):
    req = urllib.request.Request(RPC_URL, data=json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read().decode())


def _eth_price_at_block_or_now():
    """best-effort historical price; falls back to current with a flag."""
    r = eth_rates()
    return r["eth_usd"], r["eth_zar"], False  # False = not historical (per-tx)


def verify_tx(tx_hash, expected_min_eth):
    """verify tx: to treasury, enough ETH, on 4663. returns (ok, detail, sars)."""
    try:
        tx = _rpc("eth_getTransactionByHash", [tx_hash]).get("result")
        if not tx:
            return False, "tx not found on Robinhood Chain (4663) — check the hash", None
        if (tx.get("to") or "").lower() != TREASURY.lower():
            return False, f"tx went to {tx.get('to')}, not the treasury {TREASURY}", None
        wei = int(tx.get("value", "0x0"), 16)
        eth = wei / 1e18
        if eth + 1e-9 < expected_min_eth:
            return False, f"tx value {eth:.8f} ETH is short of {expected_min_eth:.8f} ETH", None
        # block timestamp = payment moment (falls back to now if pending)
        block_ts = None
        if tx.get("blockNumber"):
            blk = _rpc("eth_getBlockByNumber", [tx["blockNumber"], False]).get("result")
            if blk:
                block_ts = int(blk["timestamp"], 16)
        paid_dt = (datetime.fromtimestamp(block_ts, SAST) if block_ts
                   else datetime.now(SAST))
        usd, zar, _ = _eth_price_at_block_or_now()
        sars = {
            "paid_at": paid_dt.isoformat(),          # UTC+2 date-time of payment
            "tx_hash": tx_hash,
            "chain": f"{CHAIN_NAME} ({CHAIN_ID})",
            "token": "native ETH",
            "crypto_amount": eth,                     # exact, unrounded
            "eth_price_usd_at_payment": usd,
            "zar_per_eth_at_payment": zar,
            "value_zar_at_payment": eth * zar,        # exact, unrounded
            "price_source": "coingecko at confirmation",
        }
        return True, "verified", sars
    except Exception as e:  # noqa: BLE001
        return False, f"verification failed: {e}", None


def confirm_order(order_id, tx_hash):
    o = ORDERS.get(order_id)
    if not o:
        return None, "unknown order id"
    if o["status"] == "complete":
        return o, None
    ok, detail, sars = verify_tx(tx_hash, o["eth_amount"])
    if not ok:
        return None, detail
    o["status"] = "complete"
    o["tx_hash"] = tx_hash
    o["sars"] = sars
    o["paid_at"] = sars["paid_at"]
    _mirror_supabase(o)
    return o, None


# ---------------- supabase mirror (best-effort, never blocks) ----------------

def _mirror_supabase(order):
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        return
    try:
        body = {
            "method": order["method"], "tier": order["tier"],
            "amount_zar": order["amount_zar"], "status": order["status"],
            "tx_hash": order.get("tx_hash"), "chain": order.get("chain"),
            "token": "native ETH", "crypto_amount": order.get("eth_amount"),
            "eth_price_usd_at_payment": (order.get("sars") or {}).get("eth_price_usd_at_payment"),
            "zar_usd_at_payment": (order.get("sars") or {}).get("zar_per_eth_at_payment"),
            "value_zar_at_payment": (order.get("sars") or {}).get("value_zar_at_payment"),
            "paid_at": order.get("paid_at"),
            "meta": order,
        }
        req = urllib.request.Request(
            url.rstrip("/") + "/rest/v1/btc_payments", data=json.dumps(body).encode(),
            headers={"apikey": key, "Authorization": "Bearer " + key,
                     "Content-Type": "application/json", "Prefer": "return=minimal"},
            method="POST")
        urllib.request.urlopen(req, timeout=8)
    except Exception as e:  # noqa: BLE001
        print("supabase mirror failed:", e)


# ---------------- payfast rail (dormant until keys) ----------------

def payfast_configured():
    return all([os.environ.get("PAYFAST_MERCHANT_ID"),
                os.environ.get("PAYFAST_MERCHANT_KEY"),
                os.environ.get("PAYFAST_PASSPHRASE")])


def payfast_signature(fields, passphrase):
    """md5 over urlencoded sorted k=v joined by &, passphrase appended."""
    parts = [f"{k}={urllib.parse.quote_plus(str(v))}"
             for k, v in sorted(fields.items()) if k != "signature"]
    parts.append(f"passphrase={urllib.parse.quote_plus(passphrase)}")
    raw = "&".join(parts)
    return hashlib.md5(raw.encode()).hexdigest()


def payfast_checkout(order, base_url):
    """build the hosted-checkout form fields; caller POSTs to process_url."""
    if not payfast_configured():
        return None, "payfast merchant keys not set yet — rail is dormant"
    pid = f"BTC-{order['id']}"
    fields = {
        "merchant_id": os.environ["PAYFAST_MERCHANT_ID"],
        "merchant_key": os.environ["PAYFAST_MERCHANT_KEY"],
        "return_url": base_url + "/pay/return?id=" + order["id"],
        "cancel_url": base_url + "/pay/cancel?id=" + order["id"],
        "notify_url": base_url + "/api/payfast/itn",
        "name_first": "Beyond the Classroom learner",
        "m_payment_id": pid,
        "amount": f"{order['amount_zar']:.2f}",
        "item_name": f"BTC subscription: {order['tier']}",
        "email_confirmation": "1",
    }
    fields["signature"] = payfast_signature(fields, os.environ["PAYFAST_PASSPHRASE"])
    sandbox = os.environ.get("PAYFAST_MODE", "sandbox") == "sandbox"
    process = "https://sandbox.payfast.co.za/eng/process" if sandbox else "https://www.payfast.co.za/eng/process"
    return {"fields": fields, "process_url": process, "payment_id": pid}, None


def payfast_itn_verify(form, passphrase):
    """recompute signature over ITN fields; True when valid AND status COMPLETE."""
    sig = form.pop("signature", None)
    expected = payfast_signature(form, passphrase)
    if not sig or not hmac.compare_digest(sig, expected):
        return False, "signature mismatch"
    if form.get("payment_status") != "COMPLETE":
        return False, f"status {form.get('payment_status')} not accepted"
    return True, "ok"
