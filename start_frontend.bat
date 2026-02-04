@echo off
echo Starting Frontend Development Server...
echo.

cd /d "%~dp0frontend"

if not exist "package.json" (
    echo ERROR: Frontend directory not found!
    pause
    exit /b 1
)

echo Checking Node.js...
node --version
npm --version
echo.

echo Starting Vite development server...
echo Frontend will be available at: http://localhost:3000
echo Press Ctrl+C to stop the server
echo.

npm run dev

pause
