# How to Find Your GitHub Integration ID

The `INTEGRATION_ID` is required for GitHub-based deployments to LangSmith Cloud.

## Method 1: Via LangSmith UI

1. Go to: https://smith.langchain.com/settings/integrations
2. Look for your **GitHub** integration
3. The integration ID will be displayed (usually a UUID format)
4. Copy it to use as the `INTEGRATION_ID` secret

## Method 2: Via Control Plane API

Run this Python script to list all your integrations:

```python
import os
import requests

LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")
WORKSPACE_ID = "950d802b-125a-45bc-88e4-3d7d0edee182"

headers = {
    "X-Api-Key": LANGSMITH_API_KEY,
    "X-Tenant-Id": WORKSPACE_ID,
    "Content-Type": "application/json"
}

response = requests.get(
    "https://api.host.langchain.com/v2/integrations",
    headers=headers
)

if response.status_code == 200:
    integrations = response.json()
    print("Your integrations:")
    for integration in integrations:
        print(f"  - ID: {integration['id']}")
        print(f"    Type: {integration.get('type', 'N/A')}")
        print(f"    Provider: {integration.get('provider', 'N/A')}")
        print()

    # Find GitHub integration
    github_integrations = [i for i in integrations if i.get('provider') == 'github']
    if github_integrations:
        print(f"GitHub Integration ID: {github_integrations[0]['id']}")
    else:
        print("No GitHub integration found. Please create one in LangSmith UI.")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

Save this as `find_integration_id.py` and run:
```bash
export LANGSMITH_API_KEY="your-api-key"
python find_integration_id.py
```

## Method 3: Create New Integration

If you don't have a GitHub integration yet:

1. Go to: https://smith.langchain.com/settings/integrations
2. Click **"Add Integration"**
3. Select **GitHub**
4. Follow the OAuth flow to connect your GitHub account
5. Once connected, the integration ID will be displayed
6. Copy it for use as the `INTEGRATION_ID` secret

## What is the Integration ID Used For?

The `INTEGRATION_ID` tells LangSmith Cloud:
- Which GitHub account/organization to use
- How to authenticate with GitHub to clone your repository
- Which GitHub repositories you have access to

Without it, LangSmith cannot clone your repository for deployment.

## Troubleshooting

**Issue**: "Integration not found" error during deployment
- **Solution**: Verify the integration ID is correct and belongs to your workspace

**Issue**: "Permission denied" when cloning repository
- **Solution**: Ensure the GitHub integration has access to your repository
  - Check repository visibility (public vs private)
  - Check integration permissions in GitHub settings

**Issue**: Integration ID looks wrong (not a UUID)
- **Solution**: Integration IDs should be UUIDs like: `abc123de-f456-7890-abcd-ef1234567890`
  - If yours doesn't match this format, create a new integration

---

**Need more help?** Check the LangSmith documentation:
- https://docs.langchain.com/langsmith/integrations
- https://docs.langchain.com/langsmith/deploy-to-cloud
