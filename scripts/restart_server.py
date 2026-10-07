"""restart the local server: SIGTERM the stale listener, then it gets relaunched."""
import os, signal, time

for pid_cmd in [(17799, 'python3 scripts/serve_local.py 8712')]:
    pid, cmd = pid_cmd
    try:
        os.kill(pid, signal.SIGTERM)
        print('sent SIGTERM to', pid, cmd)
    except ProcessLookupError:
        print(pid, 'already gone')
time.sleep(1.5)
# confirm port is free
import socket
s = socket.socket()
try:
    s.connect(('127.0.0.1', 8712))
    print('port 8712 still serving — old process alive?')
    s.close()
except Exception as e:
    print('port 8712 free:', e)
