"""LangGraph agent with proper LLM integration for Indufix toolkit

This agent follows official LangGraph ReAct patterns with Claude Sonnet 4.5
and can make tool calls to the Indufix LlamaIndex toolkit.
"""
import os
from typing import Literal

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

from indufix_toolkit import TOOLS


# System message to guide the agent's behavior
SYSTEM_MESSAGE = """You are an expert assistant for the Indufix SKU Matcher system.

You have access to tools that query the Indufix knowledge base containing:
- Default values for missing product attributes
- Standard equivalences (DIN, ISO, ASTM)
- Confidence penalties for inferred values
- Product matching rules and patterns
- Technical specifications for fasteners

Your role is to help users:
1. Find default values for missing product attributes
2. Identify standard equivalences across different norms
3. Calculate confidence penalties for inferred data
4. Query the Indufix knowledge base
5. Retrieve matching rules and specifications

Always be precise and cite the confidence scores from retrieved data.
When values are inferred, clearly communicate the confidence penalty.
"""


def create_agent():
    """Create the LangGraph agent with LLM and tools bound.

    Returns:
        Compiled LangGraph agent ready for invocation
    """
    # Initialize Claude Sonnet 4.5 with proper configuration
    llm = ChatAnthropic(
        model="claude-sonnet-4-5-20250929",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        temperature=0.0,  # Deterministic for technical queries
        max_tokens=4096,
    )

    # Bind tools to the LLM
    llm_with_tools = llm.bind_tools(TOOLS)

    # Define the agent node that calls the LLM
    def call_model(state: MessagesState) -> dict:
        """Agent node that invokes the LLM with bound tools.

        Args:
            state: Current conversation state with messages

        Returns:
            Updated state with LLM response
        """
        messages = state["messages"]

        # Add system message if this is the first call
        if not any(isinstance(msg, SystemMessage) for msg in messages):
            messages = [SystemMessage(content=SYSTEM_MESSAGE)] + messages

        # Invoke LLM with tools
        response = llm_with_tools.invoke(messages)

        return {"messages": [response]}

    # Define routing logic
    def should_continue(state: MessagesState) -> Literal["tools", "end"]:
        """Determine whether to continue with tools or end.

        Args:
            state: Current conversation state

        Returns:
            "tools" if there are tool calls to execute, "end" otherwise
        """
        messages = state["messages"]
        last_message = messages[-1]

        # Check if the LLM made any tool calls
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        return "end"

    # Build the state graph
    workflow = StateGraph(MessagesState)

    # Add nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(TOOLS))

    # Add edges
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END,
        }
    )
    workflow.add_edge("tools", "agent")

    # Compile and return the graph
    return workflow.compile()


# Lazy initialization of the graph
_graph = None


def get_graph():
    """Get or create the compiled graph lazily.

    Returns:
        Compiled LangGraph agent
    """
    global _graph
    if _graph is None:
        _graph = create_agent()
    return _graph


# Create the graph attribute for backward compatibility
# This will raise an error if API key is not set, but only when accessed
try:
    graph = create_agent()
except Exception:
    # If creation fails (e.g., no API key), provide a lazy loader
    class LazyGraph:
        def __getattr__(self, name):
            return getattr(get_graph(), name)

        def __call__(self, *args, **kwargs):
            return get_graph()(*args, **kwargs)

    graph = LazyGraph()


# Convenience function for testing and direct usage
async def run_agent(query: str) -> str:
    """Run the agent with a query and return the final response.

    Args:
        query: User query to process

    Returns:
        Final agent response as string
    """
    from langchain_core.messages import HumanMessage

    result = await get_graph().ainvoke(
        {"messages": [HumanMessage(content=query)]}
    )

    return result["messages"][-1].content


if __name__ == "__main__":
    import asyncio

    # Example usage
    async def main():
        # Test query
        query = "What are the default values for a hex bolt M10 if material and finish are missing?"

        print(f"Query: {query}\n")
        response = await run_agent(query)
        print(f"Response: {response}")

    asyncio.run(main())
