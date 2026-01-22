"""Get detailed deployment information"""
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

def get_full_deployment_details():
    print("=" * 70)
    print("DETAILED DEPLOYMENT INSPECTION")
    print("=" * 70)

    url = f"{CONTROL_PLANE_BASE}/v2/deployments/{DEPLOYMENT_ID}"

    try:
        response = requests.get(url, headers=get_headers(), timeout=30)
        response.raise_for_status()

        deployment = response.json()

        print("\n[DEPLOYMENT DETAILS]")
        print(json.dumps(deployment, indent=2))

        print("\n" + "=" * 70)
        print("KEY INFORMATION")
        print("=" * 70)

        print(f"\nName: {deployment.get('name')}")
        print(f"ID: {deployment.get('id')}")
        print(f"Status: {deployment.get('status')}")
        print(f"Created: {deployment.get('created_at')}")

        # Check for URL fields
        url_field = deployment.get('url')
        public_url = deployment.get('public_url')
        internal_url = deployment.get('internal_url')
        endpoint = deployment.get('endpoint')

        print(f"\nURL: {url_field}")
        print(f"Public URL: {public_url}")
        print(f"Internal URL: {internal_url}")
        print(f"Endpoint: {endpoint}")

        # Check configuration
        config = deployment.get('source_config', {})
        print(f"\nDeployment Type: {config.get('deployment_type')}")
        print(f"Build on Push: {config.get('build_on_push')}")

        # Check revision
        revision = deployment.get('source_revision_config', {})
        print(f"\nBranch: {revision.get('repo_ref')}")
        print(f"Config Path: {revision.get('langgraph_config_path')}")

        # Check status details
        status_details = deployment.get('status_details', {})
        if status_details:
            print(f"\nStatus Details:")
            print(json.dumps(status_details, indent=2))

        return deployment

    except Exception as e:
        print(f"[ERROR] Failed to get deployment details: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_deployment_health():
    """Check deployment health via Control Plane API"""
    print("\n" + "=" * 70)
    print("CHECKING DEPLOYMENT HEALTH VIA API")
    print("=" * 70)

    url = f"{CONTROL_PLANE_BASE}/v2/deployments/{DEPLOYMENT_ID}/health"

    try:
        response = requests.get(url, headers=get_headers(), timeout=30)
        print(f"\nHealth endpoint status: {response.status_code}")

        if response.status_code == 200:
            health = response.json()
            print("[OK] Health data:")
            print(json.dumps(health, indent=2))
        else:
            print(f"Response: {response.text[:300]}")

    except Exception as e:
        print(f"[INFO] Health check: {e}")

if __name__ == "__main__":
    deployment = get_full_deployment_details()
    check_deployment_health()

    if deployment:
        print("\n" + "=" * 70)
        print("ANALYSIS")
        print("=" * 70)

        status = deployment.get('status')
        if status == 'READY':
            print("\n[OK] Deployment status is READY")
            print("\nPossible issues:")
            print("1. DNS propagation may take time (try again in 5-10 minutes)")
            print("2. Deployment might be private/internal only")
            print("3. MCP endpoint might require specific access patterns")
            print("\nRecommended Actions:")
            print("1. Check LangSmith UI: https://smith.langchain.com/deployments")
            print("2. Verify deployment is listed and running")
            print("3. Try connecting via Agent Builder UI instead of direct API")
        else:
            print(f"\n[WARNING] Deployment status: {status}")
            print("Wait for status to become READY")
