"""
Pytest fixtures for Live UI test (ngrok). BASE_URL must be set (e.g. by GitHub Actions or run_real_ui_test.bat).
"""
import os

import pytest


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the app. Required: set BASE_URL env (e.g. your ngrok URL or http://localhost:3000)."""
    env_url = (os.environ.get("BASE_URL") or "").strip().rstrip("/")
    if not env_url:
        pytest.skip("BASE_URL not set. Set it to your app URL (e.g. ngrok URL or http://localhost:3000).")
    return env_url
