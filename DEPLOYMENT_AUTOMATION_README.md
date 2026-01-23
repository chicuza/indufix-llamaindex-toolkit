# 🚀 Deployment Automation for LangSmith Cloud

**Ferramentas Python para deployment programático no LangSmith Cloud via Control Plane API**

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Instalação](#-instalação)
- [Quick Start](#-quick-start)
- [Uso da Biblioteca Python](#-uso-da-biblioteca-python)
- [CLI Interface](#-cli-interface)
- [Configuração YAML](#-configuração-yaml)
- [GitHub Actions CI/CD](#-github-actions-cicd)
- [Exemplos Completos](#-exemplos-completos)
- [Troubleshooting](#-troubleshooting)

---

## 🎯 Visão Geral

Este projeto fornece ferramentas de automação completa para deployment no LangSmith Cloud **sem usar a UI web**:

### Ferramentas Disponíveis:

1. **`LangSmithDeployClient`** - Biblioteca Python wrapper para Control Plane API
2. **`deploy_cli.py`** - Interface de linha de comando
3. **Templates YAML** - Configuração declarativa
4. **GitHub Actions Workflow** - CI/CD automatizado

### Capabilities:

✅ Criar deployments (GitHub ou Docker registry)
✅ Atualizar deployments (nova revisão)
✅ Deletar deployments
✅ Gerenciar secrets
✅ Verificar status e aguardar healthy
✅ Listar deployments e revisões
✅ Dry-run mode (preview sem executar)

---

## 📦 Instalação

### Pré-requisitos:

- Python 3.10+
- LangSmith API Key
- Workspace ID

### Install Dependencies:

```bash
pip install -r requirements-deploy.txt
```

### Configure Environment Variables:

```bash
# Linux/Mac
export LANGSMITH_API_KEY="lsv2_sk_..."
export WORKSPACE_ID="950d802b-..."
export INTEGRATION_ID="..."  # For GitHub deployments

# Windows (cmd)
set LANGSMITH_API_KEY=lsv2_sk_...
set WORKSPACE_ID=950d802b-...

# Windows (PowerShell)
$env:LANGSMITH_API_KEY="lsv2_sk_..."
$env:WORKSPACE_ID="950d802b-..."
```

---

## 🚀 Quick Start

### Opção 1: Biblioteca Python

```python
from deployment import LangSmithDeployClient

# Criar client
client = LangSmithDeployClient.from_env()

# Criar deployment do GitHub
deployment = client.create_github_deployment(
    name="my-agent",
    repo_url="https://github.com/user/repo",
    branch="main",
    secrets={"OPENAI_API_KEY": "sk-..."}
)

print(f"✅ Deployment criado: {deployment['id']}")

# Aguardar deployment ficar healthy
client.wait_for_deployment(deployment['id'])
```

### Opção 2: CLI

```bash
# Criar deployment
python -m deployment.deploy_cli create \
  --name my-agent \
  --repo https://github.com/user/repo \
  --branch main \
  --secret OPENAI_API_KEY=sk-... \
  --wait

# Listar deployments
python -m deployment.deploy_cli list

# Ver status
python -m deployment.deploy_cli status DEPLOYMENT_ID
```

### Opção 3: Config YAML

```bash
# Editar deploy_config.yaml
# Depois aplicar:
python -m deployment.deploy_cli apply -f deployment/deploy_config.yaml
```

---

## 📚 Uso da Biblioteca Python

### Importar:

```python
from deployment import LangSmithDeployClient, ResourceSpec
from deployment.exceptions import DeploymentError, DeploymentTimeoutError
```

### Criar Client:

```python
# De environment variables
client = LangSmithDeployClient.from_env()

# Ou explicitamente
client = LangSmithDeployClient(
    api_key="lsv2_sk_...",
    workspace_id="950d802b-...",
    base_url="https://api.host.langchain.com"  # opcional
)
```

### Criar Deployment (GitHub):

```python
deployment = client.create_deployment(
    name="indufix-toolkit",
    source="github",
    repo_url="https://github.com/chicuza/indufix-llamaindex-toolkit",
    branch="main",
    config_path="langgraph.json",
    secrets={
        "LLAMA_CLOUD_API_KEY": os.getenv("LLAMA_CLOUD_API_KEY")
    },
    resource_spec=ResourceSpec(
        min_scale=1,
        max_scale=3,
        cpu=1,
        memory_mb=1024
    ),
    deployment_type="dev",  # ou "prod"
    build_on_push=True,
    dry_run=False  # True para preview
)
```

### Criar Deployment (Docker Registry):

```python
deployment = client.create_docker_deployment(
    name="indufix-toolkit-docker",
    image_uri="docker.io/chicuza/indufix-toolkit:v1.0.0",
    secrets={"LLAMA_CLOUD_API_KEY": "..."}
)
```

### Listar Deployments:

```python
deployments = client.list_deployments(limit=100)

for dep in deployments:
    print(f"{dep['name']}: {dep['state']} / {dep['health']}")
```

### Verificar Status:

```python
status = client.get_deployment_status(deployment_id)

print(f"State:  {status['state']}")
print(f"Health: {status['health']}")
print(f"URL:    {status['url']}")
```

### Aguardar Deployment Healthy:

```python
try:
    client.wait_for_deployment(deployment_id, timeout=600)
    print("✅ Deployment is healthy!")
except DeploymentTimeoutError:
    print("❌ Timeout waiting for deployment")
```

### Atualizar Deployment:

```python
# Mudar branch
client.update_deployment(
    deployment_id=deployment_id,
    branch="dev",
    secrets={"NEW_SECRET": "value"}
)

# Mudar Docker image
client.update_deployment(
    deployment_id=deployment_id,
    image_uri="docker.io/user/image:v2.0.0"
)
```

### Deletar Deployment:

```python
client.delete_deployment(deployment_id, confirm=True)
```

### Gerenciar Revisões:

```python
# Listar revisões
revisions = client.list_revisions(deployment_id)

# Redeploy revisão específica
client.redeploy_revision(deployment_id, revision_id)
```

---

## 💻 CLI Interface

### Comandos Disponíveis:

```bash
python -m deployment.deploy_cli [command] [options]
```

**Comandos**:
- `create` - Criar novo deployment
- `list` - Listar deployments
- `status` - Ver status de deployment
- `update` - Atualizar deployment
- `delete` - Deletar deployment
- `apply` - Aplicar de arquivo de configuração

### Create:

```bash
python -m deployment.deploy_cli create \
  --name my-agent \
  --source github \
  --repo https://github.com/user/repo \
  --branch main \
  --config langgraph.json \
  --type dev \
  --secret OPENAI_API_KEY=sk-... \
  --secret ANTHROPIC_API_KEY=sk-ant-... \
  --min-scale 1 \
  --max-scale 3 \
  --cpu 1 \
  --memory 1024 \
  --build-on-push \
  --wait \
  --wait-timeout 600
```

**Flags importantes**:
- `--dry-run`: Preview sem criar
- `--wait`: Aguardar deployment healthy
- `--build-on-push`: Auto-build on git push

### Create (Docker):

```bash
python -m deployment.deploy_cli create \
  --name my-agent-docker \
  --source external_docker \
  --image docker.io/user/image:tag \
  --secret OPENAI_API_KEY=sk-...
```

### List:

```bash
# Formato table
python -m deployment.deploy_cli list

# JSON output
python -m deployment.deploy_cli list --json --limit 50
```

### Status:

```bash
python -m deployment.deploy_cli status DEPLOYMENT_ID

# JSON output
python -m deployment.deploy_cli status DEPLOYMENT_ID --json
```

### Update:

```bash
python -m deployment.deploy_cli update DEPLOYMENT_ID \
  --branch dev \
  --secret NEW_SECRET=value \
  --wait
```

### Delete:

```bash
python -m deployment.deploy_cli delete DEPLOYMENT_ID --confirm
```

### Apply (de arquivo YAML):

```bash
python -m deployment.deploy_cli apply -f deployment/deploy_config.yaml

# Dry-run
python -m deployment.deploy_cli apply -f deployment/deploy_config.yaml --dry-run
```

---

## 📝 Configuração YAML

### Template Básico:

```yaml
# deployment/deploy_config.yaml

deployment:
  name: indufix-llamaindex-toolkit
  source: github
  repo_url: https://github.com/chicuza/indufix-llamaindex-toolkit
  branch: main
  config_path: langgraph.json
  type: dev

secrets:
  LLAMA_CLOUD_API_KEY: ${LLAMA_CLOUD_API_KEY}
  OPENAI_API_KEY: ${OPENAI_API_KEY}

resource_spec:
  min_scale: 1
  max_scale: 3
  cpu: 1
  memory_mb: 1024
```

### Template Docker:

```yaml
# deployment/deploy_config_docker.yaml

deployment:
  name: indufix-toolkit-docker
  source: external_docker
  image_uri: docker.io/chicuza/indufix-toolkit:latest
  type: dev

secrets:
  LLAMA_CLOUD_API_KEY: ${LLAMA_CLOUD_API_KEY}
```

### Usar:

```bash
python -m deployment.deploy_cli apply -f deployment/deploy_config.yaml
```

**Comportamento**:
- Se deployment com mesmo `name` existe → **UPDATE**
- Se deployment não existe → **CREATE**

---

## ⚙️ GitHub Actions CI/CD

### Setup:

1. **Adicionar Secrets ao GitHub**:
   - `Settings` → `Secrets and variables` → `Actions` → `New repository secret`
   - Adicionar:
     - `LANGSMITH_API_KEY`
     - `WORKSPACE_ID`
     - `INTEGRATION_ID`
     - `LLAMA_CLOUD_API_KEY`

2. **Workflow Criado**:
   - Arquivo: `.github/workflows/deploy_langsmith.yml`

3. **Triggers**:
   - Push to `main` branch → Deploy prod
   - Push to `dev` branch → Deploy dev
   - Manual trigger (workflow_dispatch)

### Workflow Resumo:

```yaml
name: Deploy to LangSmith Cloud

on:
  push:
    branches: [main, dev]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - Checkout code
      - Setup Python
      - Install dependencies
      - Deploy to LangSmith (create or update)
      - Wait for healthy
```

### Executar Manualmente:

1. GitHub → Actions → "Deploy to LangSmith Cloud"
2. Click "Run workflow"
3. Escolher branch e environment (dev/prod)
4. Run

---

## 📊 Exemplos Completos

### Exemplo 1: Deployment GitHub com Wait

```python
from deployment import LangSmithDeployClient

client = LangSmithDeployClient.from_env()

# Criar deployment
deployment = client.create_github_deployment(
    name="my-fastapi-agent",
    repo_url="https://github.com/user/fastapi-agent",
    branch="main",
    secrets={
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "DATABASE_URL": os.getenv("DATABASE_URL")
    },
    deployment_type="prod"
)

print(f"Deployment criado: {deployment['id']}")

# Aguardar deployment ficar healthy
try:
    client.wait_for_deployment(deployment['id'], timeout=600)
    status = client.get_deployment_status(deployment['id'])
    print(f"✅ Deployment healthy! URL: {status['url']}")
except Exception as e:
    print(f"❌ Error: {e}")
```

### Exemplo 2: Update Deployment para Nova Branch

```python
client = LangSmithDeployClient.from_env()

# Atualizar para branch dev
deployment = client.update_deployment(
    deployment_id="abc123",
    branch="dev",
    secrets={"DEBUG": "true"}
)

# Aguardar nova revisão ficar healthy
client.wait_for_deployment("abc123", timeout=300)
```

### Exemplo 3: Docker Registry Workflow

```bash
# 1. Build local
langgraph build -t my-agent:v1.0.0

# 2. Push to registry
docker push docker.io/username/my-agent:v1.0.0

# 3. Deploy via Python
python -c "
from deployment import LangSmithDeployClient
import os

client = LangSmithDeployClient.from_env()

deployment = client.create_docker_deployment(
    name='my-agent-prod',
    image_uri='docker.io/username/my-agent:v1.0.0',
    secrets={'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')}
)

print(f'Deployed: {deployment[\"id\"]}')
"
```

### Exemplo 4: CLI com Config YAML

```bash
# 1. Editar config
cat > my_deployment.yaml <<EOF
deployment:
  name: custom-agent
  source: github
  repo_url: https://github.com/user/custom-agent
  branch: main
  type: prod

secrets:
  OPENAI_API_KEY: \${OPENAI_API_KEY}
  CUSTOM_SECRET: \${CUSTOM_SECRET}
EOF

# 2. Apply
export OPENAI_API_KEY="sk-..."
export CUSTOM_SECRET="secret-value"
python -m deployment.deploy_cli apply -f my_deployment.yaml --wait
```

---

## 🐛 Troubleshooting

### Erro: "LANGSMITH_API_KEY environment variable not set"

**Solução**: Configurar environment variables:
```bash
export LANGSMITH_API_KEY="lsv2_sk_..."
export WORKSPACE_ID="..."
```

### Erro: "integration_id or INTEGRATION_ID env var required"

**Solução**: Para GitHub deployments, precisa do Integration ID:
```bash
export INTEGRATION_ID="..."
```

Ou passar explicitamente:
```python
client.create_deployment(..., integration_id="your-id")
```

### Erro: 403 Forbidden

**Causa**: API key inválida ou workspace ID incorreto

**Solução**: Verificar credenciais em https://smith.langchain.com/settings

### Deployment Timeout

**Causa**: Deployment demorando muito para ficar healthy

**Solução**:
1. Verificar logs do deployment no LangSmith UI
2. Aumentar timeout: `wait_for_deployment(id, timeout=1200)`
3. Verificar se secrets estão corretos
4. Verificar se langgraph.json está válido

### ImportError: No module named 'deployment'

**Solução**: Executar de dentro do diretório do projeto:
```bash
cd indufix-llamaindex-toolkit
python -m deployment.deploy_cli list
```

Ou instalar como package:
```bash
pip install -e .
```

---

## 📖 API Reference

### `LangSmithDeployClient`

#### Constructor:
```python
LangSmithDeployClient(
    api_key: str,
    workspace_id: str,
    base_url: Optional[str] = "https://api.host.langchain.com",
    timeout: int = 30
)
```

#### Methods:

**Deployment Management**:
- `create_deployment(...)` - Criar deployment
- `create_github_deployment(...)` - Helper para GitHub
- `create_docker_deployment(...)` - Helper para Docker
- `list_deployments(limit=100)` - Listar deployments
- `get_deployment(deployment_id)` - Detalhes
- `update_deployment(deployment_id, ...)` - Atualizar
- `delete_deployment(deployment_id, confirm=True)` - Deletar

**Status & Monitoring**:
- `get_deployment_status(deployment_id)` - Status atual
- `wait_for_deployment(deployment_id, timeout=600)` - Aguardar healthy

**Revisions**:
- `list_revisions(deployment_id)` - Listar revisões
- `redeploy_revision(deployment_id, revision_id)` - Redeploy

---

## 🎯 Próximos Passos

1. **Testar deployment manual**:
   ```bash
   python -m deployment.deploy_cli create --name test --repo ... --wait
   ```

2. **Configurar GitHub Actions**:
   - Adicionar secrets ao GitHub
   - Push código → auto-deploy

3. **Criar workflows específicos**:
   - Dev environment (auto-deploy from `dev` branch)
   - Prod environment (manual approval)
   - Staging environment

4. **Monitoramento**:
   - Verificar deployments: `python -m deployment.deploy_cli list`
   - Ver logs no LangSmith UI

---

## 📄 Arquivos do Projeto

```
indufix-llamaindex-toolkit/
├── deployment/
│   ├── __init__.py                   # Package init
│   ├── langsmith_deploy.py           # Wrapper principal
│   ├── deploy_cli.py                 # CLI interface
│   ├── exceptions.py                 # Custom exceptions
│   ├── deploy_config.yaml            # Template GitHub
│   └── deploy_config_docker.yaml     # Template Docker
├── .github/
│   └── workflows/
│       └── deploy_langsmith.yml      # CI/CD workflow
├── requirements-deploy.txt           # Dependencies
└── DEPLOYMENT_AUTOMATION_README.md   # Esta documentação
```

---

## ✅ Conclusão

Você agora tem ferramentas completas para deployment programático no LangSmith Cloud **sem usar a UI web**:

- ✅ Python library (importável)
- ✅ CLI interface (comandos)
- ✅ Config YAML (declarativo)
- ✅ GitHub Actions (CI/CD)

**Workflow Recomendado**:
1. Dev local: usar CLI para testes
2. Produção: GitHub Actions para deployment automático
3. Infraestrutura: Config YAML versionado em Git

**Próximo passo**: Testar criação de deployment!

```bash
python -m deployment.deploy_cli create --name test-agent --repo https://github.com/user/repo --wait
```

---

**Última atualização**: 2026-01-22
**Versão**: 1.0.0

**Desenvolvido para**: Automação de deployment LangSmith Cloud
