"""e2e for the voiceover-corrections + auth-gateway build (local server)."""
import json, urllib.request, urllib.error, sys

BASE = "http://127.0.0.1:8712"
ok = fail = 0
def check(name, cond, extra=""):
    global ok, fail
    if cond: ok += 1; print(f"PASS {name}")
    else: fail += 1; print(f"FAIL {name} {extra}")

def get(path):
    try:
        with urllib.request.urlopen(BASE + path, timeout=120) as r:
            return r.status, r.read(), dict(r.headers)
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers)

def post(path, obj):
    req = urllib.request.Request(BASE + path, method="POST",
        data=json.dumps(obj).encode(),
        headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, json.loads(r.read()), {}
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read() or b"{}"), {}

# 1. static assets exist and are served
for p, name, minlen in [
    ("/", "index.html", 1000),
    ("/app.js", "app.js", 10000),
    ("/auth.js", "auth.js", 5000),
    ("/vendor/supabase.umd.js", "supabase bundle", 100000),
]:
    s, body, _ = get(p)
    check(f"static {name}", s == 200 and len(body) >= minlen, f"status={s} len={len(body)}")

# 2. auth config endpoint: unconfigured locally, well-formed
s, body, _ = get("/api/auth/config")
cfg = json.loads(body)
check("auth config 200", s == 200)
check("auth config shape", all(k in cfg for k in ("configured", "providers", "url", "anonKey")))
print("   configured:", cfg.get("configured"))

# 3. quiz has correction keys registered
s, body, _ = get("/api/quiz")
q = json.loads(body)
check("quiz 200", s == 200 and len(q["questions"]) >= 1)
qid = q["questions"][0]["id"]

# 4. correction audio: rewrite 0 in the male voice
s, body, hdr = get(f"/api/tts/{qid}:rw:0")
check("correction rewrite audio", s == 200 and len(body) > 3000,
      f"status={s} bytes={len(body)}")
check("correction audio is mpeg", hdr.get("Content-Type") == "audio/mpeg", hdr.get("Content-Type"))
size_rw = len(body)
s, body, _ = get(f"/api/tts/{qid}:rw:0")
check("correction audio cached", s == 200 and len(body) == size_rw)

# 5. option-note audio: pick a wrong option and fetch its why-note
s, body, _ = post("/api/quiz/answer", {"questionId": qid, "grade": q["questions"][0]["grade"], "choice": 0, "q": q["questions"][0]["q"], "seen": 0})
check("wrong answer accepted", s == 200 and body.get("correct") is False)
s, body, _ = get(f"/api/tts/{qid}:opt:0")
check("option-note audio", s == 200 and len(body) > 3000, f"status={s} bytes={len(body)}")

# 6. unknown key still 404s
s, body, _ = get(f"/api/tts/{qid}:rw:99")
check("unknown correction 404", s == 404)

# 7. correction voice differs from question voice (different cache entries, both render)
s, body, _ = get(f"/api/tts/{qid}")
check("question audio still works", s == 200 and len(body) > 3000, f"status={s} bytes={len(body)}")

# 8. auth.js references the pieces
js = open("/opt/data/learning-app/public/auth.js").read()
check("auth.js has google oauth", "signInWithOAuth" in js and "'google'" in js)
check("auth.js has magic link", "signInWithOtp" in js)
check("auth.js has password", "signInWithPassword" in js)
html = open("/opt/data/learning-app/public/index.html").read()
check("index loads supabase + auth", "supabase.umd.js" in html and "auth.js" in html)
check("index has signin nav", "signinLink" in html)
appjs = open("/opt/data/learning-app/public/app.js").read()
check("corrections are buttons", "saybtn" in appjs and "playCorrection" in appjs)
check("corrections hit tts keys", ":rw:" in appjs and ":opt:" in appjs)

print(f"\n{ok} passed, {fail} failed")
sys.exit(1 if fail else 0)
