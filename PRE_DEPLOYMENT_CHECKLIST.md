# Pre-Deployment Checklist

**Project**: Indufix LlamaIndex Toolkit
**Purpose**: Ensure all prerequisites are met before triggering production deployment
**Owner**: DevOps/Operations Team
**Last Updated**: 2026-01-23

---

## Critical GitHub Secrets Configuration

All secrets must be configured in GitHub repository settings before deployment.
Location: `https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions`

### Required Secrets (CRITICAL - Deployment will fail without these)

| Secret Name | Description | Where to Get | Validation |
|-------------|-------------|--------------|------------|
| `LANGSMITH_API_KEY` | LangSmith API key for deployment | https://smith.langchain.com/settings | Starts with `lsv2_pt_` or `ls__` |
| `WORKSPACE_ID` | LangSmith workspace ID | LangSmith UI > Settings > Workspace | UUID format (36 chars) |
| `INTEGRATION_ID` | GitHub integration ID | LangSmith UI > Settings > Integrations | UUID format (36 chars) |
| `LLAMA_CLOUD_API_KEY` | LlamaCloud API key for RAG | https://cloud.llamaindex.ai/api-key | Starts with `llx-` |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | https://console.anthropic.com/settings/keys | Starts with `sk-ant-` |

### Optional Secrets (Recommended for production)

| Secret Name | Description | Where to Get | Default if Not Set |
|-------------|-------------|--------------|-------------------|
| `OPENAI_API_KEY` | OpenAI API key (alternative LLM) | https://platform.openai.com/api-keys | None (uses Anthropic only) |
| `LANGCHAIN_TRACING_V2` | Enable LangSmith tracing | Manual entry | `true` |
| `LANGCHAIN_PROJECT` | LangSmith project name | Manual entry | `indufix-llamaindex-toolkit` |
| `LANGCHAIN_ENDPOINT` | LangSmith API endpoint | Manual entry | `https://api.smith.langchain.com` |

---

## Pre-Deployment Validation Steps

### Step 1: Verify Code Quality

```bash
# Run from repository root
cd C:\Users\chicu\langchain\indufix-llamaindex-toolkit

# Check git status
git status
# Expected: clean working directory or only intended changes

# Verify on correct branch
git branch
# Expected: * main (for production) or * dev (for development)

# Check recent commits
git log --oneline -5
# Expected: all commits are intended for deployment
```

**Checklist:**
- [ ] Working directory is clean (no untracked changes)
- [ ] On the correct branch (`main` for prod, `dev` for dev)
- [ ] All commits are reviewed and approved
- [ ] No debugging code or commented-out sections
- [ ] All tests passing locally

---

### Step 2: Validate Configuration Files

```bash
# Validate deployment configuration
python -c "
import yaml
from pathlib import Path

config_file = Path('deployment/deploy_config_prod.yaml')
with open(config_file) as f:
    config = yaml.safe_load(f)

print('Deployment Configuration:')
print(f'  Name: {config[\"deployment\"][\"name\"]}')
print(f'  Source: {config[\"deployment\"][\"source\"]}')
print(f'  Branch: {config[\"deployment\"][\"branch\"]}')
print(f'  Repo: {config[\"deployment\"][\"repo_url\"]}')
print(f'  Type: {config[\"deployment\"][\"type\"]}')
print(f'  Secrets configured: {len(config.get(\"secrets\", {}))}')
print('Configuration is valid!')
"
```

**Checklist:**
- [ ] `deployment/deploy_config_prod.yaml` exists and is valid
- [ ] Deployment name matches intended environment
- [ ] Repository URL is correct
- [ ] Branch is `main` for production
- [ ] Deployment type is `prod` for production
- [ ] All required secrets are listed in config

---

### Step 3: Verify GitHub Secrets

```bash
# Run the trigger_deployment.py script in dry-run mode
python trigger_deployment.py --dry-run --environment prod

# This will validate all secrets without actually deploying
```

**Expected Output:**
```
============================================================
GITHUB SECRETS VALIDATION
============================================================
Checking required GitHub Secrets...

REQUIRED SECRETS:
  ✓ LANGSMITH_API_KEY: Configured
  ✓ WORKSPACE_ID: Configured
  ✓ INTEGRATION_ID: Configured
  ✓ LLAMA_CLOUD_API_KEY: Configured
  ✓ ANTHROPIC_API_KEY: Configured

OPTIONAL SECRETS:
  ✓ OPENAI_API_KEY: Configured
  ✓ LANGCHAIN_TRACING_V2: Configured

All required secrets are configured!
============================================================
```

**Checklist:**
- [ ] All REQUIRED secrets show as "Configured"
- [ ] Secret values are current (not expired)
- [ ] Secret values are from production accounts (not test/dev)
- [ ] No warnings or errors in validation

---

### Step 4: Verify LangSmith Integration

```bash
# Test LangSmith API connection
python -c "
import os
import requests

api_key = os.environ.get('LANGSMITH_API_KEY')  # Load from .env file
workspace_id = os.environ.get('WORKSPACE_ID')

if not api_key or not workspace_id:
    print('ERROR: Set LANGSMITH_API_KEY and WORKSPACE_ID in .env file')
    exit(1)

# Test API connection
headers = {'x-api-key': api_key}
url = f'https://api.smith.langchain.com/api/v1/workspaces/{workspace_id}'

response = requests.get(url, headers=headers)
if response.status_code == 200:
    print('✓ LangSmith API connection successful')
    print(f'✓ Workspace: {response.json().get(\"display_name\")}')
else:
    print(f'ERROR: API returned {response.status_code}')
    print(response.text)
"
```

**Checklist:**
- [ ] LangSmith API connection successful
- [ ] Workspace is correct
- [ ] No authentication errors
- [ ] API quota available

---

### Step 5: Verify GitHub Integration

```bash
# Check GitHub integration status
python -c "
import os
import requests

api_key = os.environ.get('LANGSMITH_API_KEY')
workspace_id = os.environ.get('WORKSPACE_ID')
integration_id = os.environ.get('INTEGRATION_ID')

headers = {'x-api-key': api_key}
url = f'https://api.smith.langchain.com/api/v1/workspaces/{workspace_id}/integrations/{integration_id}'

response = requests.get(url, headers=headers)
if response.status_code == 200:
    integration = response.json()
    print('✓ GitHub integration found')
    print(f'✓ Provider: {integration.get(\"provider\")}')
    print(f'✓ Status: {integration.get(\"status\")}')
else:
    print(f'ERROR: Integration check failed ({response.status_code})')
"
```

**Checklist:**
- [ ] GitHub integration exists
- [ ] Integration status is "active"
- [ ] Integration provider is "github"
- [ ] Repository access granted

---

### Step 6: Test Deployment Readiness

```bash
# Run full pre-deployment validation
python trigger_deployment.py --validate-only --environment prod
```

**Expected Output:**
```
============================================================
PRE-DEPLOYMENT VALIDATION
============================================================

1. Code Quality:                    ✓ PASSED
2. Configuration Files:             ✓ PASSED
3. GitHub Secrets:                  ✓ PASSED
4. LangSmith Connection:            ✓ PASSED
5. GitHub Integration:              ✓ PASSED
6. Deployment Quota:                ✓ PASSED

ALL VALIDATIONS PASSED
Ready to deploy!
============================================================
```

**Checklist:**
- [ ] All validation checks passed
- [ ] No warnings or errors
- [ ] Deployment quota available
- [ ] Previous deployments healthy

---

## Rollback Plan

### Before Deployment: Document Current State

```bash
# Get current deployment status
python deployment_status.py --save-baseline

# This saves current state to rollback_baseline.json
```

**Checklist:**
- [ ] Current production deployment ID documented
- [ ] Current revision ID documented
- [ ] Current deployment URL verified
- [ ] Current health status confirmed as "healthy"
- [ ] Baseline metrics captured

---

### If Deployment Fails: Rollback Procedure

**Automatic Rollback:**
- GitHub Actions workflow will attempt automatic rollback on failure
- Monitor workflow logs for rollback status

**Manual Rollback (if automatic fails):**

```bash
# Run manual rollback
python -c "
import os
from deployment.langsmith_deploy import LangSmithDeployClient

# Load credentials
client = LangSmithDeployClient.from_env()

# Load baseline
import json
with open('rollback_baseline.json') as f:
    baseline = json.load(f)

deployment_id = baseline['deployment_id']
previous_revision = baseline['previous_revision_id']

print(f'Rolling back deployment {deployment_id}')
print(f'To revision: {previous_revision}')

# Execute rollback
client.rollback_to_revision(deployment_id, previous_revision)
print('Rollback initiated successfully')
"
```

**Rollback Verification:**
```bash
# Verify rollback successful
python deployment_status.py --verify-rollback
```

**Expected Time to Rollback:** < 5 minutes

**Checklist:**
- [ ] Rollback procedure tested in staging
- [ ] Rollback scripts are accessible
- [ ] Team knows how to execute rollback
- [ ] Rollback contact list is current

---

## Contact Information

### Emergency Contacts (24/7)

| Role | Contact | Phone | Slack |
|------|---------|-------|-------|
| On-Call DevOps | [Name] | [Phone] | @oncall-devops |
| Technical Lead | [Name] | [Phone] | @tech-lead |
| Platform Team Lead | [Name] | [Phone] | @platform-lead |

### Escalation Path

1. **Level 1** (0-15 min): On-Call DevOps Engineer
2. **Level 2** (15-30 min): Technical Lead
3. **Level 3** (30+ min): Platform Team Lead + CTO

### Support Resources

- **LangSmith Support**: https://docs.smith.langchain.com/support
- **GitHub Support**: https://support.github.com
- **Internal Runbook**: `DEPLOYMENT_TROUBLESHOOTING.md`
- **Status Page**: https://status.langchain.com

---

## Deployment Decision Checklist

### Is the system ready to deploy?

- [ ] **All pre-deployment validations passed** (Steps 1-6)
- [ ] **All required secrets configured and valid**
- [ ] **Rollback plan documented and tested**
- [ ] **Team is available for monitoring** (next 2 hours)
- [ ] **No planned maintenance windows** (LangSmith, GitHub)
- [ ] **No current production incidents**
- [ ] **Deployment window is appropriate** (avoid peak usage times)
- [ ] **Stakeholders have been notified**
- [ ] **Change approval obtained** (if required)
- [ ] **Backup/baseline captured**

### Red Flags - DO NOT DEPLOY IF:

- [ ] **Any validation step failed**
- [ ] **Required secrets are missing or expired**
- [ ] **Current production has active incidents**
- [ ] **Team is not available for monitoring**
- [ ] **During peak business hours** (without approval)
- [ ] **LangSmith or GitHub has service issues**
- [ ] **Rollback plan is not ready**
- [ ] **Previous deployment is unhealthy**

---

## Deployment Execution

### Ready to Deploy?

If all checks pass, proceed with deployment:

```bash
# Trigger production deployment
python trigger_deployment.py --environment prod --wait

# This will:
# 1. Validate all prerequisites
# 2. Trigger GitHub Actions workflow
# 3. Monitor deployment progress
# 4. Report final status
```

**Monitor deployment:**
- GitHub Actions: https://github.com/chicuza/indufix-llamaindex-toolkit/actions
- LangSmith UI: https://smith.langchain.com/deployments
- Deployment logs: Check workflow output

**Expected deployment time:** 15-30 minutes

---

## Post-Deployment Validation

After deployment completes, run:

```bash
# Comprehensive post-deployment validation
python post_deploy_validate.py --environment prod

# This will:
# 1. Verify deployment is ready
# 2. Test health endpoints
# 3. Validate MCP tools
# 4. Test tool invocations
# 5. Generate validation report
```

See `post_deploy_validate.py` for detailed validation steps.

---

## Sign-Off

**Deployment Date/Time**: ___________________
**Environment**: ☐ Development ☐ Production
**Prepared By**: ___________________
**Approved By**: ___________________

**Pre-Deployment Checklist Status**: ☐ Complete ☐ Incomplete
**Ready to Deploy**: ☐ Yes ☐ No

**Notes:**
_____________________________________________________________________________
_____________________________________________________________________________
_____________________________________________________________________________

---

## Appendix: Quick Reference

### Environment Variables (for local testing)

Create `.env` file with:
```bash
# LangSmith Deployment
LANGSMITH_API_KEY=lsv2_pt_your-key-here
WORKSPACE_ID=your-workspace-id
INTEGRATION_ID=your-integration-id

# Application Runtime
LLAMA_CLOUD_API_KEY=llx-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here

# LangSmith Tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=indufix-llamaindex-toolkit
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### Quick Commands

```bash
# Validate secrets only
python trigger_deployment.py --validate-secrets

# Dry run (no actual deployment)
python trigger_deployment.py --dry-run --environment prod

# Full validation without deployment
python trigger_deployment.py --validate-only --environment prod

# Deploy to development
python trigger_deployment.py --environment dev --wait

# Deploy to production
python trigger_deployment.py --environment prod --wait

# Check deployment status
python deployment_status.py

# Validate deployed application
python post_deploy_validate.py
```

---

**Document Version**: 1.0
**Last Review**: 2026-01-23
**Next Review**: 2026-02-23
