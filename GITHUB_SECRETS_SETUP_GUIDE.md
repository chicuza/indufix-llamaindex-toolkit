# GitHub Secrets Configuration Guide
## Enable CI/CD for Indufix LlamaIndex Toolkit

**Date**: 2026-01-23
**Purpose**: Configure GitHub repository secrets to enable automated deployments via GitHub Actions
**Time Required**: 10-15 minutes

---

## Why Configure GitHub Secrets?

GitHub Secrets enable your CI/CD pipeline to:
- ✅ Automatically deploy on code changes (push to main/dev)
- ✅ Securely pass credentials to deployment without exposing them
- ✅ Enable manual deployment triggers via GitHub Actions UI
- ✅ Maintain consistent deployment configuration across team

---

## Required Secrets

You need to configure **6 secrets** in your GitHub repository:

### 1. LANGSMITH_API_KEY ⭐ CRITICAL

**Purpose**: Authenticates deployment to LangSmith Cloud
**Get From**: https://smith.langchain.com/settings
**Current Value**: `lsv2_pt_YOUR-KEY-HERE`

**How to Get Your Key**:
1. Go to: https://smith.langchain.com/settings
2. Navigate to: API Keys
3. Click "Create API Key"
4. Copy the key (starts with `lsv2_pt_`)

---

### 2. WORKSPACE_ID ⭐ CRITICAL

**Purpose**: Identifies your LangSmith workspace
**Value**: `950d802b-125a-45bc-88e4-3d7d0edee182` ✅ CONFIRMED

**Note**: This is your workspace's unique identifier. Do NOT change this value.

---

### 3. INTEGRATION_ID ⭐ CRITICAL

**Purpose**: Links GitHub repository to LangSmith for automated deployments
**Value**: `2fd2db44-37bb-42ed-9f3a-9df2e769b058` ✅ CONFIRMED

**Note**: This integration was created during manual deployment. It connects your GitHub repo to LangSmith.

---

### 4. LLAMA_CLOUD_API_KEY ⭐ CRITICAL

**Purpose**: Enables tools to access Forjador Indufix knowledge base via LlamaCloud
**Get From**: https://cloud.llamaindex.ai/api-key
**Current Value**: `llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm`

**How to Get Your Key**:
1. Go to: https://cloud.llamaindex.ai
2. Navigate to: Settings → API Keys
3. Copy existing key or create new one
4. Key starts with `llx-`

---

### 5. ANTHROPIC_API_KEY 🔧 REQUIRED FOR TOOL ROUTING

**Purpose**: Powers the agent's internal LLM (Claude Sonnet 4.5) to route queries to specific tools
**Get From**: https://console.anthropic.com/settings/keys
**Format**: `sk-ant-api03-...`

**How to Get Your Key**:
1. Go to: https://console.anthropic.com/settings/keys
2. Click "Create Key"
3. Name it: "indufix-llamaindex-toolkit-deployment"
4. Copy the key (starts with `sk-ant-`)

**Important**: Without this key, tools won't be invoked and you'll get generic "Tools are available" responses.

---

### 6. OPENAI_API_KEY (Optional)

**Purpose**: Alternative LLM provider (if you prefer GPT-4 over Claude)
**Get From**: https://platform.openai.com/api-keys
**Format**: `sk-...`

**Note**: Only needed if you want to use OpenAI models instead of Anthropic.

---

## Step-by-Step Configuration Instructions

### Step 1: Navigate to Repository Secrets

1. **Open your browser**
2. **Go to**: https://github.com/chicuza/indufix-llamaindex-toolkit
3. **Click**: `Settings` (top tab)
4. **In left sidebar, click**: `Secrets and variables` → `Actions`

You should see a page titled "Actions secrets and variables"

---

### Step 2: Add Each Secret

For **EACH secret** listed above, follow these steps:

#### 2.1: Click "New repository secret"

Button is in the top-right of the secrets page.

#### 2.2: Fill in the Form

**Example for LANGSMITH_API_KEY**:

```
Name:  LANGSMITH_API_KEY
Value: lsv2_pt_YOUR-KEY-HERE
```

**Click "Add secret"**

#### 2.3: Repeat for All Secrets

Configure all 6 secrets (or 5 if skipping OPENAI_API_KEY):

1. ✅ `LANGSMITH_API_KEY`
2. ✅ `WORKSPACE_ID`
3. ✅ `INTEGRATION_ID`
4. ✅ `LLAMA_CLOUD_API_KEY`
5. ✅ `ANTHROPIC_API_KEY`
6. ⭐ `OPENAI_API_KEY` (optional)

---

### Step 3: Verify Secrets Are Added

After adding all secrets, you should see them listed on the Actions secrets page:

```
ANTHROPIC_API_KEY        Updated XX minutes ago
INTEGRATION_ID           Updated XX minutes ago
LANGSMITH_API_KEY        Updated XX minutes ago
LLAMA_CLOUD_API_KEY      Updated XX minutes ago
OPENAI_API_KEY          Updated XX minutes ago (if added)
WORKSPACE_ID            Updated XX minutes ago
```

**Note**: You can see the names but NOT the values (for security).

---

## Secrets Reference Table

Copy and paste these values when adding secrets:

| Secret Name | Value | Source |
|-------------|-------|--------|
| `LANGSMITH_API_KEY` | `lsv2_pt_YOUR-KEY-HERE` | From .env file |
| `WORKSPACE_ID` | `950d802b-125a-45bc-88e4-3d7d0edee182` | From deployment docs |
| `INTEGRATION_ID` | `2fd2db44-37bb-42ed-9f3a-9df2e769b058` | From deployment docs |
| `LLAMA_CLOUD_API_KEY` | `llx-EnmZ0pfr356dA2ac3bZJh3aTp0P0whxbnC3kilUssF072qnm` | From .env file |
| `ANTHROPIC_API_KEY` | `sk-ant-api03-...` | Get from Anthropic console |
| `OPENAI_API_KEY` | `sk-...` | Optional - get from OpenAI |

**⚠️ IMPORTANT**: The LANGSMITH_API_KEY and LLAMA_CLOUD_API_KEY values above are from your `.env` file. If you regenerated these keys, use the new values instead.

---

## After Adding Secrets - Next Steps

Once all secrets are configured:

### Option A: Trigger Manual Deployment

1. Go to: https://github.com/chicuza/indufix-llamaindex-toolkit/actions
2. Click: "Deploy to LangSmith Cloud" workflow
3. Click: "Run workflow" button (top right)
4. Select environment: `dev` or `prod`
5. Click: "Run workflow"
6. Wait 5-10 minutes for deployment to complete

### Option B: Trigger via Git Push

```bash
cd C:\Users\chicu\langchain\indufix-llamaindex-toolkit

# Create empty commit to trigger workflow
git commit --allow-empty -m "Configure GitHub secrets for CI/CD pipeline

- Added all required secrets to GitHub repository
- Enabled automated deployments
- Configured ANTHROPIC_API_KEY for tool routing

This commit triggers the deployment workflow to verify secrets are working."

# Push to trigger deployment
git push origin main
```

---

## Verify Deployment Workflow

### Watch Workflow Execution

1. Go to: https://github.com/chicuza/indufix-llamaindex-toolkit/actions
2. Click on the most recent workflow run
3. Watch the logs as it runs:
   - ✅ Validate secrets
   - ✅ Deploy to LangSmith
   - ✅ Verify deployment
   - ✅ Post-deployment tests

### Expected Result

If all secrets are correct, you should see:

```
✅ All secrets validated
✅ Deployment created/updated successfully
✅ Deployment verification passed
✅ Post-deployment health check passed
```

### If Workflow Fails

Check the logs for:
- **Invalid API key**: Double-check the key value
- **Permission denied**: Verify API key has correct permissions
- **Integration not found**: Verify INTEGRATION_ID is correct

---

## Security Best Practices

### DO ✅

- ✅ Use repository secrets (not hardcoded in code)
- ✅ Rotate API keys every 90 days
- ✅ Use different keys for dev vs prod if possible
- ✅ Monitor GitHub Actions logs for security issues

### DON'T ❌

- ❌ Commit secrets to git repository
- ❌ Share secrets in chat/email/Slack
- ❌ Use the same key across multiple projects
- ❌ Grant more permissions than needed

---

## Troubleshooting

### Problem 1: Workflow Says "Secret Not Found"

**Solution**:
1. Verify secret name matches EXACTLY (case-sensitive)
2. Check you added it to "Actions secrets" not "Environment secrets"
3. Wait 1 minute and re-run workflow (secrets need to propagate)

---

### Problem 2: "Invalid API Key" Error

**Solution**:
1. Re-copy the key from source (might have extra spaces)
2. Verify key hasn't been revoked/expired
3. Check key has correct permissions in LangSmith/Anthropic

---

### Problem 3: "Integration Not Found"

**Solution**:
1. Verify INTEGRATION_ID: `2fd2db44-37bb-42ed-9f3a-9df2e769b058`
2. Check GitHub integration still exists in LangSmith UI
3. Try manual deployment first to verify integration works

---

## Checklist

Before proceeding, verify:

- [ ] All 6 secrets added to GitHub repository (or 5 if skipping OpenAI)
- [ ] Secret names match exactly (case-sensitive)
- [ ] Secret values copied correctly (no extra spaces/newlines)
- [ ] ANTHROPIC_API_KEY obtained from Anthropic console
- [ ] Ready to trigger workflow

---

## What's Next?

After GitHub Secrets are configured:

1. **Trigger deployment** (manual or via push)
2. **Wait for workflow to complete** (5-10 minutes)
3. **Verify deployment succeeded** in GitHub Actions logs
4. **Move to Part 2**: Agent Builder Integration (GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md)

---

**Documentation Version**: 1.0
**Last Updated**: 2026-01-23
**Status**: Ready for implementation
