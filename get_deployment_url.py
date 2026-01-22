"""Get deployment URL from Control Plane API"""
import requests
import json

LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"
CONTROL_PLANE_BASE = "https://api.host.langchain.com"
DEPLOYMENT_ID = "02c0d18a-1a0b-469a-baed-274744a670c6"

def get_headers():
    return {
        "X-Api-Key": LANGSMITH_API_KEY,
        "Content-Type": "application/json"
    }

def get_deployment_details():
    print("=" * 70)
    print("GETTING DEPLOYMENT DETAILS")
    print("=" * 70)

    url = f"{CONTROL_PLANE_BASE}/v2/deployments/{DEPLOYMENT_ID}"

    try:
        response = requests.get(url, headers=get_headers(), timeout=30)
        response.raise_for_status()

        deployment = response.json()

        print(f"\nDeployment ID: {deployment.get('id')}")
        print(f"Name: {deployment.get('name')}")
        print(f"Status: {deployment.get('status')}")
        print(f"Created: {deployment.get('created_at', 'N/A')}")

        # Try to get URL
        url = deployment.get('url')
        if not url:
            # Construct from deployment ID
            url = f"https://{DEPLOYMENT_ID}.smith.langchain.com"

        print(f"\nDeployment URL: {url}")
        print(f"MCP Endpoint: {url}/mcp")
        print(f"API Endpoint: {url}/runs/stream")

        # Save to file
        with open(".deployment_url.txt", "w") as f:
            f.write(url)

        print(f"\n[OK] URL saved to .deployment_url.txt")

        return url

    except Exception as e:
        print(f"[ERROR] Failed to get deployment details: {e}")
        return None

if __name__ == "__main__":
    url = get_deployment_details()

    if url:
        print("\n" + "=" * 70)
        print("NEXT STEPS")
        print("=" * 70)
        print(f"\n1. Test deployment:")
        print(f"   python check_deployment.py")
        print(f"\n2. Connect to Agent Builder:")
        print(f"   URL: {url}/mcp")
        print(f"\n3. Test with:")
        print('   "Busque valores default para parafuso M10"')
