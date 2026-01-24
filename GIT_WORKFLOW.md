# Git Workflow Guide

This document explains the Git workflow for the Indufix LlamaIndex Toolkit deployment pipeline.

## Table of Contents
- [Branch Strategy](#branch-strategy)
- [Triggering Deployments](#triggering-deployments)
- [Commit Message Conventions](#commit-message-conventions)
- [Rollback Procedures](#rollback-procedures)
- [Release Management](#release-management)

## Branch Strategy

### Main Branches

**`main` branch (Production)**
- Protected branch with production deployments
- Auto-deploys to LangSmith production environment on push
- Requires all tests to pass before deployment
- Should only receive:
  - Merges from `dev` branch
  - Hotfix commits (emergencies only)
  - Documentation updates

**`dev` branch (Development)**
- Development and staging environment
- Auto-deploys to LangSmith development environment on push
- Used for testing features before production release
- Receives feature branch merges

### Feature Branches

Format: `feature/description-of-feature`

Examples:
- `feature/add-sku-validation`
- `feature/improve-error-handling`
- `feature/update-documentation`

Workflow:
```bash
# Create feature branch from dev
git checkout dev
git pull origin dev
git checkout -b feature/my-new-feature

# Make changes, commit, push
git add .
git commit -m "feat: add new feature"
git push origin feature/my-new-feature

# Create pull request to dev
# After review and approval, merge to dev
```

### Hotfix Branches

Format: `hotfix/description-of-fix`

Examples:
- `hotfix/fix-api-timeout`
- `hotfix/security-patch`

Workflow:
```bash
# Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-fix

# Make fix, commit, push
git add .
git commit -m "fix: resolve critical issue"
git push origin hotfix/critical-fix

# Create pull request to main
# After deployment, merge back to dev
git checkout dev
git merge hotfix/critical-fix
```

## Triggering Deployments

### Automatic Triggers

Deployments are automatically triggered by:

**1. Push to `main` branch → Production deployment**
```bash
git checkout main
git pull origin main
git merge dev  # or specific commit
git push origin main  # Triggers production deployment
```

**2. Push to `dev` branch → Development deployment**
```bash
git checkout dev
git add .
git commit -m "feat: add feature"
git push origin dev  # Triggers dev deployment
```

### Manual Triggers

You can manually trigger deployments via GitHub Actions UI:

1. Go to: https://github.com/chicuza/indufix-llamaindex-toolkit/actions
2. Click "Deploy to LangSmith Cloud"
3. Click "Run workflow"
4. Select environment (dev/prod)
5. Click "Run workflow"

### What Happens During Deployment

The GitHub Actions workflow (`deploy_langsmith.yml`) automatically:

1. **Validates secrets** - Ensures all required secrets are configured
2. **Runs tests** - Validates code and configuration files
3. **Deploys to LangSmith** - Creates/updates deployment
4. **Waits for completion** - Polls until deployment is ready
5. **Validates deployment** - Checks health and status
6. **Rolls back on failure** - Automatically reverts if deployment fails

Required secrets (configured in GitHub repository settings):
- `LANGSMITH_API_KEY`
- `WORKSPACE_ID`
- `INTEGRATION_ID`
- `LLAMA_CLOUD_API_KEY`
- `ANTHROPIC_API_KEY`
- `OPENAI_API_KEY` (optional)

## Commit Message Conventions

We follow **Conventional Commits** format for clear, semantic commit history.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring (no feature/fix)
- **test**: Adding or updating tests
- **chore**: Maintenance tasks (dependencies, config)
- **perf**: Performance improvements
- **ci**: CI/CD pipeline changes
- **build**: Build system changes

### Examples

```bash
# Feature addition
git commit -m "feat: add SKU matching functionality with LlamaIndex integration"

# Bug fix
git commit -m "fix: resolve API timeout in rule retrieval endpoint"

# Documentation
git commit -m "docs: add deployment workflow guide and setup instructions"

# Breaking change
git commit -m "feat!: update API endpoint structure

BREAKING CHANGE: API endpoints now use /v2/ prefix"

# Multi-line with body
git commit -m "feat: add deployment automation scripts

- Add PowerShell scripts for GitHub secrets setup
- Add deployment trigger automation
- Add secrets validation checks

Closes #123"
```

### Claude Code Co-authoring

When commits are created by Claude Code assistant, include:

```bash
git commit -m "feat: add deployment documentation

Generated with Claude Code assistant

Co-Authored-By: Claude <noreply@anthropic.com>"
```

## Rollback Procedures

### Automatic Rollback

The GitHub Actions workflow automatically attempts rollback on deployment failure.

### Manual Rollback via Git

**Method 1: Revert commit**
```bash
# Find the problematic commit
git log --oneline -10

# Revert the commit (creates new commit that undoes changes)
git revert <commit-sha>
git push origin main  # Triggers new deployment with reverted state
```

**Method 2: Reset to previous commit (destructive)**
```bash
# WARNING: Only use in emergencies, requires force push

# Find last good commit
git log --oneline -10

# Reset to that commit
git reset --hard <commit-sha>

# Force push (will trigger deployment)
git push --force origin main
```

**Method 3: Revert merge**
```bash
# If you merged a bad feature branch
git revert -m 1 <merge-commit-sha>
git push origin main
```

### Manual Rollback via LangSmith UI

1. Go to LangSmith deployment dashboard
2. Find your deployment: `indufix-llamaindex-toolkit`
3. View revision history
4. Click "Rollback" on previous working revision
5. Confirm rollback

### Rollback Validation

After rollback:
```bash
# Verify deployment status
python check_deployment.py

# Test MCP endpoints
python run_mcp_tests.py

# Check health
curl https://smith.langchain.com/api/v1/deployments/<deployment-id>/health
```

## Release Management

### Semantic Versioning

We use semantic versioning: `vMAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (v1.0.0 → v2.0.0)
- **MINOR**: New features, backward compatible (v1.0.0 → v1.1.0)
- **PATCH**: Bug fixes, backward compatible (v1.0.0 → v1.0.1)

### Creating a Release

**1. Tag the release**
```bash
# Ensure you're on main branch
git checkout main
git pull origin main

# Create annotated tag
git tag -a v1.0.0 -m "Release v1.0.0: Initial MCP Integration

Features:
- SKU matching with LlamaIndex integration
- Automated deployment pipeline
- GitHub Actions CI/CD
- Comprehensive documentation

Production-ready deployment with all secrets configured."

# Push tag to GitHub
git push origin v1.0.0
```

**2. Create GitHub Release**
```bash
# Using GitHub CLI
gh release create v1.0.0 \
  --title "v1.0.0: MCP Integration Complete" \
  --notes "Production release with SKU matching functionality" \
  --target main
```

Or manually via GitHub UI:
1. Go to: https://github.com/chicuza/indufix-llamaindex-toolkit/releases
2. Click "Create a new release"
3. Select tag `v1.0.0`
4. Add release notes
5. Publish release

### Pre-release Tags

For development milestones:
```bash
git tag -a v1.0.0-beta.1 -m "Beta release for testing"
git push origin v1.0.0-beta.1
```

### Listing Tags

```bash
# List all tags
git tag -l

# Show tag details
git show v1.0.0

# List tags with dates
git log --tags --simplify-by-decoration --pretty="format:%ai %d"
```

### Deleting Tags

```bash
# Delete local tag
git tag -d v1.0.0

# Delete remote tag
git push origin --delete v1.0.0
```

## Best Practices

### Before Committing

1. **Review changes**: `git diff`
2. **Stage selectively**: `git add -p` (interactive staging)
3. **Run tests locally**: `pytest tests/`
4. **Validate configs**: Check YAML files
5. **Check secrets**: Ensure no sensitive data in commits

### Before Pushing

1. **Pull latest**: `git pull --rebase origin main`
2. **Review commit history**: `git log --oneline -5`
3. **Ensure tests pass**: Run local test suite
4. **Check branch**: Verify you're on correct branch

### Security Checks

Never commit:
- `.env` files (use `.env.example` instead)
- API keys or tokens
- Passwords or credentials
- `*_secrets.*` files
- `*.key` files

The `.gitignore` is configured to prevent these, but always double-check:
```bash
# Check what will be committed
git status
git diff --cached

# Remove accidentally staged secrets
git reset HEAD .env
```

## Troubleshooting

### Deployment Failed

```bash
# Check workflow status
gh run list --workflow=deploy_langsmith.yml

# View logs
gh run view <run-id> --log

# Check deployment status
python check_deployment.py
```

### Merge Conflicts

```bash
# Update your branch
git checkout feature/my-feature
git fetch origin
git merge origin/main

# Resolve conflicts in editor
# Then mark as resolved
git add <resolved-files>
git commit -m "chore: resolve merge conflicts with main"
```

### Stuck Deployment

```bash
# Cancel workflow run
gh run cancel <run-id>

# Or via GitHub UI:
# Actions → Select run → Cancel workflow
```

## Quick Reference

```bash
# Clone repository
git clone https://github.com/chicuza/indufix-llamaindex-toolkit.git

# Create feature branch
git checkout -b feature/my-feature

# Stage changes
git add .

# Commit with conventional format
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/my-feature

# Trigger production deployment
git checkout main
git merge dev
git push origin main

# Create release tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Rollback to previous commit
git revert HEAD
git push origin main
```

## Additional Resources

- [GitHub Repository](https://github.com/chicuza/indufix-llamaindex-toolkit)
- [GitHub Actions Workflows](https://github.com/chicuza/indufix-llamaindex-toolkit/actions)
- [LangSmith Dashboard](https://smith.langchain.com)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

## Support

For issues or questions:
1. Check [COMPLETE_SETUP_EXECUTION_PLAN.md](./COMPLETE_SETUP_EXECUTION_PLAN.md)
2. Review [GITHUB_SECRETS_SETUP_GUIDE.md](./GITHUB_SECRETS_SETUP_GUIDE.md)
3. Check GitHub Actions workflow logs
4. Contact repository maintainers
