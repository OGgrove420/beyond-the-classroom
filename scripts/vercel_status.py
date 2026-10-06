"""check vercel deployments for beyond-the-classroom via API, promote latest if needed."""
import json, os, time, urllib.request

TOKEN = None
for line in open('/opt/data/conscious-ecom/.env'):
    if line.startswith('VERCEL_TOKEN='):
        TOKEN = line.split('=', 1)[1].strip().strip('"').strip("'")
assert TOKEN, 'no vercel token found'

def api(path, method='GET', body=None):
    req = urllib.request.Request('https://api.vercel.com' + path,
                                 headers={'Authorization': 'Bearer ' + TOKEN},
                                 method=method,
                                 data=json.dumps(body).encode() if body else None)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

# list projects, find beyond-the-classroom
projects = api('/v9/projects?limit=20')
names = [p['name'] for p in projects.get('projects', [])]
print('projects:', names)
match = [p for p in projects['projects'] if 'beyond' in p['name'].lower()]
assert match, 'no beyond-the-classroom project on vercel'
proj = match[0]
pid = proj['id']
print('project:', proj['name'], pid)

# latest deployments
deps = api(f'/v6/deployments?projectId={pid}&limit=5')
for d in deps.get('deployments', [])[:5]:
    print(f"  {d.get('uid')} {d.get('state'):10s} {d.get('createdAt') and time.strftime('%H:%M', time.gmtime(d['createdAt']/1000))}Z meta={json.dumps(d.get('meta',{}))[:80]}")
