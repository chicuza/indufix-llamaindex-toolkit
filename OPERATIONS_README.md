# Deployment Operations Documentation

**Complete guide to deploying and operating Indufix LlamaIndex Toolkit on LangSmith Cloud**

---

## 🚀 Quick Start

**New to deployment?** Start here:
1. **[QUICK_START_OPERATIONS.md](QUICK_START_OPERATIONS.md)** - Get deployed in 30 minutes

**For complete details:**
2. **[OPERATIONS_DELIVERY_SUMMARY.md](OPERATIONS_DELIVERY_SUMMARY.md)** - Overview of all deliverables

---

## 📋 Documentation Index

### Getting Started

| Document | Purpose | Time Required |
|----------|---------|---------------|
| **[QUICK_START_OPERATIONS.md](QUICK_START_OPERATIONS.md)** | Get up and running fast | 30 minutes |
| **[OPERATIONS_DELIVERY_SUMMARY.md](OPERATIONS_DELIVERY_SUMMARY.md)** | Complete delivery overview | 15 minutes read |
| **[DEPLOYMENT_OPERATIONS_GUIDE.md](DEPLOYMENT_OPERATIONS_GUIDE.md)** | Complete operations manual | Reference guide |

### Pre-Deployment

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **[PRE_DEPLOYMENT_CHECKLIST.md](PRE_DEPLOYMENT_CHECKLIST.md)** | Comprehensive pre-deployment checklist | Before every deployment |
| **GitHub Secrets Setup** | Configure required secrets | First-time setup |

### Deployment

| Script | Purpose | When to Use |
|--------|---------|-------------|
| **[trigger_deployment.py](trigger_deployment.py)** | Automate deployment process | Every deployment |

**Usage:**
```bash
# Validate prerequisites
python trigger_deployment.py --validate-only --environment prod

# Deploy to production
python trigger_deployment.py --environment prod --wait
```

### Post-Deployment

| Script | Purpose | When to Use |
|--------|---------|-------------|
| **[post_deploy_validate.py](post_deploy_validate.py)** | Validate deployed application | After every deployment |

**Usage:**
```bash
# Full validation (includes tool testing)
python post_deploy_validate.py --environment prod

# Quick health check
python post_deploy_validate.py --environment prod --quick
```

### Monitoring

| Script | Purpose | When to Use |
|--------|---------|-------------|
| **[deployment_status.py](deployment_status.py)** | Real-time status dashboard | Daily operations, monitoring |

**Usage:**
```bash
# One-time status check
python deployment_status.py --environment prod

# Continuous monitoring
python deployment_status.py --environment prod --watch --interval 30
```

### Troubleshooting

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **[DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md)** | Complete troubleshooting guide | When issues occur |

**Covers:**
- Pre-deployment issues (missing secrets, invalid keys)
- Deployment failures (build timeout, integration issues)
- Post-deployment issues (health check fails, MCP errors)
- Runtime issues (ANTHROPIC_API_KEY, tool timeouts)
- Rollback procedures

---

## 🎯 Common Tasks

### First-Time Setup

```bash
# 1. Install prerequisites
pip install requests pyyaml python-dotenv anthropic
# Install GitHub CLI from https://cli.github.com/

# 2. Configure GitHub Secrets
gh secret set LANGSMITH_API_KEY --body "$LANGSMITH_API_KEY"
gh secret set WORKSPACE_ID --body "$WORKSPACE_ID"
gh secret set INTEGRATION_ID --body "$INTEGRATION_ID"
gh secret set LLAMA_CLOUD_API_KEY --body "$LLAMA_CLOUD_API_KEY"
gh secret set ANTHROPIC_API_KEY --body "$ANTHROPIC_API_KEY"

# 3. Validate setup
python trigger_deployment.py --validate-only --environment prod
```

**Detailed instructions:** [QUICK_START_OPERATIONS.md](QUICK_START_OPERATIONS.md)

---

### Deploy to Production

```bash
# 1. Pre-deployment validation
python trigger_deployment.py --validate-only --environment prod

# 2. Save baseline (for rollback)
python deployment_status.py --save-baseline

# 3. Deploy
python trigger_deployment.py --environment prod --wait

# 4. Validate
python post_deploy_validate.py --environment prod

# 5. Monitor
python deployment_status.py --environment prod
```

**Detailed instructions:** [PRE_DEPLOYMENT_CHECKLIST.md](PRE_DEPLOYMENT_CHECKLIST.md)

---

### Daily Health Check

```bash
# Quick status check (5 minutes)
python deployment_status.py --environment prod

# If issues detected
python post_deploy_validate.py --environment prod --quick
```

**Detailed procedures:** [DEPLOYMENT_OPERATIONS_GUIDE.md](DEPLOYMENT_OPERATIONS_GUIDE.md#daily-operations)

---

### Rollback Deployment

```python
# Quick rollback (5 minutes)
from deployment.langsmith_deploy import LangSmithDeployClient

client = LangSmithDeployClient.from_env()
client.rollback_to_previous('deployment-id')
```

**Detailed procedures:** [DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md#rollback-procedures)

---

## 🔑 Critical GitHub Secrets

All secrets MUST be configured before deployment:

| Secret | Required | Where to Get |
|--------|----------|--------------|
| `LANGSMITH_API_KEY` | ✅ Yes | https://smith.langchain.com/settings |
| `WORKSPACE_ID` | ✅ Yes | LangSmith UI > Settings > Workspace |
| `INTEGRATION_ID` | ✅ Yes | LangSmith UI > Settings > Integrations |
| `LLAMA_CLOUD_API_KEY` | ✅ Yes | https://cloud.llamaindex.ai/api-key |
| `ANTHROPIC_API_KEY` | ✅ Yes | https://console.anthropic.com/settings/keys |
| `OPENAI_API_KEY` | ⚪ Optional | https://platform.openai.com/api-keys |

**Setup instructions:** [PRE_DEPLOYMENT_CHECKLIST.md](PRE_DEPLOYMENT_CHECKLIST.md#critical-github-secrets-configuration)

---

## 🛠️ Operational Scripts

### trigger_deployment.py

**Purpose:** Validate and trigger deployments

**Key Features:**
- ✅ Git status validation
- ✅ Configuration validation
- ✅ GitHub Secrets verification
- ✅ API connection testing
- ✅ Workflow triggering
- ✅ Deployment monitoring

**Common commands:**
```bash
# Validate secrets only
python trigger_deployment.py --validate-secrets

# Full validation (no deployment)
python trigger_deployment.py --validate-only --environment prod

# Deploy with monitoring
python trigger_deployment.py --environment prod --wait
```

---

### post_deploy_validate.py

**Purpose:** Validate deployed application

**Key Features:**
- ✅ Health endpoint testing
- ✅ MCP endpoint verification
- ✅ Tools availability check
- ✅ **Actual tool invocation testing** (guarantees ANTHROPIC_API_KEY works)
- ✅ Response time measurement

**Common commands:**
```bash
# Full validation
python post_deploy_validate.py --environment prod

# Quick health check
python post_deploy_validate.py --quick

# Generate report
python post_deploy_validate.py --report validation_report.json
```

---

### deployment_status.py

**Purpose:** Monitor deployment health

**Key Features:**
- ✅ Real-time status display
- ✅ Health checks (live)
- ✅ Environment variables review
- ✅ Metrics summary
- ✅ Baseline saving (for rollback)

**Common commands:**
```bash
# Status check
python deployment_status.py --environment prod

# Continuous monitoring
python deployment_status.py --watch --interval 30

# Save baseline
python deployment_status.py --save-baseline

# Verify rollback
python deployment_status.py --verify-rollback
```

---

## 📊 Operational Workflows

### Standard Deployment

```
PRE-DEPLOYMENT (10 min)
  ↓
  • Review PRE_DEPLOYMENT_CHECKLIST.md
  • Run trigger_deployment.py --validate-only
  • Save baseline
  ↓
DEPLOYMENT (15-30 min)
  ↓
  • Run trigger_deployment.py --wait
  • Monitor GitHub Actions
  • Monitor LangSmith UI
  ↓
POST-DEPLOYMENT (10 min)
  ↓
  • Run post_deploy_validate.py
  • Verify all tests pass
  • Monitor for 2 hours
  ↓
ONGOING MONITORING
  ↓
  • Daily: deployment_status.py
  • Weekly: post_deploy_validate.py
  • Monthly: Full review
```

### Incident Response

```
INCIDENT DETECTED
  ↓
  • Run deployment_status.py
  • Assess severity (P0/P1/P2)
  ↓
IF P0 (CRITICAL)
  ↓
  • Execute immediate rollback
  • Notify team (#oncall-alerts)
  • Create incident ticket
  ↓
IF P1 (HIGH)
  ↓
  • Consult DEPLOYMENT_TROUBLESHOOTING.md
  • Apply fix or rollback
  • Monitor closely
  ↓
IF P2 (MEDIUM)
  ↓
  • Create ticket
  • Plan fix for next deployment
```

---

## 🎓 Learning Path

### Level 1: First Deployment (1 hour)

1. Read: [QUICK_START_OPERATIONS.md](QUICK_START_OPERATIONS.md)
2. Setup: Configure GitHub Secrets
3. Practice: Deploy to dev environment
4. Validate: Run post_deploy_validate.py

### Level 2: Production Operations (2 hours)

1. Read: [PRE_DEPLOYMENT_CHECKLIST.md](PRE_DEPLOYMENT_CHECKLIST.md)
2. Read: [DEPLOYMENT_OPERATIONS_GUIDE.md](DEPLOYMENT_OPERATIONS_GUIDE.md)
3. Practice: Full deployment workflow
4. Practice: Daily operations procedures

### Level 3: Advanced Operations (4 hours)

1. Read: [DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md)
2. Practice: Rollback procedures
3. Practice: Incident response
4. Study: Complete operations guide

---

## 📞 Support Resources

### Internal

- **Daily Operations**: [DEPLOYMENT_OPERATIONS_GUIDE.md](DEPLOYMENT_OPERATIONS_GUIDE.md)
- **Troubleshooting**: [DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md)
- **Quick Reference**: [QUICK_START_OPERATIONS.md](QUICK_START_OPERATIONS.md)

### External

- **LangSmith Docs**: https://docs.smith.langchain.com
- **Anthropic Docs**: https://docs.anthropic.com
- **LlamaCloud Docs**: https://docs.cloud.llamaindex.ai

### Emergency

- **On-Call**: See [DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md#emergency-contacts)
- **LangSmith Support**: support@langchain.com
- **Anthropic Support**: support@anthropic.com

---

## ✅ Quick Commands

```bash
# Pre-deployment
python trigger_deployment.py --validate-only --environment prod

# Deployment
python trigger_deployment.py --environment prod --wait

# Post-deployment
python post_deploy_validate.py --environment prod

# Daily monitoring
python deployment_status.py --environment prod

# Continuous monitoring
python deployment_status.py --watch --interval 30

# GitHub Secrets
gh secret list
gh secret set SECRET_NAME --body "$VALUE"

# GitHub Actions
gh workflow run deploy_langsmith.yml -f environment=prod
gh run list --workflow=deploy_langsmith.yml
```

---

## 🎯 Success Criteria

### Deployment Success

✅ All pre-deployment validations pass
✅ GitHub Actions workflow completes
✅ Deployment reaches "DEPLOYED" state
✅ Health endpoint returns 200 OK
✅ MCP endpoint returns tools
✅ **Tool invocation succeeds** (ANTHROPIC_API_KEY verified)
✅ No errors in first 30 minutes

### Operational Success

✅ Daily health checks pass
✅ Response times within SLA (<5s)
✅ Error rate <0.1%
✅ Rollback capability tested
✅ Team trained on procedures

---

## 📝 Document Status

| Document | Status | Last Updated |
|----------|--------|--------------|
| QUICK_START_OPERATIONS.md | ✅ Complete | 2026-01-23 |
| PRE_DEPLOYMENT_CHECKLIST.md | ✅ Complete | 2026-01-23 |
| trigger_deployment.py | ✅ Ready | 2026-01-23 |
| post_deploy_validate.py | ✅ Ready | 2026-01-23 |
| deployment_status.py | ✅ Ready | 2026-01-23 |
| DEPLOYMENT_TROUBLESHOOTING.md | ✅ Complete | 2026-01-23 |
| DEPLOYMENT_OPERATIONS_GUIDE.md | ✅ Complete | 2026-01-23 |
| OPERATIONS_DELIVERY_SUMMARY.md | ✅ Complete | 2026-01-23 |

**All documentation is production-ready and tested.**

---

## 🚀 Ready to Deploy?

**Start here:**
1. [QUICK_START_OPERATIONS.md](QUICK_START_OPERATIONS.md) - Get deployed in 30 minutes
2. [PRE_DEPLOYMENT_CHECKLIST.md](PRE_DEPLOYMENT_CHECKLIST.md) - Ensure you're ready
3. Run: `python trigger_deployment.py --environment prod --wait`

**Need help?**
- See [DEPLOYMENT_TROUBLESHOOTING.md](DEPLOYMENT_TROUBLESHOOTING.md)
- Check [DEPLOYMENT_OPERATIONS_GUIDE.md](DEPLOYMENT_OPERATIONS_GUIDE.md)

---

**Document Version**: 1.0
**Last Updated**: 2026-01-23
**Status**: Production Ready ✅
