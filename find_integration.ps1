# PowerShell script to find INTEGRATION_ID
# Direct API call to LangSmith Control Plane

$apiKey = "lsv2_sk_YOUR_API_KEY_HERE"  # Replace with your actual LANGSMITH_API_KEY
$workspaceId = "950d802b-125a-45bc-88e4-3d7d0edee182"

Write-Host "=========================================="
Write-Host "LangSmith GitHub Integration Finder"
Write-Host "=========================================="
Write-Host ""

# Set headers
$headers = @{
    "X-Api-Key" = $apiKey
    "X-Tenant-Id" = $workspaceId
    "Content-Type" = "application/json"
}

# Try multiple API endpoints
$endpoints = @(
    "https://api.host.langchain.com/v1/integrations/github",
    "https://api.host.langchain.com/v2/integrations/github",
    "https://api.host.langchain.com/v1/integrations",
    "https://api.host.langchain.com/v2/integrations"
)

$found = $false

foreach ($endpoint in $endpoints) {
    Write-Host "Trying endpoint: $endpoint"

    try {
        $response = Invoke-RestMethod -Uri $endpoint -Method Get -Headers $headers -TimeoutSec 30

        Write-Host "[SUCCESS] Status: 200 OK" -ForegroundColor Green
        Write-Host ""

        # Check if response contains GitHub integrations
        if ($response -is [Array]) {
            $githubIntegrations = $response | Where-Object { $_.provider -eq "github" -or $_.type -like "*github*" }

            if ($githubIntegrations) {
                Write-Host "======================================"  -ForegroundColor Green
                Write-Host "GITHUB INTEGRATION FOUND!" -ForegroundColor Green
                Write-Host "======================================"  -ForegroundColor Green
                Write-Host ""

                foreach ($integration in $githubIntegrations) {
                    Write-Host "Integration Details:"
                    Write-Host "  ID:       $($integration.id)"
                    Write-Host "  Name:     $($integration.name)"
                    Write-Host "  Provider: $($integration.provider)"
                    Write-Host "  Type:     $($integration.type)"
                    Write-Host "  Owner:    $($integration.owner)"
                    Write-Host ""
                }

                $integrationId = $githubIntegrations[0].id

                Write-Host "======================================" -ForegroundColor Yellow
                Write-Host "INTEGRATION_ID TO USE:" -ForegroundColor Yellow
                Write-Host "======================================" -ForegroundColor Yellow
                Write-Host "$integrationId" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "Copy this value and add it to GitHub Secrets as:" -ForegroundColor Yellow
                Write-Host "  Name:  INTEGRATION_ID"
                Write-Host "  Value: $integrationId"

                $found = $true
                break
            }
        } elseif ($response.PSObject.Properties.Name -contains "id") {
            # Single integration response
            Write-Host "Integration ID: $($response.id)"
            $found = $true
            break
        }

    } catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "[ERROR] Status: $statusCode - $($_.Exception.Message)" -ForegroundColor Red
    }

    Write-Host ""
}

if (-not $found) {
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "NO GITHUB INTEGRATION FOUND" -ForegroundColor Red
    Write-Host "======================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "The GitHub integration does not exist yet." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "ACTION REQUIRED:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://smith.langchain.com/settings/integrations"
    Write-Host "2. Click 'Add Integration'"
    Write-Host "3. Select 'GitHub'"
    Write-Host "4. Authorize the 'hosted-langserve' GitHub App"
    Write-Host "5. Grant access to repository: chicuza/indufix-llamaindex-toolkit"
    Write-Host "6. Re-run this script to get the INTEGRATION_ID"
    Write-Host ""
}

Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
