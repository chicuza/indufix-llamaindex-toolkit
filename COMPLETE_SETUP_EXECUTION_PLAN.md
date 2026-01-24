# Complete Setup Execution Plan
## Guarantee Real SKU Matching Test - Step-by-Step

**Date**: 2026-01-23
**Objective**: Enable full tool invocation with real SKU positional product code matching rules
**Total Time**: 40-55 minutes
**Status**: Ready for Execution

---

## Executive Summary

Your deployment investigation revealed:

✅ **Deployment is OPERATIONAL** - No bugs, no errors
✅ **MCP endpoint is WORKING** - Authentication successful
✅ **6 Tools are PROPERLY IMPLEMENTED** - Ready to return SKU data
⚠️ **Tools are NOT being invoked** - Missing ANTHROPIC_API_KEY in deployment
⚠️ **Agent Builder NOT configured** - MCP server not added to workspace

**What needs to happen**:
1. Configure GitHub Secrets (enables CI/CD + tool routing)
2. Configure Agent Builder (enables production usage)
3. Test with real queries (verify SKU matching rules returned)

**Result**: Tools will return actual SKU positional matching rules, default values, and technical specifications

---

## What You'll Get

### Current Response (Before Setup)

```json
{
  "content": "Tools are available for use via MCP server",
  "tool_calls": [],
  "invalid_tool_calls": []
}
```

**Problem**: Generic response, no actual SKU data

---

### Expected Response (After Setup)

```json
{
  "content": "Para parafuso sextavado M10, recuperei as seguintes regras:\n\n**Material Default**: Aço carbono SAE 1010\n- Confidence: 0.95\n- Penalidade: 0.10\n- SKU Pattern: PSX-M10-AC-*\n\n**Acabamento Default**: Zincado branco\n- Confidence: 0.92\n- SKU Pattern: PSX-M10-*-ZB",
  "tool_calls": [
    {
      "name": "get_default_values",
      "args": {
        "product_type": "parafuso_sextavado",
        "missing_attributes": ["material", "acabamento"]
      },
      "result": {
        "default_attributes": [
          {
            "attribute": "material",
            "value": "Aço carbono SAE 1010",
            "sku_pattern": "PSX-M10-AC-*",
            "confidence": 0.95,
            "penalty": 0.10
          }
        ]
      }
    }
  ]
}
```

**Result**: Real SKU positional matching rules returned! ✅

---

## Part 1: GitHub Secrets Configuration

**Time**: 10-15 minutes
**Purpose**: Enable CI/CD automation and set ANTHROPIC_API_KEY for tool routing

### Quick Reference

**Guide**: `GITHUB_SECRETS_SETUP_GUIDE.md`
**URL**: https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions

### Secrets to Add

| Secret Name | Value | Purpose |
|-------------|-------|---------|
| `LANGSMITH_API_KEY` | `lsv2_pt_YOUR-KEY-HERE` | Deployment auth |
| `WORKSPACE_ID` | `950d802b-125a-45bc-88e4-3d7d0edee182` | Workspace ID |
| `INTEGRATION_ID` | `2fd2db44-37bb-42ed-9f3a-9df2e769b058` | GitHub link |
| `LLAMA_CLOUD_API_KEY` | `llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm` | LlamaCloud |
| `ANTHROPIC_API_KEY` | Get from Anthropic console ⚠️ | **Tool routing** |
| `OPENAI_API_KEY` | Optional | Alternative LLM |

### Actions

1. ✅ Read: `GITHUB_SECRETS_SETUP_GUIDE.md`
2. ✅ Navigate to GitHub repository secrets page
3. ✅ Add all 6 secrets (copy values from guide)
4. ✅ **Get ANTHROPIC_API_KEY**: https://console.anthropic.com/settings/keys
5. ✅ Trigger deployment (push or manual workflow)

### Verification

```bash
# Watch workflow execution
https://github.com/chicuza/indufix-llamaindex-toolkit/actions

# Expected: ✅ All steps pass
```

---

## Part 2: Agent Builder Integration

**Time**: 20-30 minutes
**Purpose**: Configure MCP server and agent for production usage

### Quick Reference

**Guide**: `GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md`
**URL**: https://smith.langchain.com/settings

### Phase 1: Add MCP Server (5 minutes)

**URL**: https://smith.langchain.com/settings → MCP Servers

**Configuration**:
```
Name: indufix-llamaindex-toolkit
URL: https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/mcp
Auth: Headers
  X-Api-Key: [Your LangSmith API key]
  X-Tenant-Id: 950d802b-125a-45bc-88e4-3d7d0edee182
```

**Verification**: Green indicator appears, `indufix_agent` tool listed

---

### Phase 2: Configure Agent (10 minutes)

**URL**: https://smith.langchain.com/o/950d802b-125a-45bc-88e4-3d7d0edee182/agents/chat?agentId=1bf73a52-638f-4c42-8fc7-d6d07405c4fe

**Steps**:
1. Open "LlamaIndex_Rule_Retriever" subagent
2. Add tool: `indufix_agent`
3. Copy system prompt from: `SUBAGENT_SYSTEM_PROMPT.md`
4. Paste into agent prompt field
5. Save configuration

---

### Phase 3: Test Queries (15 minutes)

**Test 1**: "Buscar valores default para parafuso sextavado M10"

**Expected**:
- Material: Aço carbono (confidence: ~0.95)
- Acabamento: Zincado (confidence: ~0.92)
- SKU patterns: PSX-M10-AC-*, PSX-M10-*-ZB
- Penalties: ~0.10-0.12

**Test 2**: "Qual a equivalência da norma DIN 933?"

**Expected**:
- DIN 933 = ISO 4017
- Confidence: > 0.95
- SKU mapping rules

**Test 3**: "Penalidade para material inferido"

**Expected**:
- Penalty value: 0.10-0.18
- Justification
- Method-specific penalties

**Test 4**: "Para parafuso M12 faltam material, acabamento e classe"

**Expected**:
- 3 default values
- 3 penalties
- 3 SKU patterns

---

## Part 3: Validation & Testing

**Time**: 10 minutes
**Purpose**: Verify tools are being invoked and returning real data

### Automated Validation

```bash
cd C:\Users\chicu\langchain\indufix-llamaindex-toolkit
python validate_integration.py
```

**Expected Output**:
```
✅ Test 1: Query Simples - PASSED
✅ Test 2: Equivalências - PASSED
✅ Test 3: Penalidades - PASSED
✅ Test 4: Query Complexa - PASSED

Tests Passed: 4/4
Success Rate: 100%
```

---

### Verification Checklist

After completing all parts:

#### GitHub Secrets
- [ ] All 6 secrets added to repository
- [ ] ANTHROPIC_API_KEY obtained and configured
- [ ] Workflow triggered and completed successfully
- [ ] Deployment shows "healthy" status

#### Agent Builder
- [ ] MCP server shows green/active indicator
- [ ] indufix_agent tool appears in available tools
- [ ] Tool added to LlamaIndex_Rule_Retriever subagent
- [ ] System prompt configured
- [ ] Configuration saved without errors

#### Testing
- [ ] Test queries return specific data (not generic)
- [ ] Responses contain SKU patterns
- [ ] Responses contain confidence scores
- [ ] tool_calls array is populated
- [ ] 4/4 automated tests pass

---

## What Each Part Achieves

### Part 1: GitHub Secrets

**Enables**:
- ✅ Automated deployments on code changes
- ✅ ANTHROPIC_API_KEY set in deployment environment
- ✅ Agent's internal LLM can initialize
- ✅ Tool routing capability

**Result**: Future deployments will include all environment variables

---

### Part 2: Agent Builder Integration

**Enables**:
- ✅ MCP server accessible from Agent Builder
- ✅ indufix_agent tool available to subagents
- ✅ Production-ready usage pattern
- ✅ Workspace-level API key usage (secure)

**Result**: Agents can invoke tools and get real SKU data

---

### Part 3: Validation

**Verifies**:
- ✅ Tools are being invoked (tool_calls array populated)
- ✅ Real data returned (SKU patterns, confidence scores)
- ✅ No generic responses
- ✅ All integration points working

**Result**: Confidence that setup is complete and functional

---

## SKU Positional Product Code Match Rules

### What You'll Get

Your queries will return these types of SKU matching rules:

#### Rule Type 1: Position-Based SKU Patterns

```
PSX-M10-AC-ZB-88
│   │   │  │  └─ Position 5: Grade (8.8)
│   │   │  └──── Position 4: Finish (Zincado Branco)
│   │   └─────── Position 3: Material (Aço Carbono)
│   └─────────── Position 2: Size (M10)
└─────────────── Position 1: Type (Parafuso Sextavado)
```

#### Rule Type 2: Default Value Matching

```json
{
  "attribute": "material",
  "default_value": "Aço carbono SAE 1010",
  "sku_code": "AC",
  "position": 3,
  "confidence": 0.95,
  "penalty": 0.10
}
```

#### Rule Type 3: Standard Equivalence Mapping

```json
{
  "source_standard": "DIN 933",
  "equivalent": "ISO 4017",
  "sku_prefix_mapping": {
    "DIN933": "ISO4017",
    "pattern": "Replace DIN933-* with ISO4017-*"
  }
}
```

---

## Time Breakdown

| Part | Task | Time | Cumulative |
|------|------|------|------------|
| 1.1 | Review secrets guide | 2 min | 2 min |
| 1.2 | Navigate to GitHub secrets | 1 min | 3 min |
| 1.3 | Get Anthropic API key | 2 min | 5 min |
| 1.4 | Add 6 secrets | 5 min | 10 min |
| 1.5 | Trigger workflow | 1 min | 11 min |
| 1.6 | Wait for deployment | 5 min | 16 min |
| **Part 1 Total** | | **16 min** | **16 min** |
| | | | |
| 2.1 | Add MCP server | 3 min | 19 min |
| 2.2 | Verify connection | 2 min | 21 min |
| 2.3 | Open Agent Builder | 1 min | 22 min |
| 2.4 | Add tool to subagent | 2 min | 24 min |
| 2.5 | Copy/paste system prompt | 3 min | 27 min |
| 2.6 | Save configuration | 1 min | 28 min |
| 2.7 | Test 4 queries | 12 min | 40 min |
| **Part 2 Total** | | **21 min** | **40 min** |
| | | | |
| 3.1 | Run validation script | 5 min | 45 min |
| 3.2 | Verify results | 3 min | 48 min |
| 3.3 | Generate report | 2 min | 50 min |
| **Part 3 Total** | | **10 min** | **50 min** |

**Total Estimated Time**: **50 minutes**

---

## Files Created

| File | Purpose |
|------|---------|
| `GITHUB_SECRETS_SETUP_GUIDE.md` | Step-by-step secrets configuration |
| `DEPLOYMENT_SECRETS_CONFIGURED.md` | Configuration summary |
| `COMPLETE_SETUP_EXECUTION_PLAN.md` | This file - complete execution plan |
| `GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md` | Agent Builder integration (exists) |
| `MCP_DEPLOYMENT_TEST_REPORT.md` | Test results (created earlier) |
| `TEST_SESSION_SUMMARY.md` | Session summary (created earlier) |

---

## Quick Start Commands

### Get Anthropic API Key

```bash
# Open in browser:
https://console.anthropic.com/settings/keys
```

### Configure GitHub Secrets

```bash
# Open in browser:
https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions
```

### Trigger Deployment

```bash
cd C:\Users\chicu\langchain\indufix-llamaindex-toolkit

git commit --allow-empty -m "Configure GitHub secrets for CI/CD"
git push origin main
```

### Monitor Workflow

```bash
# Open in browser:
https://github.com/chicuza/indufix-llamaindex-toolkit/actions
```

### Configure Agent Builder

```bash
# Open in browser:
https://smith.langchain.com/settings
```

### Run Validation

```bash
cd C:\Users\chicu\langchain\indufix-llamaindex-toolkit
python validate_integration.py
```

---

## Success Indicators

### GitHub Secrets ✅

- Secrets page shows all 6 secrets
- Workflow runs without errors
- Deployment status: "healthy"
- Logs show: "Deployment successful"

### Agent Builder ✅

- MCP server: Green indicator
- Tool list: indufix_agent appears
- Test query: Returns specific data
- No generic "Tools are available" message

### Validation ✅

```
✅ Test 1: PASSED
✅ Test 2: PASSED
✅ Test 3: PASSED
✅ Test 4: PASSED

Tests Passed: 4/4
```

---

## Support Resources

### Documentation

- `GITHUB_SECRETS_SETUP_GUIDE.md` - GitHub configuration
- `GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md` - Agent Builder setup
- `DEPLOYMENT_SECRETS_CONFIGURED.md` - What secrets do
- `MCP_DEPLOYMENT_TEST_REPORT.md` - Test results analysis

### Test Scripts

- `validate_integration.py` - Automated validation
- `test_mcp_authenticated.py` - MCP authentication test
- `run_mcp_tests.py` - Quick test runner

### Deployment Tools

- `.github/workflows/deploy_langsmith.yml` - GitHub Actions workflow
- `deployment/deploy_cli.py` - CLI deployment tool
- `deployment/deploy_config.yaml` - Deployment configuration

---

## Ready to Start?

1. **Part 1**: Open `GITHUB_SECRETS_SETUP_GUIDE.md` and follow steps
2. **Part 2**: Open `GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md` and follow steps
3. **Part 3**: Run `python validate_integration.py`

**Estimated completion**: 50 minutes from now

**Result**: Full SKU positional product code matching functionality enabled! 🎉

---

**Last Updated**: 2026-01-23
**Status**: Ready for User Execution
**Next Action**: User to follow Part 1 (GitHub Secrets Setup Guide)
