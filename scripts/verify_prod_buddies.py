"""verify production serves the new buddy build (marker + byte-size + api)."""
import json, urllib.request

prod = 'https://beyond-the-classroom-jade.vercel.app'
r = urllib.request.urlopen(prod + '/app.js', timeout=30)
body = r.read()
print('served app.js bytes:', len(body))
for marker in [b'CHARACTERS', b'pick your learning buddy', b'applyAccent', b'hero-avatar']:
    print(marker.decode(), '->', marker in body)
local = open('/opt/data/learning-app/public/app.js', 'rb').read()
print('byte-identical to local build:', body == local)
q = json.loads(urllib.request.urlopen(prod + '/api/quiz', timeout=30).read())
print('quiz questions:', len(q['questions']))
answers = {'buddy': 'luna', 'accent': '#22d3a7', 'enjoy': ['Science'], 'style': ['Watching videos']}
req = urllib.request.Request(prod + '/api/profile',
    data=json.dumps({'answers': answers}).encode(),
    headers={'Content-Type': 'application/json'}, method='POST')
p = json.loads(urllib.request.urlopen(req, timeout=30).read())
print('profile POST with buddy+accent ->', p['id'], p['tags'])
