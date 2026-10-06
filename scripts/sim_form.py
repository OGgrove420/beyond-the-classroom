"""simulate the learner-form DOM lifecycle from app.js alone.

models:
  renderLearner() -> innerHTML wipe + addEventListener on .opts
  user taps option buttons (multi: toggle .sel; single: exclusive .sel)
  saveProfile.onclick -> querySelectorAll('.opts[data-k=..] .opt.sel')

question: can any sequence of user actions lose multi-select data?
"""

import json, re

app = open('/opt/data/learning-app/public/app.js').read()
m = re.search(r'const PQUESTIONS = \[(.*?)\n\];', app, re.S)
src = m.group(1)
fixed = re.sub(r'(?<=[{,])\s*([A-Za-z_][A-Za-z0-9_]*)\s*:', r' "\1":', src)
fixed = fixed.replace("'", '"')
fixed = re.sub(r',\s*([\]}])', r'\1', fixed)
fixed = fixed.rstrip().rstrip(',')
PQUESTIONS = json.loads('[' + fixed + ']')

class Form:
    """faithful model of the shipped handlers."""
    def __init__(self):
        self.groups = {}   # k -> {opt: sel_bool}
        for q in PQUESTIONS:
            if q.get('opts'):
                self.groups[q['k']] = {o: False for o in q['opts']}

    def tap(self, k, opt):
        """one click on an option button"""
        g = self.groups[k]
        multi = next(q.get('multi', False) for q in PQUESTIONS if q['k'] == k)
        if multi:
            g[opt] = not g[opt]                      # toggle
        else:
            for o in g: g[o] = False                 # exclusive
            g[opt] = True

    def save(self):
        out = {}
        for q in PQUESTIONS:
            k = q['k']
            if q.get('opts'):
                sel = [o for o, s in self.groups[k].items() if s]
                out[k] = sel if q.get('multi') else (sel[0] if sel else None)
            else:
                out[k] = None
        return out

f = Form()
print('scenario: holder taps 3 subjects, 2 struggles, 2 styles, 1 focus, 1 hard')
for a in ('Mathematics', 'Science', 'Art'):                 f.tap('enjoy', a)
for a in ('Reading', 'Exams'):                              f.tap('struggle', a)
for a in ('Watching videos', 'Doing practical activities'): f.tap('style', a)
f.tap('focus', '10–20 minutes')
f.tap('hard', 'Going too fast')
saved = f.save()
print(json.dumps(saved, indent=2))

print()
print('multi-select fields survive taps:', all(saved[k] for k in ('enjoy', 'struggle', 'style')))

# the killer: renderLearner is invoked by go('learner') / nav clicks.
# each call re-runs $app.innerHTML = ... -> every .sel class is destroyed.
print()
print('BUT: every render() (nav tap, view switch) re-runs renderLearner() and')
print('sets innerHTML afresh — no selection state is stored anywhere.')
print('searching app.js for any state store for profile-form selections...')
for pat in ('btc_form', 'draft', 'localStorage', 'sessionStorage'):
    hits = [ln for ln in app.splitlines() if pat in ln]
    print(f'  {pat}: {len(hits)} hits')
