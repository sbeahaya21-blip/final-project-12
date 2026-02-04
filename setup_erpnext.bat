@echo off
REM Setup ERPNext environment variables for Windows
REM Edit the values below with your ERPNext credentials

echo ========================================
echo ERPNext Configuration Setup
echo ========================================
echo.
echo Please enter your ERPNext credentials:
echo.

set /p ERPNEXT_URL="ERPNext Base URL (e.g., https://your-instance.erpnext.com): "
set /p ERPNEXT_KEY="ERPNext API Key: "
set /p ERPNEXT_SECRET="ERPNext API Secret: "

echo.
echo Setting environment variables...
setx ERPNEXT_BASE_URL "%ERPNEXT_URL%"
setx ERPNEXT_API_KEY "%ERPNEXT_KEY%"
setx ERPNEXT_API_SECRET "%ERPNEXT_SECRET%"

echo.
echo ========================================
echo Configuration saved!
echo ========================================
echo.
echo Please restart your terminal and run: python run.py
echo.
pause
