"""Find GitHub integration ID from LangSmith API."""
import os
import sys
import requests
from pathlib import Path

# Try to load dotenv if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("Warning: python-dotenv not installed, using environment variables only")

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
WORKSPACE_ID = os.getenv("WORKSPACE_ID", "950d802b-125a-45bc-88e4-3d7d0edee182")
CONTROL_PLANE_BASE = "https://api.host.langchain.com"

def get_headers():
    """Headers for authentication."""
    return {
        "X-Api-Key": LANGSMITH_API_KEY,
        "X-Tenant-Id": WORKSPACE_ID,
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

def list_integrations():
    """List all integrations from LangSmith API."""
    print("=" * 70)
    print("FETCHING GITHUB INTEGRATIONS FROM LANGSMITH")
    print("=" * 70)
    print(f"API Key: {LANGSMITH_API_KEY[:20]}..." if LANGSMITH_API_KEY else "NOT SET")
    print(f"Workspace ID: {WORKSPACE_ID}")
    print("=" * 70)

    # Try different API endpoints
    endpoints = [
        "/v1/integrations",
        "/v1/integrations/github",
        "/v2/integrations",
        "/v2/integrations/github",
        "/integrations",
        "/integrations/github"
    ]

    found_integrations = []

    for endpoint in endpoints:
        url = f"{CONTROL_PLANE_BASE}{endpoint}"
        print(f"\nTrying endpoint: {endpoint}")

        try:
            response = requests.get(url, headers=get_headers(), timeout=30)
            print(f"  Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()

                # Handle different response formats
                integrations = []

                if isinstance(data, list):
                    integrations = data
                elif isinstance(data, dict):
                    if 'integrations' in data:
                        integrations = data['integrations']
                    elif 'id' in data:
                        # Single integration response
                        integrations = [data]

                # Extract integration info
                for item in integrations:
                    if isinstance(item, dict) and 'id' in item:
                        integration_info = {
                            'id': item.get('id'),
                            'type': item.get('type', 'unknown'),
                            'name': item.get('name', 'unknown'),
                            'status': item.get('status', 'unknown'),
                            'endpoint': endpoint
                        }

                        # Only add GitHub integrations
                        if 'github' in str(integration_info.get('type', '')).lower() or \
                           'github' in endpoint.lower():
                            found_integrations.append(integration_info)
                            print(f"  FOUND: {integration_info}")

            elif response.status_code == 404:
                print("  Endpoint not found (404)")
            elif response.status_code == 401:
                print("  Unauthorized (401) - Check API key and workspace ID")
            else:
                print(f"  Error: {response.text[:200]}")

        except requests.exceptions.Timeout:
            print("  Timeout - endpoint took too long to respond")
        except requests.exceptions.RequestException as e:
            print(f"  Request error: {e}")
        except Exception as e:
            print(f"  Unexpected error: {e}")

    # Display results
    print("\n" + "=" * 70)
    if found_integrations:
        print(f"SUCCESS - FOUND {len(found_integrations)} INTEGRATION(S)")
        print("=" * 70)

        for i, integration in enumerate(found_integrations, 1):
            print(f"\nIntegration #{i}:")
            print(f"  ID: {integration['id']}")
            print(f"  Type: {integration['type']}")
            print(f"  Name: {integration['name']}")
            print(f"  Status: {integration['status']}")
            print(f"  Found at: {integration['endpoint']}")

        # Return the first GitHub integration
        selected = found_integrations[0]
        print("\n" + "=" * 70)
        print("SELECTED INTEGRATION (first found):")
        print("=" * 70)
        print(f"\nINTEGRATION_ID={selected['id']}")
        print("\nAdd this to your .env file:")
        print("-" * 70)
        print(f"INTEGRATION_ID={selected['id']}")
        print("-" * 70)
        print("\nAdd this to GitHub Secrets:")
        print("1. Go to: https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions")
        print("2. Click 'New repository secret'")
        print("3. Name: INTEGRATION_ID")
        print(f"4. Value: {selected['id']}")

        return selected['id']
    else:
        print("NO GITHUB INTEGRATION FOUND")
        print("=" * 70)
        print("\nPOSSIBLE REASONS:")
        print("1. GitHub not connected to LangSmith workspace")
        print("2. API key doesn't have permission to view integrations")
        print("3. Wrong workspace ID")
        print("4. Integration exists but API endpoint is different")

        print("\nNEXT STEPS:")
        print("\nOption 1: Connect GitHub via LangSmith UI")
        print("  1. Go to: https://smith.langchain.com/settings")
        print("  2. Navigate to: Integrations or Workspace Settings")
        print("  3. Click 'Connect GitHub' or 'Add Integration'")
        print("  4. Authorize LangSmith to access your GitHub account")
        print("  5. Select repository: chicuza/indufix-llamaindex-toolkit")
        print("  6. After connecting, look for Integration ID in URL or settings")
        print("  7. Re-run this script: python find_integration_id.py")

        print("\nOption 2: Use existing deployment's integration")
        print("  If you already have a deployment that uses GitHub:")
        print("  1. Go to: https://smith.langchain.com/deployments")
        print("  2. Open an existing GitHub deployment")
        print("  3. Check deployment settings for 'integration_id'")
        print("  4. Copy that ID")

        print("\nOption 3: Manual API exploration")
        print("  Try these LangSmith UI pages and look for integration ID:")
        print("  - https://smith.langchain.com/settings")
        print("  - https://smith.langchain.com/settings/integrations")
        print("  - https://smith.langchain.com/workspace")

        return None

def main():
    """Main entry point."""
    if not LANGSMITH_API_KEY:
        print("=" * 70)
        print("ERROR: LANGSMITH_API_KEY not set")
        print("=" * 70)
        print("\nSet the API key in one of these ways:")
        print("\n1. Environment variable:")
        print("   export LANGSMITH_API_KEY=lsv2_sk_...")
        print("   (Windows: set LANGSMITH_API_KEY=lsv2_sk_...)")
        print("\n2. .env file (create in same directory as this script):")
        print("   LANGSMITH_API_KEY=lsv2_sk_...")
        print("   WORKSPACE_ID=950d802b-125a-45bc-88e4-3d7d0edee182")
        print("\n3. Pass via command line:")
        print("   LANGSMITH_API_KEY=lsv2_sk_... python find_integration_id.py")
        sys.exit(1)

    integration_id = list_integrations()

    if integration_id:
        # Save to .env file if it exists
        env_file = Path(__file__).parent / '.env'
        if env_file.exists():
            print(f"\n.env file found at: {env_file}")
            print("Checking if INTEGRATION_ID already set...")

            with open(env_file, 'r') as f:
                content = f.read()

            if 'INTEGRATION_ID=' in content:
                print("INTEGRATION_ID already exists in .env file")
                print("Update manually if needed")
            else:
                print("Adding INTEGRATION_ID to .env file...")
                with open(env_file, 'a') as f:
                    f.write(f"\n# GitHub Integration ID (auto-detected)\n")
                    f.write(f"INTEGRATION_ID={integration_id}\n")
                print("INTEGRATION_ID added to .env file")

        print("\n" + "=" * 70)
        print("NEXT STEPS:")
        print("=" * 70)
        print("\n1. Add INTEGRATION_ID to GitHub Secrets (if using GitHub Actions)")
        print("2. Proceed to Phase 2 of deployment workflow")
        print("3. See: DEPLOYMENT_WORKFLOW_PLAN.md")

        sys.exit(0)
    else:
        print("\n" + "=" * 70)
        print("INTEGRATION_ID NOT FOUND - MANUAL SETUP REQUIRED")
        print("=" * 70)
        print("\nFollow the instructions above to connect GitHub to LangSmith")
        sys.exit(1)

if __name__ == "__main__":
    main()
