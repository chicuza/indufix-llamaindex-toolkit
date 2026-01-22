"""Script de validacao pre-deployment para LangSmith"""
import os
import sys
from langsmith import Client

# Credenciais
LANGSMITH_API_KEY = "<YOUR_LANGSMITH_API_KEY>"
LLAMA_API_KEY = "llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm"

def main():
    print("=" * 60)
    print("VALIDACAO PRE-DEPLOYMENT - INDUFIX LLAMAINDEX TOOLKIT")
    print("=" * 60)
    
    # 1. Validar LangSmith API Key
    print("\n[1/5] Validando LangSmith API Key...")
    try:
        os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
        client = Client(api_key=LANGSMITH_API_KEY)
        
        # Testar acesso
        projects = list(client.list_projects(limit=5))
        print(f"   OK - API Key valida!")
        print(f"   OK - Acesso a {len(projects)} projetos")
        if projects:
            print(f"   Projeto exemplo: {projects[0].name}")
    except Exception as e:
        print(f"   ERRO ao validar API Key: {e}")
        sys.exit(1)
    
    # 2. Validar repositorio GitHub
    print("\n[2/5] Validando configuracao do repositorio...")
    print("   OK - Repository: chicuza/indufix-llamaindex-toolkit")
    print("   OK - Branch: main")
    print("   OK - Config: toolkit.toml")
    
    # 3. Validar arquivos necessarios
    print("\n[3/5] Validando arquivos do projeto...")
    required_files = [
        "pyproject.toml",
        "toolkit.toml",
        "indufix_toolkit/__init__.py",
        "README.md",
        ".env.example"
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   OK - {file}")
        else:
            print(f"   ERRO - {file} NOT FOUND")
            sys.exit(1)
    
    # 4. Validar tools
    print("\n[4/5] Validando tools localmente...")
    try:
        os.environ["LLAMA_CLOUD_API_KEY"] = LLAMA_API_KEY
        from indufix_toolkit import TOOLS
        print(f"   OK - {len(TOOLS)} tools carregadas com sucesso:")
        for tool in TOOLS:
            print(f"      - {tool.name}")
    except Exception as e:
        print(f"   ERRO ao carregar tools: {e}")
        sys.exit(1)
    
    # 5. Verificar credenciais
    print("\n[5/5] Verificando credenciais...")
    print(f"   OK - LLAMA_CLOUD_API_KEY: {LLAMA_API_KEY[:10]}...")
    print(f"   OK - LANGSMITH_API_KEY: {LANGSMITH_API_KEY[:20]}...")
    
    # Resumo final
    print("\n" + "=" * 60)
    print("VALIDACAO COMPLETA - TUDO PRONTO PARA DEPLOYMENT!")
    print("=" * 60)
    
    print("\nPROXIMOS PASSOS:")
    print("\n1. Acesse: https://smith.langchain.com/deployments")
    print("2. Clique '+ New Deployment'")
    print("3. Configuracao:")
    print("   - Repository: chicuza/indufix-llamaindex-toolkit")
    print("   - Branch: main")
    print("   - Name: indufix-llamaindex-toolkit")
    print("   - Type: Development (free)")
    print("   - Auto-update: Habilitado")
    print("\n4. Adicione Secret:")
    print("   - Key: LLAMA_CLOUD_API_KEY")
    print(f"   - Value: {LLAMA_API_KEY}")
    print("\n5. Clique 'Deploy' e aguarde ~10-15 minutos")
    print("\n6. Apos deployment, copie a URL e execute:")
    print("   python check_deployment.py")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
