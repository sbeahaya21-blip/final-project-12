"""
Pytest fixtures for UI tests.
- When BASE_URL is set: use it (live app or ngrok).
- When BASE_URL is not set: serve static fixture so CI can run UI tests with mocked APIs (mock ERP).
"""
import os
import socket
import threading
import time
from pathlib import Path

import pytest

try:
    from http.server import HTTPServer, SimpleHTTPRequestHandler
except ImportError:
    HTTPServer = None
    SimpleHTTPRequestHandler = None


def _wait_for_port(port: int, timeout: float = 5.0) -> None:
    """Wait until the server is accepting connections (CI stability)."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("Fixture server did not become ready in time")


def _find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


class _SPAFixtureHandler(SimpleHTTPRequestHandler):
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
    """Serve static fixture (mini SPA) when BASE_URL is not set (CI / mocked run)."""
    if HTTPServer is None or SimpleHTTPRequestHandler is None:
        pytest.skip("http.server not available")
    fixtures_dir = Path(__file__).resolve().parent / "fixtures"
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
        _wait_for_port(port)
        yield {"port": port, "server": server}
    finally:
        if server:
            server.shutdown()


@pytest.fixture(scope="session")
def base_url(request):
    """Use BASE_URL env if set (live/ngrok); else use fixture server (mocked CI)."""
    env_url = (os.environ.get("BASE_URL") or "").strip().rstrip("/")
    if env_url:
        return env_url
    port = request.getfixturevalue("ui_fixture_server")["port"]
    return "http://127.0.0.1:%s" % port
