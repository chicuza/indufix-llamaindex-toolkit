# Indufix Agent Implementation Guide

## Overview

The agent.py file now implements a production-ready LangGraph ReAct agent with proper Claude Sonnet 4.5 integration for the Indufix toolkit.

## What Was Fixed

### Before (Broken)
- No LLM integration - just a placeholder
- Tools defined but never callable
- Static response - couldn't process queries
- No system message or guidance

### After (Production-Ready)
- Full Claude Sonnet 4.5 integration
- Tools properly bound to LLM
- Real ReAct agent pattern
- Comprehensive system message
- Async support
- Error handling ready

## Architecture

### Components

1. **LLM Integration**
   - Model: `claude-sonnet-4-5-20250929`
   - Temperature: 0.0 (deterministic for technical queries)
   - Max tokens: 4096
   - Tools bound via `.bind_tools(TOOLS)`

2. **State Graph**
   - Uses `MessagesState` from LangGraph
   - Two nodes: `agent` (LLM) and `tools` (tool execution)
   - Conditional routing based on tool calls

3. **System Message**
   - Guides agent behavior for Indufix domain
   - Explains available tools and their purpose
   - Sets expectations for precision and confidence reporting

## Usage

### Basic Usage

```python
from langchain_core.messages import HumanMessage
from agent import graph

# Invoke the agent
result = await graph.ainvoke({
    "messages": [HumanMessage(content="What are default values for hex bolt M10?")]
})

# Get the response
response = result["messages"][-1].content
print(response)
```

### Using the Convenience Function

```python
from agent import run_agent

# Simple query interface
response = await run_agent("What are default values for hex bolt M10?")
print(response)
```

### Test the Agent

```bash
# Run the example in agent.py
cd C:\Users\chicu\langchain\indufix-llamaindex-toolkit
python -m agent
```

## Environment Setup

### Required Environment Variables

```bash
# Anthropic API key for Claude
ANTHROPIC_API_KEY=sk-ant-...

# LlamaCloud API key (for tools)
LLAMA_CLOUD_API_KEY=...
```

### Install Dependencies

```bash
pip install -e .
```

## Available Tools

The agent has access to 6 tools from the Indufix toolkit:

1. **retrieve_matching_rules** - Retrieve matching rules from Indufix knowledge base
2. **query_indufix_knowledge** - Query with synthesized response
3. **get_default_values** - Get default values for missing attributes
4. **get_standard_equivalences** - Find standard equivalences (DIN/ISO/ASTM)
5. **get_confidence_penalty** - Calculate confidence penalties
6. **pipeline_retrieve_raw** - Direct pipeline endpoint access

## Agent Flow

```
START
  |
  v
[Agent Node]
  |
  | (LLM decides: use tools or respond)
  |
  v
[Conditional Edge]
  |
  +----> [Tools Node] ---+
  |                      |
  |                      v
  +----> [END]     (back to Agent)
```

### Execution Steps

1. User provides query
2. Agent node invokes Claude with system message + user query
3. Claude decides whether to call tools or respond directly
4. If tools needed:
   - Tools node executes the tool calls
   - Results return to agent node
   - Claude synthesizes final response
5. Final response returned to user

## Key Implementation Details

### System Message

The system message guides Claude to:
- Understand it's working with the Indufix SKU Matcher
- Know what data is available in the knowledge base
- Use tools appropriately for different query types
- Report confidence scores accurately
- Communicate uncertainty clearly

### ReAct Pattern

The agent follows the ReAct (Reasoning + Acting) pattern:
1. **Reason**: Claude analyzes the query
2. **Act**: Calls appropriate tools if needed
3. **Observe**: Reviews tool results
4. **Synthesize**: Provides final answer

### Async Support

All operations are async-ready:
- `ainvoke()` for single queries
- Can integrate with streaming via `astream()`
- Compatible with FastAPI async endpoints

## Integration with LangSmith

The agent is ready for LangSmith deployment:

1. The `graph` object is the compiled agent
2. Can be served via LangSmith Tool Server
3. Traces will show:
   - LLM calls
   - Tool invocations
   - Decision points
   - Full conversation history

## Error Handling

The current implementation includes:
- Tool execution errors handled by ToolNode
- LLM errors propagate for visibility
- Can be extended with retry logic

### Adding Retry Logic (Optional)

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_model(state: MessagesState) -> dict:
    # ... existing code ...
```

## Testing Checklist

- [ ] Environment variables set (ANTHROPIC_API_KEY, LLAMA_CLOUD_API_KEY)
- [ ] Dependencies installed
- [ ] Can import agent module
- [ ] Agent can invoke simple query
- [ ] Agent calls tools when appropriate
- [ ] Agent returns synthesized responses
- [ ] Error handling works

## Example Queries

### Query 1: Default Values
```python
query = "What are the default values for a hex bolt M10 if material and finish are missing?"
```
Expected: Agent calls `get_default_values` tool

### Query 2: Standard Equivalences
```python
query = "What is the ISO equivalent of DIN 933?"
```
Expected: Agent calls `get_standard_equivalences` tool

### Query 3: Confidence Penalty
```python
query = "What's the confidence penalty for inferring material as 'carbon steel' using pattern matching?"
```
Expected: Agent calls `get_confidence_penalty` tool

### Query 4: General Knowledge
```python
query = "Explain the Indufix matching rules for fasteners"
```
Expected: Agent calls `query_indufix_knowledge` tool

## Production Considerations

### Performance
- Temperature 0.0 for consistent results
- Max tokens 4096 balances quality vs cost
- Async execution for scalability

### Cost Optimization
- Claude Sonnet 4.5 is cost-effective
- Tool calls are efficient (no unnecessary calls)
- System message prevents redundant queries

### Monitoring
- LangSmith will trace all executions
- Monitor tool call patterns
- Track response quality

### Security
- API keys via environment variables
- No secrets in code
- Tools validate inputs via Pydantic

## Next Steps

1. **Test the Agent**: Run example queries
2. **Deploy to LangSmith**: Follow deployment guide
3. **Monitor Performance**: Check LangSmith traces
4. **Iterate**: Adjust system message based on performance

## Troubleshooting

### "No module named 'langchain_anthropic'"
```bash
pip install langchain-anthropic
```

### "API key not found"
```bash
export ANTHROPIC_API_KEY=sk-ant-...
# or set in .env file
```

### Tools not being called
- Check system message clarity
- Verify tool descriptions in toolkit
- Review LangSmith traces for decision reasoning

### Import errors
```bash
# Reinstall in development mode
pip install -e .
```

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Claude API Documentation](https://docs.anthropic.com/)
- [LangSmith Tool Server](https://docs.smith.langchain.com/)
