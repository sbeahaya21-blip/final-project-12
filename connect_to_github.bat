@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo Connecting Project to GitHub
echo ========================================
echo.

REM Check if .git exists in current directory
if exist ".git" (
    echo Git repository already initialized.
) else (
    echo Initializing Git repository...
    git init
)

echo.
echo Please provide your GitHub repository URL:
echo Example: https://github.com/sbeahaya21-blip/invoice-parser.git
echo.
set /p REPO_URL="Enter your GitHub repository URL: "

if "%REPO_URL%"=="" (
    echo Error: Repository URL is required!
    pause
    exit /b 1
)

echo.
echo Adding remote repository...
git remote remove origin 2>nul
git remote add origin "%REPO_URL%"

echo.
echo Checking current status...
git status

echo.
echo ========================================
echo Next steps:
echo ========================================
echo 1. Add files: git add .
echo 2. Commit: git commit -m "Initial commit"
echo 3. Push: git push -u origin main
echo.
echo When prompted for password, use your Personal Access Token!
echo.
pause
