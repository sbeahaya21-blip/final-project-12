@echo off
REM Push this project to GitHub repo: final-project-12
REM Run this from: c:\Users\Admin\Desktop\final project

cd /d "%~dp0"

echo Pushing to https://github.com/sbeahaya21-blip/final-project-12.git (branch: main)
git push -u origin main

if errorlevel 1 (
  echo.
  echo If the repo does not exist yet:
  echo 1. Go to https://github.com/new
  echo 2. Repository name: final-project-12
  echo 3. Do NOT add README or .gitignore
  echo 4. Create repository, then run this script again.
  echo.
  pause
)
