"""Script para deploy programatico do toolkit no LangSmith via Control Plane API"""
import requests
import sys
import json
from typing import Dict, Any

# Configuracao
LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"
LLAMA_CLOUD_API_KEY = "llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm"

# URLs API
CONTROL_PLANE_BASE = "https://api.host.langchain.com"
GITHUB_REPO_URL = "https://github.com/chicuza/indufix-llamaindex-toolkit"
DEPLOYMENT_NAME = "indufix-llamaindex-toolkit"

def get_headers() -> Dict[str, str]:
    """Headers para autenticacao na API"""
    return {
        "Authorization": f"Bearer {LANGSMITH_API_KEY}",
        "Content-Type": "application/json"
    }

def get_github_integration_id() -> str:
    """Obtem o integration_id do GitHub"""
    print("\n[1/5] Obtendo GitHub integration ID...")

    # Primeiro, verificar se ja existe uma integracao
    url = f"{CONTROL_PLANE_BASE}/v1/integrations/github"
    response = requests.get(url, headers=get_headers(), timeout=30)

    if response.status_code == 200:
        integrations = response.json()
        if integrations:
            integration_id = integrations[0].get('id')
            print(f"   OK - Integration ID encontrado: {integration_id}")
            return integration_id

    print("   AVISO - Nenhuma integracao GitHub encontrada")
    print("   ACAO REQUERIDA: Conecte GitHub em https://smith.langchain.com/settings")
    print("   Apos conectar, execute este script novamente")
    sys.exit(1)

def create_deployment(integration_id: str) -> Dict[str, Any]:
    """Cria o deployment via API"""
    print("\n[2/5] Criando deployment via Control Plane API...")

    url = f"{CONTROL_PLANE_BASE}/v2/deployments"

    payload = {
        "name": DEPLOYMENT_NAME,
        "source": "github",
        "source_config": {
            "integration_id": integration_id,
            "repo_url": GITHUB_REPO_URL,
            "deployment_type": "dev_free",  # Free tier
            "build_on_push": True  # Auto-deploy on git push
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

    print(f"   Payload: {json.dumps(payload, indent=2)}")

    response = requests.post(url, headers=get_headers(), json=payload, timeout=60)

    if response.status_code in [200, 201]:
        deployment = response.json()
        print(f"   OK - Deployment criado com sucesso!")
        print(f"   Deployment ID: {deployment.get('id')}")
        print(f"   Revision ID: {deployment.get('latest_revision_id')}")
        return deployment
    else:
        print(f"   ERRO - Status: {response.status_code}")
        print(f"   Resposta: {response.text}")

        # Se deployment ja existe, tentar obter
        if "already exists" in response.text.lower():
            print("\n   Deployment ja existe. Tentando obter informacoes...")
            return get_existing_deployment()

        sys.exit(1)

def get_existing_deployment() -> Dict[str, Any]:
    """Obtem deployment existente"""
    url = f"{CONTROL_PLANE_BASE}/v2/deployments"
    response = requests.get(url, headers=get_headers(), timeout=30)

    if response.status_code == 200:
        deployments = response.json()
        for deployment in deployments:
            if deployment.get('name') == DEPLOYMENT_NAME:
                print(f"   OK - Deployment encontrado: {deployment.get('id')}")
                return deployment

    print("   ERRO - Nao foi possivel obter deployment existente")
    sys.exit(1)

def check_deployment_status(deployment: Dict[str, Any]) -> None:
    """Verifica status do deployment"""
    print("\n[3/5] Verificando status do deployment...")

    deployment_id = deployment.get('id')
    url = f"{CONTROL_PLANE_BASE}/v2/deployments/{deployment_id}"

    response = requests.get(url, headers=get_headers(), timeout=30)

    if response.status_code == 200:
        deployment_info = response.json()
        status = deployment_info.get('status', 'unknown')
        print(f"   Status: {status}")

        if 'url' in deployment_info:
            print(f"   URL: {deployment_info['url']}")

        return deployment_info
    else:
        print(f"   AVISO - Nao foi possivel verificar status: {response.status_code}")

def get_deployment_url(deployment: Dict[str, Any]) -> str:
    """Obtem URL do deployment"""
    print("\n[4/5] Obtendo URL do deployment...")

    # Tentar diferentes campos onde a URL pode estar
    url = deployment.get('url') or deployment.get('endpoint_url')

    if not url:
        deployment_id = deployment.get('id')
        # URL padrao baseado no deployment ID
        url = f"https://{deployment_id}.smith.langchain.com"

    print(f"   URL: {url}")
    return url

def save_deployment_info(deployment: Dict[str, Any], url: str) -> None:
    """Salva informacoes do deployment"""
    print("\n[5/5] Salvando informacoes do deployment...")

    deployment_info = {
        "deployment_id": deployment.get('id'),
        "deployment_name": DEPLOYMENT_NAME,
        "deployment_url": url,
        "mcp_url": f"{url}/mcp",
        "revision_id": deployment.get('latest_revision_id'),
        "github_repo": GITHUB_REPO_URL,
        "auto_deploy": True
    }

    # Salvar em arquivo JSON
    with open(".deployment.json", "w") as f:
        json.dump(deployment_info, f, indent=2)

    print("   OK - Informacoes salvas em .deployment.json")

    # Salvar em .env.production
    with open(".env.production", "w") as f:
        f.write(f"# Deployment Configuration\n")
        f.write(f"DEPLOYMENT_ID={deployment_info['deployment_id']}\n")
        f.write(f"DEPLOYMENT_URL={deployment_info['deployment_url']}\n")
        f.write(f"MCP_URL={deployment_info['mcp_url']}\n")
        f.write(f"LANGSMITH_API_KEY={LANGSMITH_API_KEY}\n")
        f.write(f"LLAMA_CLOUD_API_KEY={LLAMA_CLOUD_API_KEY}\n")

    print("   OK - Configuracao salva em .env.production")

def main():
    print("=" * 70)
    print("DEPLOYMENT PROGRAMATICO - INDUFIX LLAMAINDEX TOOLKIT")
    print("Usando LangSmith Control Plane API")
    print("=" * 70)

    try:
        # 1. Obter GitHub integration ID
        integration_id = get_github_integration_id()

        # 2. Criar deployment
        deployment = create_deployment(integration_id)

        # 3. Verificar status
        deployment_info = check_deployment_status(deployment)
        if deployment_info:
            deployment = deployment_info

        # 4. Obter URL
        url = get_deployment_url(deployment)

        # 5. Salvar informacoes
        save_deployment_info(deployment, url)

        # Resumo final
        print("\n" + "=" * 70)
        print("DEPLOYMENT CONCLUIDO COM SUCESSO!")
        print("=" * 70)

        print(f"\nDeployment ID: {deployment.get('id')}")
        print(f"Deployment URL: {url}")
        print(f"MCP Endpoint: {url}/mcp")

        print("\nPROXIMOS PASSOS:")
        print("\n1. Aguarde ~10-15 minutos para build completar")
        print("\n2. Verifique status em:")
        print(f"   https://smith.langchain.com/deployments/{deployment.get('id')}")
        print("\n3. Execute verificacao pos-deployment:")
        print(f"   python check_deployment.py")
        print(f"   (Digite a URL quando solicitado: {url})")
        print("\n4. Conecte ao Agent Builder:")
        print("   - Acesse: https://smith.langchain.com/agent-builder")
        print("   - Settings → Workspace → MCP Servers")
        print("   - Add Remote Server")
        print(f"   - URL: {url}/mcp")
        print("   - Name: indufix-llamacloud")
        print("\n5. Teste com prompt:")
        print('   "Busque valores default para parafuso sextavado M10"')
        print("\n" + "=" * 70)

    except KeyboardInterrupt:
        print("\n\nDeployment cancelado pelo usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
