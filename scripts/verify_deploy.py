"""wait for the vercel deploy to pick up, then verify the new code is live."""
import time, urllib.request, json

URL = 'https://beyond-the-classroom-jade.vercel.app'

def fetch(path):
    req = urllib.request.Request(URL + path, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, r.read()

deadline = time.time() + 180
live = False
while time.time() < deadline:
    s, js = fetch('/app.js')
    if b'btc_draft' in js:
        live = True
        print(f'app.js updated on live site ({len(js)} bytes)')
        break
    print('  old build still serving, waiting 15s…')
    time.sleep(15)

if not live:
    print('TIMEOUT: new code not live after 3min')
    raise SystemExit(1)

print()
s, html = fetch('/')
print('GET /', s, '| offerings nav:', b'data-view="offerings"' in html)
s, site = fetch('/api/site')
site = json.loads(site)
print('GET /api/site', s, '| tiers:', len(site['tiers']), '| streams:', len(site['revenueStreams']))
s, quiz = fetch('/api/quiz')
quiz = json.loads(quiz)
print('GET /api/quiz', s, '| questions:', len(quiz['questions']))
print()
print('LIVE AND CURRENT')
