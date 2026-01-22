"""Verify deployment with authentication"""
import requests
import json

DEPLOYMENT_URL = "https://02c0d18a-1a0b-469a-baed-274744a670c6.smith.langchain.com"
LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"

def get_headers():
    return {
        "X-Api-Key": LANGSMITH_API_KEY,
        "Authorization": f"Bearer {LANGSMITH_API_KEY}",
        "Content-Type": "application/json"
    }

def test_mcp_with_auth():
    """Test MCP endpoint with authentication"""
    print("=" * 70)
    print("TESTING MCP ENDPOINT WITH AUTHENTICATION")
    print("=" * 70)

    mcp_request = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "params": {},
        "id": 1
    }

    print(f"\nDeployment URL: {DEPLOYMENT_URL}")
    print(f"MCP Endpoint: {DEPLOYMENT_URL}/mcp")
    print("\n[1/2] Testing MCP tools/list...")

    try:
        response = requests.post(
            f"{DEPLOYMENT_URL}/mcp",
            json=mcp_request,
            headers=get_headers(),
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if "result" in result and "tools" in result["result"]:
                tools = result["result"]["tools"]
                print(f"\n[OK] {len(tools)} tools found:")
                for tool in tools:
                    print(f"  - {tool.get('name', 'unknown')}")
                    print(f"    Description: {tool.get('description', 'N/A')[:100]}...")
                return True
            else:
                print(f"[WARNING] Unexpected response structure:")
                print(json.dumps(result, indent=2)[:500])
                return False
        else:
            print(f"[ERROR] HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        return False

def test_runs_endpoint():
    """Test runs/stream endpoint"""
    print("\n[2/2] Testing runs/stream endpoint...")

    try:
        # Test with a simple invoke
        payload = {
            "input": {"messages": [{"role": "user", "content": "What tools are available?"}]},
            "config": {},
            "stream_mode": "values"
        }

        response = requests.post(
            f"{DEPLOYMENT_URL}/runs/stream",
            json=payload,
            headers=get_headers(),
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code in [200, 201]:
            print("[OK] Agent endpoint is accessible")
            return True
        else:
            print(f"[INFO] HTTP {response.status_code}")
            print(f"Response: {response.text[:300]}")
            return False

    except Exception as e:
        print(f"[INFO] Endpoint test: {e}")
        return False

def main():
    print("\n")
    results = []

    results.append(("MCP Endpoint", test_mcp_with_auth()))
    results.append(("Runs Endpoint", test_runs_endpoint()))

    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    for test_name, result in results:
        status = "[OK]" if result else "[FAILED]"
        print(f"{status} {test_name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed >= 1:
        print("\n[SUCCESS] Deployment is accessible!")
        print("\nNext Steps:")
        print("1. Connect to Agent Builder:")
        print(f"   URL: {DEPLOYMENT_URL}/mcp")
        print("   Go to: https://smith.langchain.com/agent-builder")
        print("   Settings -> Workspace -> MCP Servers -> Add Remote Server")
        print("2. Test with:")
        print('   "Busque valores default para parafuso M10"')
    else:
        print("\n[WARNING] Deployment might still be initializing")
        print("Check status at: https://smith.langchain.com/deployments")

if __name__ == "__main__":
    main()
