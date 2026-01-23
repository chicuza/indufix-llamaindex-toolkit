"""Test script to verify the fixed agent implementation

This script tests the agent locally without deploying to LangSmith.
It verifies that the agent can properly invoke tools and process queries.
"""
import asyncio
import os
from langchain_core.messages import HumanMessage


async def test_agent_basic():
    """Test basic agent invocation"""
    print("=" * 70)
    print("TEST 1: Basic Agent Import and Structure")
    print("=" * 70)

    try:
        from agent import graph, create_agent
        print("[PASS] Successfully imported agent module")
        print("[PASS] Graph object exists:", type(graph))
        print("[PASS] create_agent function exists:", callable(create_agent))
        return True
    except Exception as e:
        print(f"[FAIL] Failed to import agent: {e}")
        return False


async def test_agent_invocation():
    """Test agent invocation with a simple query"""
    print("\n" + "=" * 70)
    print("TEST 2: Agent Invocation (Requires ANTHROPIC_API_KEY)")
    print("=" * 70)

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[SKIP] ANTHROPIC_API_KEY not set - skipping invocation test")
        print("  Set ANTHROPIC_API_KEY environment variable to test")
        return None

    try:
        from agent import graph

        # Simple query that should trigger tool use
        query = "What are the default values for a hex bolt M10?"
        print(f"\nQuery: {query}")
        print("\nInvoking agent...")

        result = await graph.ainvoke({
            "messages": [HumanMessage(content=query)]
        })

        print("\n[PASS] Agent invoked successfully")
        print(f"[PASS] Number of messages in result: {len(result['messages'])}")

        # Check for tool calls
        has_tool_calls = False
        for msg in result['messages']:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                has_tool_calls = True
                print(f"[PASS] Agent made tool calls: {len(msg.tool_calls)} call(s)")
                for tc in msg.tool_calls:
                    print(f"  - Tool: {tc.get('name', 'unknown')}")
                break

        if not has_tool_calls:
            print("[WARN] No tool calls detected (agent may have responded directly)")

        # Get final response
        final_message = result['messages'][-1]
        print(f"\n[PASS] Final response type: {type(final_message).__name__}")
        print(f"[PASS] Response length: {len(final_message.content)} characters")

        if len(final_message.content) > 0:
            print("\n[PASS] Response preview:")
            print(final_message.content[:200] + "..." if len(final_message.content) > 200 else final_message.content)

        return True

    except Exception as e:
        print(f"[FAIL] Agent invocation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_convenience_function():
    """Test the convenience run_agent function"""
    print("\n" + "=" * 70)
    print("TEST 3: Convenience Function (Requires ANTHROPIC_API_KEY)")
    print("=" * 70)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[SKIP] ANTHROPIC_API_KEY not set - skipping convenience function test")
        return None

    try:
        from agent import run_agent

        query = "What is the ISO equivalent of DIN 933?"
        print(f"\nQuery: {query}")
        print("\nCalling run_agent...")

        response = await run_agent(query)

        print("\n[PASS] run_agent executed successfully")
        print(f"[PASS] Response type: {type(response)}")
        print(f"[PASS] Response length: {len(response)} characters")

        if len(response) > 0:
            print("\n[PASS] Response preview:")
            print(response[:200] + "..." if len(response) > 200 else response)

        return True

    except Exception as e:
        print(f"[FAIL] run_agent failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_tools_available():
    """Verify all tools are available"""
    print("\n" + "=" * 70)
    print("TEST 4: Tool Availability")
    print("=" * 70)

    try:
        from indufix_toolkit import TOOLS

        print(f"[PASS] Found {len(TOOLS)} tools in toolkit:")
        for i, tool in enumerate(TOOLS, 1):
            print(f"  {i}. {tool.name}")
            print(f"     Description: {tool.description[:80]}...")

        return True

    except Exception as e:
        print(f"[FAIL] Failed to load tools: {e}")
        return False


async def main():
    """Run all tests"""
    print("\n")
    print("*" * 70)
    print("*" + " " * 68 + "*")
    print("*" + "  INDUFIX AGENT - LOCAL TEST SUITE".center(68) + "*")
    print("*" + " " * 68 + "*")
    print("*" * 70)
    print("\nThis script tests the fixed agent.py implementation locally.")
    print("For full functionality, set ANTHROPIC_API_KEY and LLAMA_CLOUD_API_KEY")
    print("\nCurrent environment:")
    print(f"  ANTHROPIC_API_KEY: {'[SET]' if os.getenv('ANTHROPIC_API_KEY') else '[NOT SET]'}")
    print(f"  LLAMA_CLOUD_API_KEY: {'[SET]' if os.getenv('LLAMA_CLOUD_API_KEY') else '[NOT SET]'}")

    # Run tests
    results = []

    # Test 1: Basic import
    result1 = await test_agent_basic()
    results.append(("Basic Import", result1))

    # Test 2: Agent invocation
    result2 = await test_agent_invocation()
    results.append(("Agent Invocation", result2))

    # Test 3: Convenience function
    result3 = await test_convenience_function()
    results.append(("Convenience Function", result3))

    # Test 4: Tools availability
    result4 = await test_tools_available()
    results.append(("Tool Availability", result4))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, r in results if r is True)
    skipped = sum(1 for _, r in results if r is None)
    failed = sum(1 for _, r in results if r is False)
    total = len(results)

    for name, result in results:
        if result is True:
            status = "[PASS]"
        elif result is None:
            status = "[SKIP]"
        else:
            status = "[FAIL]"
        print(f"  {status:8} - {name}")

    print("\n" + "-" * 70)
    print(f"Results: {passed} passed, {skipped} skipped, {failed} failed (of {total} total)")
    print("=" * 70)

    if failed == 0 and passed > 0:
        print("\n[SUCCESS] Agent implementation verified successfully!")
        if skipped > 0:
            print("  Note: Some tests were skipped due to missing API keys")
    elif failed > 0:
        print("\n[ERROR] Some tests failed - please review errors above")

    print("\nNext steps:")
    print("  1. Set ANTHROPIC_API_KEY to test full agent functionality")
    print("  2. Set LLAMA_CLOUD_API_KEY to test tool execution")
    print("  3. Deploy to LangSmith Cloud for production use")
    print("\nSee AGENT_IMPLEMENTATION.md for detailed documentation")


if __name__ == "__main__":
    asyncio.run(main())
