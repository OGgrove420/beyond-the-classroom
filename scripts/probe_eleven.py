"""diagnose 401: /v1/user may need different auth. try /v1/models + direct render."""
import json
import urllib.request
import urllib.error

ENV = open("/opt/data/conscious-ecom/.env").read()
EK = ENV.split("ELEVENLABS_API_KEY=")[1].split("\n")[0]

def probe(name, path, headers):
    req = urllib.request.Request(f"https://api.elevenlabs.io{path}", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read().decode()
            print(name, "->", r.status, body[:200])
    except urllib.error.HTTPError as e:
        print(name, "-> HTTP", e.code, e.read().decode()[:200])

h = {"xi-api-key": EK}
probe("user (xi-api-key)", "/v1/user", h)
probe("models (xi-api-key)", "/v1/models", h)
# maybe the stored key has a stray character: show repr without revealing
k = EK.strip()
print("len:", len(k), "| ==stripped:", k == EK, "| charset ok:", all(c.isalnum() or c in "_-" for c in k))
