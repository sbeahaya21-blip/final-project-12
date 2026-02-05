"""
Base TestCase for UI tests using unittest + Playwright.
Real integration only: no mocks. Use BASE_URL for the app URL or defaults to http://localhost:3000.
"""
import os
import unittest

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


def _get_base_url():
    """Use BASE_URL env if set; else http://localhost:3000."""
    env_url = (os.environ.get("BASE_URL") or "").strip().rstrip("/")
    if env_url:
        return env_url
    return "http://localhost:3000"


class PlaywrightTestCase(unittest.TestCase):
    """
    Base class for UI tests. Real app only (no fixture/mock server).
    setUp: starts Playwright browser/context/page. tearDown: closes them.
    """

    def setUp(self):
        super().setUp()
        if sync_playwright is None:
            self.skipTest("Playwright not installed")
        self._pw = sync_playwright().start()
        headless = os.environ.get("CI") == "true"
        self._browser = self._pw.chromium.launch(headless=headless)
        self._context = self._browser.new_context()
        self._page = self._context.new_page()
        self.base_url = _get_base_url()

    def tearDown(self):
        if getattr(self, "_page", None):
            try:
                self._page.close()
            except Exception:
                pass
        if getattr(self, "_context", None):
            try:
                self._context.close()
            except Exception:
                pass
        if getattr(self, "_browser", None):
            try:
                self._browser.close()
            except Exception:
                pass
        if getattr(self, "_pw", None):
            try:
                self._pw.stop()
            except Exception:
                pass
        super().tearDown()


    @property
    def page(self):
        return self._page



