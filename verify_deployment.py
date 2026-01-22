"""Verify deployment is working correctly"""
import requests
import json

DEPLOYMENT_URL = "https://02c0d18a-1a0b-469a-baed-274744a670c6.smith.langchain.com"

def test_health():
    """Test health endpoint"""
    print("\n[1/4] Testing health endpoint...")
    try:
        response = requests.get(f"{DEPLOYMENT_URL}/health", timeout=10)
        if response.status_code == 200:
            print("[OK] Deployment is online and responding!")
            return True
        else:
            print(f"[WARNING] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        return False

def test_ok_endpoint():
    """Test /ok endpoint"""
    print("\n[2/4] Testing /ok endpoint...")
    try:
        response = requests.get(f"{DEPLOYMENT_URL}/ok", timeout=10)
        if response.status_code == 200:
            print("[OK] Service is healthy!")
            return True
        else:
            print(f"[WARNING] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to connect: {e}")
        return False

def test_mcp_endpoint():
    """Test MCP endpoint"""
    print("\n[3/4] Testing MCP endpoint...")
    try:
        # Try to list tools via MCP
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

        if response.status_code == 200:
            result = response.json()
            if "result" in result and "tools" in result["result"]:
                tools = result["result"]["tools"]
                print(f"[OK] {len(tools)} tools found:")
                for tool in tools:
                    print(f"  - {tool.get('name', 'unknown')}")
                return True
            else:
                print(f"[WARNING] Unexpected response: {result}")
                return False
        else:
            print(f"[WARNING] Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to test MCP: {e}")
        return False

def test_graph_endpoint():
    """Test graph endpoint"""
    print("\n[4/4] Testing graph endpoint...")
    try:
        response = requests.get(f"{DEPLOYMENT_URL}/info", timeout=10)
        if response.status_code == 200:
            info = response.json()
            print("[OK] Graph info retrieved!")
            print(f"  Graphs: {list(info.keys())}")
            return True
        else:
            print(f"[INFO] Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"[INFO] Graph endpoint test: {e}")
        return False

def main():
    print("=" * 70)
    print("DEPLOYMENT VERIFICATION")
    print("=" * 70)
    print(f"\nDeployment URL: {DEPLOYMENT_URL}")

    results = []
    results.append(("Health Check", test_health()))
    results.append(("OK Endpoint", test_ok_endpoint()))
    results.append(("MCP Endpoint", test_mcp_endpoint()))
    results.append(("Graph Info", test_graph_endpoint()))

    # Summary
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
        print("\nNext Steps:")
        print("1. Connect to Agent Builder:")
        print(f"   URL: {DEPLOYMENT_URL}/mcp")
        print("2. Test with:")
        print('   "Busque valores default para parafuso M10"')
    else:
        print("\n[WARNING] Some tests failed. Check deployment logs.")

if __name__ == "__main__":
    main()
