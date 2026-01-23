# GitHub Actions Workflow Trigger & Monitoring Guide

## 🎯 Mission: Trigger and Monitor Your First Successful Deployment

This guide shows you how to trigger the GitHub Actions workflow, monitor its execution, and verify successful deployment to LangSmith Cloud.

---

## 📋 Prerequisites

Before triggering the workflow, ensure:

- ✅ All secrets are configured (see `SECRET_CONFIGURATION_GUIDE.md`)
- ✅ Repository: `https://github.com/chicuza/indufix-llamaindex-toolkit`
- ✅ Workflow file exists: `.github/workflows/deploy_langsmith.yml`
- ✅ LangSmith deployment exists and is READY

---

## 🚀 Three Ways to Trigger the Workflow

### Method 1: Manual Trigger (Recommended for First Run) ⭐

**Best for**: Testing, debugging, immediate deployment

**Steps**:

1. Go to your repository: `https://github.com/chicuza/indufix-llamaindex-toolkit`

2. Click on the **Actions** tab (top navigation)

3. In the left sidebar, click on **"Deploy to LangSmith Cloud"** workflow

4. Click the **"Run workflow"** button (blue button, right side)
   - **Screenshot location**: Top right of the workflow runs list

5. A dropdown will appear:
   - **Branch**: Select `main` (or `dev` for development)
   - **Environment**: Choose `dev` (for testing) or `prod` (for production)

6. Click **"Run workflow"** button in the dropdown

7. The workflow will start immediately (page will refresh automatically)

**Screenshot Description**:
```
Actions Tab
  └─ Left Sidebar: "Deploy to LangSmith Cloud"
       └─ Main Panel: "Run workflow" button
            └─ Dropdown:
                 Branch: [main ▼]
                 Deployment environment: [dev ▼]
                 [Run workflow]
```

---

### Method 2: Push to Branch (Automatic)

**Best for**: Continuous deployment after initial testing

**Triggers**:
- Push to `main` branch → Deploys to production environment
- Push to `dev` branch → Deploys to development environment

**Steps**:

1. Make a change to your code
2. Commit and push to `main` or `dev` branch:
   ```bash
   git add .
   git commit -m "Trigger deployment"
   git push origin main
   ```
3. Workflow starts automatically within seconds

**Example commit** (no-op change to trigger):
```bash
# Add a comment or whitespace to README
echo "" >> README.md
git add README.md
git commit -m "chore: trigger deployment workflow"
git push origin main
```

---

### Method 3: Pull Request (Automatic)

**Best for**: Testing changes before merging

**Triggers**:
- Opening a pull request to `main` branch
- Pushing new commits to an open PR

**Steps**:

1. Create a branch: `git checkout -b feature/my-changes`
2. Make changes and commit
3. Push branch: `git push origin feature/my-changes`
4. Create pull request on GitHub targeting `main`
5. Workflow runs automatically on the PR

---

## 📊 Monitoring Workflow Execution

### Accessing the Workflow Run

1. Go to: `https://github.com/chicuza/indufix-llamaindex-toolkit/actions`
2. You'll see a list of workflow runs
3. Click on the most recent run (top of the list)

**Run Details Page Shows**:
- ✅ Overall status (pending, running, success, failed)
- ⏱️ Duration
- 👤 Triggered by (user or branch)
- 🏷️ Commit message
- 🌿 Branch name

### Understanding the Workflow Stages

The workflow has **2 main jobs**:

#### Job 1: Test ⚗️
**Duration**: ~2-3 minutes

**Steps**:
1. ✅ Checkout code (10-20 seconds)
2. ✅ Set up Python (15-30 seconds)
3. ✅ Install dependencies (30-60 seconds)
4. ✅ Run unit tests (30-60 seconds)
5. ✅ Validate deployment configs (10-20 seconds)

**What to Watch**:
- Green checkmark (✅) for each step = success
- Red X (❌) = failure, click to see logs
- Yellow circle (🟡) = currently running

#### Job 2: Deploy 🚀
**Duration**: ~10-15 minutes (depends on build time)

**Steps**:
1. ✅ Checkout code (10-20 seconds)
2. ✅ Set up Python (15-30 seconds)
3. ✅ Install deployment dependencies (20-30 seconds)
4. ✅ Determine environment (dev/prod) (5 seconds)
5. ✅ Deploy to LangSmith Cloud (8-12 minutes) ⏳
6. ✅ Post-deployment validation (30-60 seconds)
7. ✅ Create deployment summary (5 seconds)

**What to Watch**:
- **Deploy step**: This is the longest step
  - Shows real-time deployment logs
  - Includes build progress
  - Shows revision status polling
- **Post-deployment validation**: Confirms deployment health
- **Rollback on failure**: Only runs if deployment fails

---

## 🔍 Reading Workflow Logs

### Accessing Logs

1. Click on a workflow run
2. Click on a job name (e.g., "deploy")
3. Click on a step name to expand logs

### Key Log Sections

#### Deploy Step Logs

**Successful deployment logs should show**:

```
============================================================
Deploying to LangSmith Cloud
Environment: dev
Config: deployment/deploy_config.yaml
Branch: main
Commit: abc123...
============================================================

Client initialized successfully
Deployment name: indufix-llamaindex-toolkit
Source type: github
Checking for existing deployment...
Found existing deployment: <deployment-id>
Updating deployment (creates new revision)...
Deployment updated successfully

============================================================
WAITING FOR DEPLOYMENT TO COMPLETE
============================================================
Deployment ID: <deployment-id>
Revision ID: <revision-id>
Timeout: 1800 seconds (30 minutes)
============================================================

Polling revision status...
Status: BUILDING (attempt 1/360)
Status: BUILDING (attempt 2/360)
...
Status: DEPLOYED (attempt 45/360)

============================================================
DEPLOYMENT SUCCESSFUL!
============================================================
Deployment URL: https://<workspace>.langsmith.com/deployments/<deployment-id>
Health endpoint: https://<workspace>.langsmith.com/deployments/<deployment-id>/ok

Deployment completed successfully!
```

#### Post-Deployment Validation Logs

```
Running post-deployment validation...
Deployment ID: <deployment-id>
Deployment URL: https://...
Health: healthy
State: active
Post-deployment validation passed!
```

#### Deployment Summary

After the workflow completes, you'll see a **summary section** at the bottom:

```markdown
# Deployment Summary 🚀

## Configuration
- **Environment**: `dev`
- **Branch**: `main`
- **Commit**: `abc123...`
- **Triggered by**: username

## Status
✅ **Deployment successful!**

## Resources
- [LangSmith UI](https://smith.langchain.com)
- [Workflow Run](https://github.com/chicuza/indufix-llamaindex-toolkit/actions/runs/123456)
```

---

## ✅ Success Indicators

### Green Workflow ✅

**What to look for**:
1. ✅ All steps show green checkmarks
2. ✅ "Deploy" step shows "DEPLOYMENT SUCCESSFUL!"
3. ✅ "Post-deployment validation" step passes
4. ✅ Deployment summary shows "Deployment successful!"
5. ✅ Total duration: ~12-18 minutes

### Deployment URL

The logs will show a deployment URL like:
```
Deployment URL: https://api.smith.langchain.com/deployments/<deployment-id>
```

**Verify deployment**:
1. Copy the deployment URL from logs
2. Add `/ok` to the end
3. Open in browser: should return health status

**Or check in LangSmith UI**:
1. Go to: https://smith.langchain.com
2. Navigate to **Deployments** section
3. Find **indufix-llamaindex-toolkit**
4. Status should be **ACTIVE** and **HEALTHY**

---

## ❌ Failure Indicators & Troubleshooting

### Common Failures

#### 1. Secret Not Found

**Symptoms**:
```
Error: Secret INTEGRATION_ID not found
```

**Solution**:
- Go to `SECRET_CONFIGURATION_GUIDE.md`
- Verify all secrets are added correctly
- Check secret name spelling (case-sensitive)

#### 2. Authentication Failed

**Symptoms**:
```
Authentication failed. Check your LANGSMITH_API_KEY and WORKSPACE_ID
```

**Solution**:
- Verify `LANGSMITH_API_KEY` value in GitHub Secrets
- Verify `WORKSPACE_ID` value in GitHub Secrets
- Check that API key has not expired

#### 3. Integration Not Found

**Symptoms**:
```
Error: Integration 2fd2db44-37bb-42ed-9f3a-9df2e769b058 not found
```

**Solution**:
- Verify `INTEGRATION_ID` in GitHub Secrets matches:
  ```
  2fd2db44-37bb-42ed-9f3a-9df2e769b058
  ```
- Check that integration is still active in LangSmith UI

#### 4. Deployment Timeout

**Symptoms**:
```
DEPLOYMENT TIMEOUT
Deployment may still be in progress
```

**Solution**:
1. Check LangSmith UI for deployment status
2. If still building, wait and check again
3. If failed, check build logs in LangSmith UI
4. Common causes:
   - Missing dependencies in requirements.txt
   - Build errors in application code
   - Resource limits exceeded

#### 5. Test Failures

**Symptoms**:
```
pytest: command not found
or
Tests failed: AssertionError
```

**Solution**:
- Check that `requirements-dev.txt` includes pytest
- Fix failing tests in your code
- Or temporarily skip tests (not recommended for production)

---

## 🔄 Rollback on Failure

If deployment fails, the workflow **automatically attempts rollback**:

**What happens**:
1. Workflow detects deployment failure
2. "Rollback on failure" step activates
3. Attempts to rollback to previous revision
4. Logs show rollback status

**Rollback logs example**:
```
============================================================
DEPLOYMENT FAILED - Attempting Rollback
============================================================
Found deployment: <deployment-id>
Attempting rollback to previous revision...
Rollback initiated successfully
```

**If rollback fails**:
- Manual intervention required
- Go to LangSmith UI
- Navigate to deployment
- Click "Rollback" button manually

---

## 📈 Monitoring Deployment Status

### Real-Time Status

**During deployment** (8-12 minutes):
1. Open GitHub Actions workflow run
2. Watch "Deploy to LangSmith Cloud" step
3. Logs update every 5 seconds
4. Shows build progress and status

### LangSmith UI Monitoring

**Parallel monitoring in LangSmith**:

1. Open: https://smith.langchain.com
2. Navigate to **Deployments**
3. Find **indufix-llamaindex-toolkit**
4. Click to view details

**Deployment details page shows**:
- Current status (Building, Deploying, Active, Failed)
- Health status (Healthy, Unhealthy, Unknown)
- Build logs (real-time)
- Revision history
- Environment variables
- Resource usage

---

## 🎯 Verification Checklist

### Immediate Verification (During Workflow)

- [ ] Workflow started (visible in Actions tab)
- [ ] "Test" job completed successfully (green checkmark)
- [ ] "Deploy" job started
- [ ] "Deploy to LangSmith Cloud" step running
- [ ] No red error messages in logs

### Post-Deployment Verification (After Workflow)

- [ ] Workflow shows green checkmark (✅ Success)
- [ ] Total duration: 12-18 minutes
- [ ] Deployment URL present in logs
- [ ] Post-deployment validation passed
- [ ] Deployment summary shows success

### LangSmith UI Verification

- [ ] Go to https://smith.langchain.com
- [ ] Navigate to Deployments
- [ ] Find **indufix-llamaindex-toolkit**
- [ ] Status: **ACTIVE**
- [ ] Health: **HEALTHY**
- [ ] Latest revision: Matches recent commit

### Functional Verification

- [ ] Copy deployment URL from logs
- [ ] Open: `<deployment-url>/ok`
- [ ] Should return: `{"status": "ok"}` or similar
- [ ] Test API endpoint (if applicable)
- [ ] Verify application responds correctly

---

## 🔧 Advanced Monitoring

### Workflow Logs Download

**Download logs for offline analysis**:

1. Go to workflow run page
2. Click "..." (three dots) in top right
3. Select "Download log archive"
4. Extract ZIP file
5. View logs in text editor

### Workflow Notifications

**Set up notifications**:

1. Go to: https://github.com/settings/notifications
2. Enable "Actions" notifications
3. Choose: Email or GitHub web notifications
4. You'll be notified on:
   - Workflow failures
   - Workflow completions

### LangSmith Alerts

**Set up LangSmith alerts**:

1. Go to LangSmith Settings
2. Navigate to Alerts/Notifications
3. Configure:
   - Deployment failures
   - Health check failures
   - Resource threshold alerts

---

## 📊 Understanding Deployment States

### Workflow States

| State | Icon | Meaning | Action |
|-------|------|---------|--------|
| Queued | 🟡 | Waiting to start | Wait (usually 10-30 seconds) |
| Running | 🔵 | Currently executing | Monitor logs |
| Success | ✅ | Completed successfully | Verify in LangSmith UI |
| Failed | ❌ | Execution failed | Check logs, fix issues |
| Cancelled | ⚪ | Manually cancelled | Re-run if needed |

### Deployment States (LangSmith)

| State | Meaning | Duration |
|-------|---------|----------|
| BUILDING | Creating container image | 3-5 minutes |
| DEPLOYING | Starting services | 2-3 minutes |
| DEPLOYED | Successfully deployed | N/A |
| FAILED | Deployment failed | N/A |
| ROLLING_BACK | Reverting to previous | 1-2 minutes |

---

## 🚨 Emergency Procedures

### Stop Running Deployment

**If you need to cancel**:

1. Go to workflow run page
2. Click **"Cancel workflow"** button (top right)
3. Confirm cancellation
4. Deployment will stop within 30 seconds

**Note**: Partial deployments may need manual cleanup in LangSmith UI

### Force Rollback

**If deployment succeeded but application broken**:

1. Go to LangSmith UI
2. Navigate to deployment
3. Click **"Rollback"** button
4. Select previous revision
5. Confirm rollback

### Re-run Failed Workflow

**To retry after fixing issues**:

1. Go to failed workflow run page
2. Click **"Re-run failed jobs"** button (top right)
3. Or click **"Re-run all jobs"** to start fresh
4. Workflow will use latest secret values

---

## 📝 Best Practices

### Testing Strategy

1. **First deployment**: Use manual trigger with `dev` environment
2. **After success**: Push to `dev` branch for automatic testing
3. **Production**: Only push to `main` after validating in `dev`

### Monitoring Strategy

1. **Initial runs**: Watch logs in real-time
2. **Production runs**: Enable notifications, check summary
3. **Regular checks**: Review LangSmith UI weekly

### Debugging Strategy

1. **Check workflow logs first**: Most issues show here
2. **Check LangSmith build logs**: For build-specific errors
3. **Verify secrets**: Use verification checklist
4. **Test locally**: Run `python deployment/deploy_ci.py` locally

---

## 🎓 Next Steps

### After First Successful Deployment

1. ✅ Verify deployment in LangSmith UI
2. ✅ Test application endpoints
3. ✅ Review workflow logs for optimization opportunities
4. ✅ Set up monitoring and alerts
5. ✅ Document any custom configuration

### Ongoing Operations

1. **Regular deployments**: Push to `main` or `dev` as needed
2. **Monitor health**: Check LangSmith UI regularly
3. **Review logs**: Look for warnings or performance issues
4. **Update secrets**: Rotate API keys periodically
5. **Scale resources**: Adjust in `deploy_config.yaml` if needed

---

## 🆘 Getting Help

### Quick Links

- GitHub Actions Documentation: https://docs.github.com/en/actions
- LangSmith Cloud Docs: https://docs.smith.langchain.com/
- Workflow File: `.github/workflows/deploy_langsmith.yml`
- Deployment Script: `deployment/deploy_ci.py`

### Troubleshooting Resources

1. **Workflow logs**: First place to check
2. **LangSmith UI**: Build logs and deployment status
3. **GitHub Issues**: Search for similar problems
4. **LangSmith Support**: support@langchain.com

### Common Commands

```bash
# Check workflow status from CLI (requires gh CLI)
gh run list --workflow="Deploy to LangSmith Cloud"

# View latest workflow run
gh run view --log

# Trigger workflow manually (requires gh CLI)
gh workflow run "Deploy to LangSmith Cloud" --ref main
```

---

## ✨ Success Metrics

### First Deployment Success

**You've succeeded when**:

- ✅ Workflow completes with green checkmark
- ✅ Deployment shows ACTIVE and HEALTHY in LangSmith UI
- ✅ Application responds to health check
- ✅ All team members can trigger deployments

### Ongoing Success

**Healthy deployment process**:

- ✅ Deployments complete in 12-18 minutes consistently
- ✅ <5% failure rate
- ✅ Fast rollback when issues occur
- ✅ Clear logs and error messages
- ✅ Team confidence in automated deployments

---

## 🎉 Ready to Deploy!

**To trigger your first deployment**:

1. ✅ Ensure all secrets are configured
2. ✅ Go to Actions tab
3. ✅ Select "Deploy to LangSmith Cloud"
4. ✅ Click "Run workflow"
5. ✅ Choose `dev` environment
6. ✅ Watch the magic happen! ✨

**Congratulations on setting up automated deployments!** 🚀
