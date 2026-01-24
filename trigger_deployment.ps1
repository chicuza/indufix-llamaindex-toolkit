# Trigger LangSmith Deployment Workflow
# This script triggers the GitHub Actions workflow for deployment

param(
    [Parameter(Mandatory=$true)]
    [string]$GitHubToken,

    [Parameter(Mandatory=$false)]
    [string]$Environment = "dev"
)

$ErrorActionPreference = "Stop"

# Repository details
$Owner = "chicuza"
$Repo = "indufix-llamaindex-toolkit"
$WorkflowFile = "deploy_langsmith.yml"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Triggering LangSmith Deployment Workflow" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Repository: $Owner/$Repo" -ForegroundColor Yellow
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "Workflow: $WorkflowFile" -ForegroundColor Yellow
Write-Host ""

# Headers for API requests
$headers = @{
    "Authorization" = "Bearer $GitHubToken"
    "Accept" = "application/vnd.github+json"
    "X-GitHub-Api-Version" = "2022-11-28"
}

try {
    Write-Host "Step 1: Validating GitHub access..." -ForegroundColor Cyan

    $repoUri = "https://api.github.com/repos/$Owner/$Repo"
    $repoInfo = Invoke-RestMethod -Uri $repoUri -Headers $headers -Method Get
    Write-Host "  Repository found: $($repoInfo.full_name)" -ForegroundColor Green
    Write-Host "  Default branch: $($repoInfo.default_branch)" -ForegroundColor Green
    Write-Host ""

    Write-Host "Step 2: Triggering workflow dispatch..." -ForegroundColor Cyan

    $workflowUri = "https://api.github.com/repos/$Owner/$Repo/actions/workflows/$WorkflowFile/dispatches"

    $body = @{
        ref = "main"
        inputs = @{
            environment = $Environment
        }
    } | ConvertTo-Json

    Invoke-RestMethod -Uri $workflowUri -Headers $headers -Method Post -Body $body -ContentType "application/json"

    Write-Host "  Workflow triggered successfully!" -ForegroundColor Green
    Write-Host ""

    Write-Host "Step 3: Waiting for workflow run to start..." -ForegroundColor Cyan
    Start-Sleep -Seconds 3

    # Get recent workflow runs
    $runsUri = "https://api.github.com/repos/$Owner/$Repo/actions/workflows/$WorkflowFile/runs?per_page=1"
    $runs = Invoke-RestMethod -Uri $runsUri -Headers $headers -Method Get

    if ($runs.workflow_runs.Count -gt 0) {
        $run = $runs.workflow_runs[0]

        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host "Workflow Started!" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Cyan
        Write-Host "  Run ID: $($run.id)" -ForegroundColor Yellow
        Write-Host "  Status: $($run.status)" -ForegroundColor Yellow
        Write-Host "  Run Number: #$($run.run_number)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Monitor progress at:" -ForegroundColor Green
        Write-Host "  $($run.html_url)" -ForegroundColor Cyan
        Write-Host ""

        # Monitor workflow execution
        Write-Host "Monitoring deployment (press Ctrl+C to exit monitoring)..." -ForegroundColor Yellow
        Write-Host ""

        $lastStatus = ""
        $dots = 0

        while ($true) {
            Start-Sleep -Seconds 10

            $runUri = "https://api.github.com/repos/$Owner/$Repo/actions/runs/$($run.id)"
            $currentRun = Invoke-RestMethod -Uri $runUri -Headers $headers -Method Get

            if ($currentRun.status -ne $lastStatus) {
                $lastStatus = $currentRun.status
                $timestamp = Get-Date -Format "HH:mm:ss"

                Write-Host "[$timestamp] Status: $($currentRun.status)" -ForegroundColor Yellow

                if ($currentRun.status -eq "completed") {
                    Write-Host ""
                    Write-Host "============================================================" -ForegroundColor Cyan

                    if ($currentRun.conclusion -eq "success") {
                        Write-Host "DEPLOYMENT SUCCESS!" -ForegroundColor Green
                        Write-Host "============================================================" -ForegroundColor Cyan
                        Write-Host ""
                        Write-Host "The deployment completed successfully!" -ForegroundColor Green
                        Write-Host ""
                        Write-Host "Next steps:" -ForegroundColor Yellow
                        Write-Host "  1. Check LangSmith UI: https://smith.langchain.com" -ForegroundColor White
                        Write-Host "  2. Verify your deployment is listed and healthy" -ForegroundColor White
                        Write-Host "  3. Test your application endpoints" -ForegroundColor White
                        Write-Host ""
                        exit 0
                    }
                    elseif ($currentRun.conclusion -eq "failure") {
                        Write-Host "DEPLOYMENT FAILED!" -ForegroundColor Red
                        Write-Host "============================================================" -ForegroundColor Red
                        Write-Host ""
                        Write-Host "The deployment failed. Check the logs at:" -ForegroundColor Red
                        Write-Host "  $($currentRun.html_url)" -ForegroundColor Cyan
                        Write-Host ""

                        # Try to get job details
                        $jobsUri = "https://api.github.com/repos/$Owner/$Repo/actions/runs/$($run.id)/jobs"
                        $jobs = Invoke-RestMethod -Uri $jobsUri -Headers $headers -Method Get

                        Write-Host "Failed jobs:" -ForegroundColor Red
                        foreach ($job in $jobs.jobs) {
                            if ($job.conclusion -eq "failure") {
                                Write-Host "  - $($job.name): $($job.conclusion)" -ForegroundColor Red
                            }
                        }
                        Write-Host ""
                        exit 1
                    }
                    else {
                        Write-Host "DEPLOYMENT ENDED: $($currentRun.conclusion)" -ForegroundColor Yellow
                        Write-Host "============================================================" -ForegroundColor Cyan
                        Write-Host ""
                        Write-Host "Check details at: $($currentRun.html_url)" -ForegroundColor Cyan
                        Write-Host ""
                        exit 0
                    }
                }
            }
            else {
                # Show progress dots
                $dots++
                if ($dots % 6 -eq 0) {
                    $timestamp = Get-Date -Format "HH:mm:ss"
                    Write-Host "[$timestamp] Still running..." -ForegroundColor Gray
                }
            }
        }
    }
    else {
        Write-Host "  Could not find workflow run. It may take a moment to appear." -ForegroundColor Yellow
        Write-Host "  Check manually at: https://github.com/$Owner/$Repo/actions" -ForegroundColor Cyan
        Write-Host ""
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
        Write-Host "Authentication failed. Please check your GitHub token." -ForegroundColor Red
    }
    elseif ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "Workflow not found. Check that deploy_langsmith.yml exists in .github/workflows/" -ForegroundColor Red
    }

    Write-Host ""
    exit 1
}
