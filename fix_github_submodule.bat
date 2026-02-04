@echo off
chcp 65001 >nul
cd /d "C:\Users\Admin"

echo.
echo ========================================
echo Fixing GitHub Submodule Issue
echo ========================================
echo.
echo This will:
echo 1. Remove the submodule reference for "final project"
echo 2. Delete the .git folder inside "final project"
echo 3. Add all files from "final project" as regular files
echo 4. Commit and push the changes
echo.
pause

echo.
echo Step 1: Removing submodule reference...
git rm --cached "Desktop\אוטומציה\final project"
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Could not remove submodule reference. Continuing...
)

echo.
echo Step 2: Removing .git folder from final project...
if exist "Desktop\אוטומציה\final project\.git" (
    echo Found .git folder, removing it...
    rmdir /s /q "Desktop\אוטומציה\final project\.git"
    echo .git folder removed successfully
) else (
    echo No .git folder found (may have been removed already)
)

echo.
echo Step 3: Adding final project files as regular files...
git add "Desktop\אוטומציה\final project\"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to add files. Please check the path.
    pause
    exit /b 1
)

echo.
echo Step 4: Checking what will be committed...
git status --short | findstr /i "final project" | more

echo.
echo Step 5: Committing changes...
git commit -m "Fix: Convert final project from submodule to regular files"
if %ERRORLEVEL% NEQ 0 (
    echo Warning: Commit failed or no changes to commit
)

echo.
echo Step 6: Pushing to GitHub...
git push origin main
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to push. You may need to pull first or check your credentials.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Done! The final project folder should now
echo be visible with all its files on GitHub.
echo ========================================
echo.
pause
