# Test Plan – Invoice Parser Skill

## 1. What We Test

### 1.1 Skill app only (base ERP mocked)

- **API**
  - Invoice create/upload, get, list, delete.
  - Anomaly analysis (risk score, explanation).
  - Error handling (400, 404, 500, parsing errors).
  - Config and validation (e.g. ERPNext config).
  - Storage, models, controllers with **ERPNext and external services mocked**.

- **UI**
  - User journey: upload → see results and risk → open detail → submit to ERPNext.
  - Run against a **static fixture** that mirrors the app; **all API calls (including ERP) are mocked** by the test (Playwright `route`).
  - Success: journey completes and assertions on risk explanation and “Submitted to ERPNext” pass.

### 1.2 Interaction between skill and base ERP system

- **API**
  - Submit-to-ERPNext flow with **mocked ERP client**: assert correct payload (e.g. risk explanation as comment), status, and error handling when ERP is unavailable or misconfigured.
  - Covered in `tests/api/` by mocking `erpnext_client` or related layers.

- **UI**
  - Same user journey against the **real** app (and real backend + ERPNext when desired).
  - **With mocks (CI):** fixture + mocked APIs (including ERP) so the “submit” step is simulated; no real ERP needed.
  - **With real ERP (manual/ngrok):** Live UI test against real backend and ERPNext; invoice appears in ERP; run via “Live UI test (ngrok)” workflow or `run_real_ui_test.bat`.

---

## 2. Detailed Test Cases (summary)

| Area        | Test case / scenario                    | ERP / API        | Where              |
|------------|------------------------------------------|------------------|--------------------|
| API        | Create invoice (JSON)                    | Mocked           | tests/api/         |
| API        | Upload invoice (file), parse error       | Parser mocked    | tests/api/         |
| API        | Get / list / delete invoice               | Mocked           | tests/api/         |
| API        | Anomaly analysis (risk, explanation)     | Mocked           | tests/api/         |
| API        | Submit to ERPNext (success / not configured) | ERP mocked   | tests/api/         |
| API        | Error handling (400, 404, 500)            | N/A              | tests/api/         |
| API        | Config (ERP URL, env)                     | N/A              | tests/api/         |
| UI         | Full journey (upload → risk → detail → submit) | APIs + ERP mocked | tests/ui/ (fixture) |
| UI         | Full journey with real backend + ERPNext  | Real ERP         | tests/ui/ (ngrok/manual) |

---

## 3. How We Test (strategy)

- **Unit/API:** Pytest + FastAPI TestClient. Use `unittest.mock` / `patch` to mock parser, storage, and **ERPNext client** so the skill app is tested in isolation.
- **UI (mocked):** Pytest + Playwright. A small in-process server serves a static **fixture** that mirrors the app UI. Playwright **mocks all API routes** (including submit-to-ERPNext) so the UI test runs without a real backend or ERP.
- **UI (real ERP):** Same journey test run with `BASE_URL` pointing at the real app (e.g. ngrok). No mocks; backend and ERPNext are real. Used for manual / “Live UI test (ngrok)” runs only.
- **CI:** On every **pull request** (and push to main/develop), run API tests and UI tests **with mocked ERP** (fixture + route mocks). No ngrok or real ERP in CI.

---

## 4. Success Criteria

- **API**
  - All API tests pass.
  - Coverage for `app` meets project threshold (e.g. ≥ 90% or as configured).
- **UI (CI)**
  - UI journey test (with fixture + mocked APIs/ERP) passes on every PR.
- **UI (live)**
  - When run with real app and ERPNext, the invoice appears in ERP and the risk explanation is present as expected.
- **CI pipeline**
  - On every pull request to the target branches, the pipeline runs and **both API and UI tests** (mocked) pass; the skill app is tested with the base ERP system mocked.

---

## 5. CI Pipeline (GitHub Actions)

- **Trigger:** Push and pull requests to `main` and `develop`.
- **Jobs:**
  - Install dependencies (including pytest-playwright for UI).
  - Install Playwright browsers.
  - Run **API tests** (with coverage).
  - Run **UI tests** (fixture + mocked ERP) so the skill app is tested without a real ERP.
- **Optional:** “Live UI test (ngrok)” workflow for manual runs against real backend and ERPNext (not required for PRs).

This test plan ensures:
1. **Skill app only (mock ERP):** API and UI tests run in CI with ERP and external services mocked.
2. **Interaction with base ERP:** API tests assert submit/ERP behavior with mocks; UI tests do the same in CI with mocks, and can be run live (ngrok) for real ERP interaction.
3. **CI on every PR:** API and UI tests (mocked) run on every pull request.
