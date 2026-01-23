# CLI Testing Guide - Quick Start

**For**: Testing MCP server using official CLI methods
**Date**: 2026-01-22

---

## Quick Start (5 Minutes)

### Windows

```batch
REM Step 1: Run the setup script
setup_mcp_test.bat

REM You'll be prompted for your LangSmith API key
REM Tests will run automatically
```

### Linux/Mac

```bash
# Step 1: Make script executable
chmod +x setup_mcp_test.sh

# Step 2: Run the setup script
./setup_mcp_test.sh

# You'll be prompted for your LangSmith API key
# Tests will run automatically
```

---

## What This Tests

The CLI test verifies:

1. **Deployment Health** ✅
   - Checks if deployment is online
   - No authentication required

2. **MCP Endpoint Security** ✅
   - Verifies 403 Forbidden without auth
   - Confirms security is working

3. **MCP Authentication** ✅
   - Tests with X-Api-Key header
   - Verifies tool discovery works

4. **Tool Invocation** ✅
   - Tests calling the indufix_agent tool
   - Confirms end-to-end functionality

---

## Expected Results

```
======================================================================
TEST SUMMARY
======================================================================

[OK] Deployment Health
[OK] MCP Without Auth (Expected Fail)
[OK] MCP With Auth
[OK] Tool Invocation

Tests Passed: 4/4

[SUCCESS] All MCP tests passed!
```

---

## What You CANNOT Do via CLI

### ⚠️ No CLI Commands for These Actions

After testing succeeds, you **MUST** use the LangSmith UI for:

1. **Adding MCP server to workspace**
   - There are NO CLI commands for this
   - Must use: https://smith.langchain.com/settings

2. **Configuring workspace secrets**
   - There are NO CLI commands for this
   - Must use: https://smith.langchain.com/settings

3. **Managing MCP server settings**
   - There are NO CLI commands for this
   - Must use Agent Builder UI

---

## Next Steps After CLI Testing

### Step 1: Verify Tests Pass ✅

Run the CLI test and ensure all 4 tests pass.

### Step 2: Add to Agent Builder (UI Required) ⏳

**Cannot be automated - Manual UI steps required**

1. Visit: https://smith.langchain.com/settings
2. Navigate: Workspace → MCP Servers
3. Click: "Add Remote Server"

4. Configure:
   ```
   Name: indufix-llamaindex-toolkit
   URL: https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/mcp
   ```

5. Add Headers:
   ```
   Header 1:
     Name: X-Api-Key
     Value: YOUR_LANGSMITH_API_KEY

   Header 2:
     Name: X-Tenant-Id
     Value: 950d802b-125a-45bc-88e4-3d7d0edee182
   ```

6. Save and verify green/active indicator

### Step 3: Integrate with Subagent ⏳

1. Navigate to agent editor
2. Find LlamaIndex_Rule_Retriever subagent
3. Add `indufix_agent` tool
4. Update system prompt
5. Test

---

## Files Created

### CLI Testing Scripts
- ✅ `test_mcp_cli.py` - Main test script
- ✅ `setup_mcp_test.bat` - Windows setup
- ✅ `setup_mcp_test.sh` - Linux/Mac setup

### Documentation
- ✅ `MCP_CLI_GUIDE.md` - Complete CLI guide
- ✅ `CLI_TESTING_README.md` - This file
- ✅ `MCP_AUTHENTICATION_FIX.md` - Authentication fix
- ✅ `AUTHENTICATION_FIX_SUMMARY.md` - Quick summary

---

## Troubleshooting

### Issue: Script says "LANGSMITH_API_KEY environment variable not set"

**Solution**: Run the setup script (`setup_mcp_test.bat` or `setup_mcp_test.sh`)

Or manually set it:
```bash
# Windows
set LANGSMITH_API_KEY=your_key_here
python test_mcp_cli.py

# Linux/Mac
export LANGSMITH_API_KEY=your_key_here
python3 test_mcp_cli.py
```

### Issue: Tests fail with 403 Forbidden

**Diagnosis**:
- Test 2 (Without Auth) should PASS with 403 - this is expected
- Test 3 (With Auth) should PASS with 200

**If Test 3 fails with 403**:
- Verify your API key is correct
- Check API key has proper permissions
- Try generating a new API key at: https://smith.langchain.com/settings

### Issue: Deployment health check fails

**Solution**:
1. Check deployment status: https://smith.langchain.com/deployments
2. Verify URL is correct
3. Check network connectivity

---

## Summary

✅ **What CLI Testing Does**:
- Verifies MCP endpoint is accessible
- Tests authentication works
- Confirms tools can be invoked
- Validates deployment health

⚠️ **What CLI Cannot Do**:
- Add MCP server to workspace (UI required)
- Configure workspace secrets (UI required)
- Manage Agent Builder settings (UI required)

📚 **Documentation**:
- Complete Guide: `MCP_CLI_GUIDE.md`
- Auth Fix: `MCP_AUTHENTICATION_FIX.md`
- Integration: `LLAMAINDEX_RULE_RETRIEVER_INTEGRATION.md`

---

**Ready to test?** Run `setup_mcp_test.bat` (Windows) or `./setup_mcp_test.sh` (Linux/Mac)!
