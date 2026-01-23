"""Official CLI Method to Test MCP Server Connection
Uses environment variables for secure credential management.
Based on official LangSmith/LangGraph documentation.
"""
import os
import sys
import requests
import json
from datetime import datetime

# Configuration from environment variables
DEPLOYMENT_URL = os.getenv(
    "MCP_DEPLOYMENT_URL",
    "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app"
)
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
WORKSPACE_ID = os.getenv("LANGSMITH_WORKSPACE_ID", "950d802b-125a-45bc-88e4-3d7d0edee182")

def print_section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def check_credentials():
    """Verify required credentials are provided"""
    if not LANGSMITH_API_KEY:
        print("ERROR: LANGSMITH_API_KEY environment variable not set!")
        print("\nUsage:")
        print("  Windows:")
        print('    set LANGSMITH_API_KEY=your_api_key_here')
        print('    python test_mcp_cli.py')
        print("\n  Linux/Mac:")
        print('    export LANGSMITH_API_KEY=your_api_key_here')
        print('    python test_mcp_cli.py')
        print("\n  Or use .env file:")
        print('    echo "LANGSMITH_API_KEY=your_api_key_here" > .env.test')
        print('    # Then load it before running')
        return False
    return True

def test_deployment_health():
    """Test 1: Deployment Health Check (No Auth Required)"""
    print_section("Test 1: Deployment Health Check")

    try:
        response = requests.get(f"{DEPLOYMENT_URL}/ok", timeout=10)
        print(f"URL: {DEPLOYMENT_URL}/ok")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            print("\n[OK] Deployment is healthy and accessible")
            return True
        else:
            print(f"\n[FAILED] Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"\n[ERROR] Health check failed: {e}")
        return False

def test_mcp_without_auth():
    """Test 2: MCP Endpoint Without Authentication (Expected to Fail)"""
    print_section("Test 2: MCP Endpoint Without Authentication")

    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(
            f"{DEPLOYMENT_URL}/mcp",
            json=mcp_request,
            headers=headers,
            timeout=30
        )

        print(f"URL: {DEPLOYMENT_URL}/mcp")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}")

        if response.status_code == 403:
            print("\n[EXPECTED] 403 Forbidden - Authentication is required")
            print("This confirms the MCP endpoint is properly secured")
            return True
        else:
            print(f"\n[UNEXPECTED] Got {response.status_code} instead of 403")
            return False
    except Exception as e:
        print(f"\n[ERROR] Request failed: {e}")
        return False

def test_mcp_with_auth():
    """Test 3: MCP Endpoint With Authentication"""
    print_section("Test 3: MCP Endpoint With Authentication")

    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Api-Key": LANGSMITH_API_KEY,
            "X-Tenant-Id": WORKSPACE_ID
        }

        print(f"URL: {DEPLOYMENT_URL}/mcp")
        print(f"Headers:")
        print(f"  X-Api-Key: {LANGSMITH_API_KEY[:20]}...{LANGSMITH_API_KEY[-10:]}")
        print(f"  X-Tenant-Id: {WORKSPACE_ID}")

        response = requests.post(
            f"{DEPLOYMENT_URL}/mcp",
            json=mcp_request,
            headers=headers,
            timeout=30
        )

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if "result" in result and "tools" in result["result"]:
                tools = result["result"]["tools"]
                print(f"\n[SUCCESS] Found {len(tools)} tool(s):")
                for tool in tools:
                    print(f"  - {tool.get('name')}: {tool.get('description', 'No description')[:60]}...")
                return True
            else:
                print("\n[ERROR] Unexpected response structure")
                print(f"Response: {json.dumps(result, indent=2)[:500]}")
                return False
        else:
            print(f"\n[FAILED] Authentication failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"\n[ERROR] Request failed: {e}")
        return False

def test_tool_invocation():
    """Test 4: Tool Invocation With Authentication"""
    print_section("Test 4: Tool Invocation Test")

    try:
        call_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "indufix_agent",
                "arguments": {
                    "messages": [
                        {
                            "role": "user",
                            "content": "List available tools"
                        }
                    ]
                }
            },
            "id": 2
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Api-Key": LANGSMITH_API_KEY,
            "X-Tenant-Id": WORKSPACE_ID
        }

        print(f"URL: {DEPLOYMENT_URL}/mcp")
        print(f"Tool: indufix_agent")
        print(f"Query: List available tools")

        response = requests.post(
            f"{DEPLOYMENT_URL}/mcp",
            json=call_request,
            headers=headers,
            timeout=30
        )

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n[SUCCESS] Tool invocation successful")

            # Save response for inspection
            with open("mcp_tool_invocation_result.json", "w") as f:
                json.dump(result, f, indent=2)
            print("[INFO] Full response saved to: mcp_tool_invocation_result.json")
            return True
        else:
            print(f"\n[FAILED] Tool invocation failed with status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"\n[ERROR] Tool invocation failed: {e}")
        return False

def main():
    print("=" * 70)
    print("MCP SERVER CLI TEST - Official Method")
    print("=" * 70)
    print(f"\nDeployment: {DEPLOYMENT_URL}")
    print(f"Workspace: {WORKSPACE_ID}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Check credentials
    if not check_credentials():
        sys.exit(1)

    # Run tests
    results = []

    results.append(("Deployment Health", test_deployment_health()))
    results.append(("MCP Without Auth (Expected Fail)", test_mcp_without_auth()))
    results.append(("MCP With Auth", test_mcp_with_auth()))

    # Only run tool invocation if MCP auth succeeded
    if results[-1][1]:  # If MCP with auth passed
        results.append(("Tool Invocation", test_tool_invocation()))
    else:
        print_section("Test 4: Tool Invocation Test")
        print("[SKIPPED] MCP authentication failed, cannot test invocation")
        results.append(("Tool Invocation", False))

    # Summary
    print_section("TEST SUMMARY")

    print("\n[RESULTS]")
    for test_name, result in results:
        status = "[OK]" if result else "[FAILED]"
        print(f"{status} {test_name}")

    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTests Passed: {passed}/{total}")

    # Next steps
    print_section("NEXT STEPS")

    if passed == total:
        print("\n[SUCCESS] All MCP tests passed!")
        print("\nThe MCP server is working correctly via CLI/API.")
        print("\nTo add this server to Agent Builder workspace:")
        print("1. Visit: https://smith.langchain.com/settings")
        print("2. Navigate to: Workspace -> MCP Servers")
        print("3. Click: Add Remote Server")
        print("4. Configure:")
        print(f"   Name: indufix-llamaindex-toolkit")
        print(f"   URL: {DEPLOYMENT_URL}/mcp")
        print("5. Add Authentication Headers:")
        print("   Header 1: X-Api-Key = {{INDUFIX_API_KEY}}")
        print("   Header 2: X-Tenant-Id = {{INDUFIX_TENANT_ID}}")
        print("\nNote: MCP server configuration MUST be done via UI.")
        print("      There are NO CLI commands for this step.")
    else:
        print("\n[FAILED] Some tests failed")
        print("\nTroubleshooting:")
        print("1. Verify LANGSMITH_API_KEY is correct")
        print("2. Check deployment status: https://smith.langchain.com/deployments")
        print("3. Ensure API key has proper permissions")

    print("\n" + "=" * 70)
    print("END OF TEST")
    print("=" * 70)

    return 0 if passed == total else 1

if __name__ == "__main__":
    sys.exit(main())
