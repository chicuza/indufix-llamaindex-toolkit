#!/usr/bin/env python3
"""Indufix CLI - Master CLI for Indufix LlamaIndex Toolkit

Unified command-line interface for setup, testing, deployment, and validation.

Usage:
    indufix setup              # Run setup wizard
    indufix test               # Run tests
    indufix deploy             # Manage deployment
    indufix validate           # Run validation
    indufix status             # Show status dashboard
    indufix --help             # Show help

Alternative:
    python indufix_cli.py <command>
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class IndufixCLI:
    """Master CLI for Indufix toolkit"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.root_dir = Path(__file__).parent

    def print_header(self, title: str, subtitle: str = None):
        """Print formatted header"""
        if self.console:
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

    def show_banner(self):
        """Show Indufix CLI banner"""
        if self.console:
            banner = """
# Indufix LlamaIndex Toolkit CLI

**Comprehensive toolkit for managing your Indufix deployment**

Available Commands:
- `setup` - Interactive setup wizard
- `test` - Run integration tests
- `deploy` - Manage deployments
- `validate` - Validation checks
- `status` - Status dashboard
"""
            self.console.print(Panel(Markdown(banner), border_style="cyan", box=box.DOUBLE))
        else:
            print("\n" + "=" * 70)
            print("  Indufix LlamaIndex Toolkit CLI")
            print("=" * 70)
            print("\nAvailable Commands:")
            print("  setup     - Interactive setup wizard")
            print("  test      - Run integration tests")
            print("  deploy    - Manage deployments")
            print("  validate  - Validation checks")
            print("  status    - Status dashboard")
            print("=" * 70)

    def run_setup(self, args):
        """Run setup wizard"""
        cmd = [sys.executable, str(self.root_dir / "setup_cli.py")]

        if args.check_only:
            cmd.append("--check-only")
        if args.deploy:
            cmd.append("--deploy-after-setup")

        return subprocess.call(cmd)

    def run_test(self, args):
        """Run tests"""
        cmd = [sys.executable, str(self.root_dir / "test_cli.py")]

        if args.list:
            cmd.append("--list")
        elif args.all:
            cmd.append("--all")
            if args.report:
                cmd.append("--report")
        elif args.id:
            cmd.extend(["--test", str(args.id)])

        return subprocess.call(cmd)

    def run_deploy(self, args):
        """Run deployment management"""
        cmd = [sys.executable, str(self.root_dir / "deployment_cli.py")]

        if args.action:
            cmd.append(args.action)

        return subprocess.call(cmd)

    def run_validate(self, args):
        """Run validation"""
        cmd = [sys.executable, str(self.root_dir / "validate_cli.py")]

        if args.quick:
            cmd.append("--quick")
        if args.report:
            cmd.append("--report")

        return subprocess.call(cmd)

    def show_status(self):
        """Show comprehensive status dashboard"""
        self.print_header("Indufix Toolkit - Status Dashboard")

        # Environment check
        print("\n1. ENVIRONMENT VARIABLES")
        env_vars = {
            "LANGSMITH_API_KEY": os.getenv("LANGSMITH_API_KEY"),
            "LLAMA_CLOUD_API_KEY": os.getenv("LLAMA_CLOUD_API_KEY"),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "WORKSPACE_ID": os.getenv("WORKSPACE_ID"),
        }

        if self.console:
            table = Table(box=box.SIMPLE, show_header=True)
            table.add_column("Variable", style="cyan")
            table.add_column("Status", justify="center")

            for var, value in env_vars.items():
                status = "[green]✓ Set[/green]" if value else "[red]✗ Not Set[/red]"
                table.add_row(var, status)

            self.console.print(table)
        else:
            for var, value in env_vars.items():
                status = "OK" if value else "MISSING"
                print(f"  [{status}] {var}")

        # Deployment status
        print("\n2. DEPLOYMENT STATUS")
        deployment_url = os.getenv(
            "MCP_DEPLOYMENT_URL",
            "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app"
        )

        print(f"  URL: {deployment_url}")

        # Quick health check
        try:
            import requests
            response = requests.get(f"{deployment_url}/ok", timeout=5)
            if response.status_code == 200:
                if self.console:
                    self.console.print("  Health: [green]✓ Healthy[/green]")
                else:
                    print("  Health: OK")
            else:
                if self.console:
                    self.console.print(f"  Health: [yellow]⚠ Status {response.status_code}[/yellow]")
                else:
                    print(f"  Health: Status {response.status_code}")
        except Exception as e:
            if self.console:
                self.console.print(f"  Health: [red]✗ Unreachable[/red]")
            else:
                print("  Health: Unreachable")

        # Available tools
        print("\n3. AVAILABLE TOOLS")
        tools_available = [
            "setup_cli.py - Setup wizard",
            "test_cli.py - Testing interface",
            "deployment_cli.py - Deployment management",
            "validate_cli.py - Validation checks"
        ]

        for tool in tools_available:
            tool_path = self.root_dir / tool.split(" - ")[0]
            if tool_path.exists():
                if self.console:
                    self.console.print(f"  [green]✓[/green] {tool}")
                else:
                    print(f"  [OK] {tool}")
            else:
                if self.console:
                    self.console.print(f"  [red]✗[/red] {tool}")
                else:
                    print(f"  [MISSING] {tool}")

        # Quick actions
        print("\n4. QUICK ACTIONS")
        print("  Run setup:    indufix setup")
        print("  Run tests:    indufix test --all")
        print("  Validate:     indufix validate")
        print("  Check deploy: indufix deploy status")

    def show_help(self):
        """Show comprehensive help"""
        self.show_banner()

        if self.console:
            help_text = """
## Command Reference

### Setup
```bash
indufix setup                    # Run interactive setup wizard
indufix setup --check-only       # Check current configuration
indufix setup --deploy           # Setup and trigger deployment
```

### Testing
```bash
indufix test                     # Interactive test mode
indufix test --list              # List available tests
indufix test --all               # Run all tests
indufix test --all --report      # Run tests and generate report
indufix test --id 4              # Run specific test
```

### Deployment
```bash
indufix deploy                   # Interactive deployment management
indufix deploy status            # Show deployment status
indufix deploy validate          # Validate environment
indufix deploy test              # Test MCP endpoint
```

### Validation
```bash
indufix validate                 # Run all validation checks
indufix validate --quick         # Quick validation (skip integration)
indufix validate --report        # Generate validation report
```

### Status
```bash
indufix status                   # Show status dashboard
```

## Getting Started

1. **First Time Setup**
   ```bash
   indufix setup
   ```
   This will guide you through:
   - GitHub Secrets configuration
   - Deployment setup
   - Initial validation

2. **After Setup**
   ```bash
   indufix validate              # Verify everything is working
   indufix test --all            # Run integration tests
   indufix status                # Check current status
   ```

3. **Daily Usage**
   ```bash
   indufix deploy status         # Check deployment
   indufix test --all            # Run tests
   ```

## Environment Variables

Required:
- `LANGSMITH_API_KEY` - LangSmith API key
- `LLAMA_CLOUD_API_KEY` - LlamaCloud API key
- `ANTHROPIC_API_KEY` - Anthropic Claude API key (CRITICAL!)
- `WORKSPACE_ID` - LangSmith workspace ID

Optional:
- `OPENAI_API_KEY` - OpenAI API key
- `MCP_DEPLOYMENT_URL` - Custom deployment URL

## Documentation

- Setup Guide: `GITHUB_SECRETS_SETUP_GUIDE.md`
- Deployment Info: `DEPLOYMENT_SECRETS_CONFIGURED.md`
- Agent Builder: `GUIA_UI_INTEGRACAO_PASSO_A_PASSO.md`

## Support

For issues or questions:
1. Run `indufix validate` to check configuration
2. Check deployment logs
3. Review documentation files
"""
            md = Markdown(help_text)
            self.console.print(md)
        else:
            print("\nCommand Reference:")
            print("\nSetup:")
            print("  indufix setup                 - Run interactive setup")
            print("  indufix setup --check-only    - Check configuration")
            print("\nTesting:")
            print("  indufix test --all            - Run all tests")
            print("  indufix test --list           - List tests")
            print("\nDeployment:")
            print("  indufix deploy status         - Show deployment status")
            print("  indufix deploy validate       - Validate environment")
            print("\nValidation:")
            print("  indufix validate              - Run all checks")
            print("  indufix validate --quick      - Quick validation")
            print("\nStatus:")
            print("  indufix status                - Show status dashboard")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        prog="indufix",
        description="Indufix LlamaIndex Toolkit - Unified CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Run setup wizard')
    setup_parser.add_argument('--check-only', action='store_true',
                             help='Check configuration only')
    setup_parser.add_argument('--deploy', action='store_true',
                             help='Trigger deployment after setup')

    # Test command
    test_parser = subparsers.add_parser('test', help='Run tests')
    test_parser.add_argument('--list', action='store_true',
                            help='List available tests')
    test_parser.add_argument('--all', action='store_true',
                            help='Run all tests')
    test_parser.add_argument('--id', type=int, metavar='ID',
                            help='Run specific test')
    test_parser.add_argument('--report', action='store_true',
                            help='Generate report')

    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Manage deployment')
    deploy_parser.add_argument('action', nargs='?',
                              choices=['status', 'validate', 'test', 'logs'],
                              help='Deployment action')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Run validation')
    validate_parser.add_argument('--quick', action='store_true',
                                help='Quick validation')
    validate_parser.add_argument('--report', action='store_true',
                                help='Generate report')

    # Status command
    status_parser = subparsers.add_parser('status', help='Show status dashboard')

    # Help command
    help_parser = subparsers.add_parser('help', help='Show detailed help')

    args = parser.parse_args()

    # Create CLI instance
    cli = IndufixCLI()

    # Execute command
    if args.command == 'setup':
        return cli.run_setup(args)
    elif args.command == 'test':
        return cli.run_test(args)
    elif args.command == 'deploy':
        return cli.run_deploy(args)
    elif args.command == 'validate':
        return cli.run_validate(args)
    elif args.command == 'status':
        cli.show_status()
        return 0
    elif args.command == 'help':
        cli.show_help()
        return 0
    else:
        # No command provided - show banner and basic help
        cli.show_banner()
        print("\nRun 'indufix help' for detailed usage")
        print("Or 'indufix <command> --help' for command-specific help")
        return 0


if __name__ == "__main__":
    sys.exit(main())
