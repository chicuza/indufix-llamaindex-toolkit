# Quick Deployment Test Script (PowerShell)
# Tests deployed LangGraph application endpoints and functionality

param(
    [Parameter(Mandatory=$false)]
    [string]$DeploymentUrl = "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app",

    [Parameter(Mandatory=$false)]
    [string]$ApiKey = $env:ANTHROPIC_API_KEY,

    [switch]$Verbose
)

# Colors for output
$ColorPass = "Green"
$ColorFail = "Red"
$ColorWarn = "Yellow"
$ColorInfo = "Cyan"

# Test results tracking
$script:PassCount = 0
$script:FailCount = 0
$script:WarnCount = 0

function Write-TestHeader {
    param([string]$Message)
    Write-Host ""
    Write-Host "=" -NoNewline -ForegroundColor $ColorInfo
    Write-Host ("=" * 68) -ForegroundColor $ColorInfo
    Write-Host $Message -ForegroundColor $ColorInfo
    Write-Host "=" -NoNewline -ForegroundColor $ColorInfo
    Write-Host ("=" * 68) -ForegroundColor $ColorInfo
}

function Write-TestResult {
    param(
        [string]$TestName,
        [bool]$Passed,
        [string]$Message = ""
    )

    if ($Passed) {
        Write-Host "[PASS] " -NoNewline -ForegroundColor $ColorPass
        $script:PassCount++
    } else {
        Write-Host "[FAIL] " -NoNewline -ForegroundColor $ColorFail
        $script:FailCount++
    }

    Write-Host "$TestName"
    if ($Message) {
        Write-Host "       $Message" -ForegroundColor Gray
    }
}

function Write-TestWarning {
    param(
        [string]$TestName,
        [string]$Message = ""
    )

    Write-Host "[WARN] " -NoNewline -ForegroundColor $ColorWarn
    Write-Host "$TestName"
    if ($Message) {
        Write-Host "       $Message" -ForegroundColor Gray
    }
    $script:WarnCount++
}

function Test-HealthEndpoint {
    param([string]$Url)

    Write-Host "`nTesting health endpoint..." -ForegroundColor $ColorInfo

    try {
        $healthUrl = "$Url/ok"
        $response = Invoke-WebRequest -Uri $healthUrl -Method Get -TimeoutSec 10 -UseBasicParsing

        if ($response.StatusCode -eq 200) {
            Write-TestResult "Health Check" $true "Endpoint is responsive"
            return $true
        } else {
            Write-TestResult "Health Check" $false "Unexpected status code: $($response.StatusCode)"
            return $false
        }
    } catch {
        Write-TestResult "Health Check" $false "Error: $($_.Exception.Message)"
        return $false
    }
}

function Test-InfoEndpoint {
    param([string]$Url)

    Write-Host "`nTesting info endpoint..." -ForegroundColor $ColorInfo

    try {
        $infoUrl = "$Url/info"
        $response = Invoke-WebRequest -Uri $infoUrl -Method Get -TimeoutSec 10 -UseBasicParsing

        if ($response.StatusCode -eq 200) {
            $info = $response.Content | ConvertFrom-Json
            Write-TestResult "Info Endpoint" $true "Retrieved deployment info"

            if ($Verbose) {
                Write-Host "       Info data:" -ForegroundColor Gray
                $info | ConvertTo-Json -Depth 3 | Write-Host -ForegroundColor Gray
            }

            return $true
        } else {
            Write-TestResult "Info Endpoint" $false "Unexpected status code: $($response.StatusCode)"
            return $false
        }
    } catch {
        Write-TestResult "Info Endpoint" $false "Error: $($_.Exception.Message)"
        return $false
    }
}

function Test-McpAuthentication {
    param(
        [string]$Url,
        [string]$ApiKey
    )

    Write-Host "`nTesting MCP authentication..." -ForegroundColor $ColorInfo

    if (-not $ApiKey) {
        Write-TestWarning "MCP Authentication" "No API key provided - skipping auth test"
        return $null
    }

    try {
        $invokeUrl = "$Url/runs/stream"

        $headers = @{
            "Content-Type" = "application/json"
        }

        if ($ApiKey) {
            $headers["Authorization"] = "Bearer $ApiKey"
        }

        $payload = @{
            input = @{
                messages = @(
                    @{
                        role = "user"
                        content = "Hello, what tools do you have?"
                    }
                )
            }
            config = @{}
            stream_mode = @("values")
        } | ConvertTo-Json -Depth 10

        $response = Invoke-WebRequest -Uri $invokeUrl -Method Post -Headers $headers -Body $payload -TimeoutSec 30 -UseBasicParsing

        if ($response.StatusCode -eq 200) {
            Write-TestResult "MCP Authentication" $true "Successfully authenticated and invoked"
            return $true
        } else {
            Write-TestResult "MCP Authentication" $false "Unexpected status code: $($response.StatusCode)"
            return $false
        }
    } catch {
        $errorMsg = $_.Exception.Message
        if ($errorMsg -like "*401*" -or $errorMsg -like "*403*") {
            Write-TestResult "MCP Authentication" $false "Authentication failed - check API key"
        } else {
            Write-TestResult "MCP Authentication" $false "Error: $errorMsg"
        }
        return $false
    }
}

function Test-AnthropicApiKey {
    Write-Host "`nChecking ANTHROPIC_API_KEY availability..." -ForegroundColor $ColorInfo

    if ($env:ANTHROPIC_API_KEY) {
        Write-TestResult "ANTHROPIC_API_KEY Environment Variable" $true "Set in local environment"

        # Verify format (should start with sk-)
        if ($env:ANTHROPIC_API_KEY -like "sk-*") {
            Write-Host "       Key format appears valid" -ForegroundColor Gray
        } else {
            Write-TestWarning "ANTHROPIC_API_KEY Format" "Key doesn't match expected format (should start with 'sk-')"
        }

        return $true
    } else {
        Write-TestResult "ANTHROPIC_API_KEY Environment Variable" $false "Not set in local environment"
        Write-Host "       Note: This checks local env, not deployment env" -ForegroundColor Gray
        return $false
    }
}

function Test-DeploymentSecrets {
    Write-Host "`nVerifying GitHub Secrets configuration..." -ForegroundColor $ColorInfo
    Write-Host "       (This is informational - cannot verify directly)" -ForegroundColor Gray

    $requiredSecrets = @(
        "LANGSMITH_API_KEY",
        "WORKSPACE_ID",
        "INTEGRATION_ID",
        "LLAMA_CLOUD_API_KEY",
        "ANTHROPIC_API_KEY"
    )

    Write-Host "`n       Required GitHub Secrets:" -ForegroundColor Gray
    foreach ($secret in $requiredSecrets) {
        Write-Host "       - $secret" -ForegroundColor Gray
    }

    Write-Host "`n       Recommended GitHub Secrets:" -ForegroundColor Gray
    Write-Host "       - LANGCHAIN_TRACING_V2" -ForegroundColor Gray
    Write-Host "       - LANGCHAIN_PROJECT" -ForegroundColor Gray
    Write-Host "       - LANGCHAIN_ENDPOINT" -ForegroundColor Gray

    Write-TestWarning "GitHub Secrets" "Verify these are set at: https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions"
}

# Main execution
Write-TestHeader "QUICK DEPLOYMENT TEST"
Write-Host "Deployment URL: $DeploymentUrl" -ForegroundColor $ColorInfo
Write-Host "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor $ColorInfo
Write-Host ""

# Run all tests
$healthOk = Test-HealthEndpoint -Url $DeploymentUrl
$infoOk = Test-InfoEndpoint -Url $DeploymentUrl
$mcpOk = Test-McpAuthentication -Url $DeploymentUrl -ApiKey $ApiKey
$apiKeyOk = Test-AnthropicApiKey
Test-DeploymentSecrets

# Summary
Write-TestHeader "TEST SUMMARY"
Write-Host ""
Write-Host "Results:" -ForegroundColor $ColorInfo
Write-Host "  Passed:  $script:PassCount" -ForegroundColor $ColorPass
Write-Host "  Failed:  $script:FailCount" -ForegroundColor $ColorFail
Write-Host "  Warnings: $script:WarnCount" -ForegroundColor $ColorWarn
Write-Host ""

# Overall status
if ($script:FailCount -eq 0 -and $healthOk -and $infoOk) {
    Write-Host "OVERALL STATUS: " -NoNewline
    Write-Host "PASS" -ForegroundColor $ColorPass
    Write-Host "Deployment is functioning correctly!" -ForegroundColor $ColorPass
    Write-Host ""
    exit 0
} elseif ($healthOk -and $infoOk -and $mcpOk -eq $null) {
    Write-Host "OVERALL STATUS: " -NoNewline
    Write-Host "PARTIAL PASS" -ForegroundColor $ColorWarn
    Write-Host "Basic deployment is working, but some tests were skipped" -ForegroundColor $ColorWarn
    Write-Host ""
    exit 0
} else {
    Write-Host "OVERALL STATUS: " -NoNewline
    Write-Host "FAIL" -ForegroundColor $ColorFail
    Write-Host "Deployment has issues that need attention" -ForegroundColor $ColorFail
    Write-Host ""
    exit 1
}
