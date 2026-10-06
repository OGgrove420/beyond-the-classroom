"""poll the in-flight deployment until READY, then verify live content."""
import json, os, time, urllib.request

TOKEN = None
for line in open('/opt/data/conscious-ecom/.env'):
    if line.startswith('VERCEL_TOKEN='):
        TOKEN = line.split('=', 1)[1].strip().strip('"').strip("'")

UID = 'dpl_9NV6izruh2x97xvEthon3eejrMMW'
deadline = time.time() + 240
state = None
while time.time() < deadline:
    req = urllib.request.Request(f'https://api.vercel.com/v13/deployments/{UID}',
                                 headers={'Authorization': 'Bearer ' + TOKEN})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.loads(r.read())
    state = d.get('readyState')
    print('  state:', state, flush=True)
    if state in ('READY', 'ERROR', 'CANCELED'):
        break
    time.sleep(12)

print()
if state != 'READY':
    print('deploy not ready:', state)
    raise SystemExit(1)

# verify production domain serves the new build
def fetch(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read()

for attempt in range(12):
    s, js = fetch('https://beyond-the-classroom-jade.vercel.app/app.js')
    if b'btc_draft' in js:
        print(f'production serves new app.js ({len(js)} bytes)')
        break
    print('  production still cached-old, retrying…')
    time.sleep(10)
else:
    print('WARNING: new build READY but production domain still serves old app.js')
    raise SystemExit(1)

s, html = fetch('https://beyond-the-classroom-jade.vercel.app/')
print('GET /', s, '| offerings nav:', b'data-view="offerings"' in html)
s, site = fetch('https://beyond-the-classroom-jade.vercel.app/api/site')
site = json.loads(site)
print('GET /api/site', s, '| tiers:', len(site['tiers']), '| streams:', len(site['revenueStreams']))
s, quiz = fetch('https://beyond-the-classroom-jade.vercel.app/api/quiz')
quiz = json.loads(quiz)
print('GET /api/quiz', s, '| questions:', len(quiz['questions']))
print()
print('LIVE AND CURRENT on https://beyond-the-classroom-jade.vercel.app')
