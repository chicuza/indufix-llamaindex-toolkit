#!/usr/bin/env python3
"""Interactive Setup CLI for Indufix LlamaIndex Toolkit

Guides users through the complete GitHub Secrets configuration,
deployment setup, and initial validation process.

Usage:
    python setup_cli.py
    python setup_cli.py --check-only
    python setup_cli.py --deploy-after-setup
"""

import sys
import os
import argparse
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.table import Table
    from rich.prompt import Prompt, Confirm
    from rich.markdown import Markdown
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not found. Install with: pip install rich")
    print("Falling back to basic output...")

import requests
import json


class SetupCLI:
    """Interactive setup wizard for Indufix deployment"""

    def __init__(self, use_rich: bool = True):
        self.use_rich = use_rich and RICH_AVAILABLE
        if self.use_rich:
            self.console = Console()

        # Load existing secrets from .env if available
        self.env_file = Path(".env")
        self.existing_secrets = self._load_env_file()

        # GitHub configuration
        self.github_repo = "chicuza/indufix-llamaindex-toolkit"
        self.github_secrets_url = f"https://github.com/{self.github_repo}/settings/secrets/actions"

        # Required secrets
        self.required_secrets = {
            "LANGSMITH_API_KEY": {
                "description": "LangSmith API key for deployment authentication",
                "url": "https://smith.langchain.com/settings",
                "env_var": "LANGSMITH_API_KEY",
                "critical": True
            },
            "WORKSPACE_ID": {
                "description": "LangSmith workspace identifier",
                "value": "950d802b-125a-45bc-88e4-3d7d0edee182",
                "critical": True
            },
            "INTEGRATION_ID": {
                "description": "GitHub-LangSmith integration ID",
                "value": "2fd2db44-37bb-42ed-9f3a-9df2e769b058",
                "critical": True
            },
            "LLAMA_CLOUD_API_KEY": {
                "description": "LlamaCloud API key for knowledge base access",
                "url": "https://cloud.llamaindex.ai/api-key",
                "env_var": "LLAMA_CLOUD_API_KEY",
                "critical": True
            },
            "ANTHROPIC_API_KEY": {
                "description": "Anthropic Claude API key (enables tool routing)",
                "url": "https://console.anthropic.com/settings/keys",
                "critical": True,
                "note": "CRITICAL: Without this, tools won't be invoked!"
            },
            "OPENAI_API_KEY": {
                "description": "OpenAI API key (optional alternative LLM)",
                "url": "https://platform.openai.com/api-keys",
                "critical": False
            }
        }

    def _load_env_file(self) -> Dict[str, str]:
        """Load existing values from .env file"""
        secrets = {}
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        secrets[key.strip()] = value.strip()
        return secrets

    def print_header(self, title: str, subtitle: Optional[str] = None):
        """Print formatted header"""
        if self.use_rich:
            self.console.print()
            if subtitle:
                self.console.print(Panel(f"[bold cyan]{title}[/bold cyan]\n{subtitle}",
                                        border_style="cyan", box=box.DOUBLE))
            else:
                self.console.print(Panel(f"[bold cyan]{title}[/bold cyan]",
                                        border_style="cyan", box=box.DOUBLE))
        else:
            print("\n" + "=" * 70)
            print(f"  {title}")
            if subtitle:
                print(f"  {subtitle}")
            print("=" * 70)

    def print_success(self, message: str):
        """Print success message"""
        if self.use_rich:
            self.console.print(f"[green]✓[/green] {message}")
        else:
            print(f"[OK] {message}")

    def print_error(self, message: str):
        """Print error message"""
        if self.use_rich:
            self.console.print(f"[red]✗[/red] {message}")
        else:
            print(f"[ERROR] {message}")

    def print_warning(self, message: str):
        """Print warning message"""
        if self.use_rich:
            self.console.print(f"[yellow]⚠[/yellow] {message}")
        else:
            print(f"[WARNING] {message}")

    def print_info(self, message: str):
        """Print info message"""
        if self.use_rich:
            self.console.print(f"[blue]ℹ[/blue] {message}")
        else:
            print(f"[INFO] {message}")

    def show_welcome(self):
        """Show welcome screen"""
        self.print_header(
            "Indufix LlamaIndex Toolkit - Setup Wizard",
            "Interactive configuration for GitHub Secrets and deployment"
        )

        if self.use_rich:
            welcome_text = """
## What This Wizard Does

1. **Guides you through GitHub Secrets configuration**
2. **Shows you the exact values to copy**
3. **Validates secrets are correctly added**
4. **Triggers deployment (optional)**
5. **Monitors deployment progress**

## Prerequisites

- GitHub account with write access to the repository
- LangSmith account with API key
- LlamaCloud account with API key
- Anthropic API key (critical for tool invocation)

Press Enter to continue...
"""
            md = Markdown(welcome_text)
            self.console.print(md)
            input()
        else:
            print("\nWhat This Wizard Does:")
            print("  1. Guides you through GitHub Secrets configuration")
            print("  2. Shows you the exact values to copy")
            print("  3. Validates secrets are correctly added")
            print("  4. Triggers deployment (optional)")
            print("  5. Monitors deployment progress")
            print("\nPress Enter to continue...")
            input()

    def display_secrets_table(self):
        """Display table of required secrets with values"""
        self.print_header("Required GitHub Secrets", "Copy these values to GitHub")

        if self.use_rich:
            table = Table(title="GitHub Secrets Configuration",
                         box=box.ROUNDED,
                         show_header=True,
                         header_style="bold magenta")
            table.add_column("Secret Name", style="cyan", width=25)
            table.add_column("Value", style="green", width=40)
            table.add_column("Status", justify="center", width=10)

            for secret_name, config in self.required_secrets.items():
                # Get value from config or env file
                if "value" in config:
                    value = config["value"]
                    status = "[green]✓[/green]"
                elif "env_var" in config and config["env_var"] in self.existing_secrets:
                    value = self.existing_secrets[config["env_var"]]
                    status = "[green]✓[/green]"
                else:
                    value = f"[yellow]Get from: {config.get('url', 'N/A')}[/yellow]"
                    status = "[yellow]⚠[/yellow]"

                # Add critical marker
                name_display = secret_name
                if config.get("critical"):
                    name_display = f"[bold]{secret_name}[/bold] [red]*[/red]"

                table.add_row(name_display, value, status)

            self.console.print(table)
            self.console.print("\n[red]*[/red] = Critical (deployment will fail without this)")
        else:
            print("\nSecret Name                | Value                                    | Status")
            print("-" * 90)
            for secret_name, config in self.required_secrets.items():
                if "value" in config:
                    value = config["value"]
                    status = "OK"
                elif "env_var" in config and config["env_var"] in self.existing_secrets:
                    value = self.existing_secrets[config["env_var"]]
                    status = "OK"
                else:
                    value = f"Get from: {config.get('url', 'N/A')}"
                    status = "MISSING"

                critical = " *" if config.get("critical") else "  "
                print(f"{secret_name:25}{critical} | {value:40} | {status}")

    def show_secret_details(self, secret_name: str):
        """Show detailed information for a specific secret"""
        config = self.required_secrets[secret_name]

        if self.use_rich:
            details = f"""
## {secret_name}

**Description**: {config['description']}
"""
            if config.get('critical'):
                details += "\n**CRITICAL**: This secret is required for deployment\n"

            if config.get('note'):
                details += f"\n**Note**: {config['note']}\n"

            if 'value' in config:
                details += f"\n**Value to copy**:\n```\n{config['value']}\n```\n"
            elif 'env_var' in config and config['env_var'] in self.existing_secrets:
                value = self.existing_secrets[config['env_var']]
                details += f"\n**Value from .env file**:\n```\n{value}\n```\n"
            elif 'url' in config:
                details += f"\n**Get your key from**: {config['url']}\n"

            md = Markdown(details)
            self.console.print(Panel(md, border_style="cyan"))
        else:
            print(f"\n{secret_name}")
            print(f"Description: {config['description']}")
            if config.get('critical'):
                print("CRITICAL: This secret is required for deployment")
            if config.get('note'):
                print(f"Note: {config['note']}")
            if 'value' in config:
                print(f"Value to copy: {config['value']}")
            elif 'env_var' in config and config['env_var'] in self.existing_secrets:
                print(f"Value from .env: {self.existing_secrets[config['env_var']]}")
            elif 'url' in config:
                print(f"Get your key from: {config['url']}")

    def guide_github_secrets_setup(self):
        """Interactive guide for adding secrets to GitHub"""
        self.print_header("Step 1: Add Secrets to GitHub")

        self.print_info(f"Repository: {self.github_repo}")
        self.print_info(f"Secrets URL: {self.github_secrets_url}")

        if self.use_rich:
            if Confirm.ask("\nOpen GitHub Secrets page in browser?", default=True):
                webbrowser.open(self.github_secrets_url)
                self.print_success("Browser opened!")
        else:
            response = input("\nOpen GitHub Secrets page in browser? [Y/n]: ").strip().lower()
            if response != 'n':
                webbrowser.open(self.github_secrets_url)
                print("[OK] Browser opened!")

        print("\n" + "=" * 70)
        print("INSTRUCTIONS:")
        print("=" * 70)
        print("1. In the browser, click 'New repository secret'")
        print("2. For each secret below:")
        print("   - Copy the 'Name' exactly as shown")
        print("   - Copy the 'Value' exactly as shown")
        print("   - Click 'Add secret'")
        print("=" * 70)

        input("\nPress Enter when ready to see secret values...")

        # Show each secret one by one
        for i, (secret_name, config) in enumerate(self.required_secrets.items(), 1):
            print("\n" + "=" * 70)
            print(f"Secret {i}/{len(self.required_secrets)}: {secret_name}")
            print("=" * 70)

            self.show_secret_details(secret_name)

            # Show instructions for this specific secret
            if 'value' in config:
                print(f"\n1. Name: {secret_name}")
                print(f"2. Value: {config['value']}")
            elif 'env_var' in config and config['env_var'] in self.existing_secrets:
                print(f"\n1. Name: {secret_name}")
                print(f"2. Value: {self.existing_secrets[config['env_var']]}")
            else:
                print(f"\n1. Name: {secret_name}")
                print(f"2. Get your API key from: {config.get('url', 'your account')}")
                print(f"3. Paste the key value in GitHub")

            if i < len(self.required_secrets):
                input("\nPress Enter to continue to next secret...")

        print("\n" + "=" * 70)
        self.print_success("All secrets shown!")
        print("=" * 70)

    def validate_github_secrets(self) -> bool:
        """Validate that secrets are properly configured in GitHub"""
        self.print_header("Step 2: Validate GitHub Secrets")

        self.print_info("Validating secrets via GitHub API...")
        self.print_warning("Note: GitHub API doesn't expose secret values (security)")
        self.print_warning("We can only check if secrets exist, not their values")

        # Ask user to confirm they added all secrets
        if self.use_rich:
            all_added = Confirm.ask("\nDid you add all 6 required secrets to GitHub?")
        else:
            response = input("\nDid you add all 6 required secrets to GitHub? [y/N]: ").strip().lower()
            all_added = response == 'y'

        if all_added:
            self.print_success("Great! Secrets should be configured correctly")
            return True
        else:
            self.print_warning("Please complete the GitHub Secrets configuration")
            self.print_info("Re-run this wizard when ready")
            return False

    def trigger_deployment(self) -> bool:
        """Trigger a GitHub Actions deployment"""
        self.print_header("Step 3: Trigger Deployment")

        if self.use_rich:
            should_deploy = Confirm.ask("\nTrigger deployment now?", default=True)
        else:
            response = input("\nTrigger deployment now? [Y/n]: ").strip().lower()
            should_deploy = response != 'n'

        if not should_deploy:
            self.print_info("Deployment skipped")
            self.print_info("You can trigger it manually by pushing to main/dev branch")
            return False

        self.print_info("To trigger deployment, you can:")
        print("\n1. Push a commit to main or dev branch:")
        print("   git commit --allow-empty -m 'Trigger deployment'")
        print("   git push")
        print("\n2. Manually trigger workflow in GitHub Actions:")
        print(f"   https://github.com/{self.github_repo}/actions")

        if self.use_rich:
            open_actions = Confirm.ask("\nOpen GitHub Actions page?", default=True)
        else:
            response = input("\nOpen GitHub Actions page? [Y/n]: ").strip().lower()
            open_actions = response != 'n'

        if open_actions:
            webbrowser.open(f"https://github.com/{self.github_repo}/actions")
            self.print_success("Browser opened!")

        return True

    def show_next_steps(self):
        """Show next steps after setup"""
        self.print_header("Setup Complete!", "Next Steps")

        if self.use_rich:
            next_steps = """
## What's Next?

1. **Monitor Deployment**
   - Run: `python deployment_cli.py status`
   - Check GitHub Actions for build progress
   - Wait ~10-15 minutes for deployment

2. **Validate Deployment**
   - Run: `python validate_cli.py`
   - Verify all checks pass
   - Test MCP endpoints

3. **Run Tests**
   - Run: `python test_cli.py`
   - Execute integration tests
   - Verify tool invocations work

4. **Configure Agent Builder** (IMPORTANT!)
   - Follow guide: `GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md`
   - Add MCP server to workspace
   - Configure agent with indufix_agent tool

## Important Notes

- **Deployment takes 10-15 minutes** - be patient!
- **ANTHROPIC_API_KEY is critical** - without it, tools won't be invoked
- **Test both direct MCP calls AND Agent Builder** - two ways to verify
- **Check deployment logs** if anything fails

## Useful Commands

```bash
# Check deployment status
python deployment_cli.py status

# Run validation tests
python validate_cli.py

# Run integration tests
python test_cli.py --all

# View deployment logs
python deployment_cli.py logs
```

## Documentation

- Setup Guide: `GITHUB_SECRETS_SETUP_GUIDE.md`
- Secrets Info: `DEPLOYMENT_SECRETS_CONFIGURED.md`
- Agent Builder: `GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md`
"""
            md = Markdown(next_steps)
            self.console.print(md)
        else:
            print("\nWhat's Next?")
            print("\n1. Monitor Deployment")
            print("   - Run: python deployment_cli.py status")
            print("   - Wait ~10-15 minutes")
            print("\n2. Validate Deployment")
            print("   - Run: python validate_cli.py")
            print("\n3. Run Tests")
            print("   - Run: python test_cli.py")
            print("\n4. Configure Agent Builder")
            print("   - Follow: GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md")

    def run_check_only(self):
        """Check current configuration without setup"""
        self.print_header("Configuration Check", "Checking current setup status")

        # Check .env file
        if self.env_file.exists():
            self.print_success(f".env file found with {len(self.existing_secrets)} variables")
        else:
            self.print_warning(".env file not found")

        # Check which secrets are available
        self.print_info("\nSecret availability:")
        for secret_name, config in self.required_secrets.items():
            if "value" in config:
                self.print_success(f"{secret_name}: Hardcoded value available")
            elif "env_var" in config and config["env_var"] in self.existing_secrets:
                self.print_success(f"{secret_name}: Found in .env")
            else:
                self.print_warning(f"{secret_name}: Not found (need to get from {config.get('url', 'account')})")

        print("\nNext: Run without --check-only to start setup wizard")

    def run(self, check_only: bool = False, deploy_after: bool = False):
        """Run the setup wizard"""
        if check_only:
            self.run_check_only()
            return

        # Main wizard flow
        self.show_welcome()
        self.display_secrets_table()
        self.guide_github_secrets_setup()

        secrets_valid = self.validate_github_secrets()

        if secrets_valid and deploy_after:
            self.trigger_deployment()

        self.show_next_steps()

        if self.use_rich:
            self.console.print("\n[bold green]Setup wizard complete![/bold green] 🎉\n")
        else:
            print("\n[OK] Setup wizard complete!\n")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Interactive setup wizard for Indufix LlamaIndex Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full setup wizard
  python setup_cli.py

  # Check configuration only
  python setup_cli.py --check-only

  # Setup and trigger deployment
  python setup_cli.py --deploy-after-setup

  # Use basic output (no colors)
  python setup_cli.py --no-rich
"""
    )

    parser.add_argument('--check-only', action='store_true',
                       help='Check current configuration without running setup')
    parser.add_argument('--deploy-after-setup', action='store_true',
                       help='Trigger deployment after setup completes')
    parser.add_argument('--no-rich', action='store_true',
                       help='Use basic output without rich formatting')

    args = parser.parse_args()

    # Create and run wizard
    wizard = SetupCLI(use_rich=not args.no_rich)
    wizard.run(check_only=args.check_only, deploy_after=args.deploy_after_setup)

    return 0


if __name__ == "__main__":
    sys.exit(main())
