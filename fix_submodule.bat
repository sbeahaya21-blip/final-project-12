@echo off
chcp 65001 >nul
cd /d "C:\Users\Admin"

echo.
echo --- Fixing final project submodule issue ---
echo.

echo Removing submodule reference...
git rm --cached "Desktop\אוטומציה\final project"

echo.
echo Removing .git folder from final project...
if exist "Desktop\אוטומציה\final project\.git" (
    rmdir /s /q "Desktop\אוטומציה\final project\.git"
    echo .git folder removed
) else (
    echo No .git folder found
)

echo.
echo Adding final project files...
git add "Desktop\אוטומציה\final project\"

echo.
echo Committing changes...
git commit -m "Fix: Convert final project from submodule to regular files"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo Done!
pause
