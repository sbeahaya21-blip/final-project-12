@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo Regenerating PDF Invoices...
echo ========================================
echo.
python generate_pdf_invoices.py
echo.
echo ========================================
if %ERRORLEVEL% EQU 0 (
    echo PDF invoices regenerated successfully!
    echo Check: sample_invoices\pdf\
    echo.
    echo Opening folder...
    start sample_invoices\pdf
) else (
    echo Error generating PDFs.
    echo Make sure reportlab is installed:
    echo   pip install reportlab
)
pause
