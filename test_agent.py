"""Test the agent graph execution"""
import os
from agent import graph
from langchain_core.messages import HumanMessage

# Set environment variable
os.environ["LLAMA_CLOUD_API_KEY"] = "llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm"

print("=" * 70)
print("TESTING AGENT GRAPH EXECUTION")
print("=" * 70)

# Test 1: Simple invocation
print("\n[Test 1] Testing graph invocation...")
try:
    result = graph.invoke({
        "messages": [HumanMessage(content="Hello, what tools are available?")]
    })
    print(f"[OK] Graph invoked successfully")
    print(f"Messages: {len(result.get('messages', []))}")
    if result.get('messages'):
        last_msg = result['messages'][-1]
        print(f"Last message: {last_msg.content[:200]}")
except Exception as e:
    print(f"[ERROR] Graph invocation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Check available tools
print("\n[Test 2] Checking available tools...")
try:
    from indufix_toolkit import TOOLS
    print(f"[OK] {len(TOOLS)} tools available:")
    for tool in TOOLS:
        print(f"  - {tool.name}: {tool.description[:80]}...")
except Exception as e:
    print(f"[ERROR] Tool check failed: {e}")

# Test 3: Graph configuration
print("\n[Test 3] Checking graph configuration...")
try:
    print(f"[OK] Graph compiled: {graph is not None}")
    print(f"[OK] Graph type: {type(graph).__name__}")

    # Check if graph has nodes
    if hasattr(graph, 'nodes'):
        print(f"[OK] Graph nodes: {list(graph.nodes.keys()) if graph.nodes else 'N/A'}")
except Exception as e:
    print(f"[ERROR] Configuration check failed: {e}")

print("\n" + "=" * 70)
print("TESTING COMPLETE")
print("=" * 70)
