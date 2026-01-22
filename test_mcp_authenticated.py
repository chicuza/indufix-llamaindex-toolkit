"""Test MCP Endpoint with Authentication - Fix for 'Failed to load tools' Error"""
import requests
import json
from datetime import datetime

# Configuration
DEPLOYMENT_URL = "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app"
LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"
WORKSPACE_ID = "950d802b-125a-45bc-88e4-3d7d0edee182"

def get_headers(include_auth=True):
    """Get headers with or without authentication"""
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    if include_auth:
        headers["X-Api-Key"] = LANGSMITH_API_KEY
        headers["X-Tenant-Id"] = WORKSPACE_ID
    return headers

print("=" * 70)
print("MCP AUTHENTICATION FIX TEST")
print("=" * 70)
print(f"\nDeployment: {DEPLOYMENT_URL}")
print(f"Workspace: {WORKSPACE_ID}")
print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# Test 1: Without Authentication (Reproduce the Error)
print("\n" + "=" * 70)
print("[Test 1] MCP Endpoint WITHOUT Authentication (Reproducing Error)")
print("=" * 70)

try:
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 1
    }

    response = requests.post(
        f"{DEPLOYMENT_URL}/mcp",
        json=mcp_request,
        headers=get_headers(include_auth=False),
        timeout=30
    )

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")

    if response.status_code == 403:
        print("\n[EXPECTED] 403 Forbidden - Authentication required")
        print("This is the error Agent Builder sees when auth is not configured")
        auth_required = True
    else:
        print(f"\n[UNEXPECTED] Got {response.status_code} instead of 403")
        auth_required = False

except Exception as e:
    print(f"[ERROR] Request failed: {e}")
    auth_required = False

# Test 2: With X-Api-Key Only
print("\n" + "=" * 70)
print("[Test 2] MCP Endpoint WITH X-Api-Key Header")
print("=" * 70)

try:
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 2
    }

    headers_api_key_only = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Api-Key": LANGSMITH_API_KEY
    }

    response = requests.post(
        f"{DEPLOYMENT_URL}/mcp",
        json=mcp_request,
        headers=headers_api_key_only,
        timeout=30
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        if "result" in result and "tools" in result["result"]:
            tools = result["result"]["tools"]
            print(f"\n[SUCCESS] Found {len(tools)} tool(s):")
            for tool in tools:
                print(f"  - {tool.get('name')}: {tool.get('description', 'No description')[:60]}...")
            api_key_works = True
        else:
            print("\n[ERROR] Unexpected response structure")
            api_key_works = False
    else:
        print(f"\n[FAILED] Status {response.status_code}")
        print(f"Response: {response.text[:200]}")
        api_key_works = False

except Exception as e:
    print(f"[ERROR] Request failed: {e}")
    api_key_works = False

# Test 3: With Both X-Api-Key and X-Tenant-Id
print("\n" + "=" * 70)
print("[Test 3] MCP Endpoint WITH X-Api-Key AND X-Tenant-Id Headers")
print("=" * 70)

try:
    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 3
    }

    response = requests.post(
        f"{DEPLOYMENT_URL}/mcp",
        json=mcp_request,
        headers=get_headers(include_auth=True),
        timeout=30
    )

    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        if "result" in result and "tools" in result["result"]:
            tools = result["result"]["tools"]
            print(f"\n[SUCCESS] Found {len(tools)} tool(s):")
            for tool in tools:
                print(f"  - {tool.get('name')}: {tool.get('description', 'No description')[:60]}...")
            both_headers_work = True
        else:
            print("\n[ERROR] Unexpected response structure")
            both_headers_work = False
    else:
        print(f"\n[FAILED] Status {response.status_code}")
        print(f"Response: {response.text[:200]}")
        both_headers_work = False

except Exception as e:
    print(f"[ERROR] Request failed: {e}")
    both_headers_work = False

# Test 4: Test Tool Invocation with Authentication
print("\n" + "=" * 70)
print("[Test 4] Tool Invocation WITH Authentication")
print("=" * 70)

if api_key_works or both_headers_work:
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
                            "content": "What tools are available?"
                        }
                    ]
                }
            },
            "id": 4
        }

        response = requests.post(
            f"{DEPLOYMENT_URL}/mcp",
            json=call_request,
            headers=get_headers(include_auth=True),
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("\n[SUCCESS] Tool invocation successful")

            # Save response for inspection
            with open("test_4_tool_invocation.json", "w") as f:
                json.dump(result, f, indent=2)
            print("[INFO] Full response saved to: test_4_tool_invocation.json")
            tool_invocation_works = True
        else:
            print(f"\n[FAILED] Status {response.status_code}")
            print(f"Response: {response.text[:200]}")
            tool_invocation_works = False

    except Exception as e:
        print(f"[ERROR] Tool invocation failed: {e}")
        tool_invocation_works = False
else:
    print("[SKIPPED] Tool discovery failed, cannot test invocation")
    tool_invocation_works = False

# Summary
print("\n" + "=" * 70)
print("TEST SUMMARY")
print("=" * 70)

results = [
    ("Authentication Required (403 without auth)", auth_required),
    ("X-Api-Key Header Works", api_key_works),
    ("Both Headers Work", both_headers_work),
    ("Tool Invocation Works", tool_invocation_works)
]

print("\n[RESULTS]")
for test_name, result in results:
    status = "[OK]" if result else "[FAILED]"
    print(f"{status} {test_name}")

passed = sum(1 for _, r in results if r)
total = len(results)
print(f"\nTests Passed: {passed}/{total}")

# Agent Builder Configuration Instructions
print("\n" + "=" * 70)
print("AGENT BUILDER FIX - AUTHENTICATION CONFIGURATION")
print("=" * 70)

if api_key_works or both_headers_work:
    print("\n[SOLUTION CONFIRMED] The MCP endpoint works with authentication!")
    print("\nTo fix the 'Failed to load tools' error in Agent Builder:")
    print("\n1. Navigate to: Settings -> Workspace -> MCP Servers")
    print("   URL: https://smith.langchain.com/settings")

    print("\n2. When adding the MCP server, configure authentication:")
    print("   Name: indufix-llamaindex-toolkit")
    print(f"   URL: {DEPLOYMENT_URL}/mcp")

    print("\n3. Add Authentication Headers:")
    if api_key_works:
        print("\n   MINIMUM REQUIRED (Option 1):")
        print("   Header Name: X-Api-Key")
        print(f"   Header Value: {LANGSMITH_API_KEY}")

    if both_headers_work:
        print("\n   RECOMMENDED (Option 2 - Both Headers):")
        print("   Header 1:")
        print("     Name: X-Api-Key")
        print(f"     Value: {LANGSMITH_API_KEY}")
        print("   Header 2:")
        print("     Name: X-Tenant-Id")
        print(f"     Value: {WORKSPACE_ID}")

    print("\n4. Save the configuration")
    print("\n5. Verify:")
    print("   - MCP server shows as active/connected (green indicator)")
    print("   - No 'Failed to load tools' error")
    print("   - indufix_agent tool appears in available tools list")

else:
    print("\n[ERROR] Authentication fix did not work as expected")
    print("Review the test results above for details")

print("\n" + "=" * 70)
print("NEXT STEPS")
print("=" * 70)

if api_key_works or both_headers_work:
    print("\n1. [IMMEDIATE] Add authentication headers in Agent Builder")
    print("   - Follow the configuration instructions above")
    print("   - Use the exact header names and values shown")

    print("\n2. [VERIFY] Check MCP server status")
    print("   - Should show green/active indicator")
    print("   - Should list indufix_agent in available tools")

    print("\n3. [INTEGRATE] Add tool to LlamaIndex_Rule_Retriever subagent")
    print("   - See: LLAMAINDEX_RULE_RETRIEVER_INTEGRATION.md")
    print("   - See: SUBAGENT_QUICK_CONFIG.md")

    print("\n4. [TEST] Test with queries")
    print("   - 'Busque regras para parafuso M10'")
    print("   - 'Valores default para parafuso sextavado'")
    print("   - 'Equivalencia entre DIN 933 e ISO 4017'")
else:
    print("\n1. [DEBUG] Review test results above")
    print("2. [CHECK] Verify deployment status")
    print("3. [VERIFY] Check API keys are valid")

print("\n" + "=" * 70)
print("END OF TEST")
print("=" * 70)
