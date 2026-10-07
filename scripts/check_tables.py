"""Set up learning-app supabase: tables for profiles/payments, + grade-gated quiz bank."""
import os, re, json, urllib.request, urllib.error

env = open('/opt/data/learning-app/.env').read()
url = re.search(r'SUPABASE_URL=(\S+)', env).group(1)
srole = re.search(r'SUPABASE_SERVICE_ROLE_KEY=(\S+)', env).group(1)

def rest(path, key=srole, method='GET', data=None):
    req = urllib.request.Request(url + path, data=(json.dumps(data).encode() if data else None),
                                 method=method, headers={
        'apikey': key, 'Authorization': 'Bearer ' + key,
        'Content-Type': 'application/json', 'Prefer': 'return=representation'})
    with urllib.request.urlopen(req, timeout=20) as r:
        body = r.read().decode() or '{}'
        return r.status, json.loads(body) if body.strip() else {}

try:
    print('profiles:', rest('/rest/v1/btc_profiles?select=id&limit=1'))
except urllib.error.HTTPError as e:
    print('profiles missing:', e.code)
try:
    print('payments:', rest('/rest/v1/btc_payments?select=id&limit=1'))
except urllib.error.HTTPError as e:
    print('payments missing:', e.code)
