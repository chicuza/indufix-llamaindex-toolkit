"""Find GitHub integration across different API endpoints"""
import requests
import json

LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"

# Try both API bases
API_BASES = [
    "https://api.smith.langchain.com",  # Regular LangSmith API
    "https://api.host.langchain.com"     # Control Plane API
]

def get_headers():
    return {
        "Authorization": f"Bearer {LANGSMITH_API_KEY}",
        "X-API-Key": LANGSMITH_API_KEY,
        "Content-Type": "application/json"
    }

def search_for_integrations():
    print("=" * 70)
    print("BUSCANDO GITHUB INTEGRATION EM TODOS OS ENDPOINTS")
    print("=" * 70)

    endpoints_to_try = [
        # Control Plane endpoints
        "/v1/integrations/github",
        "/v1/integrations",
        "/v2/integrations/github",
        "/v2/integrations",
        "/integrations/github",
        "/integrations",
        # Workspace endpoints
        "/v1/workspaces/current/integrations",
        "/v1/workspaces/current/integrations/github",
        # OAuth/Auth endpoints
        "/v1/oauth/github",
        "/v2/oauth/github",
        # Settings endpoints
        "/v1/settings/integrations",
        "/v1/settings/integrations/github"
    ]

    for base_url in API_BASES:
        print(f"\n{'='*70}")
        print(f"API BASE: {base_url}")
        print(f"{'='*70}")

        for endpoint in endpoints_to_try:
            url = f"{base_url}{endpoint}"
            print(f"\nTesting: {endpoint}")

            try:
                response = requests.get(url, headers=get_headers(), timeout=30)
                status = response.status_code

                if status == 200:
                    data = response.json()
                    print(f"  Status: {status} - SUCCESS!")
                    print(f"  Response: {json.dumps(data, indent=2)[:500]}")

                    # If we found integrations, save and return
                    if data and (isinstance(data, list) or 'integrations' in str(data).lower()):
                        print(f"\n  INTEGRATION FOUND!")

                        with open(".github_integration.json", "w") as f:
                            json.dump({
                                "endpoint": url,
                                "data": data
                            }, f, indent=2)

                        return data

                elif status == 404:
                    print(f"  Status: {status} - Not Found")
                elif status in [401, 403]:
                    print(f"  Status: {status} - Auth Error: {response.text[:200]}")
                else:
                    print(f"  Status: {status} - {response.text[:200]}")

            except Exception as e:
                print(f"  Error: {str(e)[:100]}")

    return None

def try_direct_integration_creation():
    """Try to create GitHub integration via API"""
    print("\n" + "=" * 70)
    print("TENTANDO CRIAR GITHUB INTEGRATION VIA API")
    print("=" * 70)

    url = "https://api.host.langchain.com/v1/integrations/github"

    payload = {
        "repository": "chicuza/indufix-llamaindex-toolkit",
        "access_token": "ghp_XXX"  # This would need to be a GitHub PAT
    }

    try:
        response = requests.post(url, headers=get_headers(), json=payload, timeout=30)
        print(f"\nStatus: {response.status_code}")
        print(f"Response: {response.text}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Search for existing integrations
    integration = search_for_integrations()

    if integration:
        print("\n" + "=" * 70)
        print("SUCCESS - INTEGRATION ENCONTRADA!")
        print("=" * 70)
        print(f"\nData: {json.dumps(integration, indent=2)}")
        print("\nInformacao salva em .github_integration.json")
        print("\nAgora execute: python deploy_to_langsmith.py")
    else:
        print("\n" + "=" * 70)
        print("INTEGRATION NAO ENCONTRADA VIA API")
        print("=" * 70)
        print("\nA GitHub integration deve ser criada via UI:")
        print("1. Acesse: https://smith.langchain.com/settings")
        print("2. Procure por 'Integrations' ou 'GitHub'")
        print("3. Conecte sua conta GitHub")
        print("4. Autorize o repositorio: chicuza/indufix-llamaindex-toolkit")
        print("\nApos conectar, a integration estara disponivel para deployment via UI:")
        print("https://smith.langchain.com/deployments")
