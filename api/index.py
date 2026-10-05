"""Beyond The Classroom — Vercel Python API (single handler, memory store)."""
import base64, hashlib, hmac, json, os, random, uuid
from http.server import BaseHTTPRequestHandler

HERE = os.path.dirname(__file__)
SITE = json.load(open(os.path.join(HERE, "..", "data", "site.json")))
SECRET = os.environ.get("BTC_SECRET", "btc-demo-secret-not-for-production")

# in-memory demo state (serverless: fine for a client demo; resets per warm instance)
PROFILES = {}
QUIZ_BANK = [
    {
        "topic": "Mathematics · fractions",
        "q": "What is 1/2 + 1/4?",
        "context": "Fractions: different denominators",
        "options": ["2/6", "3/4", "1/6", "2/4"],
        "answer": 1,
        "rewrites": [
            "Think of a pizza cut into 2 pieces. You eat 1 piece. Another pizza is cut into 4 pieces and you eat 1. How much of ONE whole pizza did you eat? Cut the half-pizza into quarters and count: 2 quarters + 1 quarter = 3 quarters.",
            "Picture a bar split into 4 blocks. 1/2 fills 2 blocks. 1/4 fills 1 block. Together: 3 of the 4 blocks — that is 3/4.",
            "You have half a sandwich. Your friend gives you a quarter of another. Cut your half into two quarters. Now you hold 3 quarters of a sandwich: 3/4.",
            "Step 1: make the bottoms the same. 1/2 = 2/4. Step 2: add the tops. 2/4 + 1/4 = 3/4.",
        ],
    },
    {
        "topic": "English · parts of speech",
        "q": "Which word is an adjective? 'The quick fox jumped over the lazy dog.'",
        "context": "Adjectives describe nouns",
        "options": ["fox", "jumped", "quick", "over"],
        "answer": 2,
        "rewrites": [
            "An adjective is a describing word. Ask: what was the fox like? Quick. 'Quick' describes the fox, so it is the adjective.",
            "Nouns name things (fox, dog). Verbs are actions (jumped). Little connector words are prepositions (over). The word that paints a picture of a noun — quick — is the adjective.",
            "Say them out loud: 'a fox', 'a quick fox'. 'Quick' adds detail to 'fox'. Words that add detail like that are adjectives.",
            "Step 1: find the naming words — fox, dog. Step 2: find the word describing one of them — quick. Step 3: a word that describes a noun is an adjective.",
        ],
    },
    {
        "topic": "Science · water cycle",
        "q": "What causes water to evaporate from a dam?",
        "context": "The water cycle",
        "options": ["The wind blowing on it", "Heat from the sun", "Fish moving", "Gravity"],
        "answer": 1,
        "rewrites": [
            "Leave a glass of water on a sunny windowsill. Days later the level drops. The sun's heat turned some water into invisible vapour that floated away. That is evaporation.",
            "Heat gives water particles energy. They move faster and faster until they escape the surface into the air. The sun is the heat source, so the sun causes evaporation.",
            "A kettle on a stove steams because of heat. A dam is a giant kettle sitting on a stove called the sun — no lid, so the steam just rises.",
            "Step 1: evaporation = liquid turning into gas. Step 2: turning into gas needs energy. Step 3: the sun supplies that energy to the dam.",
        ],
    },
    {
        "topic": "Financial education · budgeting",
        "q": "You earn R500. You spend R350 on data and R200 on a gift. What is the balance?",
        "context": "Money in, money out",
        "options": ["R50 left", "-R50 (R50 short)", "R150 left", "R0"],
        "answer": 1,
        "rewrites": [
            "Think of a wallet with R500. Pay R350 for data — R150 left. The gift costs R200 but the wallet only has R150. You are R50 short. Balance: -R50.",
            "Money in: +500. Money out: 350 + 200 = 550. In minus out: 500 - 550 = -50. A negative balance means you spent more than you earned.",
            "Like a scale: R500 of income on one side, R550 of spending on the other. The spending side is heavier by R50 — you tipped R50 into debt.",
            "Step 1: add spending: 350 + 200 = 550. Step 2: subtract from income: 500 - 550. Step 3: 550 is bigger, so the answer is -50 — R50 short.",
        ],
    },
    {
        "topic": "Study skills · memory",
        "q": "Which study method is most likely to make facts stick?",
        "context": "How memory works",
        "options": [
            "Reading the page 5 times in a row",
            "Highlighting everything important",
            "Testing yourself, then re-studying what you missed",
            "Studying everything the night before",
        ],
        "answer": 2,
        "rewrites": [
            "Your brain keeps what it has to FETCH, not what it only looks at. Self-testing is fetching. Reading five times is just looking. That is why the test-then-fix loop sticks.",
            "Picture memory as a muscle: it grows when it works, not when it watches. Testing yourself is the workout. Highlighting is stretching in front of the TV.",
            "Like learning to ride a bike: you fall (get it wrong), adjust, try again. That fall-and-fix loop is exactly what self-testing does for facts.",
            "Step 1: try to recall without looking — this is the effort that builds memory. Step 2: check. Step 3: restudy only the misses. Repeat.",
        ],
    },
]

def _json(handler, code, obj):
    body = json.dumps(obj).encode()
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()
    handler.wfile.write(body)

def _grade_token(question_id, answer):
    msg = f"{question_id}:{answer}".encode()
    sig = hmac.new(SECRET.encode(), msg, hashlib.sha256).hexdigest()[:16]
    return base64.urlsafe_b64encode(f"{answer}:{sig}".encode()).decode()

def _check_grade(question_id, token):
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        answer, sig = raw.split(":", 1)
        expect = hmac.new(SECRET.encode(), f"{question_id}:{answer}".encode(),
                          hashlib.sha256).hexdigest()[:16]
        return int(answer) if hmac.compare_digest(sig, expect) else None
    except Exception:
        return None

def _new_quiz():
    qs = random.sample(QUIZ_BANK, min(4, len(QUIZ_BANK)))
    questions = []
    for x in qs:
        qid = str(uuid.uuid4())
        questions.append({
            "id": qid,
            "q": x["q"], "context": x["context"], "options": x["options"],
            "grade": _grade_token(qid, x["answer"]),
            "wrong": False, "correct": False, "answeredThisRound": False,
            "attempts": 0, "firstTry": None,
        })
    return {
        "topic": qs[0]["topic"].split("·")[0].strip(),
        "idx": 0,
        "questions": questions,
    }

class handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n) or b"{}")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,DELETE,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/api/site":
            return _json(self, 200, SITE)
        if path == "/api/quiz":
            return _json(self, 200, _new_quiz())
        if path == "/api/parent":
            # demo data, clearly labelled on the page
            return _json(self, 200, {
                "lessonsThisWeek": 12,
                "minutes": 186,
                "mastered": 9,
                "tryAgainRate": 34,
                "subjects": [
                    {"name": "Mathematics", "lessons": 5, "trend": "up", "status": "steady"},
                    {"name": "English", "lessons": 3, "trend": None, "status": "steady"},
                    {"name": "Science", "lessons": 2, "trend": "up", "status": "improving"},
                    {"name": "Financial education", "lessons": 2, "trend": None, "status": "new"},
                ],
                "insights": [
                    {"title": "learns best through visuals", "body": "Accuracy improved 22% when visual explanations were offered after a first wrong answer."},
                    {"title": "benefits from repetition in fractions", "body": "Needed 'try again' twice on fractions, then mastered the concept on the follow-up question."},
                    {"title": "confidence grows untimed", "body": "Session completion rises when questions carry no timer. Keep sessions short and untimed."},
                ],
            })
        if path == "/api/profile":
            pid = (self.path.split("?id=") + [""])[1]
            p = PROFILES.get(pid) or next(iter(PROFILES.values()), None) or DEFAULT_SUMMARY
            return _json(self, 200, p)
        _json(self, 404, {"error": "not found"})

    def do_POST(self):
        path = self.path.split("?")[0]
        if path == "/api/quiz/answer":
            b = self._body()
            qid = b.get("questionId")
            answer = _check_grade(qid, b.get("grade", ""))
            if answer is None:
                return _json(self, 400, {"error": "invalid grade token"})
            correct = b.get("choice") == answer
            if correct:
                return _json(self, 200, {"correct": True, "praise": random.choice([
                    "nice work. on to the next one.",
                    "you've got it. see how trying again works?",
                    "exactly right.",
                ])})
            # wrong: serve a rotating slice of the four rewrites (stateless)
            qs = next((x for x in QUIZ_BANK if x["q"] == b.get("q")), None)
            rewrites = (qs or {}).get("rewrites", [])
            seen = int(b.get("seen", 0))
            return _json(self, 200, {"correct": False, "rewrites": rewrites[seen:seen+2] or rewrites[:2]})
        if path == "/api/profile":
            b = self._body()
            pid = str(uuid.uuid4())[:8]
            summary, tags = summarise(b.get("answers", {}))
            PROFILES[pid] = {"id": pid, "summary": summary, "tags": tags}
            return _json(self, 200, PROFILES[pid])
        _json(self, 404, {"error": "not found"})

    def do_DELETE(self):
        if self.path.split("?")[0] == "/api/profile":
            PROFILES.clear()
            return _json(self, 200, {"ok": True})
        _json(self, 404, {"error": "not found"})

DEFAULT_SUMMARY = {
    "id": "guest",
    "summary": "No profile yet — this is the default view. Build a profile to see a personalised summary.",
    "tags": ["new learner"],
}

def summarise(a):
    lines, tags = [], []
    if a.get("style"):
        lines.append(f"Learns best through: {a['style'].lower()}.")
        tags.append(a["style"].split()[0].lower() + "-learner")
    if a.get("focus"):
        lines.append(f"Comfortable focus window: {a['focus']}. Short lessons work well.")
        tags.append("short-lessons")
    if a.get("struggle"):
        lines.append(f"Needs more repetition in: {a['struggle']}. The adaptive retry loop covers this.")
        tags.append("repetition-helps")
    if a.get("enjoy"):
        lines.append(f"Strong interest in: {a['enjoy']}. Use these subjects to build confidence.")
        tags.append("motivated")
    if a.get("hard"):
        lines.append(f"Difficulty trigger: {a['hard'].lower()}. Platform adjusts pacing and explanation count.")
        tags.append("paced-for-them")
    if a.get("strength"):
        lines.append(f"Strengths to build on: {a['strength']}.")
    if a.get("goal"):
        lines.append(f"This year's goal: {a['goal']}.")
    if not lines:
        return DEFAULT_SUMMARY["summary"], DEFAULT_SUMMARY["tags"]
    return "\n".join(lines), tags or ["new learner"]
