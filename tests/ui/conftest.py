"""
Pytest fixtures for UI tests: serve static fixture app so tests run without building React.
Set BASE_URL (e.g. BASE_URL=http://localhost:3000) to run against a real app instead.
"""
import os
import socket
import threading

import pytest

# Only load server when running UI tests that need it
try:
    from http.server import HTTPServer, SimpleHTTPRequestHandler
except ImportError:
    HTTPServer = None
    SimpleHTTPRequestHandler = None


def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


class _SPAFixtureHandler(SimpleHTTPRequestHandler):
    """Serves mini_app.html for all paths so SPA routing works."""

    html_path = None

    def do_GET(self):
        if self.html_path and self.html_path.exists():
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(self.html_path.read_bytes())
        else:
            self.send_error(404)


@pytest.fixture(scope="session")
def ui_fixture_server():
    """Start a local HTTP server serving the static fixture (mini SPA) for UI tests."""
    if HTTPServer is None or SimpleHTTPRequestHandler is None:
        pytest.skip("http.server not available")

    import pathlib
    fixtures_dir = pathlib.Path(__file__).resolve().parent / "fixtures"
    html_file = fixtures_dir / "mini_app.html"
    if not html_file.exists():
        pytest.skip("UI fixture not found: %s" % html_file)

    _SPAFixtureHandler.html_path = html_file
    port = _find_free_port()
    server = None

    try:
        server = HTTPServer(("127.0.0.1", port), _SPAFixtureHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        yield {"port": port, "server": server}
    finally:
        if server:
            server.shutdown()


@pytest.fixture(scope="session")
def base_url(request):
    """Base URL for the app. Use BASE_URL env (e.g. http://localhost:3000) to hit a real server."""
    env_url = (os.environ.get("BASE_URL") or "").strip().rstrip("/")
    if env_url:
        return env_url
    port = request.getfixturevalue("ui_fixture_server")["port"]
    return "http://127.0.0.1:%s" % port
