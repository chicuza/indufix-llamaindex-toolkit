"""Script para verificar e configurar GitHub integration"""
import requests
import webbrowser
import sys

LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"
CONTROL_PLANE_BASE = "https://api.host.langchain.com"

def get_headers():
    return {
        "Authorization": f"Bearer {LANGSMITH_API_KEY}",
        "Content-Type": "application/json"
    }

def check_github_integration():
    """Verifica integracao GitHub existente"""
    print("=" * 70)
    print("VERIFICACAO DE INTEGRACAO GITHUB")
    print("=" * 70)

    # Tentar diferentes endpoints
    endpoints_to_try = [
        "/v1/integrations/github",
        "/v1/integrations",
        "/v2/integrations/github",
        "/v2/integrations"
    ]

    print("\n[1] Verificando integracoes existentes...")

    for endpoint in endpoints_to_try:
        url = f"{CONTROL_PLANE_BASE}{endpoint}"
        print(f"\n   Tentando: {endpoint}")

        try:
            response = requests.get(url, headers=get_headers(), timeout=30)
            print(f"   Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"   Resposta: {data}")

                if data:
                    print(f"\n   OK - Integracoes encontradas!")
                    return data
            elif response.status_code == 404:
                print("   404 - Endpoint nao encontrado")
            else:
                print(f"   Erro: {response.text[:200]}")

        except Exception as e:
            print(f"   Erro: {e}")

    print("\n[2] Verificando endpoint de instalacao...")
    install_url = f"{CONTROL_PLANE_BASE}/v1/integrations/github/install"

    try:
        response = requests.get(install_url, headers=get_headers(), timeout=30)
        print(f"   Status: {response.status_code}")
        print(f"   Resposta: {response.text[:500]}")

        if response.status_code == 200:
            data = response.json()

            # Se houver uma URL de redirect, abrir no navegador
            if 'url' in data or 'install_url' in data or 'redirect_url' in data:
                install_url_actual = data.get('url') or data.get('install_url') or data.get('redirect_url')
                print(f"\n   URL de instalacao GitHub encontrada!")
                print(f"   {install_url_actual}")

                print("\n   Deseja abrir esta URL no navegador? (s/n): ", end="")
                choice = input().lower()

                if choice == 's':
                    webbrowser.open(install_url_actual)
                    print("\n   Navegador aberto. Siga as instrucoes para conectar GitHub.")
                else:
                    print(f"\n   Acesse manualmente: {install_url_actual}")

                print("\n   Apos conectar GitHub, execute:")
                print("   python deploy_to_langsmith.py")
                return None

    except Exception as e:
        print(f"   Erro: {e}")

    print("\n" + "=" * 70)
    print("CONFIGURACAO MANUAL NECESSARIA")
    print("=" * 70)

    print("\nNenhuma integracao GitHub encontrada via API.")
    print("\nOpcoes:")
    print("\n1. Conectar GitHub via UI (RECOMENDADO):")
    print("   - Acesse: https://smith.langchain.com/settings")
    print("   - Va em 'Integrations' ou 'GitHub'")
    print("   - Clique 'Connect GitHub'")
    print("   - Autorize acesso ao repositorio chicuza/indufix-llamaindex-toolkit")
    print("\n2. Apos conectar, execute:")
    print("   python deploy_to_langsmith.py")

    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_github_integration()
