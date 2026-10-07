import os, glob
# find the conscious-ecom env and any rpc mention in the project
print('env exists:', os.path.exists('/opt/data/conscious-ecom/.env'))
p = '/opt/data/conscious-ecom/.env'
if os.path.exists(p):
    for line in open(p).read().splitlines():
        if line.strip() and not line.strip().startswith('#'):
            k, _, v = line.partition('=')
            print(k, '=', (v[:10] + '...') if len(v) > 10 else v)
