# Deployment Operations Guide

**Project**: Indufix LlamaIndex Toolkit
**Purpose**: Complete operational guide for deployment management
**Owner**: DevOps/Operations Team
**Last Updated**: 2026-01-23

---

## Overview

This guide provides a complete operational framework for managing deployments of the Indufix LlamaIndex Toolkit to LangSmith Cloud. It includes pre-deployment validation, deployment execution, post-deployment verification, monitoring, and troubleshooting procedures.

---

## Quick Start

### First Time Setup

1. **Install Prerequisites:**
   ```bash
   # Install required packages
   pip install requests pyyaml python-dotenv anthropic

   # Install GitHub CLI (for deployment triggering)
   # Windows: winget install GitHub.cli
   # macOS: brew install gh
   # Linux: See https://cli.github.com/

   # Authenticate GitHub CLI
   gh auth login
   ```

2. **Configure GitHub Secrets:**
   - Follow: `PRE_DEPLOYMENT_CHECKLIST.md` Section 2
   - Or use: `GITHUB_SECRETS_SETUP_GUIDE.md`
   - Verify: `python trigger_deployment.py --validate-secrets`

3. **Set Up Local Environment:**
   ```bash
   # Copy example environment file
   cp .env.example .env

   # Edit .env with your credentials
   # Required:
   # - LANGSMITH_API_KEY
   # - WORKSPACE_ID
   # - LLAMA_CLOUD_API_KEY
   # - ANTHROPIC_API_KEY
   ```

4. **Validate Setup:**
   ```bash
   # Run full validation
   python trigger_deployment.py --validate-only --environment prod

   # Expected output: "ALL VALIDATIONS PASSED"
   ```

---

## Deployment Workflow

### Standard Deployment Process

```
┌─────────────────────────────────────────────────────────────┐
│                     PRE-DEPLOYMENT                          │
├─────────────────────────────────────────────────────────────┤
│ 1. Review PRE_DEPLOYMENT_CHECKLIST.md                      │
│ 2. Run: python trigger_deployment.py --validate-only       │
│ 3. Save baseline: python deployment_status.py --save-baseline│
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      DEPLOYMENT                             │
├─────────────────────────────────────────────────────────────┤
│ 1. Trigger: python trigger_deployment.py --environment prod --wait│
│ 2. Monitor: GitHub Actions + LangSmith UI                  │
│ 3. Expected time: 15-30 minutes                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  POST-DEPLOYMENT                            │
├─────────────────────────────────────────────────────────────┤
│ 1. Validate: python post_deploy_validate.py --environment prod│
│ 2. Check status: python deployment_status.py --environment prod│
│ 3. Monitor for 2 hours (active), then 24 hours (periodic)  │
└─────────────────────────────────────────────────────────────┘
```

---

## Operational Scripts

### 1. trigger_deployment.py

**Purpose:** Validate prerequisites and trigger deployment via GitHub Actions

**Usage:**
```bash
# Validate secrets only
python trigger_deployment.py --validate-secrets

# Dry run (validate but don't deploy)
python trigger_deployment.py --dry-run --environment prod

# Full validation without deployment
python trigger_deployment.py --validate-only --environment prod

# Deploy to development
python trigger_deployment.py --environment dev --wait

# Deploy to production
python trigger_deployment.py --environment prod --wait
```

**Features:**
- ✅ Validates Git status (branch, uncommitted changes)
- ✅ Validates configuration files (YAML syntax, required fields)
- ✅ Checks GitHub Secrets (via gh CLI)
- ✅ Tests LangSmith API connection
- ✅ Verifies GitHub integration status
- ✅ Triggers GitHub Actions workflow
- ✅ Monitors workflow execution (optional)
- ✅ Saves baseline for rollback

**Output Example:**
```
============================================================
PRE-DEPLOYMENT VALIDATION
============================================================

Validating: Code Quality (Git Status)
----------------------------------------------------------------------
Current Branch: main
Uncommitted Changes: No
Last Commit: feat: add new search tool

✓ PASSED: Git status OK (on main)

Validating: Configuration Files
----------------------------------------------------------------------
Deployment Name: indufix-llamaindex-toolkit
Source: github
Repository: https://github.com/chicuza/indufix-llamaindex-toolkit
Branch: main
Type: prod
Secrets Configured: 5

✓ PASSED: Configuration file valid: deploy_config_prod.yaml

...

============================================================
VALIDATION SUMMARY
============================================================
✓ PASSED: Code Quality (Git Status)
✓ PASSED: Configuration Files
✓ PASSED: GitHub Secrets
✓ PASSED: LangSmith Connection
✓ PASSED: GitHub Integration

✓ ALL VALIDATIONS PASSED
Ready to deploy!
```

---

### 2. post_deploy_validate.py

**Purpose:** Comprehensive post-deployment validation including health checks and tool testing

**Usage:**
```bash
# Validate current deployment
python post_deploy_validate.py

# Validate specific environment
python post_deploy_validate.py --environment prod

# Generate detailed report
python post_deploy_validate.py --report validation_report.json

# Quick health check only
python post_deploy_validate.py --quick
```

**Validation Steps:**
1. ✅ Get deployment information from LangSmith API
2. ✅ Wait for deployment to be ready (DEPLOYED + healthy)
3. ✅ Test `/ok` health endpoint
4. ✅ Test `/mcp` endpoint with authentication
5. ✅ Validate expected tools are available
6. ✅ Test actual tool invocation with real parameters
7. ✅ Verify ANTHROPIC_API_KEY is working

**Output Example:**
```
============================================================
POST-DEPLOYMENT VALIDATION
============================================================

Validating: Get Deployment Info
----------------------------------------------------------------------
Deployment ID: dep_abc123
Deployment Name: indufix-llamaindex-toolkit
Deployment URL: https://indufix-llamaindex-toolkit-xyz.langgraph.app
Health: healthy
State: DEPLOYED
Latest Revision: rev_def456

✓ PASSED: Deployment info retrieved successfully

Validating: Test Health Endpoint
----------------------------------------------------------------------
Testing: https://indufix-llamaindex-toolkit-xyz.langgraph.app/ok
Status Code: 200
Response Time: 145.23ms
Response: {"status": "ok"}

✓ PASSED: Health endpoint OK (145.23ms)

Validating: Test MCP Endpoint
----------------------------------------------------------------------
Testing: https://indufix-llamaindex-toolkit-xyz.langgraph.app/mcp
Status Code: 200
Response Time: 523.45ms
Tools Found: 3
  - search_rules: Search for rules in LlamaIndex...
  - retrieve_context: Retrieve contextual information...
  - find_equivalence: Find standard equivalences...

✓ PASSED: MCP endpoint OK (3 tools, 523.45ms)

...

============================================================
VALIDATION SUMMARY
============================================================
Environment: prod
Deployment ID: dep_abc123
Deployment URL: https://indufix-llamaindex-toolkit-xyz.langgraph.app
Duration: 45.23s

Results:
  Total: 7
  Passed: 7 ✓
  Failed: 0 ✗

✓ ALL VALIDATIONS PASSED
Deployment is healthy and operational!
```

---

### 3. deployment_status.py

**Purpose:** Real-time dashboard showing deployment status, health metrics, and configuration

**Usage:**
```bash
# Show current status
python deployment_status.py

# Show specific environment
python deployment_status.py --environment prod

# Continuous monitoring (refresh every 30s)
python deployment_status.py --watch --interval 30

# Save baseline for rollback
python deployment_status.py --save-baseline

# Verify rollback was successful
python deployment_status.py --verify-rollback
```

**Dashboard Sections:**
1. **Deployment Information:** ID, name, state, health, URL
2. **Health Checks:** `/ok` and `/mcp` endpoint testing
3. **Environment Variables:** Configured secrets (masked)
4. **Metrics Summary:** Status, uptime, recent activity
5. **Quick Actions:** Links and commands for common tasks

**Output Example:**
```
============================================================
       DEPLOYMENT STATUS DASHBOARD - PROD
============================================================

DEPLOYMENT INFORMATION
----------------------------------------------------------------------
Name:           indufix-llamaindex-toolkit
ID:             dep_abc123
Environment:    prod
State:          DEPLOYED
Health:         healthy
URL:            https://indufix-llamaindex-toolkit-xyz.langgraph.app
Latest Revision: rev_def456
Revision State:  DEPLOYED
Created:         15m ago

HEALTH CHECKS
----------------------------------------------------------------------
Testing health endpoint...
  ✓ Health endpoint: OK (156.78ms)

Testing MCP endpoint...
  ✓ MCP endpoint: OK (3 tools, 498.34ms)

  Available tools:
    - search_rules
    - retrieve_context
    - find_equivalence

ENVIRONMENT VARIABLES
----------------------------------------------------------------------
Configured variables (from local environment):
  ✓ LANGSMITH_API_KEY: lsv2_pt_...xyz123ab
  ✓ WORKSPACE_ID: e6e330e4...f307394
  ✓ LLAMA_CLOUD_API_KEY: llx-...456def
  ✓ ANTHROPIC_API_KEY: sk-ant-...789ghi
  ✓ LANGCHAIN_TRACING_V2: ***

METRICS SUMMARY
----------------------------------------------------------------------
Status:          ✓ HEALTHY

RECENT ACTIVITY
----------------------------------------------------------------------
Last updated:    5m ago
Created:         2h ago

QUICK ACTIONS
----------------------------------------------------------------------
Monitor in LangSmith UI:
  https://smith.langchain.com/deployments/dep_abc123

Run validation:
  python post_deploy_validate.py --environment prod

View logs:
  Check LangSmith UI for deployment logs

============================================================
Last updated: 2026-01-23 14:30:45
============================================================
```

---

## Operational Procedures

### Daily Operations

**Morning Health Check (5 minutes):**
```bash
# Check deployment status
python deployment_status.py --environment prod

# Expected: State=DEPLOYED, Health=healthy
# If not healthy, investigate immediately
```

**Weekly Validation (15 minutes):**
```bash
# Full validation suite
python post_deploy_validate.py --environment prod --report weekly_validation.json

# Review report for any warnings
# Update metrics dashboard
```

**Monthly Review (1 hour):**
- Review deployment metrics trends
- Check for dependency updates
- Review and update secrets (rotation)
- Update operational documentation
- Test rollback procedures in staging

---

### Incident Response

**Severity Levels:**

**P0 - Critical (System Down):**
- Deployment not accessible
- All requests failing
- Data loss/corruption

**Response:**
1. Execute immediate rollback (see below)
2. Notify team via #oncall-alerts
3. Page on-call engineer
4. Create incident ticket
5. Start incident timeline

**P1 - High (Degraded Service):**
- Partial functionality broken
- High error rate (>5%)
- Slow response times (>5s)

**Response:**
1. Assess impact and scope
2. Notify team via #engineering
3. Decide: rollback or hotfix
4. Monitor closely
5. Document in incident log

**P2 - Medium (Non-critical Issue):**
- Single tool failing
- Minor performance degradation
- Configuration issue

**Response:**
1. Create ticket
2. Investigate during business hours
3. Plan fix for next deployment
4. Monitor for escalation

---

### Rollback Procedures

**Quick Rollback (5 minutes):**
```bash
# 1. Save current state
python deployment_status.py --save-baseline

# 2. Load deployment info
python -c "
from deployment.langsmith_deploy import LangSmithDeployClient

client = LangSmithDeployClient.from_env()

# Get deployment ID (replace with actual)
deployment_id = 'dep_abc123'

# Rollback to previous revision
client.rollback_to_previous(deployment_id)
print('Rollback initiated')
"

# 3. Wait for rollback to complete
sleep 180

# 4. Verify rollback
python deployment_status.py --verify-rollback

# 5. Validate
python post_deploy_validate.py --quick
```

**Rollback to Specific Revision:**
```python
from deployment.langsmith_deploy import LangSmithDeployClient

client = LangSmithDeployClient.from_env()

# Rollback to known good revision
client.rollback_to_revision(
    deployment_id='dep_abc123',
    revision_id='rev_good456'
)
```

---

### Monitoring Schedule

**Active Monitoring (First 2 Hours Post-Deployment):**
- Check every 15 minutes
- Monitor error rates
- Watch response times
- Review logs for warnings

**Extended Monitoring (2-24 Hours Post-Deployment):**
- Check every 2 hours
- Compare to baseline metrics
- Look for trends/patterns
- Verify no degradation

**Ongoing Monitoring (After 24 Hours):**
- Daily health check
- Weekly validation
- Monthly review
- Continuous automated alerts

---

## Critical GitHub Secrets

All secrets MUST be configured before deployment:

| Secret | Required | Where to Get | Format |
|--------|----------|--------------|--------|
| LANGSMITH_API_KEY | Yes | https://smith.langchain.com/settings | `lsv2_pt_...` |
| WORKSPACE_ID | Yes | LangSmith UI > Settings > Workspace | UUID (36 chars) |
| INTEGRATION_ID | Yes | LangSmith UI > Settings > Integrations | UUID (36 chars) |
| LLAMA_CLOUD_API_KEY | Yes | https://cloud.llamaindex.ai/api-key | `llx-...` |
| ANTHROPIC_API_KEY | Yes | https://console.anthropic.com/settings/keys | `sk-ant-...` |
| OPENAI_API_KEY | No | https://platform.openai.com/api-keys | `sk-...` |

**Add Secrets:**
```bash
# Via GitHub UI
https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions

# Via GitHub CLI
gh secret set LANGSMITH_API_KEY --body "$LANGSMITH_API_KEY"
gh secret set WORKSPACE_ID --body "$WORKSPACE_ID"
gh secret set INTEGRATION_ID --body "$INTEGRATION_ID"
gh secret set LLAMA_CLOUD_API_KEY --body "$LLAMA_CLOUD_API_KEY"
gh secret set ANTHROPIC_API_KEY --body "$ANTHROPIC_API_KEY"
```

**Verify Secrets:**
```bash
gh secret list

# Expected output:
# ANTHROPIC_API_KEY
# INTEGRATION_ID
# LANGSMITH_API_KEY
# LLAMA_CLOUD_API_KEY
# WORKSPACE_ID
```

---

## Key Metrics to Monitor

### Deployment Health
- **State:** Should be "DEPLOYED"
- **Health:** Should be "healthy"
- **Uptime:** Target >99.9%

### Endpoint Performance
- **Health Endpoint (/ok):** <500ms (target <200ms)
- **MCP Endpoint (/mcp):** <2s (target <1s)
- **Tool Invocation:** <5s (target <3s)

### Error Rates
- **Total Errors:** <0.1% of requests
- **4xx Errors:** <1% (mostly 401 auth)
- **5xx Errors:** <0.01% (server errors)

### Resource Utilization
- **CPU:** <70% average
- **Memory:** <80% of allocated
- **Request Rate:** Track trend

---

## Troubleshooting Quick Reference

### Common Issues

| Issue | Quick Fix | Documentation |
|-------|-----------|---------------|
| Missing secrets | `gh secret set SECRET_NAME` | DEPLOYMENT_TROUBLESHOOTING.md #Pre-Deployment |
| Health check 404 | Wait 2-3 minutes for DNS | DEPLOYMENT_TROUBLESHOOTING.md #Post-Deployment |
| MCP 401 error | Check header names (case-sensitive) | DEPLOYMENT_TROUBLESHOOTING.md #Post-Deployment |
| Tools not available | Check tool registration code | DEPLOYMENT_TROUBLESHOOTING.md #Post-Deployment |
| ANTHROPIC_API_KEY not working | Verify in secrets + redeploy | DEPLOYMENT_TROUBLESHOOTING.md #Runtime |
| Build timeout | Check dependencies, increase timeout | DEPLOYMENT_TROUBLESHOOTING.md #Deployment |
| Integration not connected | Reconnect in LangSmith UI | DEPLOYMENT_TROUBLESHOOTING.md #Deployment |

**Full troubleshooting guide:** `DEPLOYMENT_TROUBLESHOOTING.md`

---

## Documentation Index

### Pre-Deployment
- **PRE_DEPLOYMENT_CHECKLIST.md** - Complete pre-deployment checklist
- **GITHUB_SECRETS_SETUP_GUIDE.md** - Setting up GitHub Secrets
- **PRODUCTION_DEPLOYMENT_CHECKLIST.md** - Production-specific checklist

### Deployment
- **trigger_deployment.py** - Deployment automation script
- **WORKFLOW_TRIGGER_GUIDE.md** - GitHub Actions workflow guide

### Post-Deployment
- **post_deploy_validate.py** - Validation automation
- **deployment_status.py** - Status dashboard
- **VALIDATION_REPORT.md** - Validation report template

### Operations
- **DEPLOYMENT_TROUBLESHOOTING.md** - Complete troubleshooting guide
- **DEPLOYMENT_OPERATIONS_GUIDE.md** - This document

### Technical
- **deployment/deploy_ci.py** - CI/CD deployment script
- **deployment/deploy_github_action.py** - GitHub Actions integration
- **deployment/langsmith_deploy.py** - LangSmith API client

---

## Success Criteria

### Pre-Deployment
✅ All validations pass
✅ All secrets configured
✅ Baseline saved
✅ Team notified

### Deployment
✅ Workflow completes successfully
✅ Build completes in <15 minutes
✅ Deployment reaches DEPLOYED state
✅ Health checks pass

### Post-Deployment
✅ All validation tests pass
✅ Tools are accessible and working
✅ ANTHROPIC_API_KEY validated (via tool invocation)
✅ Response times within SLA
✅ No errors in first 30 minutes
✅ Metrics match baseline

---

## Emergency Contacts

### Internal
- **On-Call DevOps:** [Contact Info]
- **Technical Lead:** [Contact Info]
- **Platform Lead:** [Contact Info]

### External
- **LangSmith Support:** support@langchain.com
- **Anthropic Support:** support@anthropic.com
- **LlamaCloud Support:** support@llamaindex.ai

---

## Quick Commands Reference

```bash
# Deployment
python trigger_deployment.py --environment prod --wait

# Validation
python post_deploy_validate.py --environment prod

# Status
python deployment_status.py --environment prod

# Monitoring
python deployment_status.py --watch --interval 30

# Baseline
python deployment_status.py --save-baseline

# Secrets
gh secret list
gh secret set SECRET_NAME --body "$VALUE"

# GitHub Actions
gh workflow run deploy_langsmith.yml -f environment=prod
gh run list --workflow=deploy_langsmith.yml
gh run view [run-id] --log

# Health Check
curl https://your-deployment.langgraph.app/ok

# MCP Test
curl -X POST https://your-deployment.langgraph.app/mcp \
  -H "X-Api-Key: $LANGSMITH_API_KEY" \
  -H "X-Tenant-Id: $WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

---

## Change Log

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-23 | Initial operational guide | DevOps Team |

---

**Next Review:** 2026-02-23
**Document Owner:** DevOps Team
**Classification:** Internal Use Only

---

## Appendix: Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      GitHub Repository                      │
│  indufix-llamaindex-toolkit                                 │
│  - Code, Tools, Configuration                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Push to main/dev
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   GitHub Actions                            │
│  Workflow: deploy_langsmith.yml                             │
│  - Validate secrets                                         │
│  - Run deployment script                                    │
│  - Monitor deployment                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Deploy via API
                     ↓
┌─────────────────────────────────────────────────────────────┐
│                   LangSmith Cloud                           │
│  - Build Docker image                                       │
│  - Deploy to infrastructure                                 │
│  - Configure secrets                                        │
│  - Expose MCP endpoint                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ Deployed at
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              Production Deployment                          │
│  https://indufix-llamaindex-toolkit-xyz.langgraph.app       │
│  - Health endpoint: /ok                                     │
│  - MCP endpoint: /mcp                                       │
│  - Tools: search, retrieve, find_equivalence                │
└─────────────────────────────────────────────────────────────┘
```

---

**End of Deployment Operations Guide**
