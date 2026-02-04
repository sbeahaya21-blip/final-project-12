# Live UI test (ngrok)

The only UI test runs the **user journey** (upload invoice → view results → submit to ERPNext) against your **real** app. It is intended to run **via ngrok** from GitHub Actions so GitHub can talk to your local machine.

## Requirements

- **pytest-playwright:** `pip install pytest-playwright`
- **Browsers:** `playwright install`
- **BASE_URL** must be set (your app URL, e.g. ngrok or http://localhost:3000).

## Run from GitHub (ngrok)

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
