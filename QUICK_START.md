# Quick Start Guide - Fixed Indufix Agent

## What Was Fixed

The agent.py now has **real LLM integration** with Claude Sonnet 4.5. It can actually call tools and process queries (instead of returning "Tools are available...").

## Prerequisites

```bash
# 1. Install dependencies
pip install -e .

# 2. Set environment variables
export ANTHROPIC_API_KEY=sk-ant-...
export LLAMA_CLOUD_API_KEY=llx-...

# Windows:
set ANTHROPIC_API_KEY=sk-ant-...
set LLAMA_CLOUD_API_KEY=llx-...
```

## Test It Works

```bash
# Run the test suite
python test_agent_local.py
```

**Expected Output**:
```
[PASS]   - Basic Import
[PASS]   - Agent Invocation
[PASS]   - Convenience Function
[PASS]   - Tool Availability

Results: 4 passed, 0 skipped, 0 failed
```

## Usage

### Python API

```python
from agent import run_agent

# Ask a question
response = await run_agent("What are default values for hex bolt M10?")
print(response)
```

### Test Example Queries

```python
import asyncio
from agent import run_agent

async def test():
    # Query 1: Default values
    response = await run_agent(
        "What are the default values for a hex bolt M10 if material is missing?"
    )
    print("Query 1:", response, "\n")

    # Query 2: Standard equivalence
    response = await run_agent(
        "What is the ISO equivalent of DIN 933?"
    )
    print("Query 2:", response, "\n")

    # Query 3: Confidence penalty
    response = await run_agent(
        "What confidence penalty should I use for inferring material as carbon steel?"
    )
    print("Query 3:", response)

asyncio.run(test())
```

## Deploy to LangSmith

```bash
# Deploy the agent
langsmith deploy agent.py:graph --name indufix-agent

# The graph object is production-ready with:
# - Claude Sonnet 4.5 integration
# - All 6 tools bound
# - Proper ReAct pattern
# - System message configured
```

## Verify Tools Are Accessible

```python
from indufix_toolkit import TOOLS

# Should show 6 tools
for tool in TOOLS:
    print(f"- {tool.name}: {tool.description[:50]}...")
```

**Expected**:
```
- retrieve_matching_rules: Recupera regras de matching da base Indufix via...
- query_indufix_knowledge: Consulta a base de conhecimento Indufix com res...
- get_default_values: Busca valores default para atributos ausentes de...
- get_standard_equivalences: Busca equivalências entre normas/padrões técn...
- get_confidence_penalty: Obtém penalidade de confiança para valor infer...
- pipeline_retrieve_raw: Chamada direta ao pipeline endpoint (fallback/d...
```

## Architecture

```
User Query
    |
    v
[Claude Sonnet 4.5 + System Message]
    |
    v
Decides: Call Tool or Respond?
    |
    +---> [Tool Execution] ---> [Synthesize Response]
    |
    +---> [Direct Response]
```

## Key Features

1. **Real LLM**: Claude Sonnet 4.5 (not a placeholder)
2. **Tool Calling**: Actually invokes the 6 Indufix tools
3. **ReAct Pattern**: Reasoning + Acting cycle
4. **System Prompt**: Domain-specific guidance
5. **Lazy Loading**: Graceful handling of missing API keys
6. **Async Ready**: Full async/await support

## Troubleshooting

### "No module named 'langchain_anthropic'"
```bash
pip install langchain-anthropic
```

### "API key validation error"
```bash
# Set the environment variable
export ANTHROPIC_API_KEY=sk-ant-...
```

### "Cannot import agent"
```bash
# Reinstall the package
pip install -e .
```

## Example Output

**Query**: "What are default values for hex bolt M10?"

**Agent Behavior**:
1. Receives query with system message
2. Claude decides to call `get_default_values` tool
3. Tool executes and returns data
4. Claude synthesizes response with confidence scores
5. Returns formatted answer to user

**Sample Response**:
```
Based on the Indufix knowledge base, for a hex bolt M10:

Default Material: Carbon Steel (Grade 8.8)
- Confidence: 0.92
- Penalty: 0.10 (default inference)

Default Finish: Zinc Plated
- Confidence: 0.88
- Penalty: 0.12 (default inference)

These values are commonly used when the specifications are not
explicitly provided. The confidence penalties reflect that these
are inferred defaults rather than explicitly specified attributes.
```

## Files Reference

- **`agent.py`**: Main agent implementation (183 lines)
- **`AGENT_IMPLEMENTATION.md`**: Detailed technical documentation
- **`AGENT_FIX_SUMMARY.md`**: Complete fix summary
- **`test_agent_local.py`**: Test suite
- **`pyproject.toml`**: Dependencies (includes langchain-anthropic)

## What's Different From Before

| Aspect | Before | After |
|--------|--------|-------|
| Can call tools? | No | Yes |
| Has real LLM? | No | Yes (Claude Sonnet 4.5) |
| Returns dynamic responses? | No | Yes |
| Production ready? | No | Yes |

## Next Steps

1. **Test locally**: `python test_agent_local.py`
2. **Try example queries**: See "Usage" section above
3. **Deploy**: `langsmith deploy agent.py:graph`
4. **Integrate**: Add to Agent Builder workspace

## Support

For detailed documentation:
- **Technical Details**: `AGENT_IMPLEMENTATION.md`
- **Fix Summary**: `AGENT_FIX_SUMMARY.md`
- **Main README**: `README.md`

---

**Status**: Production Ready
**Last Updated**: 2026-01-22
**Verified**: Test suite passing
