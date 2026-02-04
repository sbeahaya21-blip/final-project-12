@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo Connecting Project to GitHub
echo ========================================
echo.

REM Check if we're in the project directory
if not exist "app\main.py" (
    echo ERROR: Not in project directory!
    echo Please run this script from the project root folder.
    pause
    exit /b 1
)

REM Initialize Git in project directory (if not already done)
if not exist ".git" (
    echo Initializing Git repository...
    git init
)

REM Add remote
echo.
echo Adding GitHub remote...
git remote remove origin 2>nul
git remote add origin https://github.com/sbeahaya21-blip/final-project.git
git remote -v

REM Add only project files (respecting .gitignore)
echo.
echo Adding project files...
git add .

REM Check status
echo.
echo Files staged for commit:
git status --short

REM Commit
echo.
echo Creating commit...
git commit -m "Initial commit: Invoice Parser and Anomaly Detection System"

REM Push
echo.
echo ========================================
echo Ready to push to GitHub!
echo ========================================
echo.
echo Run this command to push:
echo   git push -u origin main
echo.
echo If your default branch is 'master', use:
echo   git push -u origin master
echo.
echo When prompted for password, use your Personal Access Token!
echo.
pause
