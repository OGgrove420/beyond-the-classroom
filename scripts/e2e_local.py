"""full local e2e: static pages, site api, profile multi-select round-trip,
tier/offering content requirements, quiz flow."""
import json, time, urllib.request, urllib.error, sys

BASE = 'http://127.0.0.1:8712'
ok = fail = 0

def check(name, cond, detail=''):
    global ok, fail
    if cond: ok += 1; print(f'  PASS {name}')
    else: fail += 1; print(f'  FAIL {name} {detail}')

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=15) as r:
        raw = r.read()
    try:
        return r.status, json.loads(raw)
    except Exception:
        return r.status, raw

def post(path, obj):
    req = urllib.request.Request(BASE + path, data=json.dumps(obj).encode(),
                                 headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.status, json.loads(r.read())

time.sleep(0.5)
print('== static ==')
html = open('/opt/data/learning-app/public/index.html','rb').read()
js = open('/opt/data/learning-app/public/app.js','rb').read()
check('offerings nav link', b'data-view="offerings"' in html)
check('draft persistence in js', b'btc_draft' in js)
check('tier detail renderer', b'renderTier' in js)
check('offerings renderer', b'renderOfferings' in js)
check('tier preselect (data-pick)', b'data-pick' in js)
check('save error handling', b'could not save' in js)

print('== site api ==')
s, site = get('/api/site')
check('GET /api/site 200', s == 200)
check('5 tiers', len(site['tiers']) == 5, str(len(site['tiers'])))
check('12 revenue streams', len(site['revenueStreams']) == 12)
tier_ids = [t['id'] for t in site['tiers']]
check('tier ids', tier_ids == ['discover','foundation','plus','personal','intensive'], str(tier_ids))
subjects_total = sum(len(v) for v in site['subjects'].values())
check('subject catalogue non-empty', subjects_total >= 20, str(subjects_total))

print('== profile multi-select round-trip ==')
answers = {
    'grade': 'Grade 6',
    'enjoy': ['Mathematics', 'Science', 'Art'],
    'struggle': ['Reading', 'Exams'],
    'style': ['Watching videos', 'Doing practical activities'],
    'focus': '10–20 minutes',
    'hard': 'Going too fast',
    'strength': 'building things',
    'goal': 'maths confidence',
}
s, prof = post('/api/profile', {'answers': answers, 'tier': 'plus'})
check('POST /api/profile 200', s == 200)
check('id returned', bool(prof.get('id')))
tags = ' '.join(prof['tags'])
check('multi tags: watching-learner', 'watching-learner' in tags, tags)
check('multi tags: doing-learner', 'doing-learner' in tags, tags)
summary = prof['summary']
check('summary lists enjoys', 'Mathematics' in summary)
check('summary lists repetition subjects', 'Reading' in summary)
s2, back = get(f'/api/profile?id={prof["id"]}')
check('GET back by id', s2 == 200 and back.get('id') == prof['id'])

print('== quiz ==')
s, quiz = get('/api/quiz')
check('GET /api/quiz 200', s == 200)
check('4 questions', len(quiz['questions']) == 4)
q0 = quiz['questions'][0]
check('modalities present', all(q0.get(k) for k in ('visual','kinesthetic')))
s3, ans = post('/api/quiz/answer', {'questionId': q0['id'], 'grade': q0['grade'],
                                    'choice': 99, 'q': q0['q'], 'seen': 0})
check('wrong answer returns rewrites', s3 == 200 and not ans['correct'] and ans['rewrites'])

print()
print(f'{ok} passed, {fail} failed')
sys.exit(1 if fail else 0)
