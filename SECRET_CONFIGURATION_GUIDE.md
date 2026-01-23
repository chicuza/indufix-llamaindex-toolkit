# GitHub Secrets Configuration Guide

## 🎯 Mission: Configure ALL Required Secrets for GitHub Actions Deployment

This guide provides step-by-step instructions to configure the 6 required secrets in your GitHub repository to enable automated deployments to LangSmith Cloud.

---

## 📋 Prerequisites

- GitHub repository: `https://github.com/chicuza/indufix-llamaindex-toolkit`
- GitHub account with **admin access** to the repository
- All secret values ready (provided below)

---

## 🔐 Required Secrets Overview

| Secret Name | Status | Description |
|-------------|--------|-------------|
| `LANGSMITH_API_KEY` | ✅ Ready | LangSmith API authentication |
| `WORKSPACE_ID` | ✅ Ready | LangSmith workspace identifier |
| `INTEGRATION_ID` | ⭐ FOUND | GitHub integration for deployments |
| `LLAMA_CLOUD_API_KEY` | ⚠️ User has | LlamaIndex Cloud API key |
| `ANTHROPIC_API_KEY` | ⚠️ User has | Claude/Anthropic API key |
| `OPENAI_API_KEY` | ⚠️ Optional | OpenAI API key (optional) |

---

## 🚀 Step-by-Step Configuration

### Step 1: Navigate to Repository Settings

1. Open your browser and go to:
   ```
   https://github.com/chicuza/indufix-llamaindex-toolkit
   ```

2. Click on the **Settings** tab (top navigation bar)
   - **Note**: You must have admin access to see this tab
   - If you don't see it, you need to be added as a repository admin

### Step 2: Access Secrets Configuration

1. In the left sidebar, expand **Secrets and variables**
2. Click on **Actions**
3. You should now see the "Actions secrets and variables" page

**Screenshot Description**:
- Left sidebar with "Security" section expanded
- "Secrets and variables" → "Actions" menu item highlighted
- Main panel showing "Repository secrets" section

### Step 3: Add Each Secret

For each secret below, follow these steps:

1. Click the **"New repository secret"** button (green button, top right)
2. Enter the **Name** exactly as shown (case-sensitive)
3. Copy and paste the **Value** from the table below
4. Click **"Add secret"** button

---

## 📝 Exact Secret Values (Copy-Paste Ready)

### Secret 1: LANGSMITH_API_KEY

```
Name: LANGSMITH_API_KEY
```

```
Value: lsv2_sk_f0c969d81f3c44e28d9a06f877e50915_REDACTED_GET_FROM_USER
```

**Purpose**: Authenticates GitHub Actions with LangSmith API for deployment operations.

**⚠️ IMPORTANT**: The actual API key value should be obtained from your LangSmith dashboard at https://smith.langchain.com. The value shown above is redacted for security.

---

### Secret 2: WORKSPACE_ID

```
Name: WORKSPACE_ID
```

```
Value: 950d802b-125a-45bc-88e4-3d7d0edee182
```

**Purpose**: Identifies your LangSmith workspace where the deployment will be created.

---

### Secret 3: INTEGRATION_ID ⭐ (JUST FOUND)

```
Name: INTEGRATION_ID
```

```
Value: 2fd2db44-37bb-42ed-9f3a-9df2e769b058
```

**Purpose**: Links GitHub repository to LangSmith for automated deployments from GitHub Actions.

**Status**: ✅ This was just discovered and verified as READY for use!

---

### Secret 4: LLAMA_CLOUD_API_KEY

```
Name: LLAMA_CLOUD_API_KEY
```

```
Value: [YOUR_LLAMA_CLOUD_API_KEY]
```

**Purpose**: Required for LlamaIndex document processing and retrieval operations.

**Action Required**: Replace `[YOUR_LLAMA_CLOUD_API_KEY]` with your actual LlamaCloud API key.

**Where to find it**:
- Go to: https://cloud.llamaindex.ai/
- Navigate to API Keys section
- Copy your API key

---

### Secret 5: ANTHROPIC_API_KEY

```
Name: ANTHROPIC_API_KEY
```

```
Value: [YOUR_ANTHROPIC_API_KEY]
```

**Purpose**: Required for Claude AI model access in the deployed application.

**Action Required**: Replace `[YOUR_ANTHROPIC_API_KEY]` with your actual Anthropic API key.

**Where to find it**:
- Go to: https://console.anthropic.com/
- Navigate to API Keys section
- Copy your API key

---

### Secret 6: OPENAI_API_KEY (Optional)

```
Name: OPENAI_API_KEY
```

```
Value: [YOUR_OPENAI_API_KEY]
```

**Purpose**: Optional - for OpenAI model access if needed.

**Action Required**:
- If you have an OpenAI key and want to use OpenAI models, add it
- If not, you can skip this secret (the deployment will work without it)

**Where to find it**:
- Go to: https://platform.openai.com/api-keys
- Create or copy your API key

---

## ✅ Verification Checklist

After adding all secrets, verify your configuration:

### Visual Verification

Go to: `https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions`

You should see these 6 secrets listed (or 5 if you skipped OPENAI_API_KEY):

- ✅ `LANGSMITH_API_KEY` - Updated X minutes ago
- ✅ `WORKSPACE_ID` - Updated X minutes ago
- ✅ `INTEGRATION_ID` - Updated X minutes ago
- ✅ `LLAMA_CLOUD_API_KEY` - Updated X minutes ago
- ✅ `ANTHROPIC_API_KEY` - Updated X minutes ago
- ⚪ `OPENAI_API_KEY` - (Optional) Updated X minutes ago

### Secret Name Checklist

Double-check that each secret name is **EXACTLY** as shown (case-sensitive):

- [ ] `LANGSMITH_API_KEY` (not langsmith_api_key or LangSmith_API_Key)
- [ ] `WORKSPACE_ID` (not workspace_id or WorkspaceId)
- [ ] `INTEGRATION_ID` (not integration_id or IntegrationId)
- [ ] `LLAMA_CLOUD_API_KEY` (not llama_cloud_api_key)
- [ ] `ANTHROPIC_API_KEY` (not anthropic_api_key)
- [ ] `OPENAI_API_KEY` (not openai_api_key)

### Value Checklist

Verify each secret value:

- [ ] No extra spaces before or after the value
- [ ] No quotes around the value (paste the raw key)
- [ ] Complete value copied (check start and end)
- [ ] No line breaks in the middle of the value

---

## 🔧 Troubleshooting

### Problem: "New repository secret" button is grayed out

**Solution**: You need admin access to the repository. Ask the repository owner to:
1. Go to Settings → Collaborators
2. Add you with "Admin" role

### Problem: Secrets not showing up in Actions

**Solution**:
1. Wait 1-2 minutes after adding secrets
2. Refresh the page
3. Check that you're in the correct repository

### Problem: Workflow still failing with "secret not found"

**Solution**:
1. Verify secret name spelling (case-sensitive)
2. Check that the secret is in **Repository secrets**, not Environment secrets
3. Try deleting and re-adding the secret

### Problem: API key invalid errors

**Solution**:
1. Verify the API key is still active in the provider's dashboard
2. Check for any restrictions on the API key (IP, domains, etc.)
3. Generate a new API key if needed

---

## 🎓 Understanding Secret Scopes

**Repository Secrets** (What we're using):
- Available to all workflows in the repository
- Accessible in all branches
- Used for: LANGSMITH_API_KEY, WORKSPACE_ID, INTEGRATION_ID, and API keys

**Environment Secrets** (Not used here):
- Scoped to specific environments (production, staging, etc.)
- Can have approval requirements
- Used for: More advanced deployment scenarios

---

## 🔒 Security Best Practices

1. **Never commit secrets to git**
   - Secrets should ONLY be in GitHub Secrets
   - Never in `.env` files, config files, or code

2. **Rotate secrets regularly**
   - Change API keys every 90 days
   - Update in GitHub Secrets after rotation

3. **Use least-privilege API keys**
   - Create keys with minimal required permissions
   - Use separate keys for dev/prod if possible

4. **Monitor secret usage**
   - Check GitHub Actions logs for unauthorized access
   - Enable notifications for workflow failures

---

## 📊 Configuration Status

### Current Status

| Component | Status | Notes |
|-----------|--------|-------|
| Repository access | ✅ Ready | Public repository available |
| GitHub Actions enabled | ✅ Ready | Workflow file exists |
| LangSmith deployment | ✅ Ready | Deployment exists and is READY |
| GitHub integration | ✅ Ready | INTEGRATION_ID found and verified |
| Required secrets (3/6) | ✅ Ready | LANGSMITH_API_KEY, WORKSPACE_ID, INTEGRATION_ID |
| API keys (2-3/3) | ⚠️ Pending | User needs to add LLAMA_CLOUD and ANTHROPIC keys |

### Next Steps

1. ✅ Add the 3 LangSmith secrets (provided above)
2. ⚠️ Add your LLAMA_CLOUD_API_KEY
3. ⚠️ Add your ANTHROPIC_API_KEY
4. ⚪ (Optional) Add your OPENAI_API_KEY
5. ✅ Proceed to **WORKFLOW_TRIGGER_GUIDE.md** to test the deployment

---

## 🆘 Need Help?

### Quick Links

- GitHub Secrets Documentation: https://docs.github.com/en/actions/security-guides/encrypted-secrets
- LangSmith Dashboard: https://smith.langchain.com
- LlamaIndex Cloud: https://cloud.llamaindex.ai/
- Anthropic Console: https://console.anthropic.com/

### Common Issues

1. **Workflow not starting**: Check that secrets are in Repository level, not Environment level
2. **Authentication errors**: Verify LANGSMITH_API_KEY and WORKSPACE_ID are correct
3. **Integration errors**: Ensure INTEGRATION_ID matches the one shown above
4. **API errors**: Verify your API keys are active and have correct permissions

---

## ✨ Ready to Deploy?

Once all secrets are configured:

1. Go to the **Actions** tab in your GitHub repository
2. You should see the "Deploy to LangSmith Cloud" workflow
3. Follow the **WORKFLOW_TRIGGER_GUIDE.md** for next steps

**Congratulations!** You're ready to automate your deployments! 🚀
