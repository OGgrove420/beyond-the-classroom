"""git init + push /opt/data/learning-app to OGgrove420/beyond-the-classroom (token from conscious-ecom remote, never printed)."""
import re, subprocess

url = subprocess.run(["git", "remote", "get-url", "origin"], cwd="/opt/data/conscious-ecom",
                     capture_output=True, text=True).stdout.strip()
tok = re.search(r"x-access-token:([^@]+)@", url).group(1)

ROOT = "/opt/data/learning-app"

def git(*args, cwd=ROOT):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()

print(git("init", "-b", "main"))
print(git("config", "user.name", "OGgrove420"))
print(git("config", "user.email", "natheer17@gmail.com"))
print(git("add", "-A"))
print(git("commit", "-m", "Beyond The Classroom — adaptive learning test build (phase 1)"))
print(git("remote", "add", "origin", f"https://x-access-token:{tok}@github.com/OGgrove420/beyond-the-classroom.git"))
print(git("push", "-u", "origin", "main"))
# sanity: show the remote without the token
clean = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
print("remote ok:", re.sub(r"://[^@]+@", "://***@", clean))
