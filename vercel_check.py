"""read-only vercel account check using the token from conscious-ecom/.env (never prints it)."""
import json, urllib.request, urllib.error

env = open("/opt/data/conscious-ecom/.env").read()
vc = env.split("VERCEL_TOKEN=")[1].split("\n")[0]

def vapi(path):
    req = urllib.request.Request(f"https://api.vercel.com{path}",
        headers={"Authorization": f"Bearer {vc}"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

c, user = vapi("/v2/user")
print("user:", c, user.get("user", {}).get("username"), user.get("user", {}).get("email"))

c, teams = vapi("/v2/teams?limit=5")
print("teams:", c, [(t.get("id"), t.get("slug")) for t in teams.get("teams", [])])

c, projs = vapi("/v9/projects?limit=20")
print("projects:", c, [p.get("name") for p in projs.get("projects", [])])
