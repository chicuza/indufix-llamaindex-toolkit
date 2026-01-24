# Check GitHub Secrets Status
# This script checks which secrets are configured in the repository

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken
)

$ErrorActionPreference = "Stop"

# Repository details
$Owner = "chicuza"
$Repo = "indufix-llamaindex-toolkit"

$requiredSecrets = @(
    "LANGSMITH_API_KEY",
    "WORKSPACE_ID",
    "INTEGRATION_ID",
    "LLAMA_CLOUD_API_KEY",
    "ANTHROPIC_API_KEY"
)

$optionalSecrets = @(
    "OPENAI_API_KEY"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "GitHub Secrets Status Check" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository: $Owner/$Repo" -ForegroundColor Yellow
Write-Host ""

$headers = @{
    "Authorization" = "Bearer $GitHubToken"
    "Accept" = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

try {
    Write-Host "Fetching secrets list..." -ForegroundColor Cyan
    Write-Host ""

    $secretsUri = "https://api.github.com/repos/$Owner/$Repo/actions/secrets"
    $response = Invoke-RestMethod -Uri $secretsUri -Headers $headers -Method Get

    $configuredSecrets = $response.secrets | Select-Object -ExpandProperty name

    Write-Host "Required Secrets:" -ForegroundColor Yellow
    Write-Host "=================" -ForegroundColor Yellow
    $requiredConfigured = 0

    foreach ($secret in $requiredSecrets) {
        if ($configuredSecrets -contains $secret) {
            Write-Host "  ✅ $secret" -ForegroundColor Green
            $requiredConfigured++
        }
        else {
            Write-Host "  ❌ $secret (MISSING)" -ForegroundColor Red
        }
    }

    Write-Host ""
    Write-Host "Optional Secrets:" -ForegroundColor Yellow
    Write-Host "=================" -ForegroundColor Yellow

    foreach ($secret in $optionalSecrets) {
        if ($configuredSecrets -contains $secret) {
            Write-Host "  ✅ $secret" -ForegroundColor Green
        }
        else {
            Write-Host "  ⚪ $secret (Not set)" -ForegroundColor Gray
        }
    }

    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan

    if ($requiredConfigured -eq $requiredSecrets.Count) {
        Write-Host "STATUS: Ready to Deploy! ✅" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "All required secrets are configured." -ForegroundColor Green
        Write-Host ""
        Write-Host "Next step:" -ForegroundColor Yellow
        Write-Host "  Run: .\trigger_deployment.ps1 -GitHubToken 'your-token'" -ForegroundColor White
        Write-Host "  Or manually trigger at: https://github.com/$Owner/$Repo/actions" -ForegroundColor White
        Write-Host ""
        exit 0
    }
    else {
        $missing = $requiredSecrets.Count - $requiredConfigured
        Write-Host "STATUS: Configuration Incomplete ⚠️" -ForegroundColor Yellow
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Missing $missing required secret(s)." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Add missing secrets at:" -ForegroundColor Yellow
        Write-Host "  https://github.com/$Owner/$Repo/settings/secrets/actions" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Or run: .\setup_github_secrets.ps1" -ForegroundColor White
        Write-Host ""
        exit 1
    }
}
catch {
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "ERROR" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host $_ -ForegroundColor Red
    Write-Host ""

    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "Authentication failed. Please check your GitHub token has 'repo' scope." -ForegroundColor Red
    }

    Write-Host ""
    exit 1
}
