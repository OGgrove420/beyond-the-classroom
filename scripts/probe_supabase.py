import re, base64, json

env = open('/opt/data/learning-app/.env').read()
m = re.search(r'SUPABASE_ANON_KEY=(\S+)', env)
envkey = m.group(1) if m else ''
pl = json.loads(base64.urlsafe_b64decode(envkey.split('.')[1] + '=='))
print('env anon key ref:', pl.get('ref'), '| iat', pl.get('iat'), '| exp', pl.get('exp'))

chat = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRmY3BzYXF1dHRkaXNjcWZ5dmNkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEzMDAyMjYsImV4cCI6MjEwNjg3NjIyNn0.DR-h7C6tV54aiYH0Byg1dgSSHpjZsmSRS6EWo6zcS6c'
print('same key as chat token:', envkey == chat)

m2 = re.search(r'SUPABASE_URL=(\S+)', env)
print('url:', m2.group(1))

# probe the project anonymously
import urllib.request
url = m2.group(1) + '/auth/v1/health'
try:
    with urllib.request.urlopen(urllib.request.Request(url, headers={'apikey': envkey}), timeout=15) as r:
        print('auth health:', r.status, r.read().decode()[:200])
except Exception as e:
    print('auth health failed:', e)

rest = m2.group(1) + '/rest/v1/'
try:
    req = urllib.request.Request(rest, headers={'apikey': envkey, 'Authorization': 'Bearer ' + envkey})
    with urllib.request.urlopen(req, timeout=15) as r:
        body = r.read().decode()
        print('rest root:', r.status, body[:300])
        spec = json.loads(body)
        print('tables:', sorted(spec.get('definitions', {}).keys()))
except Exception as e:
    print('rest probe failed:', e)
