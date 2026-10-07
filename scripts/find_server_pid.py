"""find and report PIDs listening on 8712 (kill is done separately)."""
import os, glob

pids = []
for p in glob.glob('/proc/[0-9]*/cmdline'):
    try:
        cmd = open(p, 'rb').read().decode().replace('\0', ' ')
        if 'serve_local.py' in cmd and '8712' in cmd:
            pids.append((p.split('/')[2], cmd.strip()))
    except Exception:
        pass
for pid, cmd in pids:
    print(pid, cmd)
if not pids:
    print('none found')
