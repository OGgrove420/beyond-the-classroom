"""run api/index.py as a real local http server for e2e testing."""
import importlib.util, sys
from http.server import ThreadingHTTPServer

spec = importlib.util.spec_from_file_location("api_index", "/opt/data/learning-app/api/index.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8712
srv = ThreadingHTTPServer(("127.0.0.1", port), m.handler)
print(f"serving on {port}", flush=True)
srv.serve_forever()
