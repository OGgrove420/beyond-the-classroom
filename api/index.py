"""Beyond The Classroom — Vercel Python API (single handler, memory store)."""
import base64, hashlib, hmac, json, os, random, re, time, urllib.parse, urllib.request, uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler

HERE = os.path.dirname(__file__)
import sys
if HERE not in sys.path:
    sys.path.insert(0, HERE)

SITE = json.load(open(os.path.join(HERE, "..", "data", "site.json")))
SECRET = os.environ.get("BTC_SECRET", "btc-demo-secret-not-for-production")

import grades as _grades
import question_bank as _qbank
import payments as _pay

# in-memory demo state (serverless: fine for a client demo; resets per warm instance)
PROFILES = {}
TTS_REGISTRY = {}  # question id -> narration text (elevenlabs read-aloud)

# correction audio: same male voice ("Bill") for every wrong-answer correction.
CORRECTION_VOICE = "pqHfZKP75CvOlQylNhV4"


def _tts_synthesize(text, voice_id=None):
    """elevenlabs premium when the key exists, free google voice otherwise."""
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if key:
        req = urllib.request.Request(
            "https://api.elevenlabs.io/v1/text-to-speech/%s" % (voice_id or "Xb7hH8MSUJpSbSDYk0k2"),
            data=json.dumps({
                "text": text[:4500], "model_id": "eleven_turbo_v2_5",
                "voice_settings": {"stability": 0.55, "similarity_boost": 0.75,
                                   "style": 0.15, "use_speaker_boost": True},
            }).encode(),
            headers={"xi-api-key": key, "Content-Type": "application/json",
                     "Accept": "audio/mpeg"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read(), None
        except Exception as e:  # noqa: BLE001 — fall back to google voice
            print("tts elevenlabs failed, falling back:", e)
    try:
        audio = b""
        for ch in _chunk_text(text):
            url = ("https://translate.google.com/translate_tts?ie=UTF-8&tl=en"
                   f"&client=tw-ob&q={urllib.parse.quote(ch)}")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as r:
                audio += r.read()
            time.sleep(0.3)
        return audio, None
    except Exception as e:  # noqa: BLE001
        return None, f"tts failed: {e}"


def _chunk_text(text, limit=180):
    sentences = re.split(r"(?<=[.!?])\s+", text or "")
    chunks, cur = [], ""
    for s in sentences:
        if len(cur) + len(s) + 1 <= limit:
            cur = (cur + " " + s).strip()
        else:
            if cur:
                chunks.append(cur)
            cur = s[:limit]
    if cur:
        chunks.append(cur)
    return chunks



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


def res_bank_q(question_text):
    """find a bank question by its text, across all bands."""
    for band, qs in _qbank.BANK.items():
        for x in qs:
            if x["q"] == question_text:
                return x
    return None

def _check_grade(question_id, token):
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        answer, sig = raw.split(":", 1)
        expect = hmac.new(SECRET.encode(), f"{question_id}:{answer}".encode(),
                          hashlib.sha256).hexdigest()[:16]
        return int(answer) if hmac.compare_digest(sig, expect) else None
    except Exception:
        return None

def _new_quiz(grade_text=None):
    """build a quiz from the learner's grade band.

    band -> question bank + intensity (gentle/standard/stretch/exam).
    no grade -> intermediate (the default band)."""
    info = _grades.grade_info(grade_text) if grade_text else None
    band = info["band"] if info else "intermediate"
    intensity = info["intensity"] if info else _grades._INTENSITY["intermediate"]
    pool = _qbank.bank_for_band(band)
    qs = random.sample(pool, min(3, len(pool)))
    questions = []
    for x in qs:
        qid = str(uuid.uuid4())
        questions.append({
            "id": qid,
            "q": x["q"], "context": x["context"], "options": x["options"],
            "grade": _grade_token(qid, x["answer"]),
            "visual": x.get("visual", ""),
            "kinesthetic": x.get("kinesthetic", ""),
            "subject": x["subject"], "topic": x["topic"],
            "wrong": False, "correct": False, "answeredThisRound": False,
            "attempts": 0, "firstTry": None,
        })
        # registry for the tts endpoint: question + options read-aloud script
        lines = [x["q"]]
        for i, opt in enumerate(x["options"], 1):
            lines.append(f"Option {i}. {opt}")
        TTS_REGISTRY[qid] = "\n".join(lines)
        # correction registry: per-rewrite and per-option spoken corrections
        # (same elevenlabs male voice for every correction, per holder spec)
        cr = {}
        for i, rw in enumerate(x.get("rewrites", [])):
            cr[f"{qid}:rw:{i}"] = "Let's try that another way. " + rw
        for oi, note in (x.get("option_notes") or {}).items():
            opt_name = x["options"][int(oi)] if int(oi) < len(x["options"]) else "that option"
            cr[f"{qid}:opt:{oi}"] = f"You chose {opt_name}. {note}"
        TTS_REGISTRY.update(cr)
    return {
        "topic": f"{band} band",
        "band": band,
        "band_label": info["band_label"] if info else "intermediate phase (grades 4-7)",
        "intensity": intensity["label"],
        "intensity_desc": intensity["desc"],
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
        if path == "/api/auth/config":
            # supabase wired client-side; this tells the front-end which
            # providers are switched on. until SUPABASE_URL/ANON_KEY env vars
            # exist on vercel, the gateway shows a friendly "setup" state.
            # url + anon key are PUBLIC by design (row-level security protects
            # data), so serving them here is standard supabase practice.
            surl = os.environ.get("SUPABASE_URL", "")
            skey = os.environ.get("SUPABASE_ANON_KEY", "")
            configured = bool(surl) and bool(skey)
            return _json(self, 200, {
                "configured": configured,
                "url": surl if configured else "",
                "anonKey": skey if configured else "",
                "providers": {
                    "google": {"enabled": configured},
                    "email_password": {"enabled": configured},
                    "magic_link": {"enabled": configured},
                },
            })
        if path == "/api/quiz":
            qgrade = (self.path.split("grade=") + [""])[1].split("&")[0]
            qgrade = urllib.parse.unquote_plus(qgrade) if qgrade else None
            return _json(self, 200, _new_quiz(qgrade))
        if path == "/api/grades":
            # what each grade band means — for the profile screen copy
            return _json(self, 200, {
                "bands": [
                    {"band": b, "label": lbl, "intensity": _grades._INTENSITY[b]["label"],
                     "desc": _grades._INTENSITY[b]["desc"]}
                    for rng, b, lbl in _grades._BANDS
                ]})
        if path == "/api/pay/quote":
            tid = (self.path.split("tier=") + [""])[1].split("&")[0]
            t = _pay.tier_by_id(urllib.parse.unquote_plus(tid))
            if not t:
                return _json(self, 404, {"error": "unknown tier"})
            if t["price"] <= 0:
                return _json(self, 200, {"tier": t["id"], "free": True})
            q = _pay.quote_zar_to_eth(t["price"])
            return _json(self, 200, {
                "tier": t["id"], "amount_zar": t["price"],
                "eth_amount": q["eth"], "eth_zar": q["eth_zar"],
                "treasury": _pay.TREASURY, "chain_id": _pay.CHAIN_ID,
                "chain": _pay.CHAIN_NAME,
                "payfast_ready": _pay.payfast_configured()})
        if path == "/api/pay/status":
            oid = (self.path.split("id=") + [""])[1].split("&")[0]
            o = _pay.ORDERS.get(oid)
            if not o:
                return _json(self, 404, {"error": "unknown order"})
            return _json(self, 200, o)
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
            # add band + intensity so the profile card can show them
            grade_text = (p.get("grade") if isinstance(p, dict) else None)
            info = _grades.grade_info(grade_text) if grade_text else None
            out = dict(p)
            if info:
                out["band"] = info["band"]
                out["intensity"] = info["intensity"]["label"]
            return _json(self, 200, out)
        if path.startswith("/api/tts/"):
            return self._tts(path[len("/api/tts/"):])
        _json(self, 404, {"error": "not found"})

    # ---- read-aloud: elevenlabs premium voice, cached on disk ----
    def _tts(self, qid_token):
        """GET /api/tts/<qid> — narrates question + options.
           GET /api/tts/<qid>:rw:<n> — narrates correction rewrite n.
           GET /api/tts/<qid>:opt:<n> — narrates why option n was wrong."""
        import hashlib
        key_raw = qid_token.partition("?")[0]
        # correction keys use a male voice; question narration keeps the default
        voice = CORRECTION_VOICE if ":rw:" in key_raw or ":opt:" in key_raw else None
        text = TTS_REGISTRY.get(key_raw)
        if not text:
            return _json(self, 404, {"error": "unknown question"})
        cache_dir = os.environ.get("TTS_CACHE_DIR") or (
            "/tmp/btc-audio" if os.environ.get("VERCEL")
            else os.path.join(HERE, "..", "data", "audio-cache"))
        os.makedirs(cache_dir, exist_ok=True)
        cache_key = hashlib.sha1((voice or "default").encode() + b"|" + text.encode()).hexdigest()[:20]
        cpath = os.path.join(cache_dir, f"{cache_key}.mp3")
        if os.path.exists(cpath) and os.path.getsize(cpath) > 1000:
            audio = open(cpath, "rb").read()
        else:
            audio, err = _tts_synthesize(text, voice_id=voice)
            if err:
                return _json(self, 503, {"error": err})
            open(cpath, "wb").write(audio)
        self.send_response(200)
        self.send_header("Content-Type", "audio/mpeg")
        self.send_header("Content-Length", str(len(audio)))
        self.send_header("Cache-Control", "public, max-age=86400")
        self.end_headers()
        self.wfile.write(audio)

    def do_POST(self):
        path = self.path.split("?")[0]
        if path == "/api/pay/intent":
            b = self._body()
            order, err = _pay.new_order(b.get("tier"), b.get("method", "crypto"))
            if err:
                return _json(self, 400, {"error": err})
            if order["method"] == "payfast":
                fields, ferr = _pay.payfast_checkout(order, b.get("base_url", ""))
                if ferr:
                    return _json(self, 503, {"error": ferr, "order_id": order["id"]})
                order["payfast"] = fields
            return _json(self, 200, order)
        if path == "/api/pay/confirm":
            b = self._body()
            o, err = _pay.confirm_order(b.get("order_id"), b.get("tx_hash"))
            if err:
                return _json(self, 400, {"error": err})
            return _json(self, 200, o)
        if path == "/api/payfast/itn":
            b = self._body()
            if not _pay.payfast_configured():
                return _json(self, 503, {"error": "merchant keys not set"})
            ok, detail = _pay.payfast_itn_verify(b, os.environ["PAYFAST_PASSPHRASE"])
            if not ok:
                return _json(self, 400, {"error": detail})
            pid = b.get("m_payment_id", "")
            oid = pid.replace("BTC-", "")
            o = _pay.ORDERS.get(oid)
            if o:
                o["status"] = "complete"
                o["pf_payment_id"] = b.get("pf_payment_id")
                o["paid_at"] = datetime.now(_pay.SAST).isoformat()
                _pay._mirror_supabase(o)
            return _json(self, 200, {"ok": True})
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
            # wrong: serve a rotating slice of the bank's rewrites (stateless)
            rewrites = (res_bank_q(b.get("q")) or {}).get("rewrites", [])
            seen = int(b.get("seen", 0))
            return _json(self, 200, {"correct": False, "rewrites": rewrites[seen:seen+2] or rewrites[:2]})
        if path == "/api/profile":
            b = self._body()
            answers = b.get("answers", {})
            grade_text = answers.get("grade")
            info = _grades.grade_info(grade_text)
            # guardian/parent co-sign: required, completed together by the
            # learner + parent or guardian (holder rule)
            g = b.get("guardian") or {}
            if not g.get("name") or not g.get("email") or "@" not in (g.get("email") or ""):
                return _json(self, 400, {
                    "error": "guardian_missing",
                    "message": "a parent or guardian must co-sign: guardian name + email required.",
                })
            pid = str(uuid.uuid4())[:8]
            summary, tags = summarise(answers)
            if info:
                summary += f"\nGrade band: {info['band_label']}. Lessons run at {info['intensity']['label']} intensity — {info['intensity']['desc']}."
                tags.append(f"{info['intensity']['label']}-intensity")
            PROFILES[pid] = {"id": pid, "summary": summary, "tags": tags,
                             "grade": grade_text, "band": info["band"] if info else None,
                             "guardian": {"name": g.get("name"), "email": g.get("email")},
                             "guardian_signed_at": datetime.now(_pay.SAST).isoformat()}
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

def _as_list(v):
    if v is None: return []
    return v if isinstance(v, list) else [v]

def summarise(a):
    lines, tags = [], []
    if a.get("style"):
        styles = _as_list(a["style"])
        lines.append("Learns best through: " + ", ".join(s.lower() for s in styles) + ".")
        for s in styles:
            tags.append(s.split()[0].lower() + "-learner")
    if a.get("focus"):
        lines.append(f"Comfortable focus window: {a['focus']}. Short lessons work well.")
        tags.append("short-lessons")
    if a.get("struggle"):
        subs = _as_list(a["struggle"])
        lines.append("Needs more repetition in: " + ", ".join(subs) + ". The adaptive retry loop covers these.")
        tags.append("repetition-helps")
    if a.get("enjoy"):
        subs = _as_list(a["enjoy"])
        lines.append("Strong interest in: " + ", ".join(subs) + ". Use these subjects to build confidence.")
        tags.append("motivated")
    if a.get("hard"):
        hard = _as_list(a["hard"])
        lines.append("Difficulty trigger: " + ", ".join(h.lower() for h in hard) + ". Platform adjusts pacing and explanation count.")
        tags.append("paced-for-them")
    if a.get("strength"):
        lines.append(f"Strengths to build on: {a['strength']}.")
    if a.get("goal"):
        lines.append(f"This year's goal: {a['goal']}.")
    if not lines:
        return DEFAULT_SUMMARY["summary"], DEFAULT_SUMMARY["tags"]
    return "\n".join(lines), tags or ["new learner"]
