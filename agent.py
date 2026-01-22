"""Minimal LangGraph agent that exposes the Indufix toolkit"""
from langgraph.graph import StateGraph, MessagesState
from langgraph.prebuilt import ToolNode
from indufix_toolkit import TOOLS

# Create a simple agent graph that can use the tools
def should_continue(state: MessagesState):
    """Determine if we should continue or end"""
    messages = state["messages"]
    last_message = messages[-1]

    # If there are no tool calls, we're done
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return "end"
    return "continue"

def call_model(state: MessagesState):
    """Placeholder model node - tools are the focus"""
    from langchain_core.messages import AIMessage
    messages = state["messages"]

    # Return a simple response
    response = AIMessage(content="Tools are available for use via MCP server")
    return {"messages": [response]}

# Build the graph
workflow = StateGraph(MessagesState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(TOOLS))

# Add edges
workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": "__end__",
    }
)
workflow.add_edge("tools", "agent")

# Compile the graph
graph = workflow.compile()
