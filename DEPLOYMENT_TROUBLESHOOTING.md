# Deployment Troubleshooting Guide

**Project**: Indufix LlamaIndex Toolkit
**Purpose**: Common deployment issues, diagnostic procedures, and solutions
**Owner**: DevOps/Operations Team
**Last Updated**: 2026-01-23

---

## Table of Contents

1. [Pre-Deployment Issues](#pre-deployment-issues)
2. [Deployment Failures](#deployment-failures)
3. [Post-Deployment Issues](#post-deployment-issues)
4. [Runtime Issues](#runtime-issues)
5. [Performance Issues](#performance-issues)
6. [Rollback Procedures](#rollback-procedures)
7. [Emergency Contacts](#emergency-contacts)

---

## Pre-Deployment Issues

### Issue: Missing GitHub Secrets

**Symptoms:**
- Deployment workflow fails with "Missing required environment variables"
- Validation script reports missing secrets

**Diagnosis:**
```bash
# Check GitHub Secrets via CLI
gh secret list

# Or run validation script
python trigger_deployment.py --validate-secrets
```

**Solutions:**

1. **Add missing secrets via GitHub UI:**
   - Go to: `https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions`
   - Click "New repository secret"
   - Add each missing secret:
     - `LANGSMITH_API_KEY` - from https://smith.langchain.com/settings
     - `WORKSPACE_ID` - from LangSmith UI
     - `INTEGRATION_ID` - from LangSmith Integrations page
     - `LLAMA_CLOUD_API_KEY` - from https://cloud.llamaindex.ai/api-key
     - `ANTHROPIC_API_KEY` - from https://console.anthropic.com/settings/keys

2. **Add missing secrets via GitHub CLI:**
   ```bash
   # Set secret from environment variable
   gh secret set LANGSMITH_API_KEY --body "$LANGSMITH_API_KEY"

   # Or set interactively
   gh secret set ANTHROPIC_API_KEY
   ```

3. **Verify secrets are set:**
   ```bash
   gh secret list
   # Should show all required secrets
   ```

**Prevention:**
- Use `PRE_DEPLOYMENT_CHECKLIST.md` before every deployment
- Keep `.env.example` updated with all required variables
- Document secret sources in `GITHUB_SECRETS_SETUP_GUIDE.md`

---

### Issue: Invalid API Keys

**Symptoms:**
- Deployment succeeds but tools fail to invoke
- API returns 401/403 errors
- "Invalid API key" messages in logs

**Diagnosis:**
```bash
# Test API keys locally
python -c "
import os
from anthropic import Anthropic

api_key = os.environ.get('ANTHROPIC_API_KEY')
client = Anthropic(api_key=api_key)

try:
    response = client.messages.create(
        model='claude-3-5-sonnet-20241022',
        max_tokens=10,
        messages=[{'role': 'user', 'content': 'test'}]
    )
    print('✓ API key is valid')
except Exception as e:
    print(f'✗ API key is invalid: {e}')
"
```

**Solutions:**

1. **Regenerate API key:**
   - Anthropic: https://console.anthropic.com/settings/keys
   - Click "Create Key" or regenerate existing key
   - Update GitHub Secret immediately

2. **Update GitHub Secret:**
   ```bash
   # Update secret with new key
   gh secret set ANTHROPIC_API_KEY --body "$NEW_API_KEY"
   ```

3. **Redeploy to pick up new secret:**
   ```bash
   python trigger_deployment.py --environment prod --wait
   ```

**Prevention:**
- Set calendar reminders for API key rotation (every 90 days)
- Use dedicated production API keys (not personal/test keys)
- Monitor API key usage in provider dashboards

---

### Issue: Wrong Git Branch

**Symptoms:**
- Validation fails with "Wrong branch" error
- Deploying dev code to production

**Diagnosis:**
```bash
# Check current branch
git branch --show-current

# Expected: 'main' for prod, 'dev' for dev
```

**Solutions:**

1. **Switch to correct branch:**
   ```bash
   # For production deployment
   git checkout main
   git pull origin main

   # For development deployment
   git checkout dev
   git pull origin dev
   ```

2. **Verify branch is clean:**
   ```bash
   git status
   # Should show: "nothing to commit, working tree clean"
   ```

**Prevention:**
- Always run `trigger_deployment.py` which validates branch
- Use branch protection rules in GitHub
- Require pull requests for main branch

---

## Deployment Failures

### Issue: Build Timeout

**Symptoms:**
- Deployment stuck in "BUILDING" state for >15 minutes
- GitHub Actions workflow times out
- Build logs show slow dependency installation

**Diagnosis:**
```bash
# Check build logs in LangSmith UI
# Or via API
python -c "
import os, requests

api_key = os.environ['LANGSMITH_API_KEY']
workspace_id = os.environ['WORKSPACE_ID']
deployment_id = 'your-deployment-id'

url = f'https://api.smith.langchain.com/api/v1/workspaces/{workspace_id}/deployments/{deployment_id}/revisions'
headers = {'x-api-key': api_key}

response = requests.get(url, headers=headers)
revisions = response.json()

# Check latest revision logs
print(revisions[0].get('build_logs', 'No logs available'))
"
```

**Solutions:**

1. **Check dependency versions:**
   ```bash
   # Review requirements.txt
   cat requirements.txt

   # Look for:
   # - Unpinned versions (no ==)
   # - Complex dependencies
   # - Heavy packages
   ```

2. **Optimize dependencies:**
   ```python
   # Pin all versions in requirements.txt
   pip freeze > requirements.txt

   # Or use lighter alternatives
   # Replace: tensorflow → tensorflow-cpu
   # Replace: torch → torch-cpu
   ```

3. **Increase timeout:**
   ```yaml
   # In .github/workflows/deploy_langsmith.yml
   - name: Deploy to LangSmith Cloud
     timeout-minutes: 45  # Increase from default 30
   ```

4. **Use Docker build cache:**
   - LangSmith should cache layers automatically
   - If not working, contact support

**Prevention:**
- Keep dependencies minimal
- Pin all versions
- Test builds in staging first
- Monitor build times trend

---

### Issue: GitHub Integration Not Connected

**Symptoms:**
- Deployment fails with "Integration not found"
- "Repository not accessible" errors
- Build cannot clone repository

**Diagnosis:**
```bash
# Check integration status
python -c "
import os, requests

api_key = os.environ['LANGSMITH_API_KEY']
workspace_id = os.environ['WORKSPACE_ID']
integration_id = os.environ['INTEGRATION_ID']

url = f'https://api.smith.langchain.com/api/v1/workspaces/{workspace_id}/integrations/{integration_id}'
headers = {'x-api-key': api_key}

response = requests.get(url, headers=headers)
integration = response.json()

print(f'Status: {integration.get(\"status\")}')
print(f'Provider: {integration.get(\"provider\")}')
"
```

**Solutions:**

1. **Reconnect GitHub integration:**
   - Go to: https://smith.langchain.com/settings/integrations
   - Click "GitHub"
   - Click "Connect" or "Reconnect"
   - Authorize LangSmith to access repository
   - Copy new integration ID

2. **Update GitHub Secret:**
   ```bash
   gh secret set INTEGRATION_ID --body "$NEW_INTEGRATION_ID"
   ```

3. **Verify repository access:**
   - Ensure repository is not private (or integration has access)
   - Check organization settings allow third-party apps
   - Verify LangSmith app installation in GitHub

4. **Redeploy:**
   ```bash
   python trigger_deployment.py --environment prod --wait
   ```

**Prevention:**
- Don't revoke GitHub app access
- Monitor integration health
- Document integration ID in secure location

---

### Issue: Invalid Configuration File

**Symptoms:**
- Deployment fails with "Invalid config" error
- YAML parsing errors
- Missing required fields

**Diagnosis:**
```bash
# Validate YAML syntax
python -c "
import yaml
from pathlib import Path

config_file = Path('deployment/deploy_config_prod.yaml')
with open(config_file) as f:
    config = yaml.safe_load(f)

print('Config is valid YAML')
print(f'Deployment name: {config[\"deployment\"][\"name\"]}')
"
```

**Solutions:**

1. **Fix YAML syntax errors:**
   ```bash
   # Common issues:
   # - Incorrect indentation (use 2 spaces, not tabs)
   # - Missing colons
   # - Unquoted special characters

   # Validate with online tool:
   # https://www.yamllint.com/
   ```

2. **Verify required fields:**
   ```yaml
   # deployment/deploy_config_prod.yaml must have:
   deployment:
     name: indufix-llamaindex-toolkit
     source: github
     repo_url: https://github.com/chicuza/indufix-llamaindex-toolkit
     branch: main
     config_path: langgraph.json
     type: prod

   secrets:
     LLAMA_CLOUD_API_KEY: ${LLAMA_CLOUD_API_KEY}
     ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
   ```

3. **Check langgraph.json:**
   ```bash
   # Validate langgraph.json exists and is valid
   python -c "
   import json
   with open('langgraph.json') as f:
       config = json.load(f)
   print('langgraph.json is valid')
   "
   ```

**Prevention:**
- Use version control for config files
- Validate before committing
- Use schema validation in CI/CD

---

## Post-Deployment Issues

### Issue: Health Check Fails (404)

**Symptoms:**
- `/ok` endpoint returns 404
- Deployment shows as "DEPLOYED" but not accessible

**Diagnosis:**
```bash
# Test health endpoint
curl -i https://your-deployment.langgraph.app/ok

# Expected: 200 OK
# Actual: 404 Not Found
```

**Solutions:**

1. **Wait for DNS propagation:**
   ```bash
   # DNS can take 2-5 minutes
   echo "Waiting for DNS..."
   sleep 120

   curl -i https://your-deployment.langgraph.app/ok
   ```

2. **Check deployment state:**
   ```bash
   python deployment_status.py --environment prod

   # Verify:
   # - State: DEPLOYED
   # - Health: healthy
   ```

3. **Check revision status:**
   - Go to LangSmith UI
   - Check revision is "DEPLOYED" (not "BUILDING" or "FAILED")
   - Review revision logs for errors

4. **If persists >10 minutes, rollback:**
   ```bash
   python -c "
   from deployment.langsmith_deploy import LangSmithDeployClient

   client = LangSmithDeployClient.from_env()
   client.rollback_to_previous('deployment-id')
   "
   ```

**Prevention:**
- Always wait 2-3 minutes after deployment
- Run automated post-deployment validation
- Monitor DNS propagation

---

### Issue: MCP Endpoint Returns 401 Unauthorized

**Symptoms:**
- `/mcp` endpoint returns 401 even with correct credentials
- Tool invocations fail with authentication errors

**Diagnosis:**
```bash
# Test MCP authentication
curl -X POST https://your-deployment.langgraph.app/mcp \
  -H "X-Api-Key: $LANGSMITH_API_KEY" \
  -H "X-Tenant-Id: $WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' \
  -i

# Check response headers and body
```

**Solutions:**

1. **Verify header names (case-sensitive):**
   ```bash
   # Correct headers:
   X-Api-Key: lsv2_pt_...
   X-Tenant-Id: workspace-uuid...

   # NOT:
   # X-API-Key (wrong case)
   # X-Tenant-ID (wrong case)
   ```

2. **Check API key is current:**
   ```bash
   # Test key directly
   curl -H "x-api-key: $LANGSMITH_API_KEY" \
     https://api.smith.langchain.com/api/v1/workspaces/$WORKSPACE_ID

   # Should return workspace info
   ```

3. **Verify workspace ID:**
   ```bash
   # Get workspace ID from LangSmith UI
   # Settings > Workspace > Copy ID

   # Update .env
   WORKSPACE_ID=correct-workspace-id
   ```

4. **Check deployment secrets:**
   - Secrets must be set in GitHub Secrets
   - Secrets are passed to deployed app
   - Verify with deployment logs

**Prevention:**
- Use exact header names from documentation
- Store credentials in secure password manager
- Test authentication in staging first

---

### Issue: Tools Not Available

**Symptoms:**
- MCP endpoint returns empty tools list
- Expected tools missing from response

**Diagnosis:**
```bash
# List available tools
python -c "
import os, requests, json

url = 'https://your-deployment.langgraph.app/mcp'
headers = {
    'X-Api-Key': os.environ['LANGSMITH_API_KEY'],
    'X-Tenant-Id': os.environ['WORKSPACE_ID'],
    'Content-Type': 'application/json'
}

payload = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'tools/list'
}

response = requests.post(url, json=payload, headers=headers)
tools = response.json().get('result', {}).get('tools', [])

print(f'Found {len(tools)} tools:')
for tool in tools:
    print(f'  - {tool[\"name\"]}')
"
```

**Solutions:**

1. **Check tool registration:**
   ```python
   # In your code, verify tools are registered
   # indufix_toolkit/__init__.py or agent.py

   # Should have:
   from .tools import search_tool, retrieval_tool

   toolkit = [search_tool, retrieval_tool]
   ```

2. **Verify toolkit.toml or langgraph.json:**
   ```bash
   # Check configuration includes tools
   cat langgraph.json

   # Should reference tool files
   ```

3. **Check deployment logs:**
   - Look for tool loading errors
   - Check import errors
   - Verify dependencies installed

4. **Redeploy with logging:**
   - Add debug logging to tool registration
   - Commit and push
   - Redeploy

**Prevention:**
- Test tool registration locally
- Add tool validation tests
- Monitor tool count in post-deployment validation

---

## Runtime Issues

### Issue: ANTHROPIC_API_KEY Not Working in Deployment

**Symptoms:**
- Tool invocations fail with "API key not found"
- Tools work locally but not in deployment
- Anthropic API errors in deployment logs

**Diagnosis:**
```bash
# Check if secret is set in GitHub
gh secret list | grep ANTHROPIC_API_KEY

# Check if secret is passed to deployment
# Review deploy_config_prod.yaml
cat deployment/deploy_config_prod.yaml | grep ANTHROPIC_API_KEY
```

**Solutions:**

1. **Verify GitHub Secret is set:**
   ```bash
   # Check secret exists
   gh secret list

   # If not set, add it
   gh secret set ANTHROPIC_API_KEY --body "$ANTHROPIC_API_KEY"
   ```

2. **Verify secret is in deployment config:**
   ```yaml
   # deployment/deploy_config_prod.yaml must include:
   secrets:
     ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
   ```

3. **Verify workflow passes secret:**
   ```yaml
   # .github/workflows/deploy_langsmith.yml must include:
   env:
     ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
   ```

4. **Redeploy to apply secret:**
   ```bash
   # Secrets are applied at deployment time
   # Must redeploy for changes to take effect
   python trigger_deployment.py --environment prod --wait
   ```

5. **Verify secret in deployment:**
   ```bash
   # After deployment, test tool invocation
   python post_deploy_validate.py --environment prod

   # Check "Test Tool Invocation" section
   ```

**Prevention:**
- Always include ANTHROPIC_API_KEY in deployment config
- Test tool invocations in post-deployment validation
- Monitor API usage to detect missing keys early

---

### Issue: Tool Invocation Timeout

**Symptoms:**
- Tool calls take >30 seconds
- Timeout errors in responses
- Slow response from deployed app

**Diagnosis:**
```bash
# Test tool response time
time python -c "
import os, requests

url = 'https://your-deployment.langgraph.app/mcp'
headers = {
    'X-Api-Key': os.environ['LANGSMITH_API_KEY'],
    'X-Tenant-Id': os.environ['WORKSPACE_ID'],
    'Content-Type': 'application/json'
}

payload = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'tools/call',
    'params': {
        'name': 'search_tool',
        'arguments': {'query': 'test'}
    }
}

response = requests.post(url, json=payload, headers=headers, timeout=60)
print(response.json())
"

# Should complete in <5 seconds
```

**Solutions:**

1. **Check LlamaCloud API latency:**
   - LlamaCloud might be slow
   - Check status: https://status.llamaindex.ai/

2. **Optimize tool code:**
   ```python
   # Add timeouts to external API calls
   import requests

   response = requests.get(url, timeout=10)  # Add timeout

   # Reduce data fetching
   # - Limit results
   # - Cache responses
   # - Use pagination
   ```

3. **Add caching:**
   ```python
   from functools import lru_cache

   @lru_cache(maxsize=128)
   def search_tool(query: str):
       # Cache results for repeated queries
       pass
   ```

4. **Increase deployment resources:**
   ```yaml
   # In deploy_config_prod.yaml
   resource_spec:
     cpu: 2      # More CPU
     memory_mb: 2048  # More memory
   ```

**Prevention:**
- Add timeouts to all external calls
- Implement caching for frequent queries
- Monitor response time metrics
- Set up alerts for slow responses

---

## Performance Issues

### Issue: High Memory Usage

**Symptoms:**
- Deployment restarts frequently
- Out of memory errors
- Slow response times

**Diagnosis:**
```bash
# Check deployment metrics in LangSmith UI
# Look for:
# - Memory usage trend
# - Restart frequency
# - Error patterns
```

**Solutions:**

1. **Increase memory allocation:**
   ```yaml
   # In deploy_config_prod.yaml
   resource_spec:
     memory_mb: 4096  # Increase from 2048
   ```

2. **Optimize memory usage:**
   ```python
   # Clear caches periodically
   import gc

   def cleanup():
       gc.collect()

   # Reduce data in memory
   # - Stream large responses
   # - Limit result sizes
   # - Use generators
   ```

3. **Profile memory usage:**
   ```python
   # Add memory profiling
   import tracemalloc

   tracemalloc.start()
   # Your code here
   snapshot = tracemalloc.take_snapshot()
   top_stats = snapshot.statistics('lineno')

   for stat in top_stats[:10]:
       print(stat)
   ```

**Prevention:**
- Monitor memory usage trends
- Load test before deployment
- Set up memory alerts

---

## Rollback Procedures

### Emergency Rollback

**When to rollback:**
- Health checks fail
- Error rate >5%
- Critical functionality broken
- Security vulnerability discovered

**Rollback steps:**

1. **Identify target revision:**
   ```bash
   # Save current state first
   python deployment_status.py --save-baseline

   # Get deployment info
   python deployment_status.py --environment prod

   # Note the deployment ID
   ```

2. **Execute rollback:**
   ```python
   # Via Python
   from deployment.langsmith_deploy import LangSmithDeployClient

   client = LangSmithDeployClient.from_env()
   deployment_id = 'your-deployment-id'

   # Rollback to previous revision
   client.rollback_to_previous(deployment_id)

   # Or rollback to specific revision
   # client.rollback_to_revision(deployment_id, 'revision-id')
   ```

3. **Verify rollback:**
   ```bash
   # Wait 2-3 minutes
   sleep 180

   # Check status
   python deployment_status.py --verify-rollback

   # Run validation
   python post_deploy_validate.py --environment prod --quick
   ```

4. **Notify team:**
   ```
   Subject: [ALERT] Production Rollback Executed

   Deployment rolled back due to: [reason]
   Previous revision: [revision-id]
   Current revision: [new-revision-id]
   Status: [HEALTHY/DEGRADED]

   Next steps:
   1. Investigate root cause
   2. Fix issue in dev
   3. Test thoroughly
   4. Schedule new deployment
   ```

**Post-rollback:**
- Create incident ticket
- Schedule post-mortem
- Document lessons learned
- Update this guide

---

## Emergency Contacts

### Critical Issues (P0 - System Down)

**Response Time:** <15 minutes

| Role | Contact | Phone | Availability |
|------|---------|-------|--------------|
| On-Call DevOps | [Name] | [Phone] | 24/7 |
| Platform Lead | [Name] | [Phone] | 24/7 |
| CTO | [Name] | [Phone] | On escalation |

**Escalation:**
1. Slack: #oncall-alerts
2. Phone: On-call rotation
3. Escalate to Platform Lead if no response in 15 min

### High Priority (P1 - Degraded Service)

**Response Time:** <1 hour

| Role | Contact | Slack | Email |
|------|---------|-------|-------|
| Technical Lead | [Name] | @tech-lead | tech-lead@company.com |
| DevOps Team | Team | #devops | devops@company.com |

### Normal Priority (P2 - Non-critical Issues)

**Response Time:** <4 hours (business hours)

- Slack: #engineering-support
- Email: engineering@company.com
- Ticket: https://tickets.company.com

---

## External Support

### LangSmith Support

- Documentation: https://docs.smith.langchain.com
- Support Portal: https://support.langchain.com
- Status Page: https://status.langchain.com
- Emergency: support@langchain.com

### Anthropic Support

- Documentation: https://docs.anthropic.com
- Support: support@anthropic.com
- Status: https://status.anthropic.com

### LlamaCloud Support

- Documentation: https://docs.cloud.llamaindex.ai
- Support: support@llamaindex.ai
- Status: https://status.llamaindex.ai

---

## Diagnostic Commands Quick Reference

```bash
# Pre-deployment validation
python trigger_deployment.py --validate-only --environment prod

# Deploy
python trigger_deployment.py --environment prod --wait

# Post-deployment validation
python post_deploy_validate.py --environment prod

# Check status
python deployment_status.py --environment prod

# Continuous monitoring
python deployment_status.py --watch --interval 30

# Save baseline for rollback
python deployment_status.py --save-baseline

# Check GitHub Secrets
gh secret list

# View workflow runs
gh run list --workflow=deploy_langsmith.yml

# View workflow logs
gh run view [run-id] --log

# Test health endpoint
curl https://your-deployment.langgraph.app/ok

# Test MCP endpoint
curl -X POST https://your-deployment.langgraph.app/mcp \
  -H "X-Api-Key: $LANGSMITH_API_KEY" \
  -H "X-Tenant-Id: $WORKSPACE_ID" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

---

## Common Log Patterns

### Success Patterns

```
✓ Health endpoint: OK
✓ MCP endpoint: OK (3 tools)
✓ Tool invocation successful
State: DEPLOYED
Health: healthy
```

### Warning Patterns

```
WARNING: Response time >2s
WARNING: Memory usage >80%
WARNING: API rate limit approaching
```

### Error Patterns

```
ERROR: Health check failed
ERROR: Missing required secret
ERROR: API returned 401
ERROR: Tool invocation timeout
✗ Deployment FAILED
```

---

## Document History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2026-01-23 | Initial version | DevOps Team |

---

**Next Review Date:** 2026-02-23

**Feedback:** If you encounter an issue not covered here, please document it and submit a PR to update this guide.
