# Quick Start - Indufix CLI Tools

Get started with Indufix CLI tools in 5 minutes.

## Prerequisites

- Python 3.11+
- Git access to chicuza/indufix-llamaindex-toolkit
- LangSmith account with API key
- LlamaCloud account with API key
- Anthropic API key (critical!)

## 5-Minute Setup

### Step 1: Install Dependencies (1 minute)

```bash
cd indufix-llamaindex-toolkit
pip install -r requirements-cli.txt
```

### Step 2: Set Environment Variables (1 minute)

**Windows (PowerShell)**:
```powershell
$env:LANGSMITH_API_KEY="lsv2_pt_your-api-key-here"
$env:LLAMA_CLOUD_API_KEY="llx-your-api-key-here"
$env:ANTHROPIC_API_KEY="sk-ant-your-api-key-here"
```

**Windows (CMD)**:
```cmd
set LANGSMITH_API_KEY=lsv2_pt_your-api-key-here
set LLAMA_CLOUD_API_KEY=llx-your-api-key-here
set ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

**Linux/Mac**:
```bash
export LANGSMITH_API_KEY="lsv2_pt_your-api-key-here"
export LLAMA_CLOUD_API_KEY="llx-your-api-key-here"
export ANTHROPIC_API_KEY="sk-ant-your-api-key-here"
```

**Or create `.env` file**:
```bash
echo "LANGSMITH_API_KEY=lsv2_pt_your-api-key-here" > .env
echo "LLAMA_CLOUD_API_KEY=llx-your-api-key-here" >> .env
echo "ANTHROPIC_API_KEY=sk-ant-your-api-key-here" >> .env
```

### Step 3: Verify Installation (30 seconds)

```bash
python indufix_cli.py status
```

Expected output:
```
✓ LANGSMITH_API_KEY: Set
✓ LLAMA_CLOUD_API_KEY: Set
✓ ANTHROPIC_API_KEY: Set
✓ Deployment: Healthy
```

### Step 4: Run Setup Wizard (2 minutes)

```bash
python setup_cli.py
```

This will:
1. Show you the exact GitHub Secrets to configure
2. Open your browser to GitHub settings
3. Guide you through adding each secret
4. Optionally trigger deployment

### Step 5: Validate Everything (30 seconds)

```bash
python validate_cli.py
```

Expected: All checks pass ✓

## Common Commands

### Check Status
```bash
python indufix_cli.py status
```

### Run All Tests
```bash
python test_cli.py --all
```

### Validate Deployment
```bash
python validate_cli.py
```

### Manage Deployment
```bash
python deployment_cli.py status
```

## What to Do Next

### If All Checks Pass ✓

1. **Run Integration Tests**
   ```bash
   python test_cli.py --all --report
   ```

2. **Configure Agent Builder**
   - Follow: `GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md`
   - Add MCP server to workspace
   - Test with sample queries

3. **Monitor Regularly**
   ```bash
   python indufix_cli.py status
   ```

### If Some Checks Fail ✗

1. **Review Validation Report**
   ```bash
   python validate_cli.py --report
   ```
   Check: `validation_report_*.json`

2. **Common Issues**

   **"ANTHROPIC_API_KEY not set"**
   - This is CRITICAL - tools won't be invoked without it
   - Add to GitHub Secrets
   - Trigger new deployment

   **"Deployment unreachable"**
   - Check LangSmith UI: https://smith.langchain.com
   - Verify deployment is running
   - Wait 10-15 minutes if just deployed

   **"Tools are available" (generic response)**
   - Means ANTHROPIC_API_KEY not in deployment
   - Add to GitHub Secrets
   - Redeploy

3. **Get Detailed Info**
   ```bash
   python deployment_cli.py validate
   python deployment_cli.py test
   ```

## Using the Master CLI

The `indufix_cli.py` provides a unified interface:

```bash
# Show help
python indufix_cli.py help

# Or use individual tools
python setup_cli.py          # Setup wizard
python test_cli.py           # Testing
python deployment_cli.py     # Deployment
python validate_cli.py       # Validation
```

### Windows Convenience

Use `indufix.bat` for shorter commands:

```cmd
indufix status
indufix test --all
indufix validate
```

## Directory Structure

```
indufix-llamaindex-toolkit/
├── indufix_cli.py              # Master CLI
├── indufix.bat                 # Windows wrapper
├── setup_cli.py                # Setup wizard
├── test_cli.py                 # Testing interface
├── deployment_cli.py           # Deployment management
├── validate_cli.py             # Validation checks
├── requirements-cli.txt        # CLI dependencies
├── CLI_TOOLS_README.md         # Complete documentation
└── QUICK_START_CLI.md          # This file
```

## Typical Workflow

### Day 1 - Initial Setup
```bash
# Install
pip install -r requirements-cli.txt

# Configure
python setup_cli.py

# Validate
python validate_cli.py

# Test
python test_cli.py --all --report
```

### Day 2+ - Regular Use
```bash
# Morning check
python indufix_cli.py status

# Before changes
python validate_cli.py --quick

# After deployment
python test_cli.py --all
```

## Troubleshooting Quick Reference

| Issue | Solution |
|-------|----------|
| Import error | `pip install -r requirements-cli.txt` |
| API key not set | Set environment variables or create `.env` |
| Deployment unreachable | Check LangSmith UI, verify URL |
| Generic responses | Add ANTHROPIC_API_KEY to GitHub Secrets |
| Tests failing | Run `python validate_cli.py --report` |

## Getting Help

1. **Check status first**
   ```bash
   python indufix_cli.py status
   ```

2. **Run validation with report**
   ```bash
   python validate_cli.py --report
   ```

3. **Review documentation**
   - Full docs: `CLI_TOOLS_README.md`
   - Setup guide: `GITHUB_SECRETS_SETUP_GUIDE.md`
   - Deployment info: `DEPLOYMENT_SECRETS_CONFIGURED.md`

## Next Steps

After successful setup:

1. **Explore CLI Features**
   ```bash
   python test_cli.py --list
   python indufix_cli.py help
   ```

2. **Automate Testing**
   - Add to CI/CD pipeline
   - Schedule regular validation
   - Monitor deployment health

3. **Integrate with Workflow**
   - Use before/after deployments
   - Run tests on code changes
   - Validate configuration updates

## Pro Tips

1. **Use tab completion** (if available in your shell)
2. **Alias common commands**:
   ```bash
   alias ifx="python indufix_cli.py"
   ifx status
   ```
3. **Save reports** for comparison:
   ```bash
   python test_cli.py --all --report
   # Creates: test_results_20260123_220000.json
   ```
4. **Run quick checks** before long operations:
   ```bash
   python validate_cli.py --quick
   ```

---

**Need Help?** Run `python indufix_cli.py help` for detailed command reference.

**Ready to Start?** Run `python setup_cli.py` now!
