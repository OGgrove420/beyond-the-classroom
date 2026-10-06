"""reproduce the multi-select bug in the learner profile form (no browser needed)."""
import json, re, sys

html = open('/opt/data/learning-app/public/app.js').read()
m = re.search(r'const PQUESTIONS = \[(.*?)\n\];', html, re.S)
assert m, 'PQUESTIONS not found'
src = m.group(1)

# quote bare js keys so the literal becomes valid json
fixed = re.sub(r'(?<=[{,])\s*([A-Za-z_][A-Za-z0-9_]*)\s*:', r' "\1":', src)
fixed = fixed.replace("'", '"')
fixed = re.sub(r',\s*([\]}])', r'\1', fixed)  # strip trailing commas
fixed = fixed.rstrip().rstrip(',')  # trailing comma before the closing bracket i add
qs = json.loads('[' + fixed + ']')
print(f'{len(qs)} profile questions loaded')

fails = []
for q in qs:
    if not q.get('opts'):
        continue
    multi = bool(q.get('multi'))
    for o in q['opts']:
        if '"' in o:
            fails.append((q['k'], o, 'double quote breaks data-v attribute'))
    if not multi and q['k'] in ('enjoy', 'struggle', 'style'):
        fails.append((q['k'], '-', 'should be multi but multi flag missing'))
    print(f"  {'multi ' if multi else 'single'}: {q['k']:9s} {len(q['opts'])} options")

print()
if fails:
    print('FAILURES:')
    for f in fails:
        print(' -', f)
    sys.exit(1)
print('attribute-level check clean — bug is elsewhere')
