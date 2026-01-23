# PowerShell script to find INTEGRATION_ID
$env:PYTHONIOENCODING = 'utf-8'
$env:LANGSMITH_API_KEY = 'lsv2_sk_YOUR_API_KEY_HERE'  # Replace with your actual LANGSMITH_API_KEY
$env:WORKSPACE_ID = '950d802b-125a-45bc-88e4-3d7d0edee182'

Write-Host "=========================================="
Write-Host "LangSmith GitHub Integration Finder"
Write-Host "=========================================="
Write-Host ""
Write-Host "Environment variables set:"
Write-Host "  LANGSMITH_API_KEY: $($env:LANGSMITH_API_KEY.Substring(0,20))..."
Write-Host "  WORKSPACE_ID: $env:WORKSPACE_ID"
Write-Host ""
Write-Host "Running integration finder script..."
Write-Host ""

python tools/find_langsmith_integration.py --github
