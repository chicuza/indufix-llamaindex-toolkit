# 🧪 Payloads de Teste - LlamaIndex Integration

**Objetivo**: Queries prontas para copiar/colar durante testes

---

## 📋 Testes Básicos (Quick Smoke Tests)

### Teste 1: Valores Default Simples
```
Buscar valores default para parafuso sextavado M10
```

**Resultado Esperado**:
- Material: Aço carbono
- Acabamento: Zincado
- Confidence: > 0.90

---

### Teste 2: Equivalência de Norma
```
Qual a equivalência da norma DIN 933?
```

**Resultado Esperado**:
- ISO 4017
- Confidence: > 0.95
- Tipo: Parafuso sextavado

---

### Teste 3: Penalidade de Confiança
```
Qual a penalidade para material inferido como aço carbono por valor default?
```

**Resultado Esperado**:
- Penalidade: 0.10-0.15
- Método: default
- Justificativa presente

---

## 🎯 Testes Intermediários (Feature Tests)

### Teste 4: Múltiplos Atributos
```
Para parafuso sextavado M12 faltam os atributos material e acabamento. Me dê os valores default e as penalidades.
```

**Resultado Esperado**:
- 2 valores default (material + acabamento)
- 2 penalidades correspondentes
- Confidence scores

---

### Teste 5: Norma Específica
```
Buscar regras de matching para parafuso sextavado DIN 933 M10
```

**Resultado Esperado**:
- Especificações DIN 933
- Dimensões M10
- Regras de classificação

---

### Teste 6: Classe de Resistência
```
Qual o valor default de classe de resistência para parafuso métrico M8?
```

**Resultado Esperado**:
- Classe: 8.8 ou 10.9
- Justificativa
- Penalidade aplicável

---

## 🚀 Testes Avançados (Integration Tests)

### Teste 7: Query Complexa Multi-Atributo
```
Para porca sextavada M16 DIN 934 faltam os seguintes atributos:
- Material
- Acabamento
- Classe de resistência

Me forneça:
1. Valores default para cada atributo
2. Penalidade de confiança individual
3. Justificativa baseada em normas
```

**Resultado Esperado**:
- 3 conjuntos de (valor default + penalidade + justificativa)
- Referências a DIN 934
- Confidence scores > 0.85

---

### Teste 8: Equivalências Múltiplas
```
Liste todas as equivalências conhecidas para DIN 125 (arruela lisa)
```

**Resultado Esperado**:
- ISO 7089 (principal)
- Outras equivalências (se houver)
- Confidence scores ordenados

---

### Teste 9: Mapeamento Odoo
```
Qual o mapeamento Odoo correto para parafuso sextavado DIN 933 M10x50 zincado?
```

**Resultado Esperado**:
- Categoria Odoo
- SKU pattern ou formato
- Regras de nomeação

---

## 🔍 Testes de Edge Cases

### Teste 10: Dimensão Não-Padrão
```
Valores default para parafuso sextavado M2.5
```

**Resultado Esperado**:
- Deve encontrar regra ou indicar "dimensão incomum"
- Confidence pode ser menor (0.70-0.80)
- Justificativa clara

---

### Teste 11: Norma Menos Comum
```
Equivalência para ASTM A307 Grade B
```

**Resultado Esperado**:
- Equivalências (DIN/ISO se disponível)
- Confidence variável
- Pode indicar "equivalência aproximada"

---

### Teste 12: Query Ambígua (Teste Negativo)
```
parafuso
```

**Resultado Esperado**:
- Agente deve pedir mais informações
- NÃO deve inventar dados
- Mensagem: "Por favor especifique tipo, dimensão..."

---

## 📊 Testes de Performance

### Teste 13: Query Longa
```
Preciso de uma análise completa para os seguintes produtos:

1. Parafuso sextavado DIN 933 M10x50
2. Porca sextavada DIN 934 M10
3. Arruela lisa DIN 125 M10

Para cada um, me forneça:
- Valores default para atributos faltantes (material, acabamento, classe)
- Penalidades de confiança
- Equivalências de normas
- Mapeamento Odoo sugerido
```

**Resultado Esperado**:
- Resposta estruturada para os 3 produtos
- Múltiplas consultas ao LlamaCloud
- Tempo de resposta < 60 segundos

---

### Teste 14: Sequência Rápida
```
Executar em sequência:

Query 1: "default material parafuso M8"
Query 2: "default acabamento parafuso M8"
Query 3: "default classe parafuso M8"
```

**Resultado Esperado**:
- 3 respostas rápidas
- Consistência nos dados (mesmo produto)
- Sem timeout

---

## 🧠 Testes de Reasoning

### Teste 15: Inferência de Contexto
```
Um parafuso está descrito como "sextavado M10 galvanizado a fogo comprimento 60mm".

Quais atributos estão faltando e quais são seus valores default?
```

**Resultado Esperado**:
- Identificar atributos ausentes (classe, norma, material base)
- Fornecer defaults para os faltantes
- NÃO sobrescrever atributos já presentes

---

### Teste 16: Validação de Lógica
```
Se um parafuso é descrito como "DIN 933 M10 classe 8.8", qual seria o material mais provável e qual a penalidade por inferência?
```

**Resultado Esperado**:
- Material: Aço carbono (classe 8.8 indica)
- Penalidade baixa (inferência lógica forte)
- Justificativa baseada em relação classe-material

---

## 🔒 Testes de Segurança/Robustez

### Teste 17: Caracteres Especiais
```
Buscar default para "parafuso M10 <script>alert('test')</script>"
```

**Resultado Esperado**:
- Tratar input de forma segura
- Extrair apenas parte válida ("parafuso M10")
- Não executar código ou quebrar

---

### Teste 18: Query Muito Longa
```
[Inserir texto de 2000+ caracteres sobre parafusos]
```

**Resultado Esperado**:
- Processar gracefully
- Extrair informação relevante
- Ou pedir resumo/simplificação

---

## 📝 Template de Teste Manual

Para criar novos testes, use este template:

```markdown
### Teste X: [Nome do Teste]

**Query**:
```
[Texto da query aqui]
```

**Resultado Esperado**:
- [Item 1 esperado]
- [Item 2 esperado]
- [Confidence/validação]

**Resultado Obtido**: [preencher após execução]

**Status**: [ ] Passou  [ ] Falhou

**Notas**: [observações adicionais]
```

---

## 🤖 Testes Automatizados (via validate_integration.py)

Os testes 1-4 acima estão incluídos no script `validate_integration.py`.

**Para executar**:
```bash
python validate_integration.py
```

**Resultados salvos em**:
```
validation_results_YYYYMMDD_HHMMSS.json
```

---

## 📊 Matriz de Cobertura de Testes

| Categoria | Testes | Status |
|-----------|--------|--------|
| Básicos | 1-3 | ✅ Implementado |
| Intermediários | 4-6 | ✅ Implementado |
| Avançados | 7-9 | ✅ Implementado |
| Edge Cases | 10-12 | ✅ Implementado |
| Performance | 13-14 | ✅ Implementado |
| Reasoning | 15-16 | ✅ Implementado |
| Segurança | 17-18 | ✅ Implementado |

**Cobertura Total**: 18 testes

---

## ✅ Critérios de Aceitação

Para considerar a integração **bem-sucedida**, os seguintes critérios devem ser atendidos:

### Must-Have (Obrigatório)
- [ ] Testes 1-3 (Básicos) passam 100%
- [ ] Testes 4-6 (Intermediários) passam >= 80%
- [ ] Sem respostas genéricas ("Tools are available...")
- [ ] Confidence scores aparecem nas respostas
- [ ] Script `validate_integration.py` passa 4/4 testes

### Nice-to-Have (Desejável)
- [ ] Testes 7-9 (Avançados) passam >= 70%
- [ ] Testes 10-12 (Edge Cases) tratados gracefully
- [ ] Performance < 30s para queries simples
- [ ] Performance < 60s para queries complexas

---

## 🎯 Como Usar Este Documento

### Durante Configuração Inicial:
1. Execute testes **1-3** (Básicos) primeiro
2. Se passarem, execute testes **4-6** (Intermediários)
3. Só então execute testes avançados

### Para Troubleshooting:
1. Se algo falha, volte aos **testes básicos**
2. Identifique onde quebrou (MCP? Subagente? LlamaCloud?)
3. Use teste 12 (Query Ambígua) para validar error handling

### Para Validação Automatizada:
```bash
python validate_integration.py
```

Isso executará automaticamente os 4 testes principais.

---

**Última atualização**: 2026-01-22
**Versão**: 1.0
**Testes Totais**: 18
