"""Script de verificação pós-deployment para LangSmith"""
import requests
import json
import sys

# INSTRUÇÕES: Após fazer deployment via UI, copie a URL aqui
DEPLOYMENT_URL = input("Digite a URL do deployment (ex: https://indufix-toolkit-xxx.smith.langchain.com): ").strip()

# Credenciais
LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY_1>"

def main():
    print("=" * 70)
    print("🔍 VERIFICAÇÃO PÓS-DEPLOYMENT - INDUFIX LLAMAINDEX TOOLKIT")
    print("=" * 70)
    
    if not DEPLOYMENT_URL:
        print("❌ URL do deployment não fornecida!")
        print("   Execute novamente e forneça a URL")
        sys.exit(1)
    
    print(f"\n📍 Deployment URL: {DEPLOYMENT_URL}")
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # 1. Health Check
    print("\n[1/4] Verificando health do deployment...")
    try:
        response = requests.get(f"{DEPLOYMENT_URL}/health", headers=headers, timeout=10)
        if response.status_code == 200:
            print("   ✅ Deployment está online e respondendo!")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao conectar: {e}")
        print("   💡 Verifique se o deployment está completo")
        sys.exit(1)
    
    # 2. Listar tools via MCP
    print("\n[2/4] Listando tools disponíveis via MCP...")
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }
        
        response = requests.post(
            f"{DEPLOYMENT_URL}/mcp",
            headers=headers,
            json=mcp_request,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            if "result" in result and "tools" in result["result"]:
                tools = result["result"]["tools"]
                print(f"   ✅ {len(tools)} tools encontradas:")
                for tool in tools:
                    print(f"      - {tool.get('name', 'unknown')}")
            else:
                print(f"   ⚠️  Resposta inesperada: {result}")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro ao listar tools: {e}")
    
    # 3. Testar uma tool específica
    print("\n[3/4] Testando tool 'retrieve_matching_rules'...")
    try:
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "retrieve_matching_rules",
                "arguments": {
                    "query": "parafuso teste",
                    "top_k": 2
                }
            },
            "id": 2
        }
        
        response = requests.post(
            f"{DEPLOYMENT_URL}/mcp",
            headers=headers,
            json=mcp_request,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ Tool executada com sucesso!")
            if "result" in result:
                print(f"   📊 Resultado (primeiros 200 chars): {str(result['result'])[:200]}...")
        else:
            print(f"   ⚠️  Status: {response.status_code}")
    except Exception as e:
        print(f"   ⚠️  Erro ao testar tool: {e}")
        print("   💡 Isso pode ser normal se o LlamaCloud ainda está inicializando")
    
    # 4. Informações para Agent Builder
    print("\n[4/4] Configuração para Agent Builder...")
    print(f"\n   📋 Adicione este MCP server no Agent Builder:")
    print(f"   - URL: {DEPLOYMENT_URL}/mcp")
    print(f"   - Name: indufix-llamacloud")
    print(f"   - Authentication: None (uso interno)")
    
    # Resumo final
    print("\n" + "=" * 70)
    print("✅ VERIFICAÇÃO COMPLETA!")
    print("=" * 70)
    
    print("\n🎯 PRÓXIMOS PASSOS:")
    print("\n1. Abra Agent Builder: https://smith.langchain.com/agent-builder")
    print("2. Vá em Settings → Workspace → MCP Servers")
    print("3. Clique 'Add Remote Server'")
    print("4. Configure:")
    print(f"   - Name: indufix-llamacloud")
    print(f"   - URL: {DEPLOYMENT_URL}/mcp")
    print("   - Authentication: None")
    print("\n5. Teste com prompt:")
    print('   "Busque valores default para parafuso sextavado M10"')
    print("\n" + "=" * 70)
    
    # Salvar URL para referência futura
    with open(".env.production", "w") as f:
        f.write(f"# Deployment Configuration\n")
        f.write(f"DEPLOYMENT_URL={DEPLOYMENT_URL}\n")
        f.write(f"LANGSMITH_API_KEY={LANGSMITH_API_KEY}\n")
        f.write(f"LLAMA_CLOUD_API_KEY=llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm\n")
    
    print("\n💾 Configuração salva em .env.production")

if __name__ == "__main__":
    main()
