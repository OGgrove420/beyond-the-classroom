"""local smoke test for api/index.py logic (no server)."""
import importlib.util, json, sys

spec = importlib.util.spec_from_file_location("api_index", "/opt/data/learning-app/api/index.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# summarise
s, tags = m.summarise({
    "style": "Watching videos", "focus": "10–20 minutes",
    "struggle": "Mathematics", "enjoy": "Science", "hard": "Going too fast",
})
print("summary ok:", len(s) > 50, "| tags:", tags)

# quiz bank integrity
for q in m.QUIZ_BANK:
    assert 0 <= q["answer"] < len(q["options"]), q["q"]
    assert len(q["rewrites"]) == 4, q["q"]
print("quiz bank ok:", len(m.QUIZ_BANK), "questions, all have 4 rewrites, valid answers")

# site json loads through the module
assert m.SITE["brand"]["name"] == "Beyond The Classroom"
print("site.json ok:", len(m.SITE["tiers"]), "tiers,", sum(len(v) for v in m.SITE["subjects"].values()), "subjects")
