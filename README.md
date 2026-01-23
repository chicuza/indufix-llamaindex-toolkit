# 🚀 Indufix LlamaIndex Toolkit - Integração LangSmith Agent Builder

**Toolkit híbrido para consulta de conhecimento técnico Indufix via LlamaCloud + MCP Server**

[![Status](https://img.shields.io/badge/status-deployed-success)](https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app)
[![LangSmith](https://img.shields.io/badge/LangSmith-Agent%20Builder-blue)](https://smith.langchain.com)
[![LlamaCloud](https://img.shields.io/badge/LlamaCloud-Pipeline-orange)](https://cloud.llamaindex.ai)

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Arquitetura](#-arquitetura)
- [Status do Deployment](#-status-do-deployment)
- [Início Rápido](#-início-rápido)
- [Recursos Disponíveis](#-recursos-disponíveis)
- [Integração com Agent Builder](#-integração-com-agent-builder)
- [Testes e Validação](#-testes-e-validação)
- [Troubleshooting](#-troubleshooting)
- [Próximos Passos](#-próximos-passos)

---

## 🎯 Visão Geral

Este projeto implementa um **MCP Server** (Model Context Protocol) que integra a base de conhecimento técnico Indufix com agentes LangSmith via LlamaCloud Index.

### O Que Este Toolkit Faz?

Permite que agentes consultem informações sobre produtos industriais (parafusos, porcas, arruelas):

1. **Valores Default**: Atributos padrão quando informação está ausente
   - Material (ex: aço carbono, aço inox)
   - Acabamento (ex: zincado, galvanizado)
   - Classe de resistência (ex: 8.8, 10.9)

2. **Equivalências de Normas**: Mapeamento entre padrões técnicos
   - DIN ↔ ISO ↔ ASTM ↔ SAE
   - Exemplo: DIN 933 = ISO 4017

3. **Penalidades de Confiança**: Ajustes de score para valores inferidos
   - Método default: 0.10-0.15
   - Método pattern matching: 0.05-0.10
   - Método LLM inference: 0.15-0.25

4. **Regras de Matching**: Critérios para associar descrições a SKUs Odoo

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                    LangSmith Agent Builder                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Main Agent (ID: 1bf73a52-638f-4c42-8fc7-d6d07405c4fe)    │  │
│  │                                                             │  │
│  │  Subagents:                                                │  │
│  │  ├─ Batch_Processor                                        │  │
│  │  ├─ LlamaIndex_Rule_Retriever ← **Target Subagent**       │  │
│  │  ├─ SKU_Matching_Engine                                    │  │
│  │  └─ Technical_Attribute_Extractor                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                     MCP Protocol (JSON-RPC 2.0)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│            MCP Server (LangGraph Cloud Deployment)               │
│                                                                  │
│  URL: https://ndufix-llamaindex-toolkit-m-...                   │
│                                                                  │
│  Ferramenta Exposta:                                            │
│  └─ indufix_agent                                               │
│     ├─ Input: messages (list of dicts)                          │
│     └─ Output: AI response                                      │
│                                                                  │
│  Ferramentas Internas (6):                                      │
│  ├─ retrieve_matching_rules                                     │
│  ├─ query_indufix_knowledge                                     │
│  ├─ get_default_values                                          │
│  ├─ get_standard_equivalences                                   │
│  ├─ get_confidence_penalty                                      │
│  └─ pipeline_retrieve_raw                                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    LlamaCloud Platform                           │
│                                                                  │
│  Pipeline: Forjador Indufix                                     │
│  ID: 1bc5e382-d0b6-4dcf-98c5-bf4ce8f67301                       │
│                                                                  │
│  Conteúdo:                                                       │
│  └─ Base de conhecimento Indufix (regras, normas, defaults)     │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Status do Deployment

### Deployment Atual

**URL**: `https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app`

**Status**: 🟢 **Online e Funcional**

**Última Validação**: 2026-01-22

**Testes CLI**: 4/4 Passaram ✅
- ✅ Deployment Health Check
- ✅ MCP Without Auth (Expected Fail)
- ✅ MCP With Auth (Tools Discovery)
- ✅ Tool Invocation

### Credenciais e IDs

```bash
# LangSmith
LANGSMITH_API_KEY=lsv2_sk_your-api-key-here
WORKSPACE_ID=950d802b-125a-45bc-88e4-3d7d0edee182
AGENT_ID=1bf73a52-638f-4c42-8fc7-d6d07405c4fe

# LlamaCloud
LLAMA_CLOUD_API_KEY=llx-*** (configurado como secret no deployment)
LLAMA_CLOUD_PIPELINE_ID=1bc5e382-d0b6-4dcf-98c5-bf4ce8f67301
```

---

## 🚀 Início Rápido

### Pré-requisitos

- Python 3.10+
- Acesso ao LangSmith Agent Builder
- Deployment MCP já deployado (URL acima)

### Instalação Local (Opcional)

```bash
# Clone o repositório
cd indufix-llamaindex-toolkit

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais
```

### Teste Rápido (CLI)

```bash
# Configurar API key
export LANGSMITH_API_KEY=lsv2_sk_your-api-key-here

# Windows
set LANGSMITH_API_KEY=lsv2_sk_your-api-key-here

# Executar testes
python test_mcp_cli.py
```

**Resultado Esperado**: 4/4 testes passam ✅

---

## 📚 Recursos Disponíveis

Este repositório contém todos os recursos necessários para integração:

### 1. 📘 Guia de Integração UI (Passo-a-Passo)

**Arquivo**: [`GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md`](./GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md)

**Tempo estimado**: 30 minutos

**Fases**:
- ⏱️ Fase 1: Adicionar MCP Server ao Workspace (5 min)
- ⏱️ Fase 2: Configurar Subagente LlamaIndex_Rule_Retriever (10 min)
- ⏱️ Fase 3: Testes Funcionais (15 min)

**Use este guia para**: Integrar o MCP server com o Agent Builder via interface gráfica.

---

### 2. 🧪 Script de Validação Automatizada

**Arquivo**: [`validate_integration.py`](./validate_integration.py)

**Execução**:
```bash
python validate_integration.py
```

**O que faz**:
- Testa conectividade MCP
- Executa 4 queries de validação
- Verifica que respostas não são genéricas
- Salva relatório JSON com timestamp

**Use este script**: APÓS configurar o subagente via UI para confirmar funcionamento.

---

### 3. 📝 System Prompt para Subagente

**Arquivo**: [`SUBAGENT_SYSTEM_PROMPT.md`](./SUBAGENT_SYSTEM_PROMPT.md)

**Conteúdo**:
- Instruções completas para o subagente LlamaIndex_Rule_Retriever
- Como formular queries eficazes
- Formato de resposta estruturado
- Exemplos de uso correto/incorreto

**Use este prompt**: Copiar e colar no campo "System Prompt" do subagente no Agent Builder.

---

### 4. 🎯 Payloads de Teste

**Arquivo**: [`PAYLOADS_TESTE.md`](./PAYLOADS_TESTE.md)

**Conteúdo**: 18 queries prontas para testar, organizadas por complexidade:
- **Básicos** (1-3): Valores default, equivalências, penalidades
- **Intermediários** (4-6): Múltiplos atributos, normas específicas
- **Avançados** (7-9): Queries complexas, mapeamento Odoo
- **Edge Cases** (10-12): Dimensões não-padrão, queries ambíguas
- **Performance** (13-14): Queries longas, sequências rápidas
- **Reasoning** (15-16): Inferência de contexto, validação lógica
- **Segurança** (17-18): Caracteres especiais, inputs extremos

**Use estes payloads**: Para testar o subagente após configuração.

---

### 5. 🔍 Investigação CLI/API

**Arquivos**:
- [`EXHAUSTIVE_CLI_API_INVESTIGATION_REPORT.md`](./EXHAUSTIVE_CLI_API_INVESTIGATION_REPORT.md)
- [`RESPOSTA_DEFINITIVA.md`](./RESPOSTA_DEFINITIVA.md)

**Conteúdo**:
- Análise de 262 endpoints da LangSmith API
- Investigação completa de SDK e documentação
- **Conclusão**: Nenhum método CLI/API existe para adicionar MCP servers ao workspace
- **Certeza**: 100% (6 fontes independentes confirmam)

**Resultado**: Integração DEVE ser feita via UI do Agent Builder.

---

### 6. 🛠️ Scripts de Teste CLI

**Arquivo**: [`test_mcp_cli.py`](./test_mcp_cli.py)

**Uso**: Testes de baixo nível (sem Agent Builder)
```bash
python test_mcp_cli.py
```

**Testa**:
- Health do deployment
- MCP endpoint sem auth (deve falhar)
- MCP endpoint com auth (deve listar ferramenta)
- Invocação da ferramenta `indufix_agent`

---

### 7. 📊 Documentação Técnica

**Arquivos**:
- [`CLI_TESTING_README.md`](./CLI_TESTING_README.md) - Quick start para testes CLI
- [`openapi_schema.json`](./openapi_schema.json) - OpenAPI completo da LangSmith API
- [`mcp_tools_detailed.json`](./mcp_tools_detailed.json) - Schema JSON-RPC da ferramenta

---

## 🔗 Integração com Agent Builder

### Resumo do Processo

**O que você vai fazer**:
1. Adicionar MCP server ao workspace LangSmith
2. Adicionar ferramenta `indufix_agent` ao subagente LlamaIndex_Rule_Retriever
3. Configurar system prompt
4. Testar com queries de exemplo

### Passo-a-Passo Detalhado

**Siga o guia completo**: [`GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md`](./GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md)

### Configuração do MCP Server

Quando adicionar o MCP server no Agent Builder, use:

**Nome**:
```
indufix-llamaindex-toolkit
```

**URL**:
```
https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/mcp
```

**Authentication Type**: `Headers`

**Headers**:
```
Header 1:
  Name: X-Api-Key
  Value: lsv2_sk_your-api-key-here

Header 2:
  Name: X-Tenant-Id
  Value: 950d802b-125a-45bc-88e4-3d7d0edee182
```

### Configuração do Subagente

**Subagente Target**: `LlamaIndex_Rule_Retriever`

**Ferramenta a adicionar**: `indufix_agent`

**System Prompt**: Copiar conteúdo completo de [`SUBAGENT_SYSTEM_PROMPT.md`](./SUBAGENT_SYSTEM_PROMPT.md)

---

## 🧪 Testes e Validação

### Teste Manual Rápido

Após configurar o subagente, teste com esta query no Agent Builder:

```
Buscar valores default para parafuso sextavado M10
```

**Resposta Esperada** ✅:
```
Resposta deve conter:
- Material: aço carbono ou similar
- Acabamento: zincado ou similar
- Confidence scores (ex: 0.95, 0.92)
- Fonte ou justificativa
```

**Resposta ERRADA** ❌:
```
"Tools are available for use via MCP server"
"I don't have access to..."
Qualquer resposta genérica sem dados específicos
```

### Validação Automatizada

Após configuração via UI, execute:

```bash
python validate_integration.py
```

**Critérios de Sucesso**:
- ✅ 4/4 testes passam
- ✅ Respostas contêm dados técnicos específicos
- ✅ Confidence scores aparecem
- ✅ Sem respostas genéricas

### Payloads de Teste Completos

Use as 18 queries em [`PAYLOADS_TESTE.md`](./PAYLOADS_TESTE.md) para testes abrangentes:

```bash
# Exemplo: Teste de equivalências
Query: "Qual a equivalência da norma DIN 933?"
Esperado: DIN 933 = ISO 4017 (confidence > 0.95)
```

---

## 🐛 Troubleshooting

### Problema: MCP Server com Indicador Vermelho no UI

**Sintomas**: Server aparece como "Offline" ou "Error"

**Soluções**:
1. Verificar URL completa (incluindo `/mcp` no final)
2. Verificar headers (copiar/colar novamente)
3. Testar deployment diretamente:
   ```bash
   curl https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/ok
   ```
4. Executar `python test_mcp_cli.py` para verificar conectividade

---

### Problema: Ferramenta Não Aparece no Subagente

**Sintomas**: `indufix_agent` não está na lista de tools disponíveis

**Soluções**:
1. Verificar que MCP server está ativo (indicador verde)
2. Fazer logout/login do LangSmith
3. Atualizar página (F5)
4. Aguardar 5 minutos (propagação de configuração)

---

### Problema: Respostas Genéricas

**Sintomas**: "Tools are available..." ou respostas vazias

**Soluções**:
1. Verificar que ferramenta foi **ADICIONADA** ao subagente (não só visível)
2. Verificar system prompt (deve instruir uso da ferramenta)
3. Testar query explícita: "Use a ferramenta indufix_agent para buscar valores default..."
4. Verificar logs do deployment (pode ter erro no backend)

---

### Problema: Timeout nas Queries

**Sintomas**: Queries demoram muito ou dão timeout

**Soluções**:
1. Verificar que deployment está online
2. Verificar secret `LLAMA_CLOUD_API_KEY` no deployment
3. Testar query mais simples primeiro
4. Aumentar timeout no MCP server config (se possível)

---

### Guia Completo de Troubleshooting

Consulte a seção "🚨 Troubleshooting" em [`GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md`](./GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md) para problemas específicos.

---

## 🎯 Próximos Passos

### Imediato (Hoje)

1. ⬜ Seguir guia [`GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md`](./GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md)
2. ⬜ Adicionar MCP server ao workspace via UI
3. ⬜ Configurar subagente LlamaIndex_Rule_Retriever
4. ⬜ Executar `python validate_integration.py`
5. ⬜ Testar com queries de [`PAYLOADS_TESTE.md`](./PAYLOADS_TESTE.md)

### Curto Prazo (Esta Semana)

1. ⬜ Coletar feedback de uso real
2. ⬜ Ajustar system prompt baseado em resultados
3. ⬜ Otimizar queries baseado em performance
4. ⬜ Integrar com outros subagentes (se aplicável)

### Médio Prazo (Este Mês)

1. ⬜ Implementar caching de queries frequentes
2. ⬜ Adicionar monitoring/logging
3. ⬜ Criar dashboards de uso
4. ⬜ Fine-tuning do LlamaCloud Index

---

## 📖 Documentação Oficial

- **LangSmith Agent Builder**: https://docs.langchain.com/langsmith/agent-builder
- **MCP Servers**: https://docs.langchain.com/langsmith/agent-builder-remote-mcp-servers
- **LangGraph Cloud**: https://langchain-ai.github.io/langgraph/cloud/
- **Model Context Protocol**: https://modelcontextprotocol.io/introduction
- **LlamaCloud**: https://docs.cloud.llamaindex.ai/

---

## 🤝 Suporte

### Se Encontrar Problemas

1. **Verificar logs** do deployment:
   - LangSmith → Deployments → indufix-llamaindex-toolkit → Logs

2. **Executar testes CLI**:
   ```bash
   python test_mcp_cli.py
   python validate_integration.py
   ```

3. **Revisar documentação**:
   - Guias neste repositório
   - Documentação oficial LangSmith/LangGraph

4. **Troubleshooting detalhado**:
   - [`GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md`](./GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md) (seção Troubleshooting)

---

## ✅ Critérios de Aceitação

Para considerar a integração **bem-sucedida**:

### Must-Have (Obrigatório)

- ⬜ MCP server adicionado ao workspace (indicador verde)
- ⬜ Ferramenta `indufix_agent` aparece no subagente
- ⬜ System prompt configurado
- ⬜ Teste manual passa (resposta com dados técnicos)
- ⬜ Script `validate_integration.py` passa 4/4 testes
- ⬜ Sem respostas genéricas ("Tools are available...")
- ⬜ Confidence scores aparecem nas respostas

### Nice-to-Have (Desejável)

- ⬜ Testes avançados (7-9) passam >= 70%
- ⬜ Edge cases tratados gracefully
- ⬜ Performance < 30s para queries simples
- ⬜ Performance < 60s para queries complexas

---

## 📊 Métricas do Projeto

**Linhas de Código/Documentação**:
- Scripts Python: ~800 linhas
- Documentação Markdown: ~2000 linhas
- Payloads de Teste: 18 queries categorizadas

**Cobertura de Testes**:
- Testes CLI: 4 testes automatizados
- Testes de Integração: 4 testes automatizados
- Payloads de Teste: 18 cenários manuais

**Tempo Estimado de Integração**: 30 minutos (seguindo guia UI)

---

## 📝 Changelog

### 2026-01-22 - Versão 1.0 (Initial Release)

**Adicionado**:
- ✅ Deployment LangGraph Cloud funcional
- ✅ MCP server com autenticação via headers
- ✅ 6 ferramentas LlamaIndex integradas
- ✅ Script de validação automatizada
- ✅ Guia UI passo-a-passo (30 min)
- ✅ System prompt otimizado para subagente
- ✅ 18 payloads de teste categorizados
- ✅ Investigação completa CLI/API (100% certeza)
- ✅ Documentação técnica completa

**Validado**:
- ✅ MCP endpoint respondendo (4/4 testes CLI)
- ✅ Ferramenta `indufix_agent` descoberta
- ✅ Autenticação via headers funcionando
- ✅ LlamaCloud pipeline acessível

---

## 🎉 Conclusão

Este projeto fornece **tudo que você precisa** para integrar o LlamaIndex toolkit com o Agent Builder:

1. 📘 **Guia UI** passo-a-passo (30 minutos)
2. 🧪 **Scripts de validação** automatizados
3. 📝 **System prompt** pronto para uso
4. 🎯 **18 payloads de teste** organizados
5. 🔍 **Troubleshooting** detalhado
6. ✅ **MCP server deployado** e testado

**Status Atual**: 🟢 **Pronto para Integração**

**Próximo Passo**: Seguir [`GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md`](./GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md)

---

**Última atualização**: 2026-01-22
**Versão**: 1.0
**Status**: ✅ Deployment Online | ⏳ Aguardando Configuração UI
**Deployment URL**: https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app

---

**Desenvolvido com**: LangSmith Agent Builder | LangGraph Cloud | LlamaCloud Index | Model Context Protocol (MCP)
