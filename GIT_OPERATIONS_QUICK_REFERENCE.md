# Git Operations Quick Reference

**Status**: ✅ READY FOR EXECUTION
**Repository**: chicuza/indufix-llamaindex-toolkit
**Branch**: main

---

## Quick Start

### Option 1: Automated Execution (Recommended)

**PowerShell (Windows)**:
```powershell
# Dry run first (preview changes)
.\execute_git_operations.ps1 -DryRun

# Execute for real
.\execute_git_operations.ps1
```

**Bash (Linux/Mac/Git Bash)**:
```bash
# Make executable
chmod +x execute_git_operations.sh

# Dry run first (preview changes)
./execute_git_operations.sh --dry-run

# Execute for real
./execute_git_operations.sh
```

### Option 2: Manual Execution

```bash
cd /c/Users/chicu/langchain/indufix-llamaindex-toolkit

# 1. Stage all files
git add .gitignore GITHUB_SECRETS_SETUP_GUIDE.md DEPLOYMENT_SECRETS_CONFIGURED.md \
  COMPLETE_SETUP_EXECUTION_PLAN.md GIT_WORKFLOW.md MCP_DEPLOYMENT_TEST_REPORT.md \
  TEST_SESSION_SUMMARY.md DEPLOYMENT_SETUP.md check_secrets_status.ps1 \
  setup_github_secrets.ps1 trigger_deployment.ps1 run_mcp_tests.py \
  mcp_test_results_analysis.json GIT_OPERATIONS_PLAN.md execute_git_operations.sh \
  execute_git_operations.ps1

# 2. Create documentation commit (see GIT_OPERATIONS_PLAN.md for full message)
git commit -m "docs: add comprehensive deployment documentation and automation scripts"

# 3. Create deployment trigger commit
git commit --allow-empty -m "ci: trigger deployment with configured GitHub Secrets"

# 4. Create release tag
git tag -a v1.0-mcp-integration -m "MCP Integration Complete - SKU Matching Enabled"

# 5. Push everything
git push origin main --tags
```

---

## What Will Happen

1. **Two commits** will be created:
   - Commit 1: Documentation and automation scripts
   - Commit 2: Deployment trigger (empty commit)

2. **One tag** will be created:
   - Tag: `v1.0-mcp-integration`

3. **GitHub Actions workflow** will trigger automatically:
   - Validates GitHub Secrets
   - Runs tests
   - Deploys to LangSmith Cloud
   - Validates deployment health

4. **Deployment URL** will be available in Actions logs

---

## Pre-Execution Checklist

Before running, ensure:

- [ ] You're on the `main` branch
- [ ] GitHub Secrets are configured (run `.\check_secrets_status.ps1`)
- [ ] No sensitive files (`.env`, `*.key`) are being committed
- [ ] You've reviewed `GIT_OPERATIONS_PLAN.md`

---

## Files Being Committed

### Documentation (9 files)
1. `GITHUB_SECRETS_SETUP_GUIDE.md` - Secrets configuration guide
2. `DEPLOYMENT_SECRETS_CONFIGURED.md` - Secrets validation
3. `COMPLETE_SETUP_EXECUTION_PLAN.md` - Execution plan
4. `GIT_WORKFLOW.md` - Git workflow guide
5. `MCP_DEPLOYMENT_TEST_REPORT.md` - Testing report
6. `TEST_SESSION_SUMMARY.md` - Test summary
7. `DEPLOYMENT_SETUP.md` - Setup guide
8. `GIT_OPERATIONS_PLAN.md` - This operations plan
9. `GIT_OPERATIONS_QUICK_REFERENCE.md` - This file

### Scripts (5 files)
1. `check_secrets_status.ps1` - Verify secrets
2. `setup_github_secrets.ps1` - Setup secrets
3. `trigger_deployment.ps1` - Trigger deployment
4. `execute_git_operations.sh` - Automated execution (Bash)
5. `execute_git_operations.ps1` - Automated execution (PowerShell)

### Testing (2 files)
1. `run_mcp_tests.py` - MCP endpoint testing
2. `mcp_test_results_analysis.json` - Test results

### Configuration (1 file)
1. `.gitignore` - Enhanced security patterns

**Total**: 17 files

---

## After Execution

### Monitor Deployment

```bash
# Visit GitHub Actions
# https://github.com/chicuza/indufix-llamaindex-toolkit/actions

# Or use GitHub CLI
gh run list --workflow=deploy_langsmith.yml --limit 1
gh run watch
```

### Verify Deployment

```bash
# Check deployment status
python check_deployment.py

# Test MCP endpoints
python run_mcp_tests.py

# View deployment in LangSmith
# https://smith.langchain.com
```

### View Release

```bash
# Via GitHub CLI
gh release view v1.0-mcp-integration

# Or visit:
# https://github.com/chicuza/indufix-llamaindex-toolkit/releases
```

---

## Rollback Procedures

### If Deployment Fails

**Option 1: Automatic Rollback**
- GitHub Actions workflow automatically attempts rollback

**Option 2: Revert Commits**
```bash
git revert HEAD~1..HEAD  # Revert last 2 commits
git push origin main
```

**Option 3: LangSmith Manual Rollback**
1. Visit: https://smith.langchain.com
2. Navigate to deployments
3. Select `indufix-llamaindex-toolkit`
4. Click "Rollback" to previous revision

**Option 4: Delete Tag**
```bash
git tag -d v1.0-mcp-integration
git push origin --delete v1.0-mcp-integration
```

---

## Troubleshooting

### Secrets Not Configured

```bash
# Check status
.\check_secrets_status.ps1

# Configure secrets
.\setup_github_secrets.ps1
```

### Deployment Fails

```bash
# View workflow logs
gh run view --log

# Check deployment status
python check_deployment.py

# Trigger manual deployment
.\trigger_deployment.ps1
```

### Sensitive Files Detected

```bash
# Remove from staging
git reset HEAD .env

# Ensure .gitignore is correct
cat .gitignore | grep -E "(\.env|secrets|\.key)"
```

---

## Important Notes

1. **Secrets Required**: Ensure all GitHub Secrets are configured before pushing
   - `LANGSMITH_API_KEY`
   - `WORKSPACE_ID`
   - `INTEGRATION_ID`
   - `LLAMA_CLOUD_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `OPENAI_API_KEY` (optional)

2. **Deployment Triggers**: Push to `main` triggers production deployment

3. **Testing**: GitHub Actions runs tests before deploying

4. **Rollback**: Automatic rollback on failure

5. **Monitoring**: Watch deployment at GitHub Actions

---

## Quick Commands

```bash
# Preview changes (dry run)
.\execute_git_operations.ps1 -DryRun

# Execute all operations
.\execute_git_operations.ps1

# Check secrets
.\check_secrets_status.ps1

# Monitor deployment
gh run watch

# Verify deployment
python check_deployment.py

# Test endpoints
python run_mcp_tests.py
```

---

## Documentation

- **GIT_OPERATIONS_PLAN.md** - Detailed operations plan with full commit messages
- **GIT_WORKFLOW.md** - Complete Git workflow, branching, and rollback guide
- **COMPLETE_SETUP_EXECUTION_PLAN.md** - Full deployment setup plan
- **GITHUB_SECRETS_SETUP_GUIDE.md** - GitHub Secrets configuration guide

---

## Support

For issues:
1. Check workflow logs: https://github.com/chicuza/indufix-llamaindex-toolkit/actions
2. Review `GIT_OPERATIONS_PLAN.md`
3. Check `GIT_WORKFLOW.md` for rollback procedures
4. Contact repository maintainers

---

**Ready to execute?** Run `.\execute_git_operations.ps1` or `./execute_git_operations.sh`
