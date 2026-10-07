import json, re, base64

d = json.load(open('/opt/data/learning-app/data/site.json'))
print('site keys:', list(d.keys()))
print('tiers:', [(t['id'], t['name'], t['price']) for t in d['tiers']])
if 'payments' in d: print('payments:', d['payments'])
if 'crypto' in d: print('crypto:', d['crypto'])

env = open('/opt/data/learning-app/.env').read()
for line in env.splitlines():
    if line.strip():
        k, _, v = line.partition('=')
        shown = v[:12] + '...' if len(v) > 12 else v
        print(k, '=', shown)

chat = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRmY3BzYXF1dHRkaXNjcWZ5dmNkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTEzMDAyMjYsImV4cCI6MjEwNjg3NjIyNn0.DR-h7C6tV54aiYH0Byg1dgSSHpjZsmSRS6EWo6zcS6c'
p = json.loads(base64.urlsafe_b64decode(chat.split('.')[1] + '=='))
print('chat jwt payload:', p)

m = re.search(r'SUPABASE_URL=(\S+)', env)
print('env supabase url:', m.group(1) if m else None)
m2 = re.search(r'SUPABASE_ANON_KEY=(\S{30})', env)
print('env anon key ref matches chat token:', 'dfcpsaquttdiscqfyvcd' in (m2.group(1) if m2 else ''))
