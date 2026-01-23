# Quick Fix Guide - Enable GitHub Actions CI/CD

**Problem**: GitHub Actions workflow fails, auto-deploy doesn't work
**Solution**: Configure GitHub Secrets (5-10 minutes)
**Status**: Your deployment is LIVE, this just enables automation

---

## Step 1: Get Your Credentials (2 minutes)

### Open Your `.env` File

**Location**: `C:\Users\chicu\langchain\indufix-llamaindex-toolkit\.env`

**Copy These Values**:

```env
LANGSMITH_API_KEY=lsv2_pt_REDACTED_GET_FROM_LANGSMITH
LLAMA_CLOUD_API_KEY=llx-REDACTED_GET_FROM_LLAMAINDEX
```

### Get Integration ID

**From**: `DEPLOYMENT_SUCCESS.md` (line 222)
```
INTEGRATION_ID=2fd2db44-37bb-42ed-9f3a-9df2e769b058
```

### Known Workspace ID
```
WORKSPACE_ID=950d802b-125a-45bc-88e4-3d7d0edee182
```

### Anthropic API Key

**If you have it**:
```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**If you DON'T have it**:
- Go to: https://console.anthropic.com/settings/keys
- Create new API key
- Copy the key (starts with `sk-ant-`)

---

## Step 2: Add GitHub Secrets (5 minutes)

### Go to GitHub Secrets Page

**URL**: https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions

Or:
1. Go to repository: https://github.com/chicuza/indufix-llamaindex-toolkit
2. Click "Settings" tab
3. Click "Secrets and variables" → "Actions" (left sidebar)
4. You'll see "Actions secrets" page

### Add Each Secret

**Click "New repository secret" button for each**:

#### Secret 1: LANGSMITH_API_KEY
```
Name: LANGSMITH_API_KEY
Value: lsv2_pt_REDACTED_GET_FROM_LANGSMITH
```
Click "Add secret"

#### Secret 2: WORKSPACE_ID
```
Name: WORKSPACE_ID
Value: 950d802b-125a-45bc-88e4-3d7d0edee182
```
Click "Add secret"

#### Secret 3: INTEGRATION_ID
```
Name: INTEGRATION_ID
Value: 2fd2db44-37bb-42ed-9f3a-9df2e769b058
```
Click "Add secret"

#### Secret 4: LLAMA_CLOUD_API_KEY
```
Name: LLAMA_CLOUD_API_KEY
Value: llx-REDACTED_GET_FROM_LLAMAINDEX
```
Click "Add secret"

#### Secret 5: ANTHROPIC_API_KEY
```
Name: ANTHROPIC_API_KEY
Value: sk-ant-your-actual-key-here
```
Click "Add secret"

#### Optional: OPENAI_API_KEY
```
Name: OPENAI_API_KEY
Value: sk-your-openai-key-here
```
Click "Add secret" (skip if you don't have OpenAI key)

### Verify Secrets

After adding, you should see:
- ✅ LANGSMITH_API_KEY
- ✅ WORKSPACE_ID
- ✅ INTEGRATION_ID
- ✅ LLAMA_CLOUD_API_KEY
- ✅ ANTHROPIC_API_KEY
- (Optional) OPENAI_API_KEY

**Note**: Secret values are hidden after creation. This is normal and secure.

---

## Step 3: Test GitHub Actions (3 minutes)

### Go to Actions Tab

**URL**: https://github.com/chicuza/indufix-llamaindex-toolkit/actions

Or:
1. Go to repository: https://github.com/chicuza/indufix-llamaindex-toolkit
2. Click "Actions" tab

### Manually Trigger Workflow

1. Click on "Deploy to LangSmith Cloud" in left sidebar
2. Click blue "Run workflow" button (top right)
3. Select branch: `main`
4. Select environment: `dev`
5. Click green "Run workflow" button
6. Wait a few seconds, then refresh page
7. You should see a new workflow run appear

### Monitor Workflow Execution

**What to expect**:

**Test Job** (2-5 minutes):
- Install dependencies ✅
- Run tests ✅
- Validate configs ✅

**Deploy Job** (10-20 minutes):
- Setup environment ✅
- Run deployment script ✅
- Wait for revision to deploy ✅
- Post-deployment validation ✅
- Create deployment summary ✅

**Total time**: ~15-25 minutes

### Verify Success

When workflow completes:
- ✅ Green checkmark appears
- ✅ Deployment summary shows in workflow output
- ✅ Deployment URL is accessible
- ✅ Deployment shows new commit in LangSmith UI

---

## Step 4: Test Auto-Deploy (2 minutes)

### Make Trivial Change

**Option 1: Via GitHub Web UI**:
1. Go to: https://github.com/chicuza/indufix-llamaindex-toolkit
2. Click on `README.md`
3. Click pencil icon (Edit)
4. Add a space or newline somewhere
5. Scroll down, enter commit message: "Test auto-deploy"
6. Click "Commit changes"

**Option 2: Via Git CLI**:
```bash
cd C:\Users\chicu\langchain\indufix-llamaindex-toolkit

# Make trivial change
echo "" >> README.md

# Commit and push
git add README.md
git commit -m "Test auto-deploy"
git push origin main
```

### Verify Workflow Triggers

1. Go to: https://github.com/chicuza/indufix-llamaindex-toolkit/actions
2. You should see a NEW workflow run appear automatically
3. Workflow should complete successfully
4. Deployment should update in LangSmith

---

## Step 5: Verify Deployment Updated (1 minute)

### Check Deployment in LangSmith

**URL**: https://smith.langchain.com/deployments

**Look for**:
- Deployment name: `indufix-llamaindex-toolkit`
- Status: READY
- Latest commit: Should match your latest push
- Build date: Should be recent

### Test Deployment Endpoint

```bash
curl https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/ok
```

**Expected**: `{"ok": true}` or similar healthy response

---

## Troubleshooting

### Workflow Fails at Test Job

**Error**: "PyYAML not installed"
**Fix**: This should be fixed in latest commit. Pull latest code:
```bash
git pull origin main
```

### Workflow Fails at Deploy Job

**Error**: "Missing environment variable: INTEGRATION_ID"
**Fix**: Double-check secret name is exactly `INTEGRATION_ID` (case-sensitive)

**Error**: "integration_id not found"
**Fix**: Verify integration ID is correct. Check LangSmith UI: https://smith.langchain.com/settings/integrations

**Error**: "Authentication failed"
**Fix**: Verify `LANGSMITH_API_KEY` secret is correct. Check `.env` file for current value.

### Workflow Succeeds But Deployment Doesn't Update

**Check**:
1. Go to LangSmith deployments: https://smith.langchain.com/deployments
2. Look for deployment health status
3. Check deployment logs for errors

**Possible Issues**:
- Deployment may still be building (wait 5-10 more minutes)
- Integration ID may be incorrect
- Repository branch mismatch

### Auto-Deploy Doesn't Trigger on Push

**Check**:
1. Verify secrets are configured
2. Verify you pushed to `main` branch
3. Check GitHub Actions tab for failed runs
4. Check if workflows are enabled: https://github.com/chicuza/indufix-llamaindex-toolkit/settings/actions

---

## What If Integration ID Is Different?

### Verify Integration ID in LangSmith UI

1. Go to: https://smith.langchain.com/settings/integrations
2. Look for GitHub integration
3. Click on it to view details
4. **Copy the Integration ID shown**
5. If different from `2fd2db44-37bb-42ed-9f3a-9df2e769b058`:
   - Go back to GitHub Secrets
   - Edit `INTEGRATION_ID` secret
   - Update with new value
   - Re-run workflow

### If No GitHub Integration Found in UI

**This means GitHub is not connected to LangSmith**

**Fix**:
1. In LangSmith UI, go to: https://smith.langchain.com/settings/integrations
2. Click "Add Integration"
3. Select "GitHub"
4. Follow OAuth flow to connect your GitHub account
5. Authorize LangSmith to access your repositories
6. Select repository: `chicuza/indufix-llamaindex-toolkit`
7. Once connected, copy the new Integration ID
8. Update GitHub Secret `INTEGRATION_ID` with new value
9. Re-run workflow

---

## Security Notes

### Are GitHub Secrets Safe?

**YES**:
- ✅ Secrets are encrypted at rest
- ✅ Secrets are never shown in logs (GitHub redacts them)
- ✅ Secrets are only accessible to workflow runs
- ✅ Only repository admins can view/edit secrets
- ✅ Secrets can be rotated anytime

### What NOT to Do

**❌ DON'T**:
- Commit secrets to `.env` file in Git
- Share secrets in issues or pull requests
- Print secrets in workflow logs
- Store secrets in code comments

**✅ DO**:
- Keep secrets in GitHub Secrets only
- Rotate API keys periodically
- Use minimal scope API keys
- Monitor secret usage in audit logs

---

## Success Criteria

After completing this guide, you should have:

- ✅ 5 required secrets configured in GitHub
- ✅ GitHub Actions workflow runs successfully
- ✅ Deployment updates automatically on code push
- ✅ CI/CD pipeline fully operational
- ✅ No more manual deployment scripts needed

---

## Next Steps After Fix

### Enable Production Deployments

**When ready for production**:
1. Update secrets to use production API keys
2. Push to `main` branch triggers prod deployment
3. Or manually select environment: `prod` when running workflow

### Monitor Deployments

**Set up monitoring**:
- Watch GitHub Actions for failures
- Monitor LangSmith deployment health
- Check deployment logs regularly
- Set up notifications for failures

### Maintain Secrets

**Regular maintenance**:
- Rotate API keys every 90 days
- Update secrets when keys change
- Remove unused secrets
- Audit secret usage monthly

---

## Time Estimate

**Total Time**: ~15 minutes

- Get credentials: 2 minutes
- Add GitHub Secrets: 5 minutes
- Test workflow: 3 minutes
- Test auto-deploy: 2 minutes
- Verify deployment: 1 minute
- Troubleshooting (if needed): 2-10 minutes

---

## Support

**If you get stuck**:

1. **Check GitHub Actions logs**:
   - https://github.com/chicuza/indufix-llamaindex-toolkit/actions
   - Click on failed run
   - Expand failed step to see error

2. **Check LangSmith logs**:
   - https://smith.langchain.com/deployments
   - Click on deployment
   - Go to "Logs" tab

3. **Review full analysis**:
   - `GIT_GITHUB_INTEGRATION_ANALYSIS.md` - Comprehensive analysis
   - `INTEGRATION_FINDINGS_EXECUTIVE_SUMMARY.md` - Executive summary

4. **Check documentation**:
   - `DEPLOYMENT_AUTOMATION_README.md` - Automation guide
   - `HOW_TO_FIND_INTEGRATION_ID.md` - Integration ID help

---

## Visual Checklist

```
Prerequisites:
[✓] Have access to GitHub repository
[✓] Have access to LangSmith workspace
[✓] Have API keys available

Step 1: Get Credentials
[✓] Copy LANGSMITH_API_KEY from .env
[✓] Copy LLAMA_CLOUD_API_KEY from .env
[✓] Copy INTEGRATION_ID from docs
[✓] Note WORKSPACE_ID
[✓] Have ANTHROPIC_API_KEY

Step 2: Configure GitHub Secrets
[✓] Go to repository secrets page
[✓] Add LANGSMITH_API_KEY
[✓] Add WORKSPACE_ID
[✓] Add INTEGRATION_ID
[✓] Add LLAMA_CLOUD_API_KEY
[✓] Add ANTHROPIC_API_KEY
[✓] Verify all secrets added

Step 3: Test Workflow
[✓] Go to Actions tab
[✓] Click "Run workflow"
[✓] Select dev environment
[✓] Monitor execution
[✓] Verify success

Step 4: Test Auto-Deploy
[✓] Make trivial change
[✓] Commit and push
[✓] Verify workflow triggers
[✓] Verify deployment updates

Step 5: Verify
[✓] Check deployment in LangSmith
[✓] Test deployment endpoint
[✓] Confirm latest commit deployed
[✓] Celebrate! 🎉
```

---

**Guide Version**: 1.0
**Last Updated**: 2026-01-23
**Estimated Completion Time**: 15 minutes
**Difficulty**: Easy ⭐
**Requirements**: GitHub access, LangSmith access, API keys
