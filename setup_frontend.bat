@echo off
REM Setup script for frontend (Windows)

echo Setting up Invoice Parser Frontend...
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed. Please install Node.js 18+ first.
    exit /b 1
)

echo [OK] Node.js found
echo.

REM Navigate to frontend directory
cd frontend
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Frontend directory not found
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)

echo [OK] Dependencies installed
echo.

REM Build frontend
echo Building frontend...
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to build frontend
    exit /b 1
)

echo.
echo [SUCCESS] Frontend setup complete!
echo.
echo You can now:
echo   - Run 'npm run dev' in the frontend directory for development
echo   - Or start the backend server to serve the built frontend
echo.

pause
