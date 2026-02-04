@echo off
REM Real UI test: no mocks, talks to backend and ERPNext.
REM Start backend (python run.py) and frontend (npm run dev) and ERPNext first.
REM Configure .env with ERPNEXT_BASE_URL, ERPNEXT_API_KEY, ERPNEXT_API_SECRET.

set BASE_URL=http://localhost:3000
set LIVE_ERPNEXT=1
echo Running real UI test (backend + ERPNext). Browser will open (--headed).
echo.
pytest tests/ui/test_user_journey.py::test_user_journey_upload_view_risk_and_submit_to_erpnext -v --headed
pause
