"""check elevenlabs key health (chars remaining, tier) without printing the key."""
import json
import urllib.request

ENV = open("/opt/data/conscious-ecom/.env").read()
EK = ENV.split("ELEVENLABS_API_KEY=")[1].split("\n")[0]
req = urllib.request.Request("https://api.elevenlabs.io/v1/user",
                             headers={"xi-api-key": EK})
with urllib.request.urlopen(req, timeout=20) as r:
    d = json.loads(r.read().decode())
sub = d.get("subscription", {})
print("key OK | tier:", sub.get("tier"),
      "| voices:", sub.get("voice_limit"),
      "| chars:", sub.get("character_count"), "/", sub.get("character_limit"))
