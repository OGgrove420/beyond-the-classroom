"""verify elevenlabs key + list which voices are actually usable (tts:ing only)."""
import json, urllib.request

key = ""
for line in open("/opt/data/conscious-ecom/.env"):
    if line.startswith("ELEVENLABS_API_KEY="):
        key = line.split("=", 1)[1].strip()

def render(voice_id, text="testing one two"):
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        data=json.dumps({"text": text, "model_id": "eleven_turbo_v2_5"}).encode(),
        headers={"xi-api-key": key, "Content-Type": "application/json",
                 "Accept": "audio/mpeg"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return len(r.read()), None
    except Exception as e:
        return 0, str(e)[:200]

# current voice (Alice) must work; probe a few male-sounding library ids
print("alice Xb7hH8MSUJpSbSDYk0k2:", render("Xb7hH8MSUJpSbSDYk0k2"))
for name, vid in [
    ("Adam(premade)", "pNInz6obpgDQGcFmaJgB"),
    ("Antoni(premade)", "ErXwobaYiN019PkySvjV"),
    ("Josh(premade)", "TxGEqnHWrfWFTfGW9XjX"),
    ("Bill(premade)", "pqHfZKP75CvOlQylNhV4"),
]:
    print(name, vid, render(vid, text="hello"))
