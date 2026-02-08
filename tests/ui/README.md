# UI tests (unittest + Playwright)

Tests use **unittest** and **Playwright** with **real integration only** (no mocks). They talk to the real backend, frontend, and ERPNext.

- **BASE_URL:** Set to your app URL (e.g. `http://localhost:3000`) or it defaults to `http://localhost:3000`.
- All tests run against the real app and ERPNext (no skip conditions).

## Requirements

- Backend, frontend, and (for submit tests) ERPNext must be running.
- **Playwright:** `pip install playwright` then `playwright install`
- **User journey test:** needs `sample_invoices/pdf/sample_invoice_1.pdf`

## How to run

From the project root (with backend and frontend running):

```bash
# Run all UI tests
python -m unittest discover -s tests/ui -p "test_*_unittest.py" -v
```

Or run a single module:

```bash
# User journey only (upload → view risk → submit to ERPNext)
python -m unittest tests.ui.test_user_journey_unittest -v
# Or with pytest + Allure:
pytest tests/ui/test_user_journey_unittest.py -v --alluredir=allure-results

python -m unittest tests.ui.test_specific_invoice_unittest -v
python -m unittest tests.ui.test_invoice_with_erpnext_verification_unittest -v
```

**Run only user journey UI test:** from project root use `run_ui_user_journey_only.bat` or:
`pytest tests/ui/test_user_journey_unittest.py -v --alluredir=allure-results`

### Optional: custom app URL

```bash
set BASE_URL=http://localhost:3000
python -m unittest discover -s tests/ui -p "test_*_unittest.py" -v
```

See **REAL_UI_TEST_WITH_ERPNEXT.md** in this folder for full steps.
