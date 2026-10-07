"""deploy the voiceover-corrections + auth-gateway build:
git commit+push, v13 file deploy to production beyond-the-classroom."""
import base64, json, os, re, time, urllib.request

ROOT = "/opt/data/learning-app"
NAME = "beyond-the-classroom"
TEAM = "team_wEyluNo7GBIA4WQVkliLTL69"

env = open("/opt/data/conscious-ecom/.env").read()
VT = env.split("VERCEL_TOKEN=")[1].split("\n")[0]

# ---- 0. git commit + push ----
os.system(f"git -C {ROOT} config user.name OGgrove420")
os.system(f"git -C {ROOT} config user.email natheer17@gmail.com")
os.system(f"git -C {ROOT} add -A")
rc = os.system(f'git -C {ROOT} commit -m "wrong-answer corrections read aloud (elevenlabs male voice, tappable buttons) + auth gateway (google/email/magic-link via supabase, activates when keys land)"')
if rc != 0:
    print("nothing to commit")
push = os.popen(f"git -C {ROOT} push origin HEAD 2>&1").read().strip()
print("push:", push[-120:])

# ---- 1. v13 file deploy (full tree, scratch excluded) ----
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".vercel"}
SKIP_FILES = set()
SKIP_PREFIX = ("data/audio-cache/",)
files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for fn in filenames:
        full = os.path.join(dirpath, fn)
        rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
        if rel.startswith(SKIP_PREFIX):
            continue
        files.append({"file": rel, "data": base64.b64encode(open(full, "rb").read()).decode(),
                      "encoding": "base64"})
print("files:", len(files))

def api(method, path, payload):
    req = urllib.request.Request(f"https://api.vercel.com{path}",
        data=json.dumps(payload).encode() if payload is not None else None,
        method=method,
        headers={"Authorization": f"Bearer {VT}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read())

dep = api("POST", f"/v13/deployments?skipAutoDetectionConfirmation=1&teamId={TEAM}",
          {"name": NAME, "target": "production", "files": files})
uid = dep.get("uid") or dep.get("id")
if not uid:
    print("raw body:", json.dumps(dep)[:800]); raise SystemExit(1)
print("deployment:", uid)
d = dep
if dep.get("readyState") != "READY":
    for _ in range(60):
        time.sleep(5)
        d = api("GET", f"/v13/deployments/{uid}?teamId={TEAM}", None)
        if d.get("readyState") in ("READY", "ERROR"):
            break
print("readyState:", d.get("readyState"))
print("aliases:", d.get("alias"))
if d.get("readyState") != "READY":
    print("errors:", json.dumps(d.get("builds", d))[:500]); raise SystemExit(1)
print("OK", d.get("url"))
open("/tmp/btc_voice_auth_deploy.txt", "w").write(d.get("url", "") + " " + uid)
