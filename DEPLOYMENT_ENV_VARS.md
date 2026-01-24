# Deployment Environment Variables Guide

This document explains all environment variables used in the LangGraph deployment on LangSmith Cloud, how they're configured in GitHub Secrets, and how to troubleshoot missing variables.

## Table of Contents

1. [Overview](#overview)
2. [GitHub Secrets Configuration](#github-secrets-configuration)
3. [Deployment-Time Variables](#deployment-time-variables)
4. [Runtime Variables](#runtime-variables)
5. [Environment Variable Flow](#environment-variable-flow)
6. [Troubleshooting](#troubleshooting)
7. [Verification](#verification)

---

## Overview

The deployment pipeline uses two types of environment variables:

1. **Deployment Credentials**: Used by GitHub Actions to authenticate with LangSmith Cloud and create/update deployments
2. **Runtime Secrets**: Passed to the deployed application and available at runtime

### Deployment URL

Current deployment:
- **URL**: `https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app`
- **Deployment ID**: `02c0d18a-1a0b-469a-baed-274744a670c6`
- **GitHub Repository**: `https://github.com/chicuza/indufix-llamaindex-toolkit`

---

## GitHub Secrets Configuration

All secrets are configured at: `https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions`

### Required Secrets

These secrets **MUST** be set for successful deployment:

#### 1. LangSmith Deployment Credentials

| Secret Name | Purpose | Where to Get |
|------------|---------|--------------|
| `LANGSMITH_API_KEY` | LangSmith API authentication | LangSmith Settings → API Keys |
| `WORKSPACE_ID` | LangSmith workspace identifier | LangSmith URL or API |
| `INTEGRATION_ID` | GitHub integration identifier | LangSmith Integrations |

**How to get these values:**
1. Go to [LangSmith](https://smith.langchain.com)
2. Navigate to Settings → API Keys
3. Create a new API key if needed
4. Note your workspace ID from the URL or API
5. Set up GitHub integration and note the integration ID

#### 2. LlamaCloud API Key

| Secret Name | Purpose | Where to Get |
|------------|---------|--------------|
| `LLAMA_CLOUD_API_KEY` | LlamaIndex toolkit authentication | [LlamaCloud Dashboard](https://cloud.llamaindex.ai) |

**Required for**: The Indufix LlamaIndex toolkit to query the knowledge base

#### 3. Anthropic API Key

| Secret Name | Purpose | Where to Get |
|------------|---------|--------------|
| `ANTHROPIC_API_KEY` | Claude LLM access | [Anthropic Console](https://console.anthropic.com) |

**Required for**: Running the LangGraph agent with Claude Sonnet 4.5

**Format**: Should start with `sk-ant-`

### Optional Secrets

These secrets are recommended but not required:

| Secret Name | Purpose | Default Value |
|------------|---------|---------------|
| `OPENAI_API_KEY` | OpenAI GPT models (optional) | Not set |
| `LANGCHAIN_TRACING_V2` | Enable LangSmith tracing | `true` |
| `LANGCHAIN_PROJECT` | LangSmith project name | `indufix-llamaindex-toolkit` |
| `LANGCHAIN_ENDPOINT` | LangSmith API endpoint | `https://api.smith.langchain.com` |

---

## Deployment-Time Variables

These variables are used **during deployment** by GitHub Actions:

### Used by CI/CD Pipeline

```yaml
# In .github/workflows/deploy_langsmith.yml
env:
  # Deployment credentials (not passed to app)
  LANGSMITH_API_KEY: ${{ secrets.LANGSMITH_API_KEY }}
  WORKSPACE_ID: ${{ secrets.WORKSPACE_ID }}
  INTEGRATION_ID: ${{ secrets.INTEGRATION_ID }}
```

**Purpose**: Authenticate GitHub Actions to create/update deployments

**Scope**: CI/CD pipeline only, **NOT** available in deployed application

---

## Runtime Variables

These variables are **passed to the deployed application** and available at runtime:

### Configured in Workflow

```yaml
# In .github/workflows/deploy_langsmith.yml (lines 174-181)
env:
  # Runtime secrets (passed to deployed app)
  LLAMA_CLOUD_API_KEY: ${{ secrets.LLAMA_CLOUD_API_KEY }}
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  LANGCHAIN_TRACING_V2: ${{ secrets.LANGCHAIN_TRACING_V2 || 'true' }}
  LANGCHAIN_PROJECT: ${{ secrets.LANGCHAIN_PROJECT || 'indufix-llamaindex-toolkit' }}
  LANGCHAIN_ENDPOINT: ${{ secrets.LANGCHAIN_ENDPOINT || 'https://api.smith.langchain.com' }}
  LANGCHAIN_API_KEY: ${{ secrets.LANGSMITH_API_KEY }}
```

### Configured in deploy_config.yaml

```yaml
# In deployment/deploy_config.yaml (lines 29-44)
secrets:
  # LlamaCloud API Key (REQUIRED)
  LLAMA_CLOUD_API_KEY: ${LLAMA_CLOUD_API_KEY}

  # LLM Provider API Keys (REQUIRED)
  ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
  OPENAI_API_KEY: ${OPENAI_API_KEY}

  # LangSmith Tracing & Observability (RECOMMENDED)
  LANGSMITH_API_KEY: ${LANGSMITH_API_KEY}
  LANGCHAIN_TRACING_V2: ${LANGCHAIN_TRACING_V2}
  LANGCHAIN_PROJECT: ${LANGCHAIN_PROJECT}
  LANGCHAIN_ENDPOINT: ${LANGCHAIN_ENDPOINT}
  LANGCHAIN_API_KEY: ${LANGCHAIN_API_KEY}
```

**Purpose**: Provide API keys and configuration to the deployed application

**Scope**: Available in the deployed LangGraph application at runtime

### How Runtime Variables Are Used

1. **ANTHROPIC_API_KEY**: Used in `agent.py` line 48
   ```python
   llm = ChatAnthropic(
       model="claude-sonnet-4-5-20250929",
       api_key=os.getenv("ANTHROPIC_API_KEY"),
       ...
   )
   ```

2. **LLAMA_CLOUD_API_KEY**: Used by the Indufix toolkit to query LlamaCloud indexes

3. **LANGCHAIN_TRACING_V2**: Enables automatic tracing of all LangGraph runs to LangSmith

4. **LANGCHAIN_PROJECT**: Organizes traces under a specific project name in LangSmith UI

---

## Environment Variable Flow

### Step 1: GitHub Secrets → GitHub Actions

```
GitHub Secrets (Repository Settings)
           ↓
GitHub Actions Workflow (.github/workflows/deploy_langsmith.yml)
           ↓
Environment Variables in CI/CD Runner
```

### Step 2: GitHub Actions → Deployment Script

```
GitHub Actions env section
           ↓
deployment/deploy_ci.py (reads env vars)
           ↓
deployment/deploy_config.yaml (${VAR_NAME} substitution)
           ↓
LangSmith Cloud API (create/update deployment)
```

### Step 3: LangSmith Cloud → Deployed Application

```
LangSmith Cloud Deployment
           ↓
Runtime Environment (container)
           ↓
agent.py (os.getenv("ANTHROPIC_API_KEY"))
indufix_toolkit (uses LLAMA_CLOUD_API_KEY)
```

---

## Troubleshooting

### Common Issues

#### 1. "ANTHROPIC_API_KEY not set" Error

**Symptom**: Deployment succeeds but agent fails at runtime

**Cause**: ANTHROPIC_API_KEY not properly passed to deployment

**Solution**:
1. Verify secret is set in GitHub: `Settings → Secrets → Actions → ANTHROPIC_API_KEY`
2. Check workflow file includes it in env section (line 175)
3. Verify deploy_config.yaml includes it in secrets section (line 36)
4. Re-run deployment workflow

#### 2. "LLAMA_CLOUD_API_KEY not found" Error

**Symptom**: Tools fail when trying to query LlamaCloud

**Cause**: LlamaCloud API key not configured

**Solution**:
1. Get API key from [LlamaCloud Dashboard](https://cloud.llamaindex.ai)
2. Add to GitHub Secrets as `LLAMA_CLOUD_API_KEY`
3. Verify it's in workflow env section (line 174)
4. Re-deploy

#### 3. Workflow Fails at "Validate required secrets" Step

**Symptom**: GitHub Actions workflow fails during validation

**Cause**: One or more required secrets not set

**Solution**:
1. Check workflow logs to see which secret is missing
2. Go to `https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions`
3. Add the missing secret(s)
4. Re-run workflow

#### 4. Deployment Succeeds but Health Check Fails

**Symptom**: Deployment completes but `/ok` endpoint returns errors

**Cause**: Runtime environment variables not properly configured

**Solution**:
1. Run verification script: `python verify_deployment_env.py --deployment-url <URL>`
2. Check LangSmith Cloud logs for the deployment
3. Verify all required secrets are present in deploy_config.yaml
4. Update deployment with correct secrets

### Verification Checklist

Use this checklist when troubleshooting:

- [ ] All required GitHub Secrets are set
- [ ] Workflow file references all required secrets
- [ ] deploy_config.yaml includes all secrets with ${VAR_NAME} syntax
- [ ] Deployment logs show successful secret substitution
- [ ] Health endpoint `/ok` returns 200
- [ ] MCP endpoint `/runs/stream` accepts requests
- [ ] LangSmith traces appear (if tracing enabled)

---

## Verification

### 1. Verify GitHub Secrets

```bash
# Cannot be automated - manual check required
# Go to: https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions
# Verify these secrets exist:
# - LANGSMITH_API_KEY
# - WORKSPACE_ID
# - INTEGRATION_ID
# - LLAMA_CLOUD_API_KEY
# - ANTHROPIC_API_KEY
```

### 2. Verify Deployment Environment

#### Using Python Script (Comprehensive)

```bash
# Install dependencies
pip install requests

# Run verification
python verify_deployment_env.py \
  --deployment-url https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app \
  --verbose
```

**Output includes**:
- Health check status
- Info endpoint data
- MCP tools availability
- Inferred environment variable status

#### Using PowerShell (Windows - Quick Test)

```powershell
# Run quick test
.\quick_deploy_test.ps1

# With custom URL
.\quick_deploy_test.ps1 -DeploymentUrl "https://your-deployment.us.langgraph.app"

# With verbose output
.\quick_deploy_test.ps1 -Verbose
```

#### Using Bash (Linux/Mac - Quick Test)

```bash
# Make executable
chmod +x quick_deploy_test.sh

# Run quick test
./quick_deploy_test.sh

# With custom URL
./quick_deploy_test.sh "https://your-deployment.us.langgraph.app"

# With verbose output
VERBOSE=true ./quick_deploy_test.sh
```

### 3. Manual Testing

#### Test Health Endpoint

```bash
curl https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/ok
# Expected: 200 OK
```

#### Test Info Endpoint

```bash
curl https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/info
# Expected: JSON with deployment info
```

#### Test Agent Invocation

```bash
curl -X POST \
  https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "messages": [
        {
          "role": "user",
          "content": "What tools do you have available?"
        }
      ]
    },
    "config": {},
    "stream_mode": ["values"]
  }'
# Expected: Streaming response with tool information
```

### 4. Check LangSmith Traces

If tracing is enabled:

1. Go to [LangSmith](https://smith.langchain.com)
2. Navigate to the `indufix-llamaindex-toolkit` project
3. Look for recent traces
4. Verify traces contain tool calls and responses

**If no traces appear**:
- Check `LANGCHAIN_TRACING_V2` is set to `"true"`
- Verify `LANGSMITH_API_KEY` or `LANGCHAIN_API_KEY` is set
- Ensure `LANGCHAIN_PROJECT` matches the project name

---

## Environment Variables Reference

### Complete List

| Variable | Type | Required | Purpose | Set In |
|----------|------|----------|---------|--------|
| `LANGSMITH_API_KEY` | Deployment | Yes | LangSmith authentication | GitHub Secrets |
| `WORKSPACE_ID` | Deployment | Yes | LangSmith workspace ID | GitHub Secrets |
| `INTEGRATION_ID` | Deployment | Yes | GitHub integration ID | GitHub Secrets |
| `LLAMA_CLOUD_API_KEY` | Runtime | Yes | LlamaCloud API access | GitHub Secrets |
| `ANTHROPIC_API_KEY` | Runtime | Yes | Claude LLM access | GitHub Secrets |
| `OPENAI_API_KEY` | Runtime | No | OpenAI GPT access | GitHub Secrets |
| `LANGCHAIN_TRACING_V2` | Runtime | No | Enable tracing | GitHub Secrets or default |
| `LANGCHAIN_PROJECT` | Runtime | No | Project name | GitHub Secrets or default |
| `LANGCHAIN_ENDPOINT` | Runtime | No | LangSmith endpoint | GitHub Secrets or default |
| `LANGCHAIN_API_KEY` | Runtime | No | Alternative to LANGSMITH_API_KEY | GitHub Secrets |

### Default Values

Variables with default values if not explicitly set:

```yaml
LANGCHAIN_TRACING_V2: "true"
LANGCHAIN_PROJECT: "indufix-llamaindex-toolkit"
LANGCHAIN_ENDPOINT: "https://api.smith.langchain.com"
```

---

## Best Practices

### Security

1. **Never commit secrets to code**
   - Use GitHub Secrets for all sensitive values
   - Never hardcode API keys in source files
   - Use `.env` files locally (excluded from git)

2. **Rotate keys regularly**
   - Update API keys every 90 days
   - Immediately rotate if compromised
   - Use separate keys for dev/prod

3. **Minimum permissions**
   - Use read-only keys where possible
   - Limit key scope to required resources
   - Monitor key usage in provider dashboards

### Deployment

1. **Validate before deploy**
   - Workflow validates all required secrets before deploying
   - Add new secrets to validation step if adding dependencies

2. **Test after deploy**
   - Always run verification scripts after deployment
   - Check LangSmith traces for first few runs
   - Monitor error rates in LangSmith dashboard

3. **Document changes**
   - Update this file when adding new environment variables
   - Document required vs optional secrets
   - Note default values and their source

### Monitoring

1. **Set up alerts**
   - Monitor deployment health endpoint
   - Alert on repeated failures
   - Track API usage and rate limits

2. **Regular audits**
   - Review which secrets are actually used
   - Remove unused secrets
   - Verify secrets are properly scoped

---

## Support

### Getting Help

1. **Check workflow logs**: GitHub Actions → Latest workflow run
2. **Check deployment logs**: LangSmith UI → Deployments → Logs
3. **Run verification**: `python verify_deployment_env.py --deployment-url <URL>`
4. **Review traces**: LangSmith UI → Project → Traces

### Resources

- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangGraph Cloud Documentation](https://langchain-ai.github.io/langgraph/cloud/)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [LlamaCloud Documentation](https://docs.cloud.llamaindex.ai/)
- [Anthropic API Documentation](https://docs.anthropic.com/)

---

**Last Updated**: 2026-01-23
**Deployment ID**: 02c0d18a-1a0b-469a-baed-274744a670c6
**Deployment URL**: https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app
