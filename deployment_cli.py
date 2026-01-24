#!/usr/bin/env python3
"""Interactive Deployment CLI for Indufix LlamaIndex Toolkit

Manages deployment status, triggers redeployment, shows logs,
validates environment variables, and tests MCP endpoints.

Usage:
    python deployment_cli.py                    # Interactive mode
    python deployment_cli.py status             # Show current status
    python deployment_cli.py deploy             # Trigger deployment
    python deployment_cli.py logs               # Show deployment logs
    python deployment_cli.py validate           # Validate configuration
    python deployment_cli.py test               # Test MCP endpoint
"""

import sys
import os
import argparse
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.live import Live
    from rich.layout import Layout
    from rich import box
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

import requests

# Import deployment client
sys.path.insert(0, str(Path(__file__).parent / "deployment"))
try:
    from deployment.langsmith_deploy import LangSmithDeployClient
    from deployment.exceptions import DeploymentError
    DEPLOYMENT_CLIENT_AVAILABLE = True
except ImportError:
    DEPLOYMENT_CLIENT_AVAILABLE = False


class DeploymentCLI:
    """Interactive deployment management CLI"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.deployment_url = os.getenv(
            "MCP_DEPLOYMENT_URL",
            "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app"
        )
        self.api_key = os.getenv("LANGSMITH_API_KEY")
        self.workspace_id = os.getenv("WORKSPACE_ID", "950d802b-125a-45bc-88e4-3d7d0edee182")
        self.integration_id = os.getenv("INTEGRATION_ID", "2fd2db44-37bb-42ed-9f3a-9df2e769b058")

        # Initialize deployment client if available
        self.client = None
        if DEPLOYMENT_CLIENT_AVAILABLE and self.api_key:
            try:
                self.client = LangSmithDeployClient(
                    api_key=self.api_key,
                    workspace_id=self.workspace_id,
                    integration_id=self.integration_id
                )
            except Exception as e:
                self.print_warning(f"Could not initialize deployment client: {e}")

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

    def print_success(self, message: str):
        """Print success message"""
        if self.console:
            self.console.print(f"[green]✓[/green] {message}")
        else:
            print(f"[OK] {message}")

    def print_error(self, message: str):
        """Print error message"""
        if self.console:
            self.console.print(f"[red]✗[/red] {message}")
        else:
            print(f"[ERROR] {message}")

    def print_warning(self, message: str):
        """Print warning message"""
        if self.console:
            self.console.print(f"[yellow]⚠[/yellow] {message}")
        else:
            print(f"[WARNING] {message}")

    def print_info(self, message: str):
        """Print info message"""
        if self.console:
            self.console.print(f"[blue]ℹ[/blue] {message}")
        else:
            print(f"[INFO] {message}")

    def check_deployment_health(self) -> Dict[str, Any]:
        """Check deployment health"""
        try:
            response = requests.get(f"{self.deployment_url}/ok", timeout=10)
            return {
                "healthy": response.status_code == 200,
                "status_code": response.status_code,
                "response": response.text,
                "latency_ms": int(response.elapsed.total_seconds() * 1000)
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }

    def get_deployment_info(self) -> Optional[Dict[str, Any]]:
        """Get deployment information from LangSmith API"""
        if not self.client:
            return None

        try:
            deployments = self.client.list_deployments()
            # Find our deployment
            deployment = next(
                (d for d in deployments if "indufix-llamaindex-toolkit" in d.get('name', '').lower()),
                None
            )
            return deployment
        except Exception as e:
            self.print_warning(f"Could not fetch deployment info: {e}")
            return None

    def show_status(self):
        """Show current deployment status"""
        self.print_header("Deployment Status", f"URL: {self.deployment_url}")

        # Check health
        self.print_info("Checking deployment health...")
        health = self.check_deployment_health()

        # Get deployment info
        deployment = self.get_deployment_info()

        if self.console:
            # Create status table
            table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
            table.add_column("Property", style="cyan", width=25)
            table.add_column("Value", width=45)

            # Basic info
            table.add_row("Deployment URL", self.deployment_url)

            # Health status
            if health.get('healthy'):
                table.add_row("Health Status", "[green]✓ Healthy[/green]")
                table.add_row("Latency", f"{health.get('latency_ms', 0)}ms")
            else:
                table.add_row("Health Status", f"[red]✗ Unhealthy[/red]")
                if 'error' in health:
                    table.add_row("Error", str(health['error']))

            # Deployment details
            if deployment:
                table.add_row("Deployment ID", deployment.get('id', 'N/A'))
                table.add_row("Name", deployment.get('name', 'N/A'))
                table.add_row("State", deployment.get('state', 'N/A'))
                table.add_row("Health", deployment.get('health', 'N/A'))
                if 'updated_at' in deployment:
                    table.add_row("Last Updated", deployment['updated_at'])
                if 'latest_revision_id' in deployment:
                    table.add_row("Latest Revision", deployment['latest_revision_id'])

            self.console.print(table)
        else:
            print("\nDeployment Status:")
            print(f"  URL: {self.deployment_url}")
            print(f"  Health: {'Healthy' if health.get('healthy') else 'Unhealthy'}")
            if deployment:
                print(f"  ID: {deployment.get('id', 'N/A')}")
                print(f"  State: {deployment.get('state', 'N/A')}")
                print(f"  Health: {deployment.get('health', 'N/A')}")

    def validate_environment(self):
        """Validate required environment variables"""
        self.print_header("Environment Validation", "Checking required configuration")

        required_vars = {
            "LANGSMITH_API_KEY": "LangSmith API key",
            "WORKSPACE_ID": "Workspace identifier",
            "INTEGRATION_ID": "GitHub integration ID",
            "LLAMA_CLOUD_API_KEY": "LlamaCloud API key",
            "ANTHROPIC_API_KEY": "Anthropic Claude API key (CRITICAL)"
        }

        optional_vars = {
            "OPENAI_API_KEY": "OpenAI API key (alternative LLM)"
        }

        if self.console:
            table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
            table.add_column("Variable", style="cyan", width=25)
            table.add_column("Description", width=35)
            table.add_column("Status", justify="center", width=15)

            for var, desc in required_vars.items():
                value = os.getenv(var)
                if value:
                    status = "[green]✓ Set[/green]"
                    # Show partial value
                    if len(value) > 20:
                        value_display = f"{value[:10]}...{value[-10:]}"
                    else:
                        value_display = value[:15] + "..."
                else:
                    status = "[red]✗ Missing[/red]"

                table.add_row(var, desc, status)

            # Add optional vars
            for var, desc in optional_vars.items():
                value = os.getenv(var)
                status = "[green]✓ Set[/green]" if value else "[dim]Not set (optional)[/dim]"
                table.add_row(var, desc, status)

            self.console.print(table)
        else:
            print("\nRequired Environment Variables:")
            for var, desc in required_vars.items():
                value = os.getenv(var)
                status = "OK" if value else "MISSING"
                print(f"  [{status}] {var}: {desc}")

        # Check if all required are set
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            self.print_error(f"Missing required variables: {', '.join(missing)}")
            return False
        else:
            self.print_success("All required environment variables are set")
            return True

    def test_mcp_endpoint(self):
        """Test MCP endpoint connectivity"""
        self.print_header("MCP Endpoint Test", "Testing tools/list endpoint")

        if not self.api_key:
            self.print_error("LANGSMITH_API_KEY not set. Cannot test authenticated endpoint.")
            return

        try:
            # Test tools/list
            self.print_info("Calling tools/list...")
            response = requests.post(
                f"{self.deployment_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "params": {},
                    "id": 1
                },
                headers={
                    "Content-Type": "application/json",
                    "X-Api-Key": self.api_key,
                    "X-Tenant-Id": self.workspace_id
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                tools = result.get("result", {}).get("tools", [])

                self.print_success(f"MCP endpoint is working! Found {len(tools)} tool(s)")

                if self.console:
                    table = Table(box=box.SIMPLE, show_header=True)
                    table.add_column("Tool Name", style="cyan")
                    table.add_column("Description", style="dim")

                    for tool in tools:
                        name = tool.get('name', 'N/A')
                        desc = tool.get('description', 'No description')[:60]
                        table.add_row(name, desc)

                    self.console.print(table)
                else:
                    print("\nAvailable tools:")
                    for tool in tools:
                        print(f"  - {tool.get('name', 'N/A')}: {tool.get('description', 'N/A')[:60]}")
            else:
                self.print_error(f"MCP endpoint returned status {response.status_code}")
                print(f"Response: {response.text[:200]}")

        except Exception as e:
            self.print_error(f"MCP endpoint test failed: {e}")

    def trigger_deployment(self):
        """Trigger a new deployment"""
        self.print_header("Trigger Deployment", "Create or update deployment")

        if not self.client:
            self.print_error("Deployment client not available. Check LANGSMITH_API_KEY.")
            self.print_info("Alternative: Push to main/dev branch or use GitHub Actions")
            return

        self.print_warning("This will trigger a new deployment/revision")

        if self.console:
            confirm = Confirm.ask("Continue?", default=False)
        else:
            confirm = input("Continue? [y/N]: ").strip().lower() == 'y'

        if not confirm:
            self.print_info("Deployment cancelled")
            return

        try:
            # Load config
            config_file = Path("deployment/deploy_config.yaml")
            if not config_file.exists():
                self.print_error("Config file not found: deployment/deploy_config.yaml")
                return

            import yaml
            with open(config_file) as f:
                config = yaml.safe_load(f)

            deployment_config = config.get('deployment', {})
            name = deployment_config.get('name', 'indufix-llamaindex-toolkit')

            # Check if exists
            self.print_info("Checking for existing deployment...")
            deployments = self.client.list_deployments()
            existing = next((d for d in deployments if d['name'] == name), None)

            if existing:
                self.print_info(f"Found existing deployment: {existing['id']}")
                self.print_info("Updating deployment (creates new revision)...")

                result = self.client.update_deployment(
                    deployment_id=existing['id'],
                    branch=deployment_config.get('branch', 'main')
                )

                self.print_success(f"Deployment updated! Revision: {result.get('latest_revision_id', 'N/A')}")
            else:
                self.print_info("No existing deployment found")
                self.print_error("Please use GitHub Actions to create initial deployment")
                return

        except Exception as e:
            self.print_error(f"Deployment failed: {e}")

    def show_logs(self):
        """Show deployment logs (simulated)"""
        self.print_header("Deployment Logs", "Recent activity")

        self.print_warning("Log retrieval not yet implemented")
        self.print_info("View logs in LangSmith UI: https://smith.langchain.com")
        self.print_info("Or check GitHub Actions: https://github.com/chicuza/indufix-llamaindex-toolkit/actions")

    def interactive_mode(self):
        """Interactive deployment management"""
        while True:
            self.print_header("Deployment Management")

            print("\nOptions:")
            print("  1. Show deployment status")
            print("  2. Validate environment variables")
            print("  3. Test MCP endpoint")
            print("  4. Trigger deployment")
            print("  5. Show logs")
            print("  0. Exit")

            choice = input("\nSelect option [0]: ").strip() or "0"

            if choice == "0":
                break
            elif choice == "1":
                self.show_status()
            elif choice == "2":
                self.validate_environment()
            elif choice == "3":
                self.test_mcp_endpoint()
            elif choice == "4":
                self.trigger_deployment()
            elif choice == "5":
                self.show_logs()
            else:
                print("Invalid option")

            input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Deployment management CLI for Indufix LlamaIndex Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python deployment_cli.py

  # Show current status
  python deployment_cli.py status

  # Validate environment
  python deployment_cli.py validate

  # Test MCP endpoint
  python deployment_cli.py test

  # Trigger deployment
  python deployment_cli.py deploy

  # Show logs
  python deployment_cli.py logs
"""
    )

    parser.add_argument('command', nargs='?', choices=['status', 'validate', 'test', 'deploy', 'logs'],
                       help='Command to execute')

    args = parser.parse_args()

    # Create CLI
    cli = DeploymentCLI()

    # Execute command
    if args.command == 'status':
        cli.show_status()
    elif args.command == 'validate':
        cli.validate_environment()
    elif args.command == 'test':
        cli.test_mcp_endpoint()
    elif args.command == 'deploy':
        cli.trigger_deployment()
    elif args.command == 'logs':
        cli.show_logs()
    else:
        # Interactive mode
        cli.interactive_mode()

    return 0


if __name__ == "__main__":
    sys.exit(main())
