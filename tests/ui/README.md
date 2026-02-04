# UI Tests (Playwright)

## What's included

- **User journey (E2E):** `test_user_journey.py` – Upload invoice → view parsed results and risk → open detail → submit to ERPNext → verify success and that the risk explanation (comment for ERPNext) is correct.
- **Component tests:** `test_upload_component.py` – Upload form/zone: happy path, errors (400/500/parse), drag-and-drop, loading state, "Upload Another", navigation to detail.
- **Legacy:** `test_invoice_ui.py` – Older tests for the static upload page (selectors may differ from the React app; may require the app to be running).

**Upload and user-journey tests** use a static HTML fixture (`tests/ui/fixtures/mini_app.html`) that mirrors the React app’s DOM and behavior. They do **not** require building or running the React app or backend; a small HTTP server serves the fixture and all API calls are mocked by the tests.

## Requirements

- **pytest-playwright:** `pip install pytest-playwright`
- **Browsers:** `playwright install`

No need to build the frontend or start the backend for `test_upload_component.py` or `test_user_journey.py`.

## Run UI tests

```bash
# Upload component + user journey (uses fixture; no app needed)
pytest tests/ui/test_user_journey.py tests/ui/test_upload_component.py -v

# Against a real app (e.g. Vite on port 3000): set BASE_URL
# Start the app first (e.g. cd frontend && npm run dev), then:
set BASE_URL=http://localhost:3000
pytest tests/ui/test_user_journey.py tests/ui/test_upload_component.py -v

# Real UI test (no mocks – talks to ERPNext). See tests/ui/REAL_UI_TEST_WITH_ERPNEXT.md
# Or from project root: run_real_ui_test.bat
set BASE_URL=http://localhost:3000
set LIVE_ERPNEXT=1
pytest tests/ui/test_user_journey.py::test_user_journey_upload_view_risk_and_submit_to_erpnext -v --headed

# With Playwright headed (see browser)
pytest tests/ui/test_user_journey.py -v --headed

# Single test
pytest tests/ui/test_user_journey.py::test_user_journey_upload_view_risk_and_submit_to_erpnext -v
```

If the `page` fixture is missing (pytest-playwright not installed), tests are skipped with a message.
