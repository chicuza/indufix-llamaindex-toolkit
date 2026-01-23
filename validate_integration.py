"""Script de Validação - Integração LlamaIndex Toolkit

Execute este script APÓS configurar o MCP server e subagente na UI
para verificar que tudo está funcionando corretamente.

Uso:
    python validate_integration.py
"""

import os
import requests
import json
from datetime import datetime
from typing import Dict, Any, List

# Configuração
DEPLOYMENT_URL = "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app"
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")  # Required: set via environment variable
WORKSPACE_ID = "950d802b-125a-45bc-88e4-3d7d0edee182"

# Testes
TEST_QUERIES = [
    {
        "name": "Query Simples - Valores Default",
        "query": "Buscar valores default para parafuso sextavado M10",
        "expected_keywords": ["material", "acabamento", "aço", "zincado"],
        "should_not_contain": ["Tools are available", "generic", "template"]
    },
    {
        "name": "Equivalências de Normas",
        "query": "Qual a equivalência da norma DIN 933?",
        "expected_keywords": ["ISO", "4017", "equivalente"],
        "should_not_contain": ["Tools are available", "generic"]
    },
    {
        "name": "Penalidades de Confiança",
        "query": "Qual a penalidade para material inferido como aço carbono?",
        "expected_keywords": ["penalidade", "confiança", "0.", "penalty"],
        "should_not_contain": ["Tools are available", "generic"]
    },
    {
        "name": "Query Complexa - Múltiplos Atributos",
        "query": "Para parafuso sextavado M12 faltam material, acabamento e classe. Me dê valores default e penalidades.",
        "expected_keywords": ["material", "acabamento", "classe", "default", "penalidade"],
        "should_not_contain": ["Tools are available", "generic"]
    }
]


def print_section(title: str):
    print("\n" + "="*70)
    print(title)
    print("="*70)


def test_mcp_endpoint() -> bool:
    """Testa se o MCP endpoint está respondendo"""
    print_section("Teste 1: MCP Endpoint Conectividade")

    try:
        # Teste tools/list
        list_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": 1
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Api-Key": LANGSMITH_API_KEY,
            "X-Tenant-Id": WORKSPACE_ID
        }

        response = requests.post(
            f"{DEPLOYMENT_URL}/mcp",
            json=list_request,
            headers=headers,
            timeout=30
        )

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            tools = result.get("result", {}).get("tools", [])
            print(f"\n[OK] Encontradas {len(tools)} ferramenta(s):")
            for tool in tools:
                print(f"  - {tool.get('name')}")
            return True
        else:
            print(f"\n[ERRO] Status inesperado: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False

    except Exception as e:
        print(f"\n[ERRO] Falha ao conectar: {e}")
        return False


def test_tool_invocation(query: str, test_name: str,
                         expected_keywords: List[str],
                         should_not_contain: List[str]) -> Dict[str, Any]:
    """Testa invocação de ferramenta com validação de resposta"""

    print_section(f"Teste: {test_name}")
    print(f"Query: {query}")

    try:
        call_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "indufix_agent",
                "arguments": {
                    "messages": [
                        {
                            "role": "user",
                            "content": query
                        }
                    ]
                }
            },
            "id": 2
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Api-Key": LANGSMITH_API_KEY,
            "X-Tenant-Id": WORKSPACE_ID
        }

        response = requests.post(
            f"{DEPLOYMENT_URL}/mcp",
            json=call_request,
            headers=headers,
            timeout=60
        )

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code != 200:
            print(f"[ERRO] Falha na requisição: {response.text[:200]}")
            return {
                "success": False,
                "query": query,
                "error": f"HTTP {response.status_code}"
            }

        result = response.json()

        # Extrair resposta
        content = result.get("result", {}).get("content", [])
        if content and len(content) > 0:
            response_text = str(content[0].get("text", ""))
        else:
            response_text = str(result)

        print(f"\nResposta (primeiros 500 chars):")
        print(response_text[:500])
        print("...")

        # Validações
        validations = {
            "has_expected_keywords": False,
            "no_generic_response": True,
            "response_length_ok": len(response_text) > 50
        }

        # Verificar keywords esperadas
        keywords_found = []
        for keyword in expected_keywords:
            if keyword.lower() in response_text.lower():
                keywords_found.append(keyword)

        validations["has_expected_keywords"] = len(keywords_found) >= 1

        # Verificar que NÃO contém frases genéricas
        for generic in should_not_contain:
            if generic.lower() in response_text.lower():
                validations["no_generic_response"] = False
                break

        # Resultado
        all_passed = all(validations.values())

        print(f"\n[VALIDAÇÕES]")
        print(f"  Keywords encontradas: {keywords_found} ({len(keywords_found)}/{len(expected_keywords)})")
        print(f"  Sem resposta genérica: {'✅' if validations['no_generic_response'] else '❌'}")
        print(f"  Tamanho adequado: {'✅' if validations['response_length_ok'] else '❌'}")

        if all_passed:
            print(f"\n[✅ PASSOU] Teste '{test_name}' passou!")
        else:
            print(f"\n[❌ FALHOU] Teste '{test_name}' falhou!")

        return {
            "success": all_passed,
            "query": query,
            "response": response_text,
            "validations": validations,
            "keywords_found": keywords_found
        }

    except Exception as e:
        print(f"\n[ERRO] Exceção durante teste: {e}")
        return {
            "success": False,
            "query": query,
            "error": str(e)
        }


def main():
    print("="*70)
    print("VALIDAÇÃO DE INTEGRAÇÃO - LlamaIndex Toolkit")
    print("="*70)

    # Validate API key is set
    if not LANGSMITH_API_KEY:
        print("\n[ERRO] LANGSMITH_API_KEY environment variable not set!")
        print("\nSet it with:")
        print("  export LANGSMITH_API_KEY=lsv2_sk_your-api-key-here  # Linux/Mac")
        print("  set LANGSMITH_API_KEY=lsv2_sk_your-api-key-here     # Windows")
        return 1

    print(f"\nDeployment: {DEPLOYMENT_URL}")
    print(f"Workspace: {WORKSPACE_ID}")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Passo 1: Testar conectividade MCP
    mcp_ok = test_mcp_endpoint()

    if not mcp_ok:
        print("\n" + "="*70)
        print("[ERRO CRÍTICO] MCP endpoint não está acessível!")
        print("="*70)
        print("\nVerifique:")
        print("1. Deployment está online")
        print("2. LANGSMITH_API_KEY está correto")
        print("3. URL do deployment está correto")
        return 1

    # Passo 2: Executar testes de queries
    print("\n" + "="*70)
    print("INICIANDO TESTES DE QUERIES")
    print("="*70)

    results = []
    for test in TEST_QUERIES:
        result = test_tool_invocation(
            query=test["query"],
            test_name=test["name"],
            expected_keywords=test["expected_keywords"],
            should_not_contain=test["should_not_contain"]
        )
        results.append(result)

    # Resumo final
    print_section("RESUMO DOS TESTES")

    passed = sum(1 for r in results if r.get("success"))
    total = len(results)

    print(f"\nTestes Executados: {total}")
    print(f"Testes Passados: {passed}")
    print(f"Taxa de Sucesso: {(passed/total*100):.1f}%")

    print("\n[RESULTADOS DETALHADOS]")
    for i, result in enumerate(results, 1):
        status = "✅ PASSOU" if result.get("success") else "❌ FALHOU"
        print(f"{i}. {TEST_QUERIES[i-1]['name']}: {status}")
        if not result.get("success"):
            print(f"   Erro: {result.get('error', 'Validação falhou')}")

    # Próximos passos
    print_section("PRÓXIMOS PASSOS")

    if passed == total:
        print("\n[🎉 SUCESSO TOTAL!]")
        print("\nIntegração funcionando perfeitamente!")
        print("\nPróximos passos:")
        print("1. Testar queries mais complexas")
        print("2. Integrar com outros subagentes")
        print("3. Configurar monitoring/logging")
        print("4. Otimizar prompts baseado em uso real")
    elif passed > 0:
        print("\n[⚠️ SUCESSO PARCIAL]")
        print(f"\n{passed}/{total} testes passaram.")
        print("\nAções recomendadas:")
        print("1. Revisar testes que falharam")
        print("2. Verificar system prompt do subagente")
        print("3. Verificar que ferramenta foi adicionada ao subagente")
        print("4. Testar manualmente no Agent Builder")
    else:
        print("\n[❌ FALHA TOTAL]")
        print("\nNenhum teste passou. Verificar:")
        print("1. MCP server foi adicionado ao workspace?")
        print("2. Ferramenta foi adicionada ao subagente?")
        print("3. Headers de autenticação estão corretos?")
        print("4. Deployment está com LLAMA_CLOUD_API_KEY configurado?")

    print("\n" + "="*70)
    print("FIM DA VALIDAÇÃO")
    print("="*70)

    # Salvar resultados
    results_file = f"validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "deployment_url": DEPLOYMENT_URL,
            "workspace_id": WORKSPACE_ID,
            "tests": results,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": total - passed,
                "success_rate": passed/total*100
            }
        }, f, indent=2, ensure_ascii=False)

    print(f"\nResultados salvos em: {results_file}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    exit(main())
