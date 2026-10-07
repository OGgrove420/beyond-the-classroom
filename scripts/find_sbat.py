"""Scan env files across the workspace for a supabase access token (sbat_ or long jwt)."""
import os, re, glob

pat = re.compile(r'SUPABASE_ACCESS_TOKEN\s*=\s*(\S+)|(\bsbat_[A-Za-z0-9_\-]{20,})')
hits = []
for root in ['/opt/data', os.path.expanduser('~')]:
    for p in glob.glob(root + '/**/.env*', recursive=True) + glob.glob(root + '/.env*'):
        try:
            txt = open(p).read()
        except Exception:
            continue
        for m in pat.finditer(txt):
            hits.append((p, (m.group(1) or m.group(2))[:10] + '...'))
for p, v in hits:
    print(p, v)
if not hits:
    print('no access token anywhere')
