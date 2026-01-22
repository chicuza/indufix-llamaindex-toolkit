"""Test deployment with correct URL"""
import requests
import json

DEPLOYMENT_URL = "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app"

def test_health():
    """Test health endpoint"""
    print("=" * 70)
    print("TESTING DEPLOYMENT - CORRECT URL")
    print("=" * 70)
    print(f"\nDeployment URL: {DEPLOYMENT_URL}")

    print("\n[1/4] Testing /health endpoint...")
    try:
        response = requests.get(f"{DEPLOYMENT_URL}/health", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("[OK] Deployment is online!")
            return True
        else:
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_ok():
    """Test /ok endpoint"""
    print("\n[2/4] Testing /ok endpoint...")
    try:
        response = requests.get(f"{DEPLOYMENT_URL}/ok", timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("[OK] Service is healthy!")
            return True
        else:
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_mcp_tools():
    """Test MCP tools/list"""
    print("\n[3/4] Testing MCP tools/list...")
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
            timeout=30
        )

        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if "result" in result and "tools" in result["result"]:
                tools = result["result"]["tools"]
                print(f"[OK] {len(tools)} tools found:")
                for tool in tools:
                    print(f"  - {tool.get('name', 'unknown')}")
                return True
            else:
                print(f"[INFO] Response:")
                print(json.dumps(result, indent=2)[:500])
                return False
        else:
            print(f"Response: {response.text[:300]}")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def test_info():
    """Test /info endpoint"""
    print("\n[4/4] Testing /info endpoint...")
    try:
        response = requests.get(f"{DEPLOYMENT_URL}/info", timeout=10)
        print(f"Status: {response.status_code}")

        if response.status_code == 200:
            info = response.json()
            print("[OK] Deployment info:")
            print(json.dumps(info, indent=2)[:500])
            return True
        else:
            print(f"[INFO] Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"[INFO] {e}")
        return False

def main():
    results = []
    results.append(("Health Check", test_health()))
    results.append(("OK Endpoint", test_ok()))
    results.append(("MCP Tools", test_mcp_tools()))
    results.append(("Info Endpoint", test_info()))

    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    for test_name, result in results:
        status = "[OK]" if result else "[FAILED]"
        print(f"{status} {test_name}")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTests Passed: {passed}/{total}")

    if passed >= 2:
        print("\n[SUCCESS] Deployment is functional!")
        print("\nDeployment URL:")
        print(f"  {DEPLOYMENT_URL}")
        print("\nMCP Endpoint:")
        print(f"  {DEPLOYMENT_URL}/mcp")
        print("\nConnect to Agent Builder:")
        print("  1. Go to: https://smith.langchain.com/agent-builder")
        print("  2. Settings -> Workspace -> MCP Servers")
        print("  3. Add Remote Server:")
        print(f"     Name: indufix-llamaindex-toolkit")
        print(f"     URL: {DEPLOYMENT_URL}/mcp")
        print("  4. Test with: 'Busque valores default para parafuso M10'")
    else:
        print("\n[WARNING] Some tests failed")
        print("Check deployment logs at: https://smith.langchain.com/deployments")

if __name__ == "__main__":
    main()
