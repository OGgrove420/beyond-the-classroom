import re
html = open('/opt/data/learning-app/public/app.js').read()
m = re.search(r'const PQUESTIONS = \[(.*?)\n\];', html, re.S)
src = m.group(1)
fixed = re.sub(r'(?<=[{,])\s*([A-Za-z_][A-Za-z0-9_]*)\s*:', r' "\1":', src)
fixed = fixed.replace("'", '"')
fixed = re.sub(r',\s*([\]}])', r'\1', fixed)
lines = fixed.splitlines()
print('total lines:', len(lines))
for i, ln in enumerate(lines):
    print(i + 1, repr(ln[:160]))
