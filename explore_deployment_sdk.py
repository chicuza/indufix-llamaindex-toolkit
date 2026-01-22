"""Explorar opcoes de deployment via LangSmith SDK"""
import os
from langsmith import Client
import inspect

LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"

def main():
    print("=" * 70)
    print("EXPLORANDO SDK LANGSMITH PARA DEPLOYMENT PROGRAMATICO")
    print("=" * 70)

    os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
    client = Client(api_key=LANGSMITH_API_KEY)

    # 1. Listar todos os metodos do client relacionados a deployment
    print("\n[1] Metodos do Client relacionados a 'deploy':")
    deployment_methods = [m for m in dir(client) if 'deploy' in m.lower()]
    for method in deployment_methods:
        print(f"   - {method}")

    # 2. Listar metodos relacionados a 'toolkit'
    print("\n[2] Metodos do Client relacionados a 'toolkit':")
    toolkit_methods = [m for m in dir(client) if 'toolkit' in m.lower() or 'tool' in m.lower()]
    for method in toolkit_methods:
        if not method.startswith('_'):
            print(f"   - {method}")

    # 3. Listar metodos relacionados a 'repo' ou 'repository'
    print("\n[3] Metodos do Client relacionados a 'repo':")
    repo_methods = [m for m in dir(client) if 'repo' in m.lower()]
    for method in repo_methods:
        print(f"   - {method}")

    # 4. Tentar listar deployments existentes
    print("\n[4] Tentando listar deployments existentes...")
    try:
        # Tentar metodos comuns de listagem
        if hasattr(client, 'list_deployments'):
            deployments = list(client.list_deployments())
            print(f"   OK - Encontrados {len(deployments)} deployments")
            for dep in deployments[:3]:
                print(f"   - {dep}")
        elif hasattr(client, 'get_deployments'):
            deployments = client.get_deployments()
            print(f"   OK - get_deployments retornou: {deployments}")
        else:
            print("   INFO - Nenhum metodo list_deployments ou get_deployments encontrado")
    except Exception as e:
        print(f"   ERRO: {e}")

    # 5. Verificar se existe API de deployment via HTTP
    print("\n[5] Verificando endpoints HTTP para deployment...")
    print("   Documentacao API: https://api.smith.langchain.com/redoc")

    # 6. Tentar usar requests diretamente na API
    print("\n[6] Tentando chamar API diretamente...")
    import requests

    headers = {
        "Authorization": f"Bearer {LANGSMITH_API_KEY}",
        "Content-Type": "application/json"
    }

    # Tentar endpoint de deployments
    urls_to_try = [
        "https://api.smith.langchain.com/api/v1/deployments",
        "https://api.smith.langchain.com/deployments",
        "https://api.smith.langchain.com/api/v1/toolkits",
        "https://api.smith.langchain.com/toolkits"
    ]

    for url in urls_to_try:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"   {url}")
            print(f"      Status: {response.status_code}")
            if response.status_code == 200:
                print(f"      Response: {response.json()}")
        except Exception as e:
            print(f"   {url} - ERRO: {e}")

    print("\n" + "=" * 70)
    print("EXPLORACAO COMPLETA")
    print("=" * 70)

if __name__ == "__main__":
    main()
