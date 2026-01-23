# MCP Server CLI Testing & Configuration Guide

**Date**: 2026-01-22
**Status**: Official Methods Only

---

## Important Discovery

**There are NO CLI commands for managing MCP servers in LangSmith.**

### What CAN be done via CLI/API:
- ✅ Test MCP endpoint connections
- ✅ Verify deployment health
- ✅ Call MCP tools programmatically
- ✅ Deploy LangGraph applications

### What MUST be done via UI:
- ⚠️ Adding MCP servers to workspace
- ⚠️ Configuring workspace secrets
- ⚠️ Managing MCP server settings in Agent Builder

---

## Official CLI Testing Methods

### Method 1: Using Our Test Script (Recommended)

**Windows:**
```batch
REM Option A: Interactive setup
setup_mcp_test.bat

REM Option B: Manual setup
set LANGSMITH_API_KEY=your_api_key_here
python test_mcp_cli.py
```

**Linux/Mac:**
```bash
# Option A: Interactive setup
chmod +x setup_mcp_test.sh
./setup_mcp_test.sh

# Option B: Manual setup
export LANGSMITH_API_KEY=your_api_key_here
python3 test_mcp_cli.py
```

**Expected Output:**
```
======================================================================
MCP SERVER CLI TEST - Official Method
======================================================================

Deployment: https://ndufix-llamaindex-toolkit-m...us.langgraph.app
Workspace: 950d802b-125a-45bc-88e4-3d7d0edee182
Test Date: 2026-01-22 HH:MM:SS

======================================================================
Test 1: Deployment Health Check
======================================================================
URL: .../ok
Status Code: 200
Response: {"ok":true}

[OK] Deployment is healthy and accessible

======================================================================
Test 2: MCP Endpoint Without Authentication
======================================================================
Status Code: 403
Response: {"detail":"Missing authentication headers"}

[EXPECTED] 403 Forbidden - Authentication is required

======================================================================
Test 3: MCP Endpoint With Authentication
======================================================================
Status Code: 200

[SUCCESS] Found 1 tool(s):
  - indufix_agent: ...

======================================================================
Test 4: Tool Invocation Test
======================================================================
Status Code: 200

[SUCCESS] Tool invocation successful

======================================================================
TEST SUMMARY
======================================================================

[OK] Deployment Health
[OK] MCP Without Auth (Expected Fail)
[OK] MCP With Auth
[OK] Tool Invocation

Tests Passed: 4/4
```

---

### Method 2: Using curl (Command Line HTTP Client)

**Test 1: Health Check**
```bash
curl -X GET "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/ok"
```

Expected: `{"ok":true}`

**Test 2: MCP Tool Discovery (With Auth)**
```bash
curl -X POST "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "X-Api-Key: YOUR_LANGSMITH_API_KEY" \
  -H "X-Tenant-Id: 950d802b-125a-45bc-88e4-3d7d0edee182" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
  }'
```

Expected: List of available tools

**Test 3: Tool Invocation**
```bash
curl -X POST "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -H "X-Api-Key: YOUR_LANGSMITH_API_KEY" \
  -H "X-Tenant-Id: 950d802b-125a-45bc-88e4-3d7d0edee182" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "indufix_agent",
      "arguments": {
        "messages": [
          {
            "role": "user",
            "content": "List available tools"
          }
        ]
      }
    },
    "id": 2
  }'
```

---

### Method 3: Using Python Requests (Programmatic)

```python
import requests
import os

DEPLOYMENT_URL = "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app"
API_KEY = os.getenv("LANGSMITH_API_KEY")
WORKSPACE_ID = "950d802b-125a-45bc-88e4-3d7d0edee182"

# Test MCP endpoint
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "X-Api-Key": API_KEY,
    "X-Tenant-Id": WORKSPACE_ID
}

mcp_request = {
    "jsonrpc": "2.0",
    "method": "tools/list",
    "params": {},
    "id": 1
}

response = requests.post(
    f"{DEPLOYMENT_URL}/mcp",
    json=mcp_request,
    headers=headers
)

print(f"Status: {response.status_code}")
print(f"Tools: {response.json()}")
```

---

## What CANNOT Be Done via CLI

### ❌ Adding MCP Server to Workspace

**Why**: No CLI commands exist for workspace MCP server management.

**Official Method**: Use LangSmith UI

**Steps**:
1. Visit: https://smith.langchain.com/settings
2. Navigate: Workspace → MCP Servers
3. Click: "Add Remote Server"
4. Configure server settings
5. Add authentication headers

**There is NO alternative CLI method for this step.**

---

### ❌ Managing Workspace Secrets

**Why**: No CLI commands exist for secret management.

**Official Method**: Use LangSmith UI

**Steps**:
1. Visit: https://smith.langchain.com/settings
2. Navigate: Workspace → Secrets
3. Click: "Add secret"
4. Enter secret name and value

**Alternative**: Secrets can be added during deployment via API, but NOT managed afterward.

---

## Official API Methods (Programmatic Alternative)

### Using LangSmith Control Plane API

**Base URL**: `https://api.host.langchain.com`

**Get Deployment Status:**
```bash
curl -X GET "https://api.host.langchain.com/v2/deployments/DEPLOYMENT_ID" \
  -H "Authorization: Bearer YOUR_LANGSMITH_API_KEY"
```

**List Deployments:**
```bash
curl -X GET "https://api.host.langchain.com/v2/deployments" \
  -H "Authorization: Bearer YOUR_LANGSMITH_API_KEY" \
  -H "X-Tenant-Id: YOUR_WORKSPACE_ID"
```

**Note**: These API endpoints do NOT support MCP server workspace configuration.

---

## Complete Workflow

### Step 1: Test MCP Server (CLI)

```bash
# Windows
setup_mcp_test.bat

# Linux/Mac
./setup_mcp_test.sh
```

**Verify**: All 4 tests pass

---

### Step 2: Add to Agent Builder (UI - REQUIRED)

**Cannot be done via CLI - Must use UI**

1. **Create Workspace Secrets** (if using secret interpolation)
   - Settings → Workspace → Secrets
   - Add: `INDUFIX_API_KEY` = your LangSmith API key
   - Add: `INDUFIX_TENANT_ID` = 950d802b-125a-45bc-88e4-3d7d0edee182

2. **Add MCP Server**
   - Settings → Workspace → MCP Servers → Add Remote Server
   - Name: `indufix-llamaindex-toolkit`
   - URL: `https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/mcp`

3. **Configure Authentication**
   - Authentication Type: Headers
   - Header 1: `X-Api-Key` = `{{INDUFIX_API_KEY}}`
   - Header 2: `X-Tenant-Id` = `{{INDUFIX_TENANT_ID}}`

4. **Save and Verify**
   - Click "Save server"
   - Verify green/active indicator
   - Check tool appears in available tools

---

### Step 3: Integrate with Subagent (UI)

1. Navigate to agent editor
2. Find LlamaIndex_Rule_Retriever subagent
3. Add `indufix_agent` tool
4. Update system prompt
5. Test with queries

---

## Troubleshooting via CLI

### Issue: Test fails with 403 Forbidden

**Diagnosis via CLI:**
```bash
# Test without auth (should get 403)
curl -X POST "DEPLOYMENT_URL/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}'
```

**Expected**: `{"detail":"Missing authentication headers"}`

**Fix**: Ensure LANGSMITH_API_KEY is set correctly

---

### Issue: Test fails with other errors

**Check deployment health:**
```bash
curl -X GET "DEPLOYMENT_URL/ok"
```

**Expected**: `{"ok":true}`

**Check deployment status via API:**
```bash
curl -X GET "https://api.host.langchain.com/v2/deployments" \
  -H "Authorization: Bearer YOUR_LANGSMITH_API_KEY"
```

---

## Summary

### ✅ What You CAN Do via CLI/API
1. Test MCP endpoint connectivity
2. Verify authentication works
3. Call tools programmatically
4. Check deployment health
5. Monitor deployment status

### ⚠️ What You MUST Do via UI
1. Add MCP server to workspace
2. Configure workspace secrets (after creation)
3. Manage MCP server settings
4. Add tools to Agent Builder agents

### 📝 Official Documentation
- LangSmith Control Plane API: https://api.host.langchain.com/docs
- LangGraph Platform Docs: https://docs.langchain.com/langgraph-platform
- MCP Server Docs: https://docs.langchain.com/langgraph-platform/server-mcp

---

## Files in This Repository

### Testing Scripts
- `test_mcp_cli.py` - Official CLI test script (Python)
- `setup_mcp_test.bat` - Windows setup script
- `setup_mcp_test.sh` - Linux/Mac setup script

### Documentation
- `MCP_CLI_GUIDE.md` - This file
- `MCP_AUTHENTICATION_FIX.md` - Authentication fix guide
- `AUTHENTICATION_FIX_SUMMARY.md` - Quick overview
- `INTEGRATION_SUMMARY.md` - Integration status

---

**Last Updated**: 2026-01-22
**Status**: Official Methods Documented
**CLI Support**: Testing Only (Configuration Must Use UI)
