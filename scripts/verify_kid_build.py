"""verify live prod serves the new kid build."""
import json, urllib.request
BASE = 'https://beyond-the-classroom-jade.vercel.app'
def get(path):
    req = urllib.request.Request(BASE + path, headers={'User-Agent': 'btc-verify'})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.status, r.read()
s, css = get('/style.css')
print('css', s, len(css), 'crayon theme:', b'fff8ec' in css)
s, api = get('/api/site')
d = json.loads(api)
print('api/site', s, 'tiers:', len(d['tiers']), 'streams:', len(d['revenueStreams']))
s, quiz = get('/api/quiz')
d = json.loads(quiz)
print('api/quiz', s, 'questions:', len(d['questions']))
s, home = get('/')
print('home', s)
