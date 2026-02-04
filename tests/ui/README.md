# UI tests

One **user journey** test: upload invoice → view results and risk → submit to ERPNext.

- **CI (every PR):** Runs with **mocked ERP** (static fixture + Playwright route mocks). No real backend or ERPNext.
- **Live (optional):** Set `BASE_URL` and `LIVE_ERPNEXT=1` to run against real app and ERPNext (locally or via ngrok).

See **TEST_PLAN.md** in the project root for full test plan, strategy, and success criteria.

## Requirements

- **pytest-playwright:** `pip install pytest-playwright`
- **Browsers:** `playwright install`

## Run in CI (mocked)

On every pull request, the pipeline runs `pytest tests/ui/` with no `BASE_URL`; the fixture is served and all APIs (including ERP) are mocked.

## Run from GitHub (ngrok, live)

1. Start backend, frontend, and ERPNext locally.
2. Expose frontend with ngrok: `ngrok http 3000`
3. In GitHub: Settings → Secrets → add **LIVE_TEST_BASE_URL** = your ngrok URL (e.g. `https://xxxx.ngrok-free.dev`).
4. Actions → **Live UI test (ngrok)** → Run workflow.

See **.github/NGROK_LIVE_UI_TEST.md** for full steps.

## Run locally (no ngrok)

1. Start backend (`python run.py`), frontend (`npm run dev`), and ERPNext.
2. Set BASE_URL and LIVE_ERPNEXT, then run:

```cmd
run_real_ui_test.bat
```

Or:

```cmd
set BASE_URL=http://localhost:3000
set LIVE_ERPNEXT=1
pytest tests/ui/test_user_journey.py::test_user_journey_upload_view_risk_and_submit_to_erpnext -v --headed
```

See **tests/ui/REAL_UI_TEST_WITH_ERPNEXT.md** for details.
