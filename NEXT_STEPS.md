# Next Steps - Immediate Actions

**Status**: All automated work complete ✅
**Ready for**: UI Configuration

---

## Option 1: Manual UI Configuration (Recommended First)

### Time Required: 15-20 minutes

Follow these steps in Agent Builder:

### Step 1: Add MCP Server (5 min)

1. Go to: https://smith.langchain.com/settings
2. Click: Workspace -> MCP Servers
3. Click: Add Remote Server
4. Enter Basic Settings:
   - **Name**: indufix-llamaindex-toolkit
   - **URL**: https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/mcp

5. **IMPORTANT**: Add Authentication Headers (fixes "Failed to load tools" error)

   **Option 1 (Minimum Required)**:
   - Header Name: X-Api-Key
   - Header Value: <YOUR_LANGSMITH_API_KEY>

   **Option 2 (Recommended)**:
   - Header 1: Name: X-Api-Key, Value: <YOUR_LANGSMITH_API_KEY>
   - Header 2: Name: X-Tenant-Id, Value: 950d802b-125a-45bc-88e4-3d7d0edee182

6. Save and verify:
   - Green/active indicator appears
   - No "Failed to load tools" error
   - indufix_agent tool is listed

### Step 2: Configure LlamaIndex_Rule_Retriever (10 min)

1. Go to: https://smith.langchain.com/o/950d802b-125a-45bc-88e4-3d7d0edee182/agents/editor?agentId=1bf73a52-638f-4c42-8fc7-d6d07405c4fe

2. Find: LlamaIndex_Rule_Retriever subagent

3. Add Tool:
   - Click: Add Tool
   - Select: indufix_agent
   - Save

4. Update System Prompt:
   - Open prompt editor
   - Add the following:

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

5. Save configuration

### Step 3: Test (5 min)

1. Open agent chat interface

2. Test queries:
   ```
   "Busque regras para parafuso M10"
   "Valores default para parafuso sextavado"
   "Equivalência entre DIN 933 e ISO 4017"
   ```

3. Verify:
   - Subagent is invoked
   - Tool is called
   - Responses are relevant
   - No errors

---

## Option 2: Commit Changes to Git

If you want to save all the work to the repository first:

```bash
cd indufix-llamaindex-toolkit

git add .

git commit -m "Add LlamaIndex_Rule_Retriever subagent integration

- Add test script: test_llamaindex_rule_retriever.py
- Add comprehensive guide: LLAMAINDEX_RULE_RETRIEVER_INTEGRATION.md
- Add quick config: SUBAGENT_QUICK_CONFIG.md
- Update INTEGRATION_SUMMARY.md with subagent info
- All automated tests passing (2/2)

Ready for UI configuration in Agent Builder.

🤖 Generated with Claude Code (https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

---

## Option 3: Create Additional Test Scenarios

If you want more comprehensive testing:

1. Test with edge cases
2. Test with Portuguese vs English queries
3. Test with invalid/nonsensical queries
4. Load testing (multiple concurrent requests)
5. Test all 6 internal tools explicitly

---

## What's Already Done ✅

1. ✅ MCP server deployed and operational
2. ✅ Tool accessible via MCP protocol
3. ✅ Direct tool invocation tested (3 query types)
4. ✅ Test script created and passing (2/2 tests)
5. ✅ Comprehensive integration guide (300+ lines)
6. ✅ Quick configuration guide with checklist
7. ✅ Integration summary updated
8. ✅ System prompt template ready
9. ✅ Test queries documented
10. ✅ Troubleshooting guide included

---

## What You Should Do Now

**Recommended Order**:

1. **First**: Complete UI configuration (Option 1) - 15-20 minutes
   - This makes the tool functional for your users
   - Can be tested immediately

2. **Then**: Commit changes to Git (Option 2) - 2 minutes
   - Preserves all documentation and tests
   - Enables collaboration

3. **Finally**: Monitor and iterate
   - Review traces in LangSmith
   - Gather user feedback
   - Refine prompts as needed

---

## Support During Configuration

If you encounter issues during UI configuration:

**Tool not appearing**:
- Refresh the page
- Verify MCP server shows as active
- Check browser console for errors

**Subagent not using tool**:
- Verify tool is saved in subagent config
- Check system prompt was saved
- Try more explicit queries

**Empty responses**:
- Check LlamaCloud index has content
- Verify LLAMA_CLOUD_API_KEY in deployment secrets
- Review deployment logs

---

## Quick Reference

- **Agent Editor**: https://smith.langchain.com/o/950d802b-125a-45bc-88e4-3d7d0edee182/agents/editor?agentId=1bf73a52-638f-4c42-8fc7-d6d07405c4fe
- **Settings**: https://smith.langchain.com/settings
- **Deployments**: https://smith.langchain.com/deployments
- **MCP URL**: https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/mcp

---

**Status**: ✅ Ready for your action
**Blocking on**: UI configuration (manual step)
**Estimated time**: 15-20 minutes total
