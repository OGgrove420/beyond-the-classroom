import os, re, json, urllib.request, urllib.error

env = open('/opt/data/learning-app/.env').read()
url = re.search(r'SUPABASE_URL=(\S+)', env).group(1)
anon = re.search(r'SUPABASE_ANON_KEY=(\S+)', env).group(1)
srole = re.search(r'SUPABASE_SERVICE_ROLE_KEY=(\S+)', env).group(1)

def probe(path, key, label):
    req = urllib.request.Request(url + path, headers={
        'apikey': key, 'Authorization': 'Bearer ' + key})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            body = r.read().decode()
            try:
                spec = json.loads(body)
                tables = sorted(spec.get('definitions', {}).keys())
                print(label, r.status, 'tables:', tables)
            except Exception:
                print(label, r.status, body[:200])
    except urllib.error.HTTPError as e:
        print(label, 'HTTP', e.code, e.read().decode()[:200])
    except Exception as e:
        print(label, 'failed:', e)

probe('/rest/v1/', anon, 'rest+anon:')
probe('/rest/v1/', srole, 'rest+service:')
