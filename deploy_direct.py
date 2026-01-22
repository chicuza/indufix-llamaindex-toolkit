"""Deploy directly without GitHub integration ID - try alternative approaches"""
import requests
import json
import sys

LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"
LLAMA_CLOUD_API_KEY = "llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm"
CONTROL_PLANE_BASE = "https://api.host.langchain.com"
GITHUB_REPO_URL = "https://github.com/chicuza/indufix-llamaindex-toolkit"
DEPLOYMENT_NAME = "indufix-llamaindex-toolkit"

def get_headers():
    """Headers that work based on debug"""
    return {
        "Authorization": f"Bearer {LANGSMITH_API_KEY}",
        "X-API-Key": LANGSMITH_API_KEY,
        "Content-Type": "application/json"
    }

def try_deployment_approaches():
    """Try different approaches to create deployment"""
    print("=" * 70)
    print("TENTATIVAS DE DEPLOYMENT DIRETO")
    print("=" * 70)

    # Approach 1: Try without integration_id (maybe it's optional)
    print("\n[Approach 1] Tentando deployment sem integration_id...")
    payload1 = {
        "name": DEPLOYMENT_NAME,
        "source": "github",
        "source_config": {
            "repo_url": GITHUB_REPO_URL,
            "deployment_type": "dev_free",
            "build_on_push": True
        },
        "source_revision_config": {
            "repo_ref": "main",
            "langgraph_config_path": "toolkit.toml"
        },
        "secrets": [
            {
                "name": "LLAMA_CLOUD_API_KEY",
                "value": LLAMA_CLOUD_API_KEY
            }
        ]
    }

    url = f"{CONTROL_PLANE_BASE}/v2/deployments"
    response = requests.post(url, headers=get_headers(), json=payload1, timeout=60)

    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:1000]}")

    if response.status_code in [200, 201]:
        print("\nSUCCESS - Deployment criado!")
        return response.json()

    # Approach 2: Try with empty string integration_id
    print("\n[Approach 2] Tentando com integration_id vazio...")
    payload2 = payload1.copy()
    payload2["source_config"]["integration_id"] = ""

    response = requests.post(url, headers=get_headers(), json=payload2, timeout=60)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:1000]}")

    if response.status_code in [200, 201]:
        print("\nSUCCESS - Deployment criado!")
        return response.json()

    # Approach 3: Try external_docker source
    print("\n[Approach 3] Tentando com external_docker source...")
    payload3 = {
        "name": DEPLOYMENT_NAME,
        "source": "external_docker",
        "source_config": {
            "deployment_type": "dev_free"
        },
        "source_revision_config": {
            "image_uri": "ghcr.io/chicuza/indufix-llamaindex-toolkit:latest"
        },
        "secrets": [
            {
                "name": "LLAMA_CLOUD_API_KEY",
                "value": LLAMA_CLOUD_API_KEY
            }
        ]
    }

    response = requests.post(url, headers=get_headers(), json=payload3, timeout=60)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:1000]}")

    if response.status_code in [200, 201]:
        print("\nSUCCESS - Deployment criado!")
        return response.json()

    # Approach 4: Check OpenAPI spec for required fields
    print("\n[Approach 4] Obtendo especificacao OpenAPI...")
    spec_url = f"{CONTROL_PLANE_BASE}/openapi.json"
    response = requests.get(spec_url, timeout=30)

    if response.status_code == 200:
        spec = response.json()

        # Find deployment create schema
        if "paths" in spec and "/v2/deployments" in spec["paths"]:
            post_spec = spec["paths"]["/v2/deployments"].get("post", {})
            request_body = post_spec.get("requestBody", {})

            print("\nSchema encontrado:")
            print(json.dumps(request_body, indent=2)[:2000])

            # Extract required fields
            if "content" in request_body:
                schema = request_body["content"]["application/json"]["schema"]
                print(f"\nRequired fields: {schema.get('required', [])}")

    print("\n" + "=" * 70)
    print("TODAS AS TENTATIVAS FALHARAM")
    print("=" * 70)
    return None

def check_github_app_installation():
    """Check if there's a GitHub App that needs to be installed"""
    print("\n" + "=" * 70)
    print("VERIFICANDO GITHUB APP")
    print("=" * 70)

    # Try to get GitHub app installation URL
    endpoints = [
        "/v1/github/app/install",
        "/v1/integrations/github/app",
        "/v2/integrations/github/app",
        "/github/install"
    ]

    for endpoint in endpoints:
        url = f"{CONTROL_PLANE_BASE}{endpoint}"
        print(f"\nTentando: {endpoint}")

        try:
            response = requests.get(url, headers=get_headers(), timeout=30)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)[:500]}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Try deployment approaches
    deployment = try_deployment_approaches()

    if deployment:
        print(f"\nDeployment ID: {deployment.get('id')}")
        print(f"URL: {deployment.get('url')}")

        # Save deployment info
        with open(".deployment.json", "w") as f:
            json.dump(deployment, f, indent=2)

        print("\nDeployment info salvo em .deployment.json")
    else:
        # Check GitHub app
        check_github_app_installation()

        print("\n" + "=" * 70)
        print("PROXIMOS PASSOS")
        print("=" * 70)
        print("\nO deployment via API requer GitHub integration.")
        print("\nOpcoes:")
        print("\n1. UI Deployment (RECOMENDADO):")
        print("   https://smith.langchain.com/deployments")
        print("\n2. Verificar se GitHub App precisa ser instalado:")
        print("   https://smith.langchain.com/settings")
        print("\n3. Usar langgraph CLI (se disponivel):")
        print("   langgraph deploy --repo chicuza/indufix-llamaindex-toolkit")
