"""run api/index.py as a real local http server for e2e testing.
mirrors vercel.json routing: /api/* -> handler, everything else -> public/."""
import importlib.util, os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PUBLIC = "/opt/data/learning-app/public"

spec = importlib.util.spec_from_file_location("api_index", "/opt/data/learning-app/api/index.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8712

class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=PUBLIC, **kw)
    def translate_path(self, path):
        p = path.split("?")[0]
        if p.startswith("/api/"):
            return p  # won't exist as a file; do_GET intercepts first
        if p in ("/", "/index.html", ""):
            return os.path.join(PUBLIC, "index.html")
        return super().translate_path(path)
    def do_GET(self):
        if self.path.split("?")[0].startswith("/api/"):
            return m.handler.do_GET(self)
        return SimpleHTTPRequestHandler.do_GET(self)
    def do_POST(self):
        if self.path.split("?")[0].startswith("/api/"):
            return m.handler.do_POST(self)
        self.send_error(404)
    def do_OPTIONS(self):
        return m.handler.do_OPTIONS(self)
    def log_message(self, *a):
        pass

srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
# the lambda class keeps its helpers to itself; lend them to the local wrapper
for _name in ("_tts", "_body"):
    setattr(Handler, _name, getattr(m.handler, _name))
print(f"serving api+static on {port}", flush=True)
srv.serve_forever()
