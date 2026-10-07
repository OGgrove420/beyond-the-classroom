"""Grade banding + intensity for beyond-the-classroom.

maps a learner's stated grade to:
  - a grade band (foundation / intermediate / senior / fet)
  - question difficulty mix (intensity) per band

CAPS grades (SA): 1-3 foundation, 4-7 intermediate, 8-9 senior, 10-12 FET.
'a grade R' and 'grade 0' also map to foundation.
"""

# accepted grade strings -> (band, number)
_BANDS = [
    (range(1, 4), "foundation",   "foundation phase (grades 1-3)"),
    (range(4, 8), "intermediate", "intermediate phase (grades 4-7)"),
    (range(8, 10), "senior",      "senior phase (grades 8-9)"),
    (range(10, 13), "fet",        "FET phase (grades 10-12)"),
]

_INTENSITY = {
    # band: how hard the question mix runs, and how much scaffolding
    "foundation": {
        "label": "gentle",
        "desc": "short sentences, one idea per question, everyday objects in examples, always 4 rewrites",
        "max_options": 3,
        "rewrites_target": 4,
        "reading_level": "grade 1-3 vocabulary",
    },
    "intermediate": {
        "label": "standard",
        "desc": "clear sentences, two-step problems appear, mixed concrete and abstract examples",
        "max_options": 4,
        "rewrites_target": 3,
        "reading_level": "grade 4-7 vocabulary",
    },
    "senior": {
        "label": "stretch",
        "desc": "multi-step problems, abstract reasoning, exam-style wording introduced",
        "max_options": 4,
        "rewrites_target": 3,
        "reading_level": "grade 8-9 vocabulary",
    },
    "fet": {
        "label": "exam",
        "desc": "full exam register, multi-step with interpretation, mark-weighted style",
        "max_options": 4,
        "rewrites_target": 2,
        "reading_level": "grade 10-12 vocabulary",
    },
}

def parse_grade(text):
    """'Grade 6', 'grade 6', '6', 'G6' -> 6. returns None when unparseable."""
    if not text:
        return None
    t = str(text).strip().lower()
    digits = "".join(ch for ch in t if ch.isdigit())
    if not digits:
        # R / RR = reception
        if t in ("r", "rr", "grade r", "reception", "grade 0", "0"):
            return 0
        return None
    try:
        n = int(digits)
    except ValueError:
        return None
    if 0 <= n <= 12:
        return n
    return None

def grade_info(text):
    """grade text -> {grade, band, band_label, intensity:{...}} or None."""
    n = parse_grade(text)
    if n is None:
        return None
    for rng, band, label in _BANDS:
        if n in rng:
            info = {"grade": n, "band": band, "band_label": label}
            info["intensity"] = dict(_INTENSITY[band])
            return info
    if n == 0:
        info = {"grade": 0, "band": "foundation", "band_label": "foundation phase (grade R)"}
        info["intensity"] = dict(_INTENSITY["foundation"])
        return info
    return None

def band_of(text):
    info = grade_info(text)
    return info["band"] if info else "intermediate"

def intensity_of(text):
    info = grade_info(text)
    return info["intensity"]["label"] if info else "standard"
