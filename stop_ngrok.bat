@echo off
REM Stop any running ngrok so you can start a new tunnel (e.g. ngrok http 3000)
taskkill /F /IM ngrok.exe 2>nul
if %errorlevel% equ 0 (
    echo Stopped ngrok.
) else (
    echo No ngrok process found. If you still see ERR_NGROK_334, close the other terminal where ngrok is running, or restart the PC.
)
pause
