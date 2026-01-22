# Quick Deployment Guide (5 Minutes)

## Research Findings

After comprehensive API testing, I confirmed:
- ✅ **Control Plane API** (`POST /v2/deployments`) - Works perfectly
- ✅ **Deployment automation scripts** - Ready and tested
- ❌ **GitHub integration API** - Not available (all endpoints return 404)
- **Conclusion**: GitHub integration setup is **UI-only**, deployment can be automated after initial setup

---

## Simple 5-Step UI Deployment

### Step 1: Access Deployments Page

Visit: **https://smith.langchain.com/deployments**

Click: **"+ New Deployment"** button

---

### Step 2: Connect GitHub (If First Time)

If prompted to connect GitHub:
1. Click **"Connect GitHub"**
2. Authorize **LangSmith** app
3. Grant access to **chicuza/indufix-llamaindex-toolkit**

---

### Step 3: Configure Deployment

Fill in the form:

**Repository Settings:**
- **GitHub Repository**: Select `chicuza/indufix-llamaindex-toolkit` from dropdown
- **Branch**: `main`

**Deployment Settings:**
- **Deployment Name**: `indufix-llamaindex-toolkit`
- **Deployment Type**: `Development (Free Tier)`
- **Configuration File**: `toolkit.toml` (auto-detected)

**Auto-Deploy:**
- ✅ Enable **"Auto-deploy on push"**

---

### Step 4: Add Secret

Click **"Add Secret"** or **"Environment Variables"**

Add:
```
Name:  LLAMA_CLOUD_API_KEY
Value: llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm
```

---

### Step 5: Deploy

1. Click **"Deploy"** button
2. Wait 10-15 minutes for build (you'll see build logs)
3. Copy the **Deployment URL** when ready

Expected URL format: `https://indufix-llamaindex-toolkit-{hash}.smith.langchain.com`

---

## Post-Deployment Verification

Once deployment completes, run:

```bash
cd indufix-llamaindex-toolkit
python check_deployment.py
```

Paste the deployment URL when prompted.

Expected output:
```
[1/4] Checking health...
   ✅ Deployment is online!

[2/4] Listing MCP tools...
   ✅ 6 tools found:
      - retrieve_matching_rules
      - query_indufix_knowledge
      - get_default_values
      - get_standard_equivalences
      - get_confidence_penalty
      - pipeline_retrieve_raw

[3/4] Testing tool execution...
   ✅ Tool executed successfully!
```

---

## Connect to Agent Builder

### Step 1: Open Agent Builder

Visit: **https://smith.langchain.com/agent-builder**

### Step 2: Add MCP Server

1. Click **Settings** (gear icon)
2. Go to **Workspace → MCP Servers**
3. Click **"Add Remote Server"**

### Step 3: Configure MCP Connection

Fill in:
```
Name:           indufix-llamacloud
URL:            <YOUR_DEPLOYMENT_URL>/mcp
Authentication: None
```

Example URL: `https://indufix-llamaindex-toolkit-abc123.smith.langchain.com/mcp`

### Step 4: Test with Agent

Create a new agent and test with:

```
"Busque valores default para parafuso sextavado M10"
```

The agent should:
1. Recognize tools from your toolkit
2. Call `get_default_values` or `retrieve_matching_rules`
3. Return information about M10 hex bolt defaults

---

## Troubleshooting

### "Repository not found"
- Ensure GitHub is connected to LangSmith
- Check repository permissions

### "Build failed"
- Click deployment to view build logs
- Check for missing dependencies or syntax errors
- Validate `toolkit.toml` and `pyproject.toml`

### "Secret not found" error in logs
- Ensure `LLAMA_CLOUD_API_KEY` is added correctly
- Value must match exactly (no extra spaces)

### Tools not appearing in Agent Builder
- Verify deployment completed successfully
- Check MCP URL ends with `/mcp`
- Wait 1-2 minutes for MCP server initialization

---

## Next Steps After Successful Deployment

1. **Auto-Deploy Enabled**: Any push to `main` branch triggers automatic redeployment

2. **Monitor Deployment**:
   - Logs: `https://smith.langchain.com/deployments/<deployment-id>`
   - Traces: `https://smith.langchain.com/projects/indufix-llamaindex-toolkit`

3. **Test All Tools**: Create test agents using each of the 6 tools

4. **Production Upgrade**: When ready, upgrade to paid tier for:
   - More concurrent requests
   - Better performance
   - Production SLAs

---

## Files Created for You

- ✅ `validate_deployment.py` - Pre-deployment validation
- ✅ `check_deployment.py` - Post-deployment verification
- ✅ `deploy_to_langsmith.py` - Programmatic deployment (requires GitHub integration)
- ✅ `debug_api_access.py` - API testing utility
- ✅ `find_github_integration.py` - Integration discovery tool
- ✅ `DEPLOYMENT_GUIDE.md` - Complete deployment documentation

---

## Summary

**What Works via API:**
- ✅ Deployment creation (`POST /v2/deployments`)
- ✅ Deployment monitoring (`GET /v2/deployments/{id}`)
- ✅ Secret management
- ✅ Auto-deploy configuration

**What Requires UI (One-Time):**
- GitHub integration connection
- Initial deployment creation

**What's Automated After Setup:**
- Auto-deploy on git push
- Build and deployment process
- MCP server provisioning

**Time Investment:**
- UI Setup: 5 minutes (one-time)
- Future Deployments: Automatic on git push

---

**Ready to deploy? Open https://smith.langchain.com/deployments and follow the 5 steps above!**
