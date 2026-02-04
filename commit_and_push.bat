@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo.
echo --- Committing and Pushing Changes ---
echo.

REM Check if we're in a git repository
if not exist .git (
    echo Initializing git repository...
    git init
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Failed to initialize Git. Exiting.
        pause
        exit /b 1
    )
)

REM Check if remote is configured
git remote -v >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Adding remote origin...
    git remote add origin https://github.com/sbeahaya21-blip/final-project.git
)

echo.
echo Staging all changes...
git add .
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to stage files. Exiting.
    pause
    exit /b 1
)

echo.
echo Checking status...
git status --short

echo.
echo Creating commit...
git commit -m "Update: Convert invoice list to table layout and reduce sidebar width"
if %ERRORLEVEL% NEQ 0 (
    echo Warning: No changes to commit or commit failed. Continuing.
)

echo.
echo Pushing to GitHub...
git push -u origin master
if %ERRORLEVEL% NEQ 0 (
    REM Try main branch if master doesn't work
    echo Trying 'main' branch instead...
    git push -u origin main
)

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Successfully committed and pushed changes!
) else (
    echo.
    echo ❌ Failed to push to GitHub. Please check the error messages above.
    echo    You might need to manually run 'git push -u origin master' (or main)
)

echo.
pause
