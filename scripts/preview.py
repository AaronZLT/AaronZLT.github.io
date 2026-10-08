from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlsplit

from build import DIST, build


class PreviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if urlsplit(self.path).path in ("/", "/index.html"):
            build()
        super().do_GET()


if __name__ == "__main__":
    build()
    server = HTTPServer(
        ("127.0.0.1", 4173),
        partial(PreviewHandler, directory=str(DIST)),
    )
    print("Local preview: http://127.0.0.1:4173/", flush=True)
    print("Refresh the page after editing content, templates, or styles.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
