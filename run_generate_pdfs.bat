@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Generating PDF invoices...
python generate_pdf_invoices.py
if %ERRORLEVEL% EQU 0 (
    echo.
    echo PDF invoices generated successfully!
    echo Check the sample_invoices\pdf\ folder
) else (
    echo.
    echo Error generating PDFs. Make sure reportlab is installed:
    echo   pip install reportlab
)
pause
