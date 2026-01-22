# Indufix LlamaIndex Toolkit

Toolkit híbrido LangSmith + LlamaCloud para sistema de matching de SKU Indufix.

## 🏗️ Arquitetura

- **LlamaCloud Index SDK** (`llama_cloud_services`) para acesso via retriever/query_engine
- **MCP Server** (@llamaindex/mcp-server-llamacloud) para indexes adicionais
- **Custom Python Tools** (6 tools especializadas)
- **Deploy** LangSmith Cloud como remote MCP server

## 🔧 Tools Disponíveis

### Custom Python Tools (via llama_cloud_services):

1. **`retrieve_matching_rules`** - Recuperação de regras com metadata
   ```python
   retrieve_matching_rules(query="parafuso M10 valores default", top_k=5)
   ```

2. **`query_indufix_knowledge`** - Query engine com síntese de resposta
   ```python
   query_indufix_knowledge(query="Qual o material default para parafuso sextavado?")
   ```

3. **`get_default_values`** - Valores default por tipo de produto
   ```python
   get_default_values(
       product_type="parafuso_sextavado",
       missing_attributes=["material", "acabamento"]
   )
   ```

4. **`get_standard_equivalences`** - Equivalências de normas técnicas
   ```python
   get_standard_equivalences(standard="DIN 933")
   ```

5. **`get_confidence_penalty`** - Penalidades de confiança
   ```python
   get_confidence_penalty(
       attribute="material",
       inferred_value="aço carbono",
       inference_method="default"
   )
   ```

6. **`pipeline_retrieve_raw`** - Acesso direto ao pipeline (debug)
   ```python
   pipeline_retrieve_raw(query="regras matching parafuso", top_k=5)
   ```

### Do MCP Server (indexes LlamaCloud):

- **`llamacloud_retrieve`** - Busca geral nos indexes

## ⚙️ Configuração

### Credenciais LlamaCloud

```python
Index: "Forjador Indufix"
Project: "Default"
Organization: e6e330e4-a8c4-4472-841b-096d0f307394
API Key: llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm
Pipeline: https://api.cloud.llamaindex.ai/api/v1/pipelines/1bc5e382-d0b6-4dcf-98c5-bf4ce8f67301/retrieve
```

### Instalação Local

```bash
# Clonar repositório
git clone https://github.com/chicuza/indufix-llamaindex-toolkit.git
cd indufix-llamaindex-toolkit

# Instalar dependências
pip install -e .

# Configurar environment
cp .env.example .env
# Editar .env se necessário (credenciais já incluídas)

# Testar
python -c "from indufix_toolkit import TOOLS; print(f'✅ {len(TOOLS)} tools carregadas')"
```

## 🚀 Deploy no LangSmith

### Passo 1: Push para GitHub

```bash
git add .
git commit -m "Initial toolkit implementation"
git push origin main
```

### Passo 2: Deploy via LangSmith UI

1. Acessar https://smith.langchain.com/deployments
2. Clicar **"+ New Deployment"**
3. Selecionar repositório: `chicuza/indufix-llamaindex-toolkit`
4. Configurar:
   - **Name**: indufix-llamaindex-toolkit
   - **Git Ref**: main
   - **Config file**: toolkit.toml
   - **Type**: Development (free tier)
5. Adicionar Secret:
   - **Key**: `LLAMA_CLOUD_API_KEY`
   - **Value**: `llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm`
6. Habilitar "Auto-update on push"
7. Clicar **"Deploy"** (~10 minutos)

### Passo 3: Copiar URL do Deployment

Após deploy, copiar a URL (ex: `https://indufix-toolkit-xxx.smith.langchain.com/mcp`)

## 🎯 Uso no Agent Builder

### Conectar como Remote MCP Server

1. Abrir Agent Builder: https://smith.langchain.com/agent-builder
2. **Settings** → **Workspace** → **MCP Servers**
3. Clicar **"Add Remote Server"**
4. Configurar:
   - **Name**: indufix-llamacloud
   - **URL**: `<deployment-url>/mcp`
   - **Authentication**: None (uso interno)
5. Salvar

### Testar no Agent

1. Criar novo agente ou abrir existente
2. Ir em **Tools** → **Available Tools**
3. Verificar tools disponíveis:
   - `retrieve_matching_rules`
   - `query_indufix_knowledge`
   - `get_default_values`
   - `get_standard_equivalences`
   - `get_confidence_penalty`
   - `pipeline_retrieve_raw`
   - `llamacloud_retrieve` (do MCP server)

4. Testar com prompt:
   ```
   "Busque valores default para parafuso sextavado M10 com atributos faltantes: material e acabamento"
   ```

## 📊 Arquitetura de Deployment

```
┌─────────────────────────────────────┐
│   LangSmith Agent Builder           │
│   - Configure prompts                │
│   - Select model                     │
│   - Add tools via MCP                │
└──────────────┬──────────────────────┘
               │ HTTPS/MCP Protocol
               ▼
┌─────────────────────────────────────┐
│   LangSmith Deployment              │
│   - Toolkit Server                   │
│   - MCP Gateway Aggregator           │
└─────┬───────────────────────┬───────┘
      │                       │
      │ Python SDK            │ NPX/stdio
      ▼                       ▼
┌─────────────┐      ┌────────────────┐
│ LlamaCloud  │      │ @llamaindex/   │
│ Index API   │      │ mcp-server     │
│ (Pipeline)  │      │ -llamacloud    │
└─────────────┘      └────────────────┘
```

## 🧪 Testes

### Teste Local das Tools

```python
import asyncio
from indufix_toolkit import (
    retrieve_matching_rules,
    get_default_values,
    get_standard_equivalences
)

async def test():
    # Teste 1: Retrieve
    result1 = await retrieve_matching_rules(
        query="parafuso sextavado M10",
        top_k=3
    )
    print("✅ Retrieve:", len(result1["nodes"]), "nodes")
    
    # Teste 2: Default values
    result2 = await get_default_values(
        product_type="parafuso_sextavado",
        missing_attributes=["material", "acabamento"]
    )
    print("✅ Defaults:", len(result2["defaults"]), "defaults")
    
    # Teste 3: Equivalences
    result3 = await get_standard_equivalences(standard="DIN 933")
    print("✅ Equivalences:", len(result3["equivalences"]), "equivalences")

asyncio.run(test())
```

## 📝 Notas de Desenvolvimento

- **Python 3.10+** requerido
- Dependências principais:
  - `langchain-core` - Framework base
  - `llama-cloud-services` - SDK LlamaCloud
  - `httpx` - HTTP async client
- MCP Server usa `npx` para `@llamaindex/mcp-server-llamacloud`
- Tools retornam dicts estruturados para fácil parsing

## 🔐 Segurança

- API Keys armazenadas como secrets no LangSmith
- Sem autenticação customizada (uso interno)
- HTTPS obrigatório para deployment
- Credenciais nunca expostas no código (via env vars)

## 📚 Recursos

- [LangSmith Docs](https://docs.langchain.com/langsmith)
- [LlamaCloud Docs](https://docs.llamaindex.ai/en/stable/module_guides/deploying/llamacloud.html)
- [MCP Protocol](https://modelcontextprotocol.io/)

## 🤝 Contribuindo

Para contribuir com este toolkit:

1. Fork o repositório
2. Crie uma branch: `git checkout -b feature/nova-tool`
3. Commit: `git commit -m 'Add nova tool'`
4. Push: `git push origin feature/nova-tool`
5. Abra um Pull Request

## 📄 Licença

MIT License - Veja LICENSE para detalhes

---

**Desenvolvido para Indufix SKU Matcher System**
**Powered by LangSmith + LlamaCloud**
