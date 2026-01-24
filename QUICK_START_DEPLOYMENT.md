# Quick Start: Deployment Execution Guide

This guide provides step-by-step instructions to execute and verify your GitHub Actions deployment.

---

## Prerequisites Checklist

Before deploying, ensure you have:

- [ ] GitHub repository access: `https://github.com/chicuza/indufix-llamaindex-toolkit`
- [ ] GitHub Actions enabled
- [ ] All required API keys obtained:
  - [ ] LangSmith API Key from https://smith.langchain.com
  - [ ] LlamaCloud API Key from https://cloud.llamaindex.ai
  - [ ] Anthropic API Key from https://console.anthropic.com
- [ ] Workspace ID and Integration ID from LangSmith

---

## Step 1: Configure GitHub Secrets (5 minutes)

### 1.1 Navigate to Secrets Settings

Go to: `https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions`

### 1.2 Add Required Secrets

Click "New repository secret" for each of the following:

#### Required Deployment Secrets

| Secret Name | Where to Get It | Example Format |
|-------------|-----------------|----------------|
| `LANGSMITH_API_KEY` | LangSmith Settings → API Keys | `lsv2_pt_...` |
| `WORKSPACE_ID` | LangSmith workspace UUID | `1234abcd-...` |
| `INTEGRATION_ID` | LangSmith Integrations page | `5678efgh-...` |
| `LLAMA_CLOUD_API_KEY` | LlamaCloud Dashboard → API Keys | `llx-...` |
| `ANTHROPIC_API_KEY` | Anthropic Console → API Keys | `sk-ant-...` |

#### Recommended Secrets (Optional)

| Secret Name | Value | Purpose |
|-------------|-------|---------|
| `LANGCHAIN_TRACING_V2` | `true` | Enable tracing |
| `LANGCHAIN_PROJECT` | `indufix-llamaindex-toolkit` | Project name |
| `OPENAI_API_KEY` | Your OpenAI key (optional) | If using GPT models |

### 1.3 Verify Secrets

After adding all secrets, you should see them listed (values hidden).

**Screenshot Location**: Click on each secret to verify it was saved (you won't see the value, just confirm it exists).

---

## Step 2: Trigger Deployment (2 minutes)

### Option A: Push to Main Branch

```bash
# If you have local changes
git add .
git commit -m "Trigger deployment"
git push origin main
```

### Option B: Manual Workflow Trigger (Recommended for First Run)

1. Go to: `https://github.com/chicuza/indufix-llamaindex-toolkit/actions`
2. Click on "Deploy to LangSmith Cloud" workflow
3. Click "Run workflow" button (top right)
4. Select:
   - **Branch**: `main`
   - **Environment**: `dev`
5. Click green "Run workflow" button

### Option C: GitHub CLI

```bash
gh workflow run deploy_langsmith.yml -f environment=dev
```

---

## Step 3: Monitor Deployment (15-30 minutes)

### 3.1 Watch Workflow Progress

1. Go to: `https://github.com/chicuza/indufix-llamaindex-toolkit/actions`
2. Click on the running workflow (top of list)
3. Click on the "deploy" job
4. Watch the logs in real-time

### 3.2 Key Steps to Watch

The workflow will:

1. **Run Tests** (Job 1)
   - Install dependencies
   - Run unit tests
   - Validate deployment configs
   - **Expected time**: 2-3 minutes

2. **Validate Secrets** (Job 2, Step 1)
   - Check all required secrets are set
   - **Expected output**: "All required secrets are present!"
   - **If this fails**: Go back to Step 1 and add missing secrets

3. **Deploy to LangSmith Cloud** (Job 2, Step 2)
   - Initialize deployment client
   - Create or update deployment
   - Upload code to LangSmith
   - Poll revision status
   - **Expected time**: 10-20 minutes
   - **Look for**: "DEPLOYMENT COMPLETED SUCCESSFULLY!"

4. **Post-Deployment Validation** (Job 2, Step 3)
   - Verify deployment exists
   - Check health status
   - **Expected output**: "Post-deployment validation passed!"

### 3.3 Success Indicators

You'll see these messages if deployment succeeds:

```
============================================================
DEPLOYMENT COMPLETED SUCCESSFULLY!
============================================================

Next steps:
1. Verify deployment in LangSmith UI: https://smith.langchain.com
2. Check deployment health and status
3. Test application endpoints
```

### 3.4 Failure Handling

If deployment fails, the workflow will:
- Automatically attempt rollback
- Show error details in logs
- Exit with failure status

**Check the logs for**:
- Which step failed
- Error message details
- Stack trace (if applicable)

---

## Step 4: Verify Deployment (5 minutes)

### 4.1 Quick Health Check

#### Windows (PowerShell)

```powershell
# Navigate to project directory
cd C:\Users\chicu\langchain\indufix-llamaindex-toolkit

# Run quick test
.\quick_deploy_test.ps1

# Expected output:
# [PASS] Health Check
# [PASS] Info Endpoint
# [PASS] MCP Authentication
# OVERALL STATUS: PASS
```

#### Linux/Mac (Bash)

```bash
# Navigate to project directory
cd ~/langchain/indufix-llamaindex-toolkit

# Make script executable (first time only)
chmod +x quick_deploy_test.sh

# Run quick test
./quick_deploy_test.sh

# Expected output:
# [PASS] Health Check
# [PASS] Info Endpoint
# [PASS] MCP Authentication
# OVERALL STATUS: PASS
```

#### Manual curl Test

```bash
# Test health endpoint
curl https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/ok

# Expected: {"status":"ok"} or 200 OK
```

### 4.2 Comprehensive Verification

```bash
# Install dependencies (if not already installed)
pip install requests

# Run comprehensive verification
python verify_deployment_env.py \
  --deployment-url https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app \
  --verbose

# Expected: Detailed report with all tests passing
```

### 4.3 Test Agent Invocation

```bash
# Test the agent with a real query
curl -X POST \
  https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "messages": [
        {
          "role": "user",
          "content": "What tools do you have available?"
        }
      ]
    },
    "config": {},
    "stream_mode": ["values"]
  }'

# Expected: Streaming response with tool information
```

### 4.4 Check LangSmith Traces (If Tracing Enabled)

1. Go to: `https://smith.langchain.com`
2. Navigate to Projects → `indufix-llamaindex-toolkit`
3. Look for recent traces
4. Click on a trace to see details

**If no traces appear**:
- Verify `LANGCHAIN_TRACING_V2` is set to `"true"`
- Check `LANGSMITH_API_KEY` is set
- Run agent invocation again and wait 30 seconds

---

## Step 5: Post-Deployment Tasks (Optional)

### 5.1 Save Deployment Information

Create a file `deployment-info.txt` with:

```
Deployment Date: 2026-01-23
Deployment ID: 02c0d18a-1a0b-469a-baed-274744a670c6
Deployment URL: https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app
GitHub Workflow Run: [paste URL from browser]
LangSmith Project: indufix-llamaindex-toolkit
Status: Active
```

### 5.2 Set Up Monitoring (Recommended)

1. **Health Endpoint Monitoring**
   ```bash
   # Create a cron job or scheduled task to check health every 5 minutes
   curl https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/ok
   ```

2. **LangSmith Dashboard**
   - Add to bookmarks: `https://smith.langchain.com`
   - Check daily for traces and errors

3. **GitHub Actions Notifications**
   - Enable email notifications for workflow failures
   - Settings → Notifications → GitHub Actions

### 5.3 Document for Team

Share with your team:
- Deployment URL
- LangSmith project URL
- Link to `DEPLOYMENT_ENV_VARS.md`
- How to run verification scripts

---

## Troubleshooting Common Issues

### Issue 1: "LANGSMITH_API_KEY secret is not set"

**Symptom**: Workflow fails at "Validate required secrets" step

**Solution**:
1. Go to GitHub Secrets settings
2. Add `LANGSMITH_API_KEY` secret
3. Re-run workflow

### Issue 2: "Deployment timeout"

**Symptom**: Workflow runs for 30 minutes then times out

**Solution**:
1. Check LangSmith Cloud status
2. Verify your workspace has available capacity
3. Check if there's a long build queue
4. Re-run workflow (may just be temporary slowness)

### Issue 3: "Health check failed"

**Symptom**: Deployment succeeds but health check returns error

**Solution**:
1. Wait 2-3 minutes for deployment to fully start
2. Check LangSmith Cloud logs for runtime errors
3. Verify `ANTHROPIC_API_KEY` is set correctly
4. Verify `LLAMA_CLOUD_API_KEY` is set correctly
5. Check agent.py for initialization errors

### Issue 4: "MCP authentication failed"

**Symptom**: Quick test shows MCP authentication failure

**Solution**:
1. Verify you're using correct deployment URL
2. Check API key is valid (not expired)
3. Verify API key has correct permissions
4. Test with a different API key

### Issue 5: "No traces in LangSmith"

**Symptom**: Agent works but no traces appear

**Solution**:
1. Verify `LANGCHAIN_TRACING_V2` is set to `"true"`
2. Check `LANGSMITH_API_KEY` or `LANGCHAIN_API_KEY` is set
3. Verify `LANGCHAIN_PROJECT` matches project name
4. Wait 1-2 minutes (traces may be delayed)
5. Check LangSmith project name is correct

---

## Success Criteria

Your deployment is successful when:

- [ ] GitHub Actions workflow completes with "DEPLOYMENT COMPLETED SUCCESSFULLY"
- [ ] Health endpoint returns 200 OK
- [ ] Info endpoint returns deployment information
- [ ] Agent responds to test queries
- [ ] Quick test scripts show "OVERALL STATUS: PASS"
- [ ] (Optional) Traces appear in LangSmith UI

---

## Next Steps After Successful Deployment

1. **Test with Real Queries**
   ```bash
   curl -X POST <deployment-url>/runs/stream \
     -H "Content-Type: application/json" \
     -d '{"input":{"messages":[{"role":"user","content":"YOUR QUERY"}]}}'
   ```

2. **Integrate into Your Application**
   - Use the deployment URL in your client code
   - Reference LangGraph Cloud SDK documentation
   - Test with your production use cases

3. **Set Up Production Deployment**
   - Create `deployment/deploy_config_prod.yaml`
   - Add production secrets to GitHub
   - Configure manual approval for production

4. **Monitor and Maintain**
   - Check LangSmith traces regularly
   - Monitor API usage
   - Review error rates
   - Update dependencies periodically

---

## Quick Reference

### Important URLs

```
GitHub Repository:
https://github.com/chicuza/indufix-llamaindex-toolkit

GitHub Actions:
https://github.com/chicuza/indufix-llamaindex-toolkit/actions

GitHub Secrets:
https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions

Deployment URL:
https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app

LangSmith Dashboard:
https://smith.langchain.com

LangSmith Project:
https://smith.langchain.com/projects (find: indufix-llamaindex-toolkit)
```

### Quick Commands

```bash
# Trigger deployment
gh workflow run deploy_langsmith.yml -f environment=dev

# Test health
curl <deployment-url>/ok

# Run quick test (Windows)
.\quick_deploy_test.ps1

# Run quick test (Linux/Mac)
./quick_deploy_test.sh

# Run comprehensive verification
python verify_deployment_env.py --deployment-url <URL>
```

---

## Support

If you encounter issues not covered here:

1. Check `DEPLOYMENT_ENV_VARS.md` for detailed troubleshooting
2. Review workflow logs in GitHub Actions
3. Check LangSmith Cloud deployment logs
4. Consult LangSmith documentation: https://docs.smith.langchain.com/

---

**Estimated Total Time**: 25-40 minutes
**Difficulty**: Intermediate
**Prerequisites**: GitHub access, API keys

**You're ready to deploy! Start with Step 1 above.**
