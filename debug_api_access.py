"""Debug script to test different API access patterns"""
import requests
import json

LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"
CONTROL_PLANE_BASE = "https://api.host.langchain.com"

def test_with_different_headers():
    """Test API with different header combinations"""
    print("=" * 70)
    print("DEBUG: TESTANDO DIFERENTES PADROES DE HEADERS")
    print("=" * 70)

    # Parse API key to extract workspace/tenant info
    # Format: lsv2_sk_{workspace_hash}_{key_hash}
    parts = LANGSMITH_API_KEY.split('_')
    print(f"\nAPI Key parts: {parts}")

    header_variants = [
        {
            "Authorization": f"Bearer {LANGSMITH_API_KEY}",
            "Content-Type": "application/json"
        },
        {
            "Authorization": f"Bearer {LANGSMITH_API_KEY}",
            "Content-Type": "application/json",
            "X-API-Key": LANGSMITH_API_KEY
        },
        {
            "x-api-key": LANGSMITH_API_KEY,
            "Content-Type": "application/json"
        }
    ]

    endpoints_to_test = [
        "/v1/integrations/github",
        "/v2/integrations/github",
        "/v1/integrations",
        "/v2/integrations",
        "/v2/deployments"
    ]

    for i, headers in enumerate(header_variants, 1):
        print(f"\n[{i}] Testing header variant:")
        print(f"    {json.dumps(headers, indent=4)}")

        for endpoint in endpoints_to_test:
            url = f"{CONTROL_PLANE_BASE}{endpoint}"
            print(f"\n  Endpoint: {endpoint}")

            try:
                response = requests.get(url, headers=headers, timeout=30)
                print(f"  Status: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    print(f"  Response: {json.dumps(data, indent=2)[:300]}")

                    if data:
                        print(f"  SUCCESS - Data found!")
                        return headers, endpoint, data

                elif response.status_code in [401, 403]:
                    print(f"  Auth Error: {response.text[:200]}")
                elif response.status_code == 404:
                    print(f"  404 - Not Found")
                else:
                    print(f"  Error: {response.text[:200]}")

            except Exception as e:
                print(f"  Exception: {e}")

    print("\n" + "=" * 70)
    print("Nenhuma combinacao funcionou")
    print("=" * 70)
    return None, None, None

def check_deployments_list():
    """List existing deployments to understand structure"""
    print("\n" + "=" * 70)
    print("LISTANDO DEPLOYMENTS EXISTENTES")
    print("=" * 70)

    headers = {
        "Authorization": f"Bearer {LANGSMITH_API_KEY}",
        "Content-Type": "application/json"
    }

    url = f"{CONTROL_PLANE_BASE}/v2/deployments"

    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text[:500]}")

        if response.status_code == 200:
            deployments = response.json()
            print(f"\nEncontrados {len(deployments)} deployments")
            for dep in deployments:
                print(f"\n  Deployment:")
                print(f"    ID: {dep.get('id')}")
                print(f"    Name: {dep.get('name')}")
                print(f"    Source: {dep.get('source')}")
                print(f"    URL: {dep.get('url')}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test different header combinations
    working_headers, working_endpoint, data = test_with_different_headers()

    if working_headers:
        print(f"\n✅ WORKING COMBINATION FOUND!")
        print(f"   Headers: {json.dumps(working_headers, indent=4)}")
        print(f"   Endpoint: {working_endpoint}")
        print(f"   Data: {json.dumps(data, indent=2)}")

    # Also check deployments
    check_deployments_list()
