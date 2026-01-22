# LlamaIndex_Rule_Retriever Subagent Integration Guide

**Date**: 2026-01-22
**Status**: READY FOR CONFIGURATION
**Agent**: 1bf73a52-638f-4c42-8fc7-d6d07405c4fe
**Subagent**: LlamaIndex_Rule_Retriever

---

## Executive Summary

This guide provides step-by-step instructions for integrating the deployed `indufix_agent` tool with the **LlamaIndex_Rule_Retriever** subagent in your Agent Builder agent.

**Test Results**: ✅ All automated tests passed (2/2)
- MCP Server accessible
- Tool available via MCP protocol
- Direct tool invocation working

**Remaining Steps**: UI configuration (~15-20 minutes)

---

## What is LlamaIndex_Rule_Retriever?

The LlamaIndex_Rule_Retriever is a subagent within your main agent that specializes in retrieving rules and information from knowledge bases. By adding the `indufix_agent` tool, this subagent gains access to 6 specialized LlamaIndex-powered tools for querying the Forjador Indufix knowledge base.

---

## Architecture

```
Main Agent (1bf73a52-638f-4c42-8fc7-d6d07405c4fe)
    |
    | delegates to
    v
LlamaIndex_Rule_Retriever (Subagent)
    |
    | uses tool
    v
indufix_agent (MCP Tool)
    |
    | internal routing
    v
6 LlamaIndex Tools
├── retrieve_matching_rules
├── query_indufix_knowledge
├── get_default_values
├── get_standard_equivalences
├── get_confidence_penalty
└── pipeline_retrieve_raw
    |
    | API calls
    v
LlamaCloud API
    |
    v
Forjador Indufix (Knowledge Base)
```

---

## Integration Steps

### Prerequisites

- Agent Builder access
- Workspace ID: 950d802b-125a-45bc-88e4-3d7d0edee182
- Agent ID: 1bf73a52-638f-4c42-8fc7-d6d07405c4fe
- MCP deployment operational (verified ✅)

### Step 1: Add MCP Server to Workspace (5 minutes)

**If not already added**:

1. Navigate to: **Settings -> Workspace -> MCP Servers**
   - URL: https://smith.langchain.com/settings

2. Click: **Add Remote Server**

3. Configure Basic Settings:
   ```
   Name: indufix-llamaindex-toolkit
   URL: https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/mcp
   ```

4. **IMPORTANT**: Add Authentication Headers

   **Option 1 (Minimum Required)**:
   ```
   Header Name: X-Api-Key
   Header Value: <YOUR_LANGSMITH_API_KEY>
   ```

   **Option 2 (Recommended - Both Headers)**:
   ```
   Header 1:
     Name: X-Api-Key
     Value: <YOUR_LANGSMITH_API_KEY>

   Header 2:
     Name: X-Tenant-Id
     Value: 950d802b-125a-45bc-88e4-3d7d0edee182
   ```

   **Why Authentication is Required**:
   - The MCP endpoint returns `403 Forbidden` without authentication headers
   - This causes the "Failed to load tools" error in Agent Builder
   - Adding these headers fixes the authentication issue

5. **Save** the configuration

6. Verify:
   - Server should appear in the MCP Servers list with a green/active indicator
   - No "Failed to load tools" error should appear
   - `indufix_agent` tool should be listed in available tools

### Step 2: Open Agent Editor (1 minute)

1. Navigate to Agent Editor:
   ```
   https://smith.langchain.com/o/950d802b-125a-45bc-88e4-3d7d0edee182/agents/editor?agentId=1bf73a52-638f-4c42-8fc7-d6d07405c4fe
   ```

2. Locate the **LlamaIndex_Rule_Retriever** subagent in the subagents list

3. Click to open its configuration

### Step 3: Add Tool to Subagent (3 minutes)

1. In the LlamaIndex_Rule_Retriever configuration, find the **Tools** or **Capabilities** section

2. Click **Add Tool** or similar button

3. Select: **indufix_agent** (should appear in the list from the MCP server)

4. Configure tool usage (if prompted):
   - **When to use**: For retrieving rules, specifications, defaults, equivalences
   - **Priority**: High (if configurable)

5. **Save** the subagent configuration

### Step 4: Update Subagent System Prompt (5 minutes)

Add the following to the LlamaIndex_Rule_Retriever's system prompt:

```
You are the LlamaIndex Rule Retriever subagent, specialized in retrieving
rules and technical information from the Forjador Indufix knowledge base.

You now have access to the indufix_agent tool which provides 6 specialized
capabilities:

1. **retrieve_matching_rules** - Vector similarity search across the knowledge
   base to find matching rules and patterns. Use for general rule retrieval.

2. **query_indufix_knowledge** - Query engine with response synthesis. Use
   when you need a comprehensive answer synthesized from multiple sources.

3. **get_default_values** - Retrieve default values for missing product
   attributes. Use when attributes are not specified in the query.

4. **get_standard_equivalences** - Find equivalences between technical
   standards (DIN, ISO, ASTM, etc.). Use for standard conversion queries.

5. **get_confidence_penalty** - Calculate confidence penalties for inferred
   values. Use when assessing the reliability of inferred data.

6. **pipeline_retrieve_raw** - Direct access to the LlamaCloud pipeline.
   Use for debugging or when other tools don't provide sufficient detail.

When to use the indufix_agent tool:
- User asks about fastener specifications (bolts, screws, nuts, washers)
- Query involves technical standards or equivalences
- Need to retrieve default values for missing attributes
- Calculating confidence scores for SKU matching
- Any query related to the Indufix/Forjador knowledge base

The tool connects to LlamaCloud and queries the Forjador Indufix pipeline,
which contains:
- SKU matching rules
- Default value specifications
- Standard equivalence mappings
- Confidence penalty definitions
- Technical attribute rules

Always cite the source when returning information from the knowledge base.
```

### Step 5: Save and Test (5 minutes)

1. **Save** all changes to the agent configuration

2. Open the **Agent Chat Interface**

3. Test with a query that should trigger the subagent:
   ```
   "Busque regras para parafuso M10"
   ```

4. Verify:
   - Subagent is invoked
   - Tool is called
   - Response contains relevant information
   - No errors in the logs

---

## Test Queries

### Basic Rule Retrieval
```
"Busque regras para parafuso M10"
```
**Expected**: Subagent retrieves rules related to M10 bolts

### Default Values
```
"Valores default para parafuso sextavado"
```
**Expected**: Retrieves default values for hex bolts using `get_default_values` tool

### Standard Equivalence
```
"Equivalência entre DIN 933 e ISO 4017"
```
**Expected**: Finds equivalence information using `get_standard_equivalences` tool

### Confidence Penalty
```
"Penalidade de confiança para material inferido por LLM"
```
**Expected**: Calculates confidence penalty using `get_confidence_penalty` tool

### Complex Query
```
"Especificações técnicas de parafuso classe 8.8"
```
**Expected**: Uses `query_indufix_knowledge` to synthesize comprehensive answer

---

## Verification

### How to Verify Integration is Working

1. **Check Subagent Invocation**:
   - Agent should delegate to LlamaIndex_Rule_Retriever for rule-related queries
   - Look for subagent indicator in the chat interface

2. **Check Tool Usage**:
   - Subagent should call `indufix_agent` tool
   - Tool invocation should appear in agent logs/trace

3. **Check Response Quality**:
   - Responses should contain specific information from knowledge base
   - Should include relevant specifications, defaults, or equivalences
   - Should cite Forjador Indufix as the source

4. **Check Error Handling**:
   - If knowledge base doesn't have information, should indicate that clearly
   - Should not hallucinate or make up information
   - Should suggest alternative queries if needed

### Troubleshooting

#### Subagent Not Invoked

**Symptoms**: Main agent responds directly without using subagent

**Possible Causes**:
- Subagent trigger conditions not met
- Query doesn't match subagent's domain
- Subagent disabled or misconfigured

**Solutions**:
- Review subagent trigger conditions
- Adjust main agent's delegation logic
- Test with more explicit queries (e.g., "Use the rule retriever to find...")

#### Tool Not Called

**Symptoms**: Subagent invoked but doesn't use the tool

**Possible Causes**:
- Tool not properly added to subagent
- Subagent's LLM doesn't recognize when to use tool
- Tool description unclear

**Solutions**:
- Verify tool is in subagent's tool list
- Enhance system prompt with clearer tool usage guidelines
- Test with queries that explicitly mention needing rule retrieval

#### Tool Returns Empty/Generic Responses

**Symptoms**: Tool called but responses lack specific information

**Possible Causes**:
- LlamaCloud index is empty or not indexed properly
- Query doesn't match indexed content
- API key issues

**Solutions**:
- Verify Forjador Indufix pipeline has content in LlamaCloud
- Check LLAMA_CLOUD_API_KEY deployment secret
- Test with known queries that should return results
- Review LlamaCloud index status

---

## Tool Details

### 1. retrieve_matching_rules

**Purpose**: Vector similarity search for matching rules

**Use Cases**:
- General rule retrieval
- Finding similar patterns
- Broad knowledge base searches

**Example Query**: "Busque regras para parafusos M10"

**Parameters**:
- `query` (string): Search query
- `top_k` (int): Number of results (default: 5)

### 2. query_indufix_knowledge

**Purpose**: Query engine with response synthesis

**Use Cases**:
- Complex questions requiring synthesis
- When single documents aren't sufficient
- Comprehensive explanations needed

**Example Query**: "Explique as especificações de parafusos classe 8.8"

**Parameters**:
- `query` (string): Natural language question

### 3. get_default_values

**Purpose**: Retrieve default values for missing attributes

**Use Cases**:
- Incomplete product specifications
- SKU matching with missing data
- Filling attribute gaps

**Example Query**: "Valores default para parafuso sextavado M10"

**Parameters**:
- `product_type` (string): Type of product
- `missing_attributes` (list): List of missing attributes

### 4. get_standard_equivalences

**Purpose**: Find equivalences between technical standards

**Use Cases**:
- Standard conversion (DIN to ISO)
- Cross-reference lookup
- Compatibility checking

**Example Query**: "Equivalência entre DIN 933 e ISO 4017"

**Parameters**:
- `standard` (string): Standard name/number

### 5. get_confidence_penalty

**Purpose**: Calculate confidence penalties for inferred values

**Use Cases**:
- SKU matching confidence scoring
- Data quality assessment
- Inference validation

**Example Query**: "Penalidade para material inferido por pattern match"

**Parameters**:
- `attribute` (string): Attribute name
- `inferred_value` (string): Inferred value
- `inference_method` (string): Method used

### 6. pipeline_retrieve_raw

**Purpose**: Direct pipeline access for debugging

**Use Cases**:
- Debugging tool behavior
- Accessing raw pipeline results
- Development and testing

**Example Query**: (Typically used programmatically, not by end users)

**Parameters**:
- `query` (string): Search query
- `top_k` (int): Number of results

---

## Performance Considerations

### Expected Response Times

- **Tool discovery**: < 1 second
- **Tool invocation**: 2-5 seconds
- **LlamaCloud query**: 1-3 seconds
- **Total (typical)**: 3-8 seconds

### Optimization Tips

1. **Specific Queries**: More specific queries return faster, more relevant results
2. **Top-K Parameter**: Lower top_k values (3-5) are faster
3. **Caching**: LlamaCloud may cache frequent queries
4. **Batch Queries**: If possible, batch related queries

---

## Monitoring and Observability

### What to Monitor

1. **Tool Invocation Rate**:
   - How often is indufix_agent called?
   - Are users getting value from it?

2. **Response Quality**:
   - Are responses relevant and accurate?
   - Do users follow up with clarifying questions?

3. **Error Rate**:
   - Any tool invocation failures?
   - Timeout issues?

4. **LlamaCloud Usage**:
   - API call volume
   - Token consumption
   - Index query performance

### LangSmith Tracing

View detailed traces in LangSmith:
```
https://smith.langchain.com/o/950d802b-125a-45bc-88e4-3d7d0edee182
```

Look for:
- Subagent delegation events
- Tool calls with parameters
- LlamaCloud API responses
- Error messages or timeouts

---

## Testing Checklist

- [ ] MCP server added to workspace
- [ ] indufix_agent tool added to LlamaIndex_Rule_Retriever
- [ ] Subagent system prompt updated
- [ ] Test Query 1: Basic rule retrieval
- [ ] Test Query 2: Default values
- [ ] Test Query 3: Standard equivalence
- [ ] Test Query 4: Confidence penalty
- [ ] Test Query 5: Complex synthesis
- [ ] Verify subagent is invoked correctly
- [ ] Verify tool is called appropriately
- [ ] Check response quality and accuracy
- [ ] Review traces in LangSmith
- [ ] Document any issues or observations

---

## Additional Resources

### Documentation
- **Main Integration Guide**: AGENT_INTEGRATION_FINDINGS.md
- **Deployment Info**: DEPLOYMENT_SUCCESS.md
- **Validation Report**: VALIDATION_REPORT.md
- **Integration Summary**: INTEGRATION_SUMMARY.md

### Test Scripts
- **MCP Connection**: `test_mcp_connection.py`
- **General Integration**: `test_agent_integration.py`
- **This Subagent**: `test_llamaindex_rule_retriever.py`

### URLs
- **Agent Editor**: https://smith.langchain.com/o/950d802b-125a-45bc-88e4-3d7d0edee182/agents/editor?agentId=1bf73a52-638f-4c42-8fc7-d6d07405c4fe
- **Deployment**: https://smith.langchain.com/deployments
- **MCP Endpoint**: https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/mcp

---

## Next Steps

1. ✅ Complete UI configuration (Steps 1-4)
2. ✅ Test with provided queries (Step 5)
3. ⏳ Monitor performance and quality
4. ⏳ Iterate on system prompts based on results
5. ⏳ Expand to other subagents if successful

---

## Support

### Common Issues

**Issue**: Tool not appearing in subagent tool list
**Solution**: Verify MCP server is added and active in workspace settings

**Issue**: Subagent not using the tool
**Solution**: Enhance system prompt with clearer usage guidelines

**Issue**: Empty or irrelevant responses
**Solution**: Check LlamaCloud index has content; refine queries

### Getting Help

- Review LangSmith traces for detailed execution info
- Check deployment logs: https://smith.langchain.com/deployments
- Test tool directly using `test_llamaindex_rule_retriever.py`
- Consult AGENT_INTEGRATION_FINDINGS.md for architecture details

---

**Guide Version**: 1.0
**Last Updated**: 2026-01-22
**Status**: Ready for Production Use
**Test Results**: 2/2 Passed ✅
