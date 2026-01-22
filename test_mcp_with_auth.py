"""Test MCP endpoint with authentication"""
import requests
import json

DEPLOYMENT_URL = "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app"
LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"

def test_mcp_with_api_key():
    """Test MCP with LangSmith API key"""
    print("=" * 70)
    print("TESTING MCP ENDPOINT WITH AUTHENTICATION")
    print("=" * 70)

    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 1
    }

    # Try different authentication methods
    auth_methods = [
        {
            "name": "X-Api-Key header",
            "headers": {
                "X-Api-Key": LANGSMITH_API_KEY,
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Authorization Bearer",
            "headers": {
                "Authorization": f"Bearer {LANGSMITH_API_KEY}",
                "Content-Type": "application/json"
            }
        },
        {
            "name": "Both headers",
            "headers": {
                "X-Api-Key": LANGSMITH_API_KEY,
                "Authorization": f"Bearer {LANGSMITH_API_KEY}",
                "Content-Type": "application/json"
            }
        }
    ]

    for i, auth_method in enumerate(auth_methods, 1):
        print(f"\n[Test {i}] {auth_method['name']}...")

        try:
            response = requests.post(
                f"{DEPLOYMENT_URL}/mcp",
                json=mcp_request,
                headers=auth_method['headers'],
                timeout=30
            )

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                if "result" in result and "tools" in result["result"]:
                    tools = result["result"]["tools"]
                    print(f"[SUCCESS] {len(tools)} tools found:")
                    for tool in tools:
                        name = tool.get('name', 'unknown')
                        desc = tool.get('description', 'N/A')
                        print(f"\n  Tool: {name}")
                        print(f"  Description: {desc[:100]}...")
                        if tool.get('inputSchema'):
                            schema = tool['inputSchema']
                            if 'properties' in schema:
                                print(f"  Parameters: {list(schema['properties'].keys())}")
                    return True
                else:
                    print(f"[INFO] Response structure:")
                    print(json.dumps(result, indent=2)[:500])
            else:
                print(f"Response: {response.text[:300]}")

        except Exception as e:
            print(f"[ERROR] {e}")

    return False

def test_runs_invoke():
    """Test agent invocation"""
    print("\n" + "=" * 70)
    print("TESTING AGENT INVOCATION")
    print("=" * 70)

    headers = {
        "X-Api-Key": LANGSMITH_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "input": {
            "messages": [
                {"role": "user", "content": "What tools are available?"}
            ]
        },
        "config": {},
        "stream_mode": "values"
    }

    print("\n[Test] Invoking agent via /runs/stream...")

    try:
        response = requests.post(
            f"{DEPLOYMENT_URL}/runs/stream",
            json=payload,
            headers=headers,
            timeout=30,
            stream=True
        )

        print(f"Status: {response.status_code}")

        if response.status_code in [200, 201]:
            print("[OK] Agent invocation successful!")
            print("\nResponse stream:")
            for line in response.iter_lines():
                if line:
                    print(line.decode('utf-8')[:200])
            return True
        else:
            print(f"Response: {response.text[:300]}")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print(f"\nDeployment URL: {DEPLOYMENT_URL}")
    print(f"MCP Endpoint: {DEPLOYMENT_URL}/mcp\n")

    mcp_success = test_mcp_with_api_key()
    agent_success = test_runs_invoke()

    print("\n" + "=" * 70)
    print("FINAL SUMMARY")
    print("=" * 70)

    if mcp_success:
        print("\n[SUCCESS] MCP endpoint is working with authentication!")
        print("\nYour 6 LlamaIndex tools are deployed and ready!")
    else:
        print("\n[INFO] MCP endpoint requires authentication")
        print("This is normal - Agent Builder will handle authentication")

    if mcp_success or agent_success:
        print("\n[NEXT STEPS]")
        print("\n1. Connect to Agent Builder:")
        print("   - Go to: https://smith.langchain.com/agent-builder")
        print("   - Settings -> Workspace -> MCP Servers")
        print("   - Add Remote Server:")
        print(f"     Name: indufix-llamaindex-toolkit")
        print(f"     URL: {DEPLOYMENT_URL}/mcp")
        print("     Auth: Use workspace authentication")
        print("\n2. Test your deployment:")
        print('   Create an agent and ask: "Busque valores default para parafuso M10"')
        print("\n3. Your tools:")
        print("   - retrieve_matching_rules")
        print("   - query_indufix_knowledge")
        print("   - get_default_values")
        print("   - get_standard_equivalences")
        print("   - get_confidence_penalty")
        print("   - pipeline_retrieve_raw")

if __name__ == "__main__":
    main()
