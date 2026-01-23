# Indufix LlamaIndex Toolkit - Deployment Guide

## 🎯 Deployment Objective

Deploy the indufix-llamaindex-toolkit to LangSmith Cloud with full automation.

---

## ✅ Pre-Deployment Checklist

### Required API Keys

**LangSmith Cloud:**
- LANGSMITH_API_KEY
- WORKSPACE_ID
- INTEGRATION_ID

**LLM Provider:**
- ANTHROPIC_API_KEY (recommended)

**LlamaCloud:**
- LLAMA_CLOUD_API_KEY

### GitHub Secrets Configuration

Add to: Settings → Secrets → Actions
1. LANGSMITH_API_KEY
2. WORKSPACE_ID
3. INTEGRATION_ID
4. LLAMA_CLOUD_API_KEY
5. ANTHROPIC_API_KEY

---

## 🚀 Quick Deploy

```bash
# Commit changes
git add .
git commit -m "Deploy indufix-llamaindex-toolkit"

# Push to deploy
git push origin main
```

Then approve deployment in GitHub Actions UI.

---

## 📊 Monitor Deployment

- GitHub Actions: https://github.com/chicuza/indufix-llamaindex-toolkit/actions
- LangSmith UI: https://smith.langchain.com

---

Ready to deploy! 🚀
