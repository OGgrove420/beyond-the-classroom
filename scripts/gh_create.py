"""create OGgrove420/beyond-the-classroom via github api (token from conscious-ecom remote, never printed)."""
import json, re, subprocess, sys, urllib.request, urllib.error

url = subprocess.run(["git", "remote", "get-url", "origin"], cwd="/opt/data/conscious-ecom",
                     capture_output=True, text=True).stdout.strip()
tok = re.search(r"x-access-token:([^@]+)@", url).group(1)

name = "beyond-the-classroom"
desc = "Different Pace. Same Potential. — adaptive online learning platform test build (Conscious Mind Concepts)."

def gh(method, path, body=None):
    req = urllib.request.Request(f"https://api.github.com{path}",
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"token {tok}", "Accept": "application/vnd.github+json",
                 "User-Agent": "kiddie-6171", "Content-Type": "application/json"},
        method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")

c, existing = gh("GET", f"/repos/OGgrove420/{name}")
if c == 200:
    print("repo already exists:", existing.get("html_url"))
    sys.exit(0)

c, repo = gh("POST", "/user/repos", {
    "name": name, "description": desc, "private": False,
    "auto_init": False, "has_issues": True, "has_wiki": False,
})
print("create:", c)
if c not in (201, 422):
    print(json.dumps(repo)[:500]); sys.exit(1)
print("url:", repo.get("html_url", f"https://github.com/OGgrove420/{name}"))
