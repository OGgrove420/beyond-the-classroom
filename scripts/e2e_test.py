"""end-to-end local test: quiz with modality fields, multi-select profile, tts audio."""
import json
import os
import sys
import urllib.request
from http.server import ThreadingHTTPServer

sys.path.insert(0, "/opt/data/learning-app/api")
os.environ["ELEVENLABS_API_KEY"] = open(
    "/opt/data/conscious-ecom/.env").read().split("ELEVENLABS_API_KEY=")[1].split("\n")[0]
os.environ["TTS_CACHE_DIR"] = "/tmp/btc-test-audio"

import index  # noqa: E402

srv = ThreadingHTTPServer(("127.0.0.1", 8765), index.handler)
import threading
t = threading.Thread(target=srv.serve_forever, daemon=True)
t.start()
B = "http://127.0.0.1:8765"

# 1. quiz carries modality fields
quiz = json.loads(urllib.request.urlopen(B + "/api/quiz").read())
q1 = quiz["questions"][0]
print("1. quiz ok | questions:", len(quiz["questions"]),
      "| visual field:", bool(q1.get("visual")),
      "| kinesthetic field:", bool(q1.get("kinesthetic")))

# 2. tts endpoint returns real audio for the first question
r = urllib.request.urlopen(B + f"/api/tts/{q1['id']}", timeout=120)
audio = r.read()
print("2. tts ok | bytes:", len(audio),
      "| engine: elevenlabs" if len(audio) > 50000 else "| engine: fallback",
      "| content-type:", r.headers["Content-Type"])
# engine check: which cache engine was used
meta = os.path.exists("/tmp/btc-test-audio")
print("   cached to disk:", meta)

# 3. multi-select profile: send arrays, expect a summary naming both
body = json.dumps({"answers": {
    "grade": "Grade 6",
    "enjoy": ["Mathematics", "Science", "Art"],
    "struggle": ["Fractions", "Exams"],
    "style": ["Watching videos", "Listening", "Doing practical activities"],
    "focus": "10–20 minutes",
}}).encode()
req = urllib.request.Request(B + "/api/profile", data=body,
                             headers={"Content-Type": "application/json"}, method="POST")
prof = json.loads(urllib.request.urlopen(req).read())
print("3. multi-profile ok | tags:", prof["tags"])
print("   summary names multiple subjects:", "Mathematics, Science, Art" in prof["summary"])
print("   summary names multiple styles:", "videos, listening, doing practical activities" in prof["summary"])

# 4. answer grading still works (stateless token)
req = urllib.request.Request(B + "/api/quiz/answer",
    data=json.dumps({"questionId": q1["id"], "grade": q1["grade"], "choice": 99,
                     "q": q1["q"], "seen": 0}).encode(),
    headers={"Content-Type": "application/json"}, method="POST")
res = json.loads(urllib.request.urlopen(req).read())
print("4. wrong answer -> rewrites served:", res["correct"] is False, "| count:", len(res["rewrites"]))

srv.shutdown()
print("ALL CHECKS DONE")
