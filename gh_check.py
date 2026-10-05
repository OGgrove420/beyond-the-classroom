"""verify github token from conscious-ecom remote (never prints the token)."""
import json, re, subprocess, urllib.request

url = subprocess.run(["git", "remote", "get-url", "origin"], cwd="/opt/data/conscious-ecom",
                     capture_output=True, text=True).stdout.strip()
m = re.search(r"x-access-token:([^@]+)@", url)
if not m:
    raise SystemExit("no token in remote url")
tok = m.group(1)

req = urllib.request.Request("https://api.github.com/user",
                             headers={"Authorization": f"token {tok}", "User-Agent": "kiddie"})
with urllib.request.urlopen(req, timeout=30) as r:
    u = json.loads(r.read().decode())
print("github user:", u["login"])
# check scopes on the response headers
req2 = urllib.request.Request("https://api.github.com/user", headers={"Authorization": f"token {tok}"})
with urllib.request.urlopen(req2, timeout=30) as r2:
    print("token scopes:", r2.headers.get("X-OAuth-Scopes"))
