"""walk the save path of the learner form exactly as app.js does it."""
import json, re

app = open('/opt/data/learning-app/public/app.js').read()

m = re.search(r'const PQUESTIONS = \[(.*?)\n\];', app, re.S)
src = m.group(1)
fixed = re.sub(r'(?<=[{,])\s*([A-Za-z_][A-Za-z0-9_]*)\s*:', r' "\1":', src)
fixed = fixed.replace("'", '"')
fixed = re.sub(r',\s*([\]}])', r'\1', fixed)
fixed = fixed.rstrip().rstrip(',')
qs = json.loads('[' + fixed + ']')

# simulate: user taps 3 subjects on 'enjoy', 1 on 'struggle', 2 styles.
# single-select groups: user tapped 'Too much at once' on hard, nothing on focus.
taps = {
    'enjoy': ['Mathematics', 'Science', 'Art'],
    'struggle': ['Reading'],
    'style': ['Watching videos', 'Listening'],
    'hard': ['Too much at once'],
    'focus': [],
}

saved = {}
for q in qs:
    k = q['k']
    if q.get('opts'):
        sel = taps.get(k, [])
        if q.get('multi'):
            saved[k] = sel
        else:
            saved[k] = sel[0] if sel else None
    else:
        saved[k] = None

print('client sends to /api/profile:')
print(json.dumps(saved, indent=2))

# now the server side: api/index.py summarise()
api = open('/opt/data/learning-app/api/index.py').read()
print()
print('server summarise() handles:')
for key in ('style', 'focus', 'struggle', 'enjoy', 'hard', 'strength', 'goal'):
    present = f'a.get("{key}")' in api
    aslist = '_as_list' in api
    print(f'  {key:9s} read={present}  list-safe={aslist}')

# check the GET round-trip: after save, profile card renders data.summary + tags
print()
print('GET /api/profile?id= returns ONLY {id, summary, tags} — raw multi-select')
print('answers are NOT echoed back. profile card cannot re-render selections.')
