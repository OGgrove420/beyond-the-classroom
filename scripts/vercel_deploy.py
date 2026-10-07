"""trigger a vercel deployment from the local tree (files API), then verify."""
import base64, json, os, time, urllib.request

TOKEN = None
for line in open('/opt/data/conscious-ecom/.env'):
    if line.startswith('VERCEL_TOKEN='):
        TOKEN = line.split('=', 1)[1].strip().strip('"').strip("'")
assert TOKEN

ROOT = '/opt/data/learning-app'
FILES = [
    ('public/index.html', 'text/plain; charset=utf-8'),
    ('public/app.js',     'text/plain; charset=utf-8'),
    ('public/auth.js',    'text/plain; charset=utf-8'),
    ('public/vendor/supabase.umd.js', 'text/plain; charset=utf-8'),
    ('public/style.css',  'text/plain; charset=utf-8'),
    ('api/index.py',      'text/x-python'),
    ('api/grades.py',     'text/x-python'),
    ('api/question_bank.py', 'text/x-python'),
    ('api/payments.py',   'text/x-python'),
    ('data/site.json',    'application/json'),
    ('vercel.json',       'application/json'),
]

files = []
for rel, enc in FILES:
    data = open(os.path.join(ROOT, rel), 'rb').read()
    files.append({'file': rel, 'data': base64.b64encode(data).decode(), 'encoding': 'base64'})
    print('packing', rel, len(data), 'bytes')

body = {
    'name': 'beyond-the-classroom',
    'files': files,
    'target': 'production',
    'projectSettings': {'framework': None},
}

req = urllib.request.Request('https://api.vercel.com/v13/deployments',
                             headers={'Authorization': 'Bearer ' + TOKEN,
                                      'Content-Type': 'application/json'},
                             method='POST',
                             data=json.dumps(body).encode())
with urllib.request.urlopen(req, timeout=60) as r:
    dep = json.loads(r.read())
did = dep.get('uid') or dep.get('id')
if not did:
    print('unexpected response:', json.dumps(dep)[:2000])
    raise SystemExit(1)
uid = did
print('deployment created:', uid, dep.get('url'))

# poll until ready
deadline = time.time() + 240
while time.time() < deadline:
    req2 = urllib.request.Request(f'https://api.vercel.com/v13/deployments/{uid}',
                                  headers={'Authorization': 'Bearer ' + TOKEN})
    with urllib.request.urlopen(req2, timeout=30) as r:
        d = json.loads(r.read())
    state = d.get('readyState') or d.get('state')
    print('  state:', state)
    if state in ('READY', 'ERROR', 'CANCELED'):
        break
    time.sleep(10)

if state != 'READY':
    print('DEPLOY FAILED:', state)
    raise SystemExit(1)

print('READY:', d.get('url'))
open('/tmp/btc_last_deploy.txt', 'w').write(d.get('url', ''))
