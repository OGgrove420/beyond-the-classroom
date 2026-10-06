"""end-to-end check of the live site: profile multi-select + quiz + pricing."""
import json, urllib.request, urllib.error

BASE = 'https://beyond-the-classroom-jade.vercel.app'

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=30) as r:
        raw = r.read()
    try:
        return r.status, json.loads(raw)
    except Exception:
        return r.status, raw

def post(path, obj):
    req = urllib.request.Request(BASE + path, data=json.dumps(obj).encode(),
                                 headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.status, json.loads(r.read())

print('1. GET /            ', get('/')[0])
print('2. GET /api/site    ', end=' ')
s, site = get('/api/site')
print(s, f'({len(site["tiers"])} tiers, {len(site["revenueStreams"])} revenue streams)')

print('3. POST /api/profile with multi-select answers')
s, prof = post('/api/profile', {'answers': {
    'grade': 'Grade 6',
    'enjoy': ['Mathematics', 'Science', 'Art'],
    'struggle': ['Reading', 'Exams'],
    'style': ['Watching videos', 'Doing practical activities'],
    'focus': '10–20 minutes',
    'hard': 'Going too fast',
    'strength': 'building things',
    'goal': 'maths confidence',
}})
print('   ', s, prof['id'], '| tags:', prof['tags'])
assert 'learner' in ' '.join(prof['tags']), 'multi-select tags missing'

# GET the profile back by id (what the profile card does)
with urllib.request.urlopen(f'{BASE}/api/profile?id={prof["id"]}', timeout=30) as r:
    back = json.loads(r.read())
print('4. GET /api/profile?id=', s, '-> id', back.get('id'))
print('   answers echoed back?', [k for k in back.keys()])
print()
print('PROFILE CARD KEYS:', sorted(back.keys()))
print('=> if answers/summary mismatch, card cannot show WHAT was multi-selected')
