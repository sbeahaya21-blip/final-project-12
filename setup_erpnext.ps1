# PowerShell script to setup ERPNext environment variables
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "ERPNext Configuration Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$baseUrl = Read-Host "Enter ERPNext Base URL (e.g., https://your-instance.erpnext.com)"
$apiKey = Read-Host "Enter ERPNext API Key" -AsSecureString
$apiSecret = Read-Host "Enter ERPNext API Secret" -AsSecureString

# Convert secure strings to plain text
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
$plainApiKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiSecret)
$plainApiSecret = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Set environment variables for current session
$env:ERPNEXT_BASE_URL = $baseUrl
$env:ERPNEXT_API_KEY = $plainApiKey
$env:ERPNEXT_API_SECRET = $plainApiSecret

# Set environment variables permanently
[System.Environment]::SetEnvironmentVariable("ERPNEXT_BASE_URL", $baseUrl, "User")
[System.Environment]::SetEnvironmentVariable("ERPNEXT_API_KEY", $plainApiKey, "User")
[System.Environment]::SetEnvironmentVariable("ERPNEXT_API_SECRET", $plainApiSecret, "User")

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Configuration saved!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Now run: python run.py" -ForegroundColor Yellow
Write-Host ""
