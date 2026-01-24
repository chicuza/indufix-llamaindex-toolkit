# Indufix CLI Tools - Complete Guide

Production-ready command-line interface tools for managing the Indufix LlamaIndex Toolkit deployment.

## Overview

The Indufix CLI provides a comprehensive suite of tools for:
- **Setup**: Interactive wizard for GitHub Secrets configuration
- **Testing**: Running integration tests and generating reports
- **Deployment**: Managing deployments and monitoring status
- **Validation**: Comprehensive validation checks with actionable feedback
- **Status**: Real-time status dashboard

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements-cli.txt
```

**Dependencies**:
- `rich>=13.7.0` - Beautiful terminal formatting (recommended but optional)
- `requests>=2.31.0` - HTTP client
- `pyyaml>=6.0.1` - YAML configuration

### 2. Set Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required
LANGSMITH_API_KEY=lsv2_pt_your-api-key-here
LLAMA_CLOUD_API_KEY=llx-your-api-key-here
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# Optional (use defaults if not set)
WORKSPACE_ID=950d802b-125a-45bc-88e4-3d7d0edee182
INTEGRATION_ID=2fd2db44-37bb-42ed-9f3a-9df2e769b058
MCP_DEPLOYMENT_URL=https://your-deployment-url.app
```

### 3. Verify Installation

```bash
python indufix_cli.py status
```

## Available Tools

### 1. Master CLI - `indufix_cli.py`

Unified interface for all tools.

```bash
# Show status dashboard
python indufix_cli.py status

# Run setup wizard
python indufix_cli.py setup

# Run all tests
python indufix_cli.py test --all

# Validate deployment
python indufix_cli.py validate

# Show help
python indufix_cli.py help
```

### 2. Setup CLI - `setup_cli.py`

Interactive setup wizard for GitHub Secrets configuration.

```bash
# Run full setup wizard
python setup_cli.py

# Check current configuration
python setup_cli.py --check-only

# Setup and trigger deployment
python setup_cli.py --deploy-after-setup
```

**Features**:
- Step-by-step GitHub Secrets configuration
- Shows exact values to copy
- Opens browser to GitHub settings
- Validates configuration
- Optional deployment trigger

### 3. Test CLI - `test_cli.py`

Interactive testing interface with 7 test scenarios.

```bash
# Interactive mode
python test_cli.py

# List available tests
python test_cli.py --list

# Run all tests
python test_cli.py --all

# Run specific test
python test_cli.py --test 4

# Run and generate report
python test_cli.py --all --report
```

**Test Categories**:
- **Connectivity**: Health checks and reachability
- **Security**: Authentication validation
- **MCP**: Tools list and endpoint verification
- **Integration**: Query tests and tool invocation validation

**Available Tests**:
1. MCP Health Check
2. MCP Authentication Test
3. MCP Tools List
4. Default Values Query
5. Standard Equivalence Query
6. Confidence Penalty Query
7. Complex Multi-Attribute Query

### 4. Deployment CLI - `deployment_cli.py`

Deployment management and monitoring.

```bash
# Interactive mode
python deployment_cli.py

# Show deployment status
python deployment_cli.py status

# Validate environment variables
python deployment_cli.py validate

# Test MCP endpoint
python deployment_cli.py test

# Show logs (simulated)
python deployment_cli.py logs
```

**Features**:
- Real-time deployment status
- Health monitoring
- Environment variable validation
- MCP endpoint testing
- Deployment info from LangSmith API

### 5. Validation CLI - `validate_cli.py`

Comprehensive validation with 11 checks across 4 categories.

```bash
# Run all validation checks
python validate_cli.py

# Quick validation (skip integration tests)
python validate_cli.py --quick

# Generate detailed report
python validate_cli.py --report
```

**Validation Categories**:
- **Environment**: API keys and configuration
- **Deployment**: Reachability and health
- **MCP**: Authentication, tools, endpoints
- **Integration**: Query testing and tool invocation
- **Configuration**: Required files

## Quick Start Guide

### First Time Setup

1. **Run Setup Wizard**
   ```bash
   python setup_cli.py
   ```
   - Follow the interactive prompts
   - Configure GitHub Secrets
   - Wait for deployment (~10-15 minutes)

2. **Validate Deployment**
   ```bash
   python validate_cli.py
   ```
   - Ensures all checks pass
   - Identifies any issues

3. **Run Integration Tests**
   ```bash
   python test_cli.py --all --report
   ```
   - Verifies tool invocations
   - Generates test report

### Daily Workflow

```bash
# Check status
python indufix_cli.py status

# Run validation
python indufix_cli.py validate --quick

# Run specific test
python indufix_cli.py test --id 4
```

## CLI Features

### Rich Terminal Output

When `rich` library is installed:
- Color-coded output
- Beautiful tables and panels
- Progress bars and spinners
- Formatted markdown rendering
- Interactive prompts

Without `rich`:
- Falls back to plain text
- Still fully functional
- All features available

### Error Handling

All CLIs provide:
- Clear error messages
- Actionable suggestions
- Exit codes for CI/CD integration
- Detailed logging

### Report Generation

Test and validation CLIs generate JSON reports:

```json
{
  "timestamp": "2026-01-23T22:30:00",
  "deployment_url": "https://...",
  "summary": {
    "total": 7,
    "passed": 6,
    "failed": 1,
    "success_rate": 85.7
  },
  "tests": [...]
}
```

## Command Reference

### Master CLI Commands

```bash
indufix setup [--check-only] [--deploy]
indufix test [--list] [--all] [--id ID] [--report]
indufix deploy [status|validate|test|logs]
indufix validate [--quick] [--report]
indufix status
indufix help
```

### Setup CLI Options

```bash
--check-only              # Check configuration without setup
--deploy-after-setup      # Trigger deployment after setup
--no-rich                 # Use plain text output
```

### Test CLI Options

```bash
--list                    # List available tests
--all                     # Run all tests
--test ID                 # Run specific test by ID
--report                  # Generate and save report
--url URL                 # Custom deployment URL
--api-key KEY             # Custom API key
```

### Deployment CLI Commands

```bash
status                    # Show deployment status
validate                  # Validate environment variables
test                      # Test MCP endpoint
logs                      # Show deployment logs
```

### Validation CLI Options

```bash
--quick                   # Skip integration tests
--report                  # Generate validation report
--output FILE             # Custom report filename
```

## Environment Variables

### Required

| Variable | Description | Source |
|----------|-------------|--------|
| `LANGSMITH_API_KEY` | LangSmith API key | https://smith.langchain.com/settings |
| `LLAMA_CLOUD_API_KEY` | LlamaCloud API key | https://cloud.llamaindex.ai/api-key |
| `ANTHROPIC_API_KEY` | Anthropic Claude API key | https://console.anthropic.com/settings/keys |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `WORKSPACE_ID` | LangSmith workspace ID | `950d802b-125a-45bc-88e4-3d7d0edee182` |
| `INTEGRATION_ID` | GitHub integration ID | `2fd2db44-37bb-42ed-9f3a-9df2e769b058` |
| `MCP_DEPLOYMENT_URL` | Deployment URL | Hardcoded default |
| `OPENAI_API_KEY` | OpenAI API key | None (optional) |

## Troubleshooting

### Common Issues

#### 1. "LANGSMITH_API_KEY not set"

**Solution**:
```bash
# Windows
set LANGSMITH_API_KEY=your-key-here

# Linux/Mac
export LANGSMITH_API_KEY=your-key-here

# Or create .env file
echo "LANGSMITH_API_KEY=your-key-here" >> .env
```

#### 2. "Deployment unreachable"

**Solution**:
1. Check deployment is running in LangSmith UI
2. Verify `MCP_DEPLOYMENT_URL` is correct
3. Run `python deployment_cli.py status`

#### 3. "Tools are available" (generic response)

**Cause**: `ANTHROPIC_API_KEY` not set in deployment

**Solution**:
1. Add `ANTHROPIC_API_KEY` to GitHub Secrets
2. Trigger new deployment
3. Run `python validate_cli.py`

#### 4. "Import Error: No module named 'rich'"

**Solution**:
```bash
pip install rich
# Or use plain text mode
python setup_cli.py --no-rich
```

### Getting Help

1. **Check Status**
   ```bash
   python indufix_cli.py status
   ```

2. **Run Validation**
   ```bash
   python validate_cli.py --report
   ```

3. **Review Reports**
   - Test reports: `test_results_*.json`
   - Validation reports: `validation_report_*.json`

4. **Check Documentation**
   - Setup: `GITHUB_SECRETS_SETUP_GUIDE.md`
   - Deployment: `DEPLOYMENT_SECRETS_CONFIGURED.md`
   - Agent Builder: `GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md`

## Advanced Usage

### CI/CD Integration

All CLIs return appropriate exit codes:
- `0` - Success
- `1` - Failure
- `2` - Configuration error

Example GitHub Action:
```yaml
- name: Validate deployment
  run: python validate_cli.py --quick

- name: Run tests
  run: python test_cli.py --all --report
```

### Custom Deployment URL

```bash
python test_cli.py --all --url https://custom-deployment.app
```

### Automated Testing

```bash
# Run tests and fail on any error
python test_cli.py --all || exit 1

# Generate report and upload
python test_cli.py --all --report
aws s3 cp test_results_*.json s3://my-bucket/
```

### Monitoring Script

```bash
#!/bin/bash
# monitor.sh - Run every 5 minutes

python deployment_cli.py status > status.log 2>&1
python validate_cli.py --quick --report

if [ $? -ne 0 ]; then
  echo "Validation failed!" | mail -s "Indufix Alert" admin@example.com
fi
```

## Architecture

### Tool Organization

```
indufix-llamaindex-toolkit/
├── indufix_cli.py           # Master CLI (unified interface)
├── setup_cli.py             # Setup wizard
├── test_cli.py              # Testing interface
├── deployment_cli.py        # Deployment management
├── validate_cli.py          # Validation checks
├── requirements-cli.txt     # CLI dependencies
└── CLI_TOOLS_README.md      # This file
```

### Design Principles

1. **Progressive Enhancement**: Works without `rich`, enhanced with it
2. **Clear Feedback**: Colored output, progress indicators, clear messages
3. **Actionable Errors**: Every error includes suggestions
4. **Composable**: Each tool can be used standalone or via master CLI
5. **CI/CD Ready**: Exit codes, JSON reports, non-interactive modes

### Dependencies

- **Core**: `requests`, `pyyaml` (required)
- **Enhanced UX**: `rich` (optional but recommended)
- **Deployment**: `langsmith` (for deployment client)

## Examples

### Complete Setup Flow

```bash
# 1. Check current state
python setup_cli.py --check-only

# 2. Run setup wizard
python setup_cli.py

# 3. Validate everything is working
python validate_cli.py

# 4. Run integration tests
python test_cli.py --all --report

# 5. Check final status
python indufix_cli.py status
```

### Daily Monitoring

```bash
# Morning check
python indufix_cli.py status

# Before making changes
python validate_cli.py --quick

# After deployment
python test_cli.py --all
```

### Debugging Failed Deployment

```bash
# 1. Check what's wrong
python validate_cli.py --report

# 2. Check deployment status
python deployment_cli.py status

# 3. Validate environment
python deployment_cli.py validate

# 4. Test MCP endpoint
python deployment_cli.py test

# 5. Run specific test
python test_cli.py --test 3
```

## Contributing

When adding new CLI features:

1. Follow existing patterns (rich/fallback design)
2. Provide clear error messages
3. Add to master CLI if appropriate
4. Update this README
5. Test with and without `rich` library

## Support

- **Issues**: Check validation report for detailed diagnostics
- **Questions**: Review documentation files
- **Updates**: Re-run setup wizard for configuration changes

## License

Same as main project.

---

**Last Updated**: 2026-01-23
**Version**: 1.0.0
**Status**: Production Ready
