# LangSmith Deployment Setup Guide

This guide will help you set up and execute the deployment to LangSmith Cloud.

## Prerequisites

You need the following API keys:
- ✅ LANGSMITH_API_KEY
- ✅ LLAMA_CLOUD_API_KEY
- ✅ ANTHROPIC_API_KEY
- ✅ OPENAI_API_KEY (optional)

## Step 1: Configure GitHub Secrets

### Option A: Using GitHub Web UI (Recommended)

1. Go to: https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions

2. Click "New repository secret" and add each of the following:

   | Secret Name | Value | Status |
   |------------|--------|--------|
   | `LANGSMITH_API_KEY` | Your LangSmith API key | ⏳ Required |
   | `WORKSPACE_ID` | `950d802b-125a-45bc-88e4-3d7d0edee182` | ⏳ Required |
   | `INTEGRATION_ID` | `2fd2db44-37bb-42ed-9f3a-9df2e769b058` | ⏳ Required |
   | `LLAMA_CLOUD_API_KEY` | Your Llama Cloud API key | ⏳ Required |
   | `ANTHROPIC_API_KEY` | Your Anthropic API key | ⏳ Required |
   | `OPENAI_API_KEY` | Your OpenAI API key | ✅ Optional |

3. After adding all secrets, verify they appear in the list.

### Option B: Using PowerShell Script

If you prefer automation, you can use the PowerShell scripts:

```powershell
# First, create a GitHub Personal Access Token (PAT) at:
# https://github.com/settings/tokens/new
# Required scopes: repo, workflow

# Then run:
cd C:\Users\chicu\langchain\indufix-llamaindex-toolkit

# You'll be prompted for the token and API keys
.\setup_github_secrets.ps1 `
    -GitHubToken "your_github_token" `
    -LangSmithApiKey "your_langsmith_key" `
    -LlamaCloudApiKey "your_llama_key" `
    -AnthropicApiKey "your_anthropic_key" `
    -OpenAiApiKey "your_openai_key"
```

## Step 2: Trigger Deployment

### Option A: Manual Trigger via GitHub UI

1. Go to: https://github.com/chicuza/indufix-llamaindex-toolkit/actions/workflows/deploy_langsmith.yml

2. Click "Run workflow" button

3. Select environment:
   - `dev` - For development/testing
   - `prod` - For production (requires manual approval)

4. Click "Run workflow"

### Option B: Trigger via PowerShell

```powershell
cd C:\Users\chicu\langchain\indufix-llamaindex-toolkit

.\trigger_deployment.ps1 `
    -GitHubToken "your_github_token" `
    -Environment "dev"
```

### Option C: Automatic Trigger via Git Push

Push to the `main` branch to automatically trigger deployment:

```bash
git add .
git commit -m "Trigger deployment"
git push origin main
```

## Step 3: Monitor Deployment

### Via GitHub Actions UI

1. Go to: https://github.com/chicuza/indufix-llamaindex-toolkit/actions

2. Click on the running workflow

3. Monitor the following jobs:
   - **test** - Validates configuration and runs tests
   - **deploy** - Deploys to LangSmith Cloud

4. Check the deployment summary in the workflow run

### Via PowerShell Script

If you used the PowerShell trigger script, it will automatically monitor progress and show:
- Deployment status updates
- Success/failure notifications
- Links to logs and LangSmith UI

## Step 4: Verify Deployment

After successful deployment:

1. Go to LangSmith UI: https://smith.langchain.com

2. Navigate to your workspace

3. Check deployments section for:
   - Deployment name: `indufix-llamaindex-toolkit`
   - Status: Should be "healthy"
   - URL: Your deployment endpoint

4. Test the application endpoints

## Troubleshooting

### Secrets Not Configured Error

If you see:
```
ERROR: LANGSMITH_API_KEY secret is not set
```

**Solution**: Add the missing secret via GitHub UI (Step 1, Option A)

### Deployment Fails with Authentication Error

**Possible causes:**
- Invalid LANGSMITH_API_KEY
- Wrong WORKSPACE_ID or INTEGRATION_ID

**Solution:**
1. Verify your API keys are correct
2. Check that WORKSPACE_ID matches your LangSmith workspace
3. Update secrets in GitHub and retry

### Deployment Timeout

If deployment takes longer than 30 minutes:

**Solution:**
1. Check LangSmith UI for deployment status
2. Review workflow logs for specific errors
3. May need to manually rollback if stuck

### Test Job Fails

**Common causes:**
- Invalid YAML in config files
- Missing dependencies

**Solution:**
1. Check workflow logs for specific test failures
2. Fix configuration issues locally
3. Commit and push changes

## Rollback

If deployment fails, automatic rollback is attempted. To manually rollback:

1. Go to LangSmith UI
2. Navigate to your deployment
3. Click "Rollback" to previous revision
4. Or use the LangSmith CLI:
   ```bash
   langsmith deployment rollback <deployment-id>
   ```

## Next Steps After Successful Deployment

1. ✅ Verify deployment health in LangSmith UI
2. ✅ Test application endpoints
3. ✅ Set up monitoring and alerts
4. ✅ Configure production environment (if deploying to prod)
5. ✅ Document deployment URL and access instructions

## Support

- LangSmith Docs: https://docs.smith.langchain.com
- GitHub Actions Logs: https://github.com/chicuza/indufix-llamaindex-toolkit/actions
- Workflow File: `.github/workflows/deploy_langsmith.yml`

---

**Repository**: https://github.com/chicuza/indufix-llamaindex-toolkit
**Current Branch**: main
**Workflow File**: .github/workflows/deploy_langsmith.yml
