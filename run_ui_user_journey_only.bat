@echo off
REM Run only the user journey UI test (test_user_journey_unittest.py).
REM Backend and frontend must be running. Optional: Allure report with --alluredir.

echo Running UI tests: test_user_journey_unittest.py only...
echo.
pytest tests/ui/test_user_journey_unittest.py -v --alluredir=allure-results
echo.
echo To view Allure report: allure serve allure-results
pause
