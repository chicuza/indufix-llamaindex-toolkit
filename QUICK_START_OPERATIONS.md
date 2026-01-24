# Quick Start: Deployment Operations

**Get your deployment running in 30 minutes**

---

## Prerequisites (5 minutes)

```bash
# 1. Install required packages
pip install requests pyyaml python-dotenv anthropic

# 2. Install GitHub CLI
# Windows: winget install GitHub.cli
# macOS: brew install gh
# Linux: See https://cli.github.com/

# 3. Authenticate GitHub CLI
gh auth login
```

---

## Configure GitHub Secrets (10 minutes)

### Quick Method (GitHub CLI)

```bash
# Set your credentials as environment variables first
# Then add them as GitHub Secrets

gh secret set LANGSMITH_API_KEY --body "$LANGSMITH_API_KEY"
gh secret set WORKSPACE_ID --body "$WORKSPACE_ID"
gh secret set INTEGRATION_ID --body "$INTEGRATION_ID"
gh secret set LLAMA_CLOUD_API_KEY --body "$LLAMA_CLOUD_API_KEY"
gh secret set ANTHROPIC_API_KEY --body "$ANTHROPIC_API_KEY"

# Optional but recommended
gh secret set OPENAI_API_KEY --body "$OPENAI_API_KEY"

# Verify all secrets are set
gh secret list
```

### Where to Get Credentials

| Secret | Get it from |
|--------|-------------|
| LANGSMITH_API_KEY | https://smith.langchain.com/settings |
| WORKSPACE_ID | LangSmith UI > Settings > Workspace (copy ID) |
| INTEGRATION_ID | LangSmith UI > Settings > Integrations > GitHub (copy ID) |
| LLAMA_CLOUD_API_KEY | https://cloud.llamaindex.ai/api-key |
| ANTHROPIC_API_KEY | https://console.anthropic.com/settings/keys |
| OPENAI_API_KEY | https://platform.openai.com/api-keys |

---

## Validate Setup (2 minutes)

```bash
# Create .env file with your credentials (for local testing)
cp .env.example .env
# Edit .env with your values

# Run validation
python trigger_deployment.py --validate-only --environment prod
```

**Expected output:**
```
✓ PASSED: Code Quality (Git Status)
✓ PASSED: Configuration Files
✓ PASSED: GitHub Secrets
✓ PASSED: LangSmith Connection
✓ PASSED: GitHub Integration

✓ ALL VALIDATIONS PASSED
Ready to deploy!
```

---

## Deploy to Development (First Test) (15 minutes)

```bash
# 1. Deploy to dev environment
python trigger_deployment.py --environment dev --wait

# 2. Validate deployment
python post_deploy_validate.py --environment dev

# 3. Check status
python deployment_status.py --environment dev
```

**What happens:**
1. Script validates all prerequisites ✅
2. Triggers GitHub Actions workflow ✅
3. Monitors deployment (15-30 min) ✅
4. Reports success or failure ✅

---

## Deploy to Production (When Ready)

```bash
# 1. Save baseline (for rollback if needed)
python deployment_status.py --save-baseline

# 2. Deploy to production
python trigger_deployment.py --environment prod --wait

# 3. Comprehensive validation
python post_deploy_validate.py --environment prod

# 4. Monitor status
python deployment_status.py --environment prod
```

---

## Daily Operations (5 minutes)

```bash
# Check deployment health
python deployment_status.py --environment prod

# If issues detected
python post_deploy_validate.py --environment prod --quick
```

---

## If Something Goes Wrong

### Quick Rollback (5 minutes)

```python
# Run this Python code
from deployment.langsmith_deploy import LangSmithDeployClient

client = LangSmithDeployClient.from_env()

# Replace with your deployment ID (get from deployment_status.py)
deployment_id = 'dep_abc123'

# Rollback to previous revision
client.rollback_to_previous(deployment_id)
print('Rollback initiated - wait 3 minutes')
```

### Get Help

1. Check: `DEPLOYMENT_TROUBLESHOOTING.md`
2. Search for your error message
3. Follow the solution steps

---

## Key Commands Reference

```bash
# Validate secrets
python trigger_deployment.py --validate-secrets

# Validate everything
python trigger_deployment.py --validate-only --environment prod

# Deploy (with monitoring)
python trigger_deployment.py --environment prod --wait

# Validate deployment
python post_deploy_validate.py --environment prod

# Check status
python deployment_status.py --environment prod

# Continuous monitoring
python deployment_status.py --watch --interval 30

# Check GitHub Secrets
gh secret list

# View GitHub Actions
gh run list --workflow=deploy_langsmith.yml
```

---

## Success Checklist

After deployment, verify:

- [ ] Health endpoint works: `curl https://your-deployment.langgraph.app/ok`
- [ ] MCP endpoint returns tools (run `post_deploy_validate.py`)
- [ ] Tool invocation succeeds (proves ANTHROPIC_API_KEY works)
- [ ] No errors in first 30 minutes
- [ ] Response times are acceptable (<5s)

---

## What to Monitor

### Daily
- Deployment state: Should be "DEPLOYED"
- Health status: Should be "healthy"
- Basic health check response

### Weekly
- Full validation suite
- Response time trends
- Error rate trends

### Monthly
- Dependency updates
- Secret rotation
- Documentation updates

---

## Critical Files

| File | Purpose |
|------|---------|
| `PRE_DEPLOYMENT_CHECKLIST.md` | Complete pre-deployment checklist |
| `trigger_deployment.py` | Deployment automation |
| `post_deploy_validate.py` | Post-deployment validation |
| `deployment_status.py` | Status monitoring |
| `DEPLOYMENT_TROUBLESHOOTING.md` | Issue resolution |
| `DEPLOYMENT_OPERATIONS_GUIDE.md` | Complete operations guide |

---

## Need More Details?

- **Complete setup**: See `DEPLOYMENT_OPERATIONS_GUIDE.md`
- **Troubleshooting**: See `DEPLOYMENT_TROUBLESHOOTING.md`
- **Pre-deployment**: See `PRE_DEPLOYMENT_CHECKLIST.md`
- **Overview**: See `OPERATIONS_DELIVERY_SUMMARY.md`

---

## Emergency Contacts

**If deployment fails:**
1. Don't panic - automatic rollback may trigger
2. Check `DEPLOYMENT_TROUBLESHOOTING.md`
3. Contact: [Your on-call engineer]

**Critical issues:**
- Slack: #oncall-alerts
- Email: oncall@company.com
- Phone: [Emergency number]

---

**Remember**: The scripts do most of the work. Your job is to:
1. Ensure secrets are configured
2. Run the validation script
3. Trigger deployment
4. Monitor and validate

**Everything else is automated!** ✅

---

**Last Updated**: 2026-01-23
**Status**: Production Ready
