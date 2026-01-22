# Quick Configuration: LlamaIndex_Rule_Retriever + indufix_agent

**Time Required**: 15-20 minutes
**Status**: All tests passed ✅ Ready for UI configuration

---

## Checklist

### Pre-Configuration ✅

- [x] MCP server deployed and operational
- [x] Tool available via MCP (indufix_agent)
- [x] Direct tool invocation tested and working
- [x] Test scripts created and passed

### UI Configuration (To Do)

- [ ] **Step 1**: Add MCP Server to Workspace
  - [ ] Go to: Settings -> Workspace -> MCP Servers
  - [ ] Click: Add Remote Server
  - [ ] Name: `indufix-llamaindex-toolkit`
  - [ ] URL: `https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/mcp`
  - [ ] **IMPORTANT**: Add authentication headers (REQUIRED to fix "Failed to load tools" error):
    - [ ] Header 1: Name: `X-Api-Key`, Value: `<YOUR_LANGSMITH_API_KEY>`
    - [ ] Header 2 (optional): Name: `X-Tenant-Id`, Value: `950d802b-125a-45bc-88e4-3d7d0edee182`
  - [ ] Save and verify green/active status
  - [ ] Verify no "Failed to load tools" error appears

- [ ] **Step 2**: Open Agent Editor
  - [ ] Navigate to: https://smith.langchain.com/o/950d802b-125a-45bc-88e4-3d7d0edee182/agents/editor?agentId=1bf73a52-638f-4c42-8fc7-d6d07405c4fe
  - [ ] Locate: LlamaIndex_Rule_Retriever subagent

- [ ] **Step 3**: Add Tool to Subagent
  - [ ] Open LlamaIndex_Rule_Retriever configuration
  - [ ] Go to: Tools section
  - [ ] Add: indufix_agent
  - [ ] Save configuration

- [ ] **Step 4**: Update System Prompt
  - [ ] Add the prompt from "System Prompt Addition" section below
  - [ ] Save configuration

### Testing (To Do)

- [ ] **Test 1**: Basic rule retrieval
  - Query: "Busque regras para parafuso M10"
  - Expected: Subagent retrieves M10 rules

- [ ] **Test 2**: Default values
  - Query: "Valores default para parafuso sextavado"
  - Expected: Returns default values for hex bolts

- [ ] **Test 3**: Standard equivalence
  - Query: "Equivalência entre DIN 933 e ISO 4017"
  - Expected: Returns equivalence information

- [ ] **Test 4**: Verify in traces
  - [ ] Check LangSmith traces
  - [ ] Confirm subagent was invoked
  - [ ] Confirm tool was called
  - [ ] Review response quality

---

## System Prompt Addition

Copy and paste this into the LlamaIndex_Rule_Retriever system prompt:

```
You are the LlamaIndex Rule Retriever subagent, specialized in retrieving
rules and technical information from the Forjador Indufix knowledge base.

You now have access to the indufix_agent tool which provides 6 specialized
capabilities:

1. **retrieve_matching_rules** - Vector similarity search for matching rules
2. **query_indufix_knowledge** - Query engine with response synthesis
3. **get_default_values** - Default values for missing attributes
4. **get_standard_equivalences** - Standard equivalences (DIN/ISO/ASTM)
5. **get_confidence_penalty** - Confidence penalties for inferred values
6. **pipeline_retrieve_raw** - Direct pipeline access (debug)

Use the indufix_agent tool when you need to:
- Retrieve rules from the Forjador Indufix knowledge base
- Query product specifications for fasteners (bolts, screws, nuts, washers)
- Get default values for missing product attributes
- Find equivalences between technical standards
- Calculate confidence scores for SKU matching
- Access any information from the Indufix knowledge base

The tool connects to LlamaCloud and queries the Forjador Indufix pipeline.
Always cite the knowledge base as the source when returning information.
```

---

## Quick Test Commands

After configuration, run these tests:

### Via Agent Chat UI:
```
Busque regras para parafuso M10
```

### Via Test Script:
```bash
cd indufix-llamaindex-toolkit
python test_llamaindex_rule_retriever.py
```

---

## Expected Flow

```
User Query
  ↓
Main Agent (decides to use subagent)
  ↓
LlamaIndex_Rule_Retriever (subagent invoked)
  ↓
indufix_agent tool (MCP call)
  ↓
Internal routing to appropriate LlamaIndex tool
  ↓
LlamaCloud API query
  ↓
Forjador Indufix knowledge base
  ↓
Results returned through chain
```

---

## Troubleshooting Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| MCP server not showing | Verify URL and save again |
| Tool not in list | Refresh page, check MCP server is active |
| Subagent not using tool | Enhance system prompt, test with explicit queries |
| Empty responses | Check LlamaCloud index has content |
| Timeout errors | Check deployment status, API keys |

---

## Resources

- **Full Guide**: LLAMAINDEX_RULE_RETRIEVER_INTEGRATION.md
- **Test Script**: test_llamaindex_rule_retriever.py
- **MCP Tests**: test_mcp_connection.py
- **Agent Guide**: AGENT_INTEGRATION_FINDINGS.md

---

## Success Criteria

✅ Configuration complete when:
- [ ] MCP server shows green/active in workspace
- [ ] indufix_agent appears in subagent's tool list
- [ ] Test queries return relevant results
- [ ] Traces show subagent → tool → LlamaCloud flow
- [ ] No errors in execution logs

---

**Quick Start Time**: ~15-20 minutes
**Status**: Ready to configure
**Test Results**: 2/2 passed ✅
