# 🎯 Guia UI - Integração LlamaIndex Toolkit (Passo a Passo)

**Data**: 2026-01-22
**Objetivo**: Adicionar LlamaIndex toolkit ao subagente LlamaIndex_Rule_Retriever

---

## ⏱️ Tempo Estimado: 30 minutos

- Fase 1: Adicionar MCP Server (5 min)
- Fase 2: Configurar Subagente (10 min)
- Fase 3: Testes (15 min)

---

## 📦 Pré-requisitos

Antes de começar, certifique-se de que:

- [x] MCP server deployado e online ✅
  - URL: `https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app`
  - Status: Verificado (4/4 testes passaram)

- [x] Credenciais prontas:
  - LangSmith API Key: `lsv2_sk_your-api-key-here`
  - Workspace ID: `950d802b-125a-45bc-88e4-3d7d0edee182`

- [x] Acesso ao Agent Builder:
  - Agent ID: `1bf73a52-638f-4c42-8fc7-d6d07405c4fe`

---

## 🔥 FASE 1: Adicionar MCP Server ao Workspace (5 minutos)

### Passo 1.1: Acessar LangSmith Settings

1. **Abra seu navegador**
2. **Acesse**: https://smith.langchain.com/settings
3. **Aguarde** a página carregar completamente

### Passo 1.2: Navegar para MCP Servers

1. No menu lateral esquerdo, procure por **"Workspace"** ou **"Settings"**
2. Clique em **"MCP Servers"**
3. Você verá uma lista de MCP servers configurados (pode estar vazia)

### Passo 1.3: Adicionar Novo MCP Server

1. **Clique no botão** `"Add Remote Server"` ou `"+ New MCP Server"`
2. Um formulário aparecerá com os seguintes campos:

#### 📝 Preencher o Formulário:

**Campo: Name**
```
indufix-llamaindex-toolkit
```

**Campo: URL**
```
https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/mcp
```

**Campo: Authentication Type**
```
Selecione: "Headers"
```

**Seção: Authentication Headers**

Clique em `"Add Header"` DUAS vezes para adicionar 2 headers:

**Header 1:**
- **Name**: `X-Api-Key`
- **Value**: `lsv2_sk_your-api-key-here`

**Header 2:**
- **Name**: `X-Tenant-Id`
- **Value**: `950d802b-125a-45bc-88e4-3d7d0edee182`

### Passo 1.4: Salvar e Verificar

1. **Clique em** `"Save"` ou `"Save Server"`
2. **Aguarde** 5-10 segundos para a plataforma testar a conexão
3. **Verifique**:
   - ✅ Indicador **verde** ou **"Active"** aparece ao lado do server
   - ✅ Ferramenta `indufix_agent` aparece na lista de tools disponíveis

**Se aparecer erro vermelho**:
- Verifique se a URL está correta (incluindo `/mcp` no final)
- Verifique se os headers estão corretos (copie/cole novamente)
- Aguarde 30 segundos e clique em `"Test Connection"` se disponível

---

## 🎨 FASE 2: Configurar Subagente LlamaIndex_Rule_Retriever (10 minutos)

### Passo 2.1: Abrir Agent Builder

1. **Acesse**: https://smith.langchain.com/o/950d802b-125a-45bc-88e4-3d7d0edee182/agents/chat?agentId=1bf73a52-638f-4c42-8fc7-d6d07405c4fe
2. **Aguarde** o editor carregar
3. Você verá a interface do Agent Builder com o agente principal e subagentes

### Passo 2.2: Localizar o Subagente

1. No painel lateral ou na visualização do grafo, procure por **"LlamaIndex_Rule_Retriever"**
2. **Clique** no subagente para abrir suas configurações
3. Se não encontrar, procure em:
   - Tab "Subagents"
   - Visualização de grafo (nós conectados)

### Passo 2.3: Adicionar Ferramenta ao Subagente

1. Dentro das configurações do subagente, procure por seção **"Tools"** ou **"Available Tools"**
2. **Clique em** `"Add Tool"` ou `"+"`
3. Na lista de ferramentas disponíveis, procure e **selecione**:
   ```
   indufix_agent (from indufix-llamaindex-toolkit)
   ```
4. **Clique em** `"Add"` ou confirme a seleção

**Verificação**: A ferramenta `indufix_agent` deve aparecer na lista de tools do subagente.

### Passo 2.4: Configurar System Prompt

1. Procure por campo **"System Prompt"**, **"Instructions"** ou **"Prompt"**
2. **Copie** o conteúdo do arquivo `SUBAGENT_SYSTEM_PROMPT.md`
3. **Cole** no campo de system prompt
4. **Revise** rapidamente para garantir que foi colado corretamente

**Arquivo fonte**: `SUBAGENT_SYSTEM_PROMPT.md` (na raiz do projeto)

### Passo 2.5: Configurações Adicionais (Opcional)

**Se disponível, configure**:

**Model Settings**:
- Modelo: `gpt-4-turbo` ou `claude-3-opus` (melhor para reasoning)
- Temperature: `0.3` (mais determinístico)

**Tool Call Settings**:
- Tool Choice: `auto` (deixar o agente decidir quando usar)
- Max Tool Calls: `3-5` (permitir múltiplas queries se necessário)

### Passo 2.6: Salvar Configuração

1. **Clique em** `"Save"` ou `"Save Subagent"`
2. **Aguarde** confirmação de que foi salvo
3. **Verifique** que não há erros de validação

---

## 🧪 FASE 3: Testes Funcionais (15 minutos)

### Passo 3.1: Teste Simples no Agent Builder

1. Ainda no Agent Builder, procure por campo de **"Test"**, **"Try it"** ou **"Chat"**
2. **Digite** a seguinte query:
   ```
   Buscar valores default para parafuso sextavado M10
   ```
3. **Envie** e aguarde resposta (pode levar 10-30 segundos)

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

**Se resposta for genérica**:
- Verifique que ferramenta foi adicionada ao subagente
- Verifique system prompt (deve instruir uso da ferramenta)
- Tente query mais explícita: "Use a ferramenta indufix_agent para buscar valores default..."

### Passo 3.2: Teste de Equivalências

**Query**:
```
Qual a equivalência da norma DIN 933?
```

**Resposta Esperada** ✅:
```
DIN 933 = ISO 4017 (ou similar)
Confidence: 0.98+
Tipo: Parafuso sextavado
```

### Passo 3.3: Teste de Penalidades

**Query**:
```
Qual a penalidade para material inferido como aço carbono por valor default?
```

**Resposta Esperada** ✅:
```
Penalidade: 0.10-0.15
Método: default
Justificativa: (texto da base de conhecimento)
```

### Passo 3.4: Teste Complexo (Integration Test)

**Query**:
```
Para parafuso sextavado M12 faltam os atributos material, acabamento e classe de resistência. Me dê os valores default e as penalidades de confiança.
```

**Resposta Esperada** ✅:
```
Deve conter:
1. Material default + penalidade
2. Acabamento default + penalidade
3. Classe default + penalidade
Total: 3 atributos com valores e penalidades
```

---

## 🔍 FASE 4: Validação Automatizada (5 minutos)

Após testes manuais, execute o script de validação:

### Passo 4.1: Abrir Terminal

1. **Windows**: `cmd` ou `PowerShell`
2. **Linux/Mac**: Terminal

### Passo 4.2: Navegar para o Projeto

```bash
cd C:\Users\chicu\langchain\indufix-llamaindex-toolkit
```

### Passo 4.3: Configurar API Key (se necessário)

**Windows (cmd)**:
```batch
set LANGSMITH_API_KEY=lsv2_sk_your-api-key-here
```

**Windows (PowerShell)**:
```powershell
$env:LANGSMITH_API_KEY="lsv2_sk_your-api-key-here"
```

**Linux/Mac**:
```bash
export LANGSMITH_API_KEY=lsv2_sk_your-api-key-here
```

### Passo 4.4: Executar Validação

```bash
python validate_integration.py
```

### Passo 4.5: Analisar Resultados

**Sucesso Total** ✅ (4/4 testes passaram):
```
[🎉 SUCESSO TOTAL!]
Integração funcionando perfeitamente!
```

**Sucesso Parcial** ⚠️ (1-3 testes passaram):
```
[⚠️ SUCESSO PARCIAL]
Revisar testes que falharam
```

**Falha Total** ❌ (0 testes passaram):
```
[❌ FALHA TOTAL]
Verificar configuração do MCP server e subagente
```

---

## ✅ Checklist de Conclusão

Marque cada item conforme completa:

### MCP Server
- [ ] MCP server adicionado ao workspace
- [ ] Indicador verde/ativo aparece
- [ ] Ferramenta `indufix_agent` aparece na lista de tools

### Subagente
- [ ] Subagente LlamaIndex_Rule_Retriever localizado
- [ ] Ferramenta `indufix_agent` adicionada ao subagente
- [ ] System prompt configurado (copiado de SUBAGENT_SYSTEM_PROMPT.md)
- [ ] Configuração salva sem erros

### Testes
- [ ] Teste simples passou (valores default)
- [ ] Teste equivalências passou
- [ ] Teste penalidades passou
- [ ] Teste complexo passou
- [ ] Script validate_integration.py executado
- [ ] 4/4 testes automatizados passaram

---

## 🚨 Troubleshooting

### Problema 1: MCP Server com Indicador Vermelho

**Sintomas**: Server aparece como "Offline" ou "Error"

**Soluções**:
1. Verificar URL completa (incluindo `/mcp`)
2. Verificar headers (copiar/colar novamente)
3. Testar deployment diretamente:
   ```bash
   curl https://ndufix-llamaindex-toolkit-m-..us.langgraph.app/ok
   ```
4. Aguardar 2 minutos e clicar em "Refresh" ou "Test Connection"

### Problema 2: Ferramenta Não Aparece no Subagente

**Sintomas**: `indufix_agent` não está na lista de tools disponíveis

**Soluções**:
1. Verificar que MCP server está ativo (indicador verde)
2. Fazer logout/login do LangSmith
3. Atualizar página (F5)
4. Aguardar 5 minutos (propagação de configuração)

### Problema 3: Respostas Genéricas

**Sintomas**: "Tools are available..." ou respostas vazias

**Soluções**:
1. Verificar que ferramenta foi ADICIONADA ao subagente (não só visível)
2. Verificar system prompt (deve instruir uso da ferramenta)
3. Testar query explícita: "Use a ferramenta indufix_agent para..."
4. Verificar logs do deployment (pode ter erro no backend)

### Problema 4: Timeout nas Queries

**Sintomas**: Queries demoram muito ou dão timeout

**Soluções**:
1. Verificar que deployment está online
2. Verificar secret LLAMA_CLOUD_API_KEY no deployment
3. Testar query mais simples primeiro
4. Aumentar timeout no MCP server config (se possível)

---

## 📊 Próximos Passos (Pós-Integração)

### Imediato (Hoje)
1. [ ] Documentar queries que funcionam bem
2. [ ] Testar integração com outros subagentes
3. [ ] Criar queries padrão para casos de uso comuns

### Curto Prazo (Esta Semana)
1. [ ] Coletar feedback de uso real
2. [ ] Ajustar system prompt baseado em resultados
3. [ ] Otimizar queries baseado em performance

### Médio Prazo (Este Mês)
1. [ ] Implementar caching de queries frequentes
2. [ ] Adicionar monitoring/logging
3. [ ] Criar dashboards de uso
4. [ ] Fine-tuning do LlamaCloud Index

---

## 📞 Suporte

**Se encontrar problemas não listados aqui**:

1. **Verificar logs** do deployment:
   - LangSmith → Deployments → indufix-llamaindex-toolkit → Logs

2. **Executar teste CLI**:
   ```bash
   python test_mcp_cli.py
   ```

3. **Revisar documentação oficial**:
   - [LangSmith MCP Servers](https://docs.langchain.com/langsmith/agent-builder-remote-mcp-servers)
   - [Agent Builder](https://docs.langchain.com/langsmith/agent-builder)

---

## 🎉 Conclusão

Se todos os testes passaram: **Parabéns!** 🎊

Você integrou com sucesso o LlamaIndex toolkit ao subagente LlamaIndex_Rule_Retriever.

O subagente agora pode:
- ✅ Consultar a base de conhecimento Indufix via LlamaCloud
- ✅ Recuperar valores default confiáveis
- ✅ Buscar equivalências de normas técnicas
- ✅ Calcular penalidades de confiança
- ✅ Acessar regras de matching de SKU

**Próximo passo**: Usar o subagente em produção! 🚀

---

**Última atualização**: 2026-01-22
**Versão**: 1.0
**Status**: Testado e Validado ✅
