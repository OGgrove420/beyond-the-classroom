"""full local e2e: static pages, site api, grade-banded quizzes, guardian rule,
payment rails (crypto live + payfast dormant), profile multi-select round-trip."""
import json, time, urllib.request, urllib.error, sys

BASE = 'http://127.0.0.1:8712'
ok = fail = 0

def check(name, cond, detail=''):
    global ok, fail
    if cond: ok += 1; print(f'  PASS {name}')
    else: fail += 1; print(f'  FAIL {name} {detail}')

def get(path):
    with urllib.request.urlopen(BASE + path, timeout=20) as r:
        raw = r.read()
    try:
        return r.status, json.loads(raw)
    except Exception:
        return r.status, raw

def post(path, obj, want_fail=False):
    req = urllib.request.Request(BASE + path, data=json.dumps(obj).encode(),
                                 headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        try: body = json.loads(body)
        except Exception: pass
        if want_fail:
            return e.code, body
        raise

time.sleep(0.5)
print('== static ==')
html = open('/opt/data/learning-app/public/index.html','rb').read()
js = open('/opt/data/learning-app/public/app.js','rb').read()
check('offerings nav link', b'data-view="offerings"' in html)
check('draft persistence in js', b'btc_draft' in js)
check('tier detail renderer', b'renderTier' in js)
check('payment view renderer', b'renderPay' in js)
check('crypto flow in js', b'cryptoFlow' in js and b'treasury' in js)
check('payfast flow in js', b'payfastFlow' in js)
check('sars record shown', b'sars record saved' in js)
check('guardian co-sign in form', b'guardian co-sign' in js and b'in_gname' in js)
check('grade select picker', b'type:\'select\'' in js and b'Grade R' in js)
check('band preview live', b'bandbox' in js and b'showBand' in js)
check('quiz shows band+intensity', b'intensity' in js and b'band' in js)

print('== site api ==')
s, site = get('/api/site')
check('GET /api/site 200', s == 200)
check('5 tiers', len(site['tiers']) == 5, str(len(site['tiers'])))
tier_ids = [t['id'] for t in site['tiers']]
check('tier ids', tier_ids == ['discover','foundation','plus','personal','intensive'], str(tier_ids))

print('== grade bands ==')
s, grades = get('/api/grades')
check('GET /api/grades 200', s == 200)
bands = [b['band'] for b in grades['bands']]
check('4 bands', bands == ['foundation','intermediate','senior','fet'], str(bands))
intens = {b['band']: b['intensity'] for b in grades['bands']}
check('intensity ladder', (intens['foundation'], intens['intermediate'], intens['senior'], intens['fet'])
      == ('gentle','standard','stretch','exam'), str(intens))

print('== grade-gated quiz ==')
for grade, band in [('Grade 2','foundation'), ('Grade 6','intermediate'),
                    ('Grade 9','senior'), ('Grade 11','fet')]:
    s, quiz = get(f'/api/quiz?grade={urllib.parse.quote(grade)}' if False else f'/api/quiz?grade={grade.replace(" ","%20")}')
    check(f'{grade} -> {band} band', quiz.get('band') == band, str(quiz.get('band')))
    check(f'{grade} intensity', quiz.get('intensity') is not None, str(quiz.get('intensity')))
    check(f'{grade} 3 questions', len(quiz['questions']) == 3, str(len(quiz['questions'])))
    q0 = quiz['questions'][0]
    check(f'{grade} modalities present', all(q0.get(k) for k in ('visual','kinesthetic')))
    s3, ans = post('/api/quiz/answer', {'questionId': q0['id'], 'grade': q0['grade'],
                                        'choice': 99, 'q': q0['q'], 'seen': 0})
    check(f'{grade} wrong answer -> rewrites', s3 == 200 and not ans['correct'] and ans['rewrites'])
# default quiz (no grade) still works
s, dq = get('/api/quiz')
check('no-grade quiz falls back to intermediate', dq.get('band') == 'intermediate', str(dq.get('band')))

print('== guardian rule ==')
answers = {
    'grade': 'Grade 6',
    'enjoy': ['Mathematics', 'Science', 'Art'],
    'struggle': ['Reading', 'Exams'],
    'style': ['Watching videos', 'Doing practical activities'],
    'focus': '10–20 minutes',
    'hard': ['Going too fast', 'Too much at once'],
    'strength': 'building things',
    'goal': 'maths confidence',
    'buddy': 'zippy',
    'accent': '#22d3a7',
}
s, prof = post('/api/profile', {'answers': answers, 'tier': 'plus'}, want_fail=True)
check('profile without guardian REJECTED', s == 400 and prof.get('error') == 'guardian_missing', f'{s} {prof}')
s, prof = post('/api/profile', {'answers': answers, 'guardian': {'name': 'Thandi Adams', 'email': 'parent@example.com'}, 'tier': 'plus'})
check('profile with guardian 200', s == 200)
check('id returned', bool(prof.get('id')))
check('band recorded', prof.get('band') == 'intermediate', str(prof.get('band')))
check('guardian recorded', prof.get('guardian', {}).get('name') == 'Thandi Adams')
check('guardian timestamp', bool(prof.get('guardian_signed_at')))
tags = ' '.join(prof['tags'])
check('multi tags: watching-learner', 'watching-learner' in tags, tags)
check('multi tags: doing-learner', 'doing-learner' in tags, tags)
check('intensity tag', 'standard-intensity' in tags, tags)
summary = prof['summary']
check('summary lists enjoys', 'Mathematics' in summary)
check('summary mentions band intensity', 'intermediate' in summary and 'standard' in summary, summary)
s2, back = get(f'/api/profile?id={prof["id"]}')
check('GET back by id', s2 == 200 and back.get('id') == prof['id'])
check('band in GET', back.get('band') == 'intermediate' and back.get('intensity') == 'standard', str(back.get('band')))

print('== payments: crypto rail ==')
s, q = get('/api/pay/quote?tier=plus')
check('quote 200', s == 200)
check('quote zar', q.get('amount_zar') == 599, str(q.get('amount_zar')))
check('quote eth > 0', (q.get('eth_amount') or 0) > 0, str(q.get('eth_amount')))
check('treasury present', q.get('treasury', '').startswith('0x'))
check('chain id 4663', q.get('chain_id') == 4663)
check('payfast not ready (no keys)', q.get('payfast_ready') is False)
s, free = get('/api/pay/quote?tier=discover')
check('free tier flagged', free.get('free') is True, str(free))

s, o = post('/api/pay/intent', {'tier': 'plus', 'method': 'crypto'})
check('crypto intent 200', s == 200)
check('order pending', o.get('status') == 'pending')
check('order has eth amount', (o.get('eth_amount') or 0) > 0)
oid = o.get('id')
s, e1 = post('/api/pay/confirm', {'order_id': oid, 'tx_hash': '0x' + '11'*32}, want_fail=True)
check('bogus tx rejected', s == 400, f'{s} {e1}')

s, pf = post('/api/pay/intent', {'tier': 'plus', 'method': 'payfast',
                                 'base_url': 'https://beyondtheclassroom.co.za'}, want_fail=True)
check('payfast dormant -> 503 pending keys', s == 503, f'{s} {pf}')
check('dormant message mentions keys', 'keys' in str(pf.get('error', '')), str(pf))

print('== profile multi-select round-trip ==')
check('summary lists repetition subjects', 'Reading' in prof['summary'])
check('summary lists both hard triggers', 'going too fast' in prof['summary'] and 'too much at once' in prof['summary'], prof['summary'])

print()
print(f'{ok} passed, {fail} failed')
sys.exit(1 if fail else 0)
