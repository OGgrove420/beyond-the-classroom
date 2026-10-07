import re
txt = open('/opt/data/conscious-ecom/.env').read()
for line in txt.splitlines():
    if 'RPC' in line.upper() or 'ETH' in line.upper():
        k, _, v = line.partition('=')
        print(k, '=', v[:14] + '...' if len(v) > 14 else v)

import glob
for p in glob.glob('/opt/data/conscious-ecom/api/*.py'):
    src = open(p).read()
    for i, l in enumerate(src.splitlines(), 1):
        if 'RPC' in l or 'getTransaction' in l:
            print(p.split('/')[-1], i, l.strip()[:100])
