# Deployment Guide: Indufix LlamaIndex Toolkit

## Deployment Summary

✅ **Repository**: `chicuza/indufix-llamaindex-toolkit` - Ready
✅ **Validation**: All 6 tools loaded successfully
✅ **API Scripts**: Programmatic deployment script created
⚠️ **GitHub Integration**: Requires one-time manual setup

---

## Option 1: Programmatic Deployment (95% Automated)

### Prerequisites
1. One-time GitHub integration setup (2 minutes)

### Step 1: Connect GitHub Integration

Visit: https://smith.langchain.com/settings

- Navigate to **Integrations** or **GitHub** section
- Click **Connect GitHub** or **Add GitHub Integration**
- Authorize LangSmith to access your GitHub account
- Grant access to repository: `chicuza/indufix-llamaindex-toolkit`

### Step 2: Run Automated Deployment

```bash
cd indufix-llamaindex-toolkit
python deploy_to_langsmith.py
```

**What this script does:**
- ✅ Retrieves GitHub integration ID via API
- ✅ Creates deployment via Control Plane API (POST /v2/deployments)
- ✅ Configures repository: `chicuza/indufix-llamaindex-toolkit`
- ✅ Sets branch: `main`
- ✅ Adds secret: `LLAMA_CLOUD_API_KEY`
- ✅ Enables auto-deploy on push
- ✅ Saves deployment info to `.deployment.json` and `.env.production`
- ✅ Provides MCP endpoint URL for Agent Builder

**Expected output:**
```
==================================================================
DEPLOYMENT CONCLUIDO COM SUCESSO!
==================================================================

Deployment ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
Deployment URL: https://indufix-llamaindex-toolkit-xxx.smith.langchain.com
MCP Endpoint: https://indufix-llamaindex-toolkit-xxx.smith.langchain.com/mcp
```

### Step 3: Verify Deployment

Wait 10-15 minutes for build to complete, then run:

```bash
python check_deployment.py
```

When prompted, enter the deployment URL from Step 2.

---

## Option 2: Manual UI Deployment (Backup Method)

If the programmatic deployment fails:

### Step 1: Access LangSmith Deployments

Visit: https://smith.langchain.com/deployments

### Step 2: Create New Deployment

Click **+ New Deployment**

Configure:
- **Repository**: Select `chicuza/indufix-llamaindex-toolkit` from dropdown
- **Branch**: `main`
- **Name**: `indufix-llamaindex-toolkit`
- **Type**: `Development (free)`
- **Auto-update**: ✅ Enabled

### Step 3: Add Secret

Click **Add Secret**:
- **Key**: `LLAMA_CLOUD_API_KEY`
- **Value**: `llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm`

### Step 4: Deploy

Click **Deploy** and wait 10-15 minutes for build to complete.

### Step 5: Copy Deployment URL

After deployment completes, copy the deployment URL (format: `https://indufix-llamaindex-toolkit-xxx.smith.langchain.com`)

### Step 6: Verify

Run verification script:

```bash
python check_deployment.py
```

Enter the deployment URL when prompted.

---

## Post-Deployment: Connect to Agent Builder

### Step 1: Access Agent Builder

Visit: https://smith.langchain.com/agent-builder

### Step 2: Add MCP Server

- Go to **Settings → Workspace → MCP Servers**
- Click **Add Remote Server**
- Configure:
  - **Name**: `indufix-llamacloud`
  - **URL**: `<YOUR_DEPLOYMENT_URL>/mcp`
  - **Authentication**: None (internal use)

### Step 3: Test Integration

Create a new agent in Agent Builder and test with:

```
"Busque valores default para parafuso sextavado M10"
```

Expected: Agent should call tools from the toolkit and return default values for M10 hex bolt.

---

## API Endpoints Used (Programmatic Deployment)

### 1. Get GitHub Integration ID
```
GET https://api.host.langchain.com/v1/integrations/github
Authorization: Bearer {LANGSMITH_API_KEY}
```

### 2. Create Deployment
```
POST https://api.host.langchain.com/v2/deployments
Authorization: Bearer {LANGSMITH_API_KEY}
Content-Type: application/json

{
  "name": "indufix-llamaindex-toolkit",
  "source": "github",
  "source_config": {
    "integration_id": "<INTEGRATION_ID>",
    "repo_url": "https://github.com/chicuza/indufix-llamaindex-toolkit",
    "deployment_type": "dev_free",
    "build_on_push": true
  },
  "source_revision_config": {
    "repo_ref": "main",
    "langgraph_config_path": "toolkit.toml"
  },
  "secrets": [
    {
      "name": "LLAMA_CLOUD_API_KEY",
      "value": "llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm"
    }
  ]
}
```

### 3. Check Deployment Status
```
GET https://api.host.langchain.com/v2/deployments/{deployment_id}
Authorization: Bearer {LANGSMITH_API_KEY}
```

---

## Troubleshooting

### Error: "Invalid token"
- **Cause**: API key might not have correct permissions
- **Solution**: Use the UI deployment method (Option 2)

### Error: "GitHub integration not found"
- **Cause**: GitHub hasn't been connected yet
- **Solution**: Complete Step 1 of Option 1 to connect GitHub

### Error: "Deployment already exists"
- **Cause**: Deployment with this name already created
- **Solution**: Script will automatically retrieve existing deployment info

### Build failing
- **Cause**: Missing dependencies or configuration errors
- **Solution**: Check deployment logs at https://smith.langchain.com/deployments

---

## Files Created

- ✅ `deploy_to_langsmith.py` - Programmatic deployment script
- ✅ `setup_github_integration.py` - GitHub integration checker
- ✅ `validate_deployment.py` - Pre-deployment validation
- ✅ `check_deployment.py` - Post-deployment verification
- ✅ `.deployment.json` - Deployment metadata (created after deployment)
- ✅ `.env.production` - Production environment config (created after deployment)

---

## Next Steps After Successful Deployment

1. **Monitor Deployment**: https://smith.langchain.com/deployments
2. **View Traces**: https://smith.langchain.com/projects/indufix-llamaindex-toolkit
3. **Test Tools**: Use Agent Builder to create test agents
4. **Update Code**: Push to `main` branch triggers auto-deployment
5. **Scale Up**: Upgrade to paid plan for production workloads

---

## Credentials Used

- **LangSmith API Key**: `<YOUR_LANGSMITH_API_KEY>`
- **LlamaCloud API Key**: `llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm`
- **GitHub Repository**: `chicuza/indufix-llamaindex-toolkit`
- **Organization ID**: `e6e330e4-a8c4-4472-841b-096d0f307394`
- **Pipeline ID**: `1bc5e382-d0b6-4dcf-98c5-bf4ce8f67301`

---

## Support

For issues or questions:
- **LangSmith Docs**: https://docs.langchain.com/langsmith/home
- **Control Plane API**: https://api.host.langchain.com/docs
- **LangGraph CLI**: https://docs.langchain.com/langsmith/cli
