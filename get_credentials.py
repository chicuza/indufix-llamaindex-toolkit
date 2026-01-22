"""
Official CLI Script: Get LangSmith Credentials for Deployment
Uses official Control Plane API as documented at:
https://docs.langchain.com/langsmith/api-ref-control-plane
"""
import requests
import json
import sys

# API Configuration
LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"
CONTROL_PLANE_BASE = "https://api.host.langchain.com"  # US region
LANGSMITH_API_BASE = "https://api.smith.langchain.com"

def get_headers():
    """Standard headers for Control Plane API"""
    return {
        "X-Api-Key": LANGSMITH_API_KEY,
        "Content-Type": "application/json"
    }

def get_workspaces():
    """Get workspace information (for X-Tenant-Id)"""
    print("=" * 70)
    print("STEP 1: RETRIEVING WORKSPACE INFORMATION")
    print("=" * 70)

    url = f"{LANGSMITH_API_BASE}/api/v1/workspaces"

    try:
        response = requests.get(url, headers=get_headers(), timeout=30)
        response.raise_for_status()

        workspaces = response.json()

        if workspaces:
            print(f"\n[OK] Found {len(workspaces)} workspace(s):")
            for ws in workspaces:
                print(f"\n  Workspace: {ws.get('display_name', 'N/A')}")
                print(f"  ID: {ws.get('id')}")
                print(f"  Tenant ID: {ws.get('tenant_id')}")

            # Return first workspace
            workspace = workspaces[0]
            return {
                "id": workspace.get("id"),
                "tenant_id": workspace.get("tenant_id"),
                "name": workspace.get("display_name")
            }
        else:
            print("\n[ERROR] No workspaces found")
            return None

    except Exception as e:
        print(f"\n[ERROR] Failed to get workspaces: {e}")
        return None

def get_github_integrations(tenant_id):
    """Get GitHub integration ID"""
    print("\n" + "=" * 70)
    print("STEP 2: RETRIEVING GITHUB INTEGRATION")
    print("=" * 70)

    # Try different endpoints
    endpoints = [
        f"{CONTROL_PLANE_BASE}/v1/integrations/github",
        f"{CONTROL_PLANE_BASE}/v2/integrations/github"
    ]

    headers = get_headers()
    if tenant_id:
        headers["X-Tenant-Id"] = tenant_id

    for endpoint in endpoints:
        print(f"\nTrying: {endpoint}")

        try:
            response = requests.get(endpoint, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()
                print(f"[OK] Response received")

                if data:
                    print(f"\n[SUCCESS] GitHub integrations found:")
                    if isinstance(data, list):
                        for integration in data:
                            print(f"\n  Integration ID: {integration.get('id')}")
                            print(f"  Name: {integration.get('name', 'N/A')}")
                            print(f"  Owner: {integration.get('owner', 'N/A')}")

                        return data[0] if data else None
                    else:
                        print(json.dumps(data, indent=2))
                        return data
                else:
                    print("[WARNING] No integrations found in response")
            elif response.status_code == 404:
                print(f"[INFO] Endpoint not found (404)")
            else:
                print(f"[ERROR] Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")

        except Exception as e:
            print(f"[ERROR] Request failed: {e}")

    print("\n[INFO] GitHub integration must be set up via UI first")
    print("Visit: https://smith.langchain.com/settings")
    return None

def list_deployments(tenant_id):
    """List existing deployments"""
    print("\n" + "=" * 70)
    print("STEP 3: LISTING EXISTING DEPLOYMENTS")
    print("=" * 70)

    url = f"{CONTROL_PLANE_BASE}/v2/deployments"

    headers = get_headers()
    if tenant_id:
        headers["X-Tenant-Id"] = tenant_id

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        result = response.json()
        deployments = result.get("resources", [])

        if deployments:
            print(f"\n[OK] Found {len(deployments)} deployment(s):")
            for dep in deployments:
                print(f"\n  Name: {dep.get('name')}")
                print(f"  ID: {dep.get('id')}")
                print(f"  Status: {dep.get('status', 'N/A')}")
                print(f"  URL: {dep.get('url', 'N/A')}")
        else:
            print("\n[INFO] No deployments found")

        return deployments

    except Exception as e:
        print(f"\n[ERROR] Failed to list deployments: {e}")
        return []

def save_credentials(workspace, integration, deployments):
    """Save credentials to .env.deployment file"""
    print("\n" + "=" * 70)
    print("STEP 4: SAVING CREDENTIALS")
    print("=" * 70)

    with open(".env.deployment", "w") as f:
        f.write("# LangSmith Deployment Credentials\n")
        f.write("# Retrieved from official Control Plane API\n\n")

        f.write("# API Keys\n")
        f.write(f"LANGSMITH_API_KEY={LANGSMITH_API_KEY}\n")
        f.write(f"LLAMA_CLOUD_API_KEY=llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm\n\n")

        if workspace:
            f.write("# Workspace Information\n")
            f.write(f"WORKSPACE_ID={workspace['id']}\n")
            f.write(f"WORKSPACE_NAME={workspace['name']}\n")
            if workspace.get('tenant_id'):
                f.write(f"TENANT_ID={workspace['tenant_id']}\n")
            f.write("\n")

        if integration:
            f.write("# GitHub Integration\n")
            f.write(f"INTEGRATION_ID={integration.get('id', 'NOT_FOUND')}\n")
            f.write(f"INTEGRATION_NAME={integration.get('name', 'N/A')}\n\n")
        else:
            f.write("# GitHub Integration\n")
            f.write("# INTEGRATION_ID=<SETUP_REQUIRED_VIA_UI>\n")
            f.write("# Visit: https://smith.langchain.com/settings\n\n")

        f.write("# API Endpoints\n")
        f.write(f"CONTROL_PLANE_BASE={CONTROL_PLANE_BASE}\n")
        f.write(f"LANGSMITH_API_BASE={LANGSMITH_API_BASE}\n")

    print("\n[OK] Credentials saved to: .env.deployment")

def main():
    print("=" * 70)
    print("LANGSMITH CREDENTIAL RETRIEVAL")
    print("Using Official Control Plane API")
    print("=" * 70)

    # Step 1: Get workspace
    workspace = get_workspaces()

    if not workspace:
        print("\n[ERROR] Failed to retrieve workspace information")
        sys.exit(1)

    tenant_id = workspace.get("tenant_id")

    # Step 2: Get GitHub integration
    integration = get_github_integrations(tenant_id)

    # Step 3: List deployments
    deployments = list_deployments(tenant_id)

    # Step 4: Save credentials
    save_credentials(workspace, integration, deployments)

    # Summary
    print("\n" + "=" * 70)
    print("CREDENTIAL RETRIEVAL COMPLETE")
    print("=" * 70)

    print("\n[SUMMARY]")
    print(f"Workspace ID: {workspace['id']}")
    if tenant_id:
        print(f"Tenant ID: {tenant_id}")

    if integration:
        print(f"GitHub Integration: {integration.get('id')} (READY)")
        print("\n[NEXT STEP]")
        print("Run: python deploy_official_cli.py")
    else:
        print("GitHub Integration: NOT FOUND")
        print("\n[ACTION REQUIRED]")
        print("1. Visit: https://smith.langchain.com/settings")
        print("2. Connect GitHub integration")
        print("3. Re-run this script")
        print("4. Then run: python deploy_official_cli.py")

if __name__ == "__main__":
    main()
