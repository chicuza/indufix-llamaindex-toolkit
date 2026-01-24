#!/usr/bin/env python3
"""Validation CLI for Indufix LlamaIndex Toolkit

Runs comprehensive validation checks on deployment, configuration,
and integration. Provides actionable feedback and detailed reports.

Usage:
    python validate_cli.py                  # Run all checks
    python validate_cli.py --quick          # Quick validation
    python validate_cli.py --check health   # Run specific check
    python validate_cli.py --report         # Generate detailed report
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.tree import Tree
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

import requests


class ValidationCheck:
    """Single validation check"""

    def __init__(self, name: str, description: str, category: str):
        self.name = name
        self.description = description
        self.category = category
        self.status = "pending"  # pending, passed, failed, warning
        self.message = ""
        self.details = {}
        self.suggestions = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "status": self.status,
            "message": self.message,
            "details": self.details,
            "suggestions": self.suggestions
        }


class ValidationCLI:
    """Comprehensive validation CLI"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.deployment_url = os.getenv(
            "MCP_DEPLOYMENT_URL",
            "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app"
        )
        self.api_key = os.getenv("LANGSMITH_API_KEY")
        self.workspace_id = os.getenv("WORKSPACE_ID", "950d802b-125a-45bc-88e4-3d7d0edee182")

        self.checks: List[ValidationCheck] = []
        self.initialize_checks()

    def initialize_checks(self):
        """Initialize all validation checks"""
        # Environment checks
        self.checks.append(ValidationCheck(
            "env_langsmith_api_key",
            "LangSmith API key is configured",
            "environment"
        ))
        self.checks.append(ValidationCheck(
            "env_llama_cloud_api_key",
            "LlamaCloud API key is configured",
            "environment"
        ))
        self.checks.append(ValidationCheck(
            "env_anthropic_api_key",
            "Anthropic API key is configured (CRITICAL)",
            "environment"
        ))

        # Deployment checks
        self.checks.append(ValidationCheck(
            "deployment_reachable",
            "Deployment URL is reachable",
            "deployment"
        ))
        self.checks.append(ValidationCheck(
            "deployment_health",
            "Deployment health endpoint responds OK",
            "deployment"
        ))

        # MCP checks
        self.checks.append(ValidationCheck(
            "mcp_auth_required",
            "MCP endpoint requires authentication",
            "mcp"
        ))
        self.checks.append(ValidationCheck(
            "mcp_tools_list",
            "MCP tools/list returns tools",
            "mcp"
        ))
        self.checks.append(ValidationCheck(
            "mcp_indufix_agent",
            "indufix_agent tool is available",
            "mcp"
        ))

        # Integration checks
        self.checks.append(ValidationCheck(
            "integration_query_test",
            "Sample query returns valid response",
            "integration"
        ))
        self.checks.append(ValidationCheck(
            "integration_tool_invocation",
            "Tools are actually invoked (not generic response)",
            "integration"
        ))

        # Configuration checks
        self.checks.append(ValidationCheck(
            "config_files_present",
            "Required configuration files exist",
            "configuration"
        ))

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

    def print_check_result(self, check: ValidationCheck):
        """Print result of a validation check"""
        if self.console:
            if check.status == "passed":
                icon = "[green]✓[/green]"
            elif check.status == "failed":
                icon = "[red]✗[/red]"
            elif check.status == "warning":
                icon = "[yellow]⚠[/yellow]"
            else:
                icon = "[dim]○[/dim]"

            self.console.print(f"{icon} {check.name}: {check.message}")
        else:
            status_icon = {
                "passed": "[OK]",
                "failed": "[FAIL]",
                "warning": "[WARN]",
                "pending": "[...]"
            }.get(check.status, "[?]")
            print(f"{status_icon} {check.name}: {check.message}")

    def check_environment_variables(self):
        """Check required environment variables"""
        required_vars = {
            "LANGSMITH_API_KEY": "env_langsmith_api_key",
            "LLAMA_CLOUD_API_KEY": "env_llama_cloud_api_key",
            "ANTHROPIC_API_KEY": "env_anthropic_api_key"
        }

        for env_var, check_id in required_vars.items():
            check = next(c for c in self.checks if c.name == check_id)

            value = os.getenv(env_var)
            if value:
                check.status = "passed"
                check.message = f"{env_var} is set"
                check.details = {"length": len(value), "preview": value[:10] + "..."}
            else:
                check.status = "failed"
                check.message = f"{env_var} is not set"
                check.suggestions = [
                    f"Set {env_var} in your environment",
                    f"Or add to .env file: {env_var}=your-key-here"
                ]

                # Special handling for critical variables
                if env_var == "ANTHROPIC_API_KEY":
                    check.suggestions.append(
                        "WITHOUT ANTHROPIC_API_KEY, tools won't be invoked!"
                    )

    def check_deployment_reachable(self):
        """Check if deployment URL is reachable"""
        check = next(c for c in self.checks if c.name == "deployment_reachable")

        try:
            response = requests.get(self.deployment_url, timeout=10)
            check.status = "passed"
            check.message = f"Deployment is reachable (status {response.status_code})"
            check.details = {"status_code": response.status_code, "url": self.deployment_url}
        except requests.exceptions.ConnectionError:
            check.status = "failed"
            check.message = "Cannot connect to deployment"
            check.suggestions = [
                "Check if deployment URL is correct",
                "Verify deployment is running in LangSmith",
                f"URL: {self.deployment_url}"
            ]
        except Exception as e:
            check.status = "failed"
            check.message = f"Error connecting: {str(e)}"

    def check_deployment_health(self):
        """Check deployment health endpoint"""
        check = next(c for c in self.checks if c.name == "deployment_health")

        try:
            response = requests.get(f"{self.deployment_url}/ok", timeout=10)
            if response.status_code == 200:
                check.status = "passed"
                check.message = "Health endpoint OK"
                check.details = {
                    "status_code": 200,
                    "latency_ms": int(response.elapsed.total_seconds() * 1000)
                }
            else:
                check.status = "failed"
                check.message = f"Health check returned {response.status_code}"
                check.suggestions = ["Check deployment logs", "Verify deployment is healthy"]
        except Exception as e:
            check.status = "failed"
            check.message = f"Health check failed: {str(e)}"

    def check_mcp_auth_required(self):
        """Check that MCP endpoint requires authentication"""
        check = next(c for c in self.checks if c.name == "mcp_auth_required")

        try:
            # Try without auth
            response = requests.post(
                f"{self.deployment_url}/mcp",
                json={"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1},
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code == 403:
                check.status = "passed"
                check.message = "MCP endpoint properly secured (403 without auth)"
            else:
                check.status = "warning"
                check.message = f"Unexpected status {response.status_code} (expected 403)"
        except Exception as e:
            check.status = "failed"
            check.message = f"Auth check failed: {str(e)}"

    def check_mcp_tools_list(self):
        """Check MCP tools/list endpoint"""
        check = next(c for c in self.checks if c.name == "mcp_tools_list")

        if not self.api_key:
            check.status = "failed"
            check.message = "Cannot test - LANGSMITH_API_KEY not set"
            check.suggestions = ["Set LANGSMITH_API_KEY environment variable"]
            return

        try:
            response = requests.post(
                f"{self.deployment_url}/mcp",
                json={"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1},
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

                if len(tools) > 0:
                    check.status = "passed"
                    check.message = f"Found {len(tools)} tool(s)"
                    check.details = {"tools": [t.get("name") for t in tools]}
                else:
                    check.status = "failed"
                    check.message = "No tools returned"
                    check.suggestions = ["Check deployment configuration", "Verify agent.py is correct"]
            else:
                check.status = "failed"
                check.message = f"MCP request failed with status {response.status_code}"
        except Exception as e:
            check.status = "failed"
            check.message = f"Tools list failed: {str(e)}"

    def check_mcp_indufix_agent(self):
        """Check that indufix_agent tool is available"""
        check = next(c for c in self.checks if c.name == "mcp_indufix_agent")

        if not self.api_key:
            check.status = "failed"
            check.message = "Cannot test - LANGSMITH_API_KEY not set"
            return

        try:
            response = requests.post(
                f"{self.deployment_url}/mcp",
                json={"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1},
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
                tool_names = [t.get("name") for t in tools]

                if "indufix_agent" in tool_names:
                    check.status = "passed"
                    check.message = "indufix_agent tool is available"
                else:
                    check.status = "failed"
                    check.message = f"indufix_agent not found. Available: {', '.join(tool_names)}"
                    check.suggestions = ["Check agent.py configuration", "Verify deployment"]
            else:
                check.status = "failed"
                check.message = "Cannot check - tools/list failed"
        except Exception as e:
            check.status = "failed"
            check.message = f"Check failed: {str(e)}"

    def check_integration_query(self):
        """Check integration with a sample query"""
        check = next(c for c in self.checks if c.name == "integration_query_test")

        if not self.api_key:
            check.status = "failed"
            check.message = "Cannot test - LANGSMITH_API_KEY not set"
            return

        try:
            query = "Buscar valores default para parafuso M10"
            response = requests.post(
                f"{self.deployment_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "indufix_agent",
                        "arguments": {
                            "messages": [{"role": "user", "content": query}]
                        }
                    },
                    "id": 1
                },
                headers={
                    "Content-Type": "application/json",
                    "X-Api-Key": self.api_key,
                    "X-Tenant-Id": self.workspace_id
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("result", {}).get("content", [])
                response_text = str(content[0].get("text", "")) if content else ""

                if len(response_text) > 50:
                    check.status = "passed"
                    check.message = "Query returned valid response"
                    check.details = {"response_length": len(response_text)}
                else:
                    check.status = "failed"
                    check.message = "Response too short or empty"
                    check.suggestions = ["Check agent configuration", "Verify ANTHROPIC_API_KEY"]
            else:
                check.status = "failed"
                check.message = f"Query failed with status {response.status_code}"
        except Exception as e:
            check.status = "failed"
            check.message = f"Query test failed: {str(e)}"

    def check_tool_invocation(self):
        """Check that tools are actually being invoked"""
        check = next(c for c in self.checks if c.name == "integration_tool_invocation")

        if not self.api_key:
            check.status = "failed"
            check.message = "Cannot test - LANGSMITH_API_KEY not set"
            return

        try:
            query = "Buscar valores default para parafuso M10"
            response = requests.post(
                f"{self.deployment_url}/mcp",
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "indufix_agent",
                        "arguments": {
                            "messages": [{"role": "user", "content": query}]
                        }
                    },
                    "id": 1
                },
                headers={
                    "Content-Type": "application/json",
                    "X-Api-Key": self.api_key,
                    "X-Tenant-Id": self.workspace_id
                },
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                content = result.get("result", {}).get("content", [])
                response_text = str(content[0].get("text", "")) if content else ""

                # Check for generic responses
                generic_phrases = ["Tools are available", "generic", "template"]
                is_generic = any(phrase.lower() in response_text.lower() for phrase in generic_phrases)

                # Check for expected content
                expected_keywords = ["material", "acabamento", "aço", "default"]
                has_content = any(kw.lower() in response_text.lower() for kw in expected_keywords)

                if not is_generic and has_content:
                    check.status = "passed"
                    check.message = "Tools are being invoked properly"
                    check.details = {"has_real_content": True}
                elif is_generic:
                    check.status = "failed"
                    check.message = "Response is generic - tools NOT being invoked"
                    check.suggestions = [
                        "CRITICAL: Check ANTHROPIC_API_KEY is set in deployment",
                        "Verify GitHub Secrets are configured",
                        "Check deployment logs for errors"
                    ]
                else:
                    check.status = "warning"
                    check.message = "Response received but content unclear"
            else:
                check.status = "failed"
                check.message = "Cannot check - query failed"
        except Exception as e:
            check.status = "failed"
            check.message = f"Tool invocation check failed: {str(e)}"

    def check_config_files(self):
        """Check that required config files exist"""
        check = next(c for c in self.checks if c.name == "config_files_present")

        required_files = [
            "langgraph.json",
            "deployment/deploy_config.yaml",
            ".env.example"
        ]

        missing = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing.append(file_path)

        if not missing:
            check.status = "passed"
            check.message = f"All {len(required_files)} config files present"
        else:
            check.status = "warning"
            check.message = f"{len(missing)} config file(s) missing"
            check.details = {"missing": missing}
            check.suggestions = [f"Create or restore: {f}" for f in missing]

    def run_all_checks(self, quick: bool = False):
        """Run all validation checks"""
        self.print_header("Running Validation Checks", f"Mode: {'Quick' if quick else 'Full'}")

        if self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=self.console
            ) as progress:
                task = progress.add_task("Validating...", total=len(self.checks))

                for check in self.checks:
                    if quick and check.category == "integration":
                        check.status = "skipped"
                        check.message = "Skipped in quick mode"
                        progress.advance(task)
                        continue

                    progress.update(task, description=f"Checking: {check.description}")

                    # Run appropriate check
                    if check.name.startswith("env_"):
                        self.check_environment_variables()
                    elif check.name == "deployment_reachable":
                        self.check_deployment_reachable()
                    elif check.name == "deployment_health":
                        self.check_deployment_health()
                    elif check.name == "mcp_auth_required":
                        self.check_mcp_auth_required()
                    elif check.name == "mcp_tools_list":
                        self.check_mcp_tools_list()
                    elif check.name == "mcp_indufix_agent":
                        self.check_mcp_indufix_agent()
                    elif check.name == "integration_query_test":
                        self.check_integration_query()
                    elif check.name == "integration_tool_invocation":
                        self.check_tool_invocation()
                    elif check.name == "config_files_present":
                        self.check_config_files()

                    progress.advance(task)
        else:
            print("\nRunning checks...")
            # Run all checks without progress bar
            self.check_environment_variables()
            self.check_deployment_reachable()
            self.check_deployment_health()
            self.check_mcp_auth_required()
            self.check_mcp_tools_list()
            self.check_mcp_indufix_agent()
            if not quick:
                self.check_integration_query()
                self.check_tool_invocation()
            self.check_config_files()

    def show_results(self):
        """Display validation results"""
        self.print_header("Validation Results")

        # Group by category
        categories = {}
        for check in self.checks:
            if check.category not in categories:
                categories[check.category] = []
            categories[check.category].append(check)

        # Display by category
        for category, checks in categories.items():
            print(f"\n{category.upper()}:")
            for check in checks:
                self.print_check_result(check)

                # Show suggestions if failed
                if check.status == "failed" and check.suggestions:
                    for suggestion in check.suggestions:
                        if self.console:
                            self.console.print(f"  [dim]→ {suggestion}[/dim]")
                        else:
                            print(f"    -> {suggestion}")

    def show_summary(self):
        """Show summary statistics"""
        passed = sum(1 for c in self.checks if c.status == "passed")
        failed = sum(1 for c in self.checks if c.status == "failed")
        warning = sum(1 for c in self.checks if c.status == "warning")
        total = len([c for c in self.checks if c.status != "skipped"])

        self.print_header("Validation Summary")

        if self.console:
            table = Table(box=box.SIMPLE, show_header=False)
            table.add_column("Metric", style="bold")
            table.add_column("Count")

            table.add_row("Total Checks", str(total))
            table.add_row("Passed", f"[green]{passed}[/green]")
            table.add_row("Failed", f"[red]{failed}[/red]" if failed > 0 else "0")
            table.add_row("Warnings", f"[yellow]{warning}[/yellow]" if warning > 0 else "0")
            table.add_row("Success Rate", f"{(passed/total*100):.1f}%" if total > 0 else "N/A")

            self.console.print(table)
        else:
            print(f"\nTotal Checks: {total}")
            print(f"Passed: {passed}")
            print(f"Failed: {failed}")
            print(f"Warnings: {warning}")
            print(f"Success Rate: {(passed/total*100):.1f}%" if total > 0 else "N/A")

        # Overall status
        if failed == 0:
            if self.console:
                self.console.print("\n[bold green]✓ All checks passed![/bold green]")
            else:
                print("\n[OK] All checks passed!")
        else:
            if self.console:
                self.console.print(f"\n[bold red]✗ {failed} check(s) failed[/bold red]")
            else:
                print(f"\n[FAILED] {failed} check(s) failed")

    def save_report(self, filename: str = None):
        """Save validation report"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validation_report_{timestamp}.json"

        passed = sum(1 for c in self.checks if c.status == "passed")
        failed = sum(1 for c in self.checks if c.status == "failed")

        report = {
            "timestamp": datetime.now().isoformat(),
            "deployment_url": self.deployment_url,
            "summary": {
                "total": len(self.checks),
                "passed": passed,
                "failed": failed,
                "success_rate": (passed / len(self.checks)) * 100 if self.checks else 0
            },
            "checks": [c.to_dict() for c in self.checks]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        if self.console:
            self.console.print(f"\n[green]Report saved:[/green] {filename}")
        else:
            print(f"\nReport saved: {filename}")

        return filename


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validation CLI for Indufix LlamaIndex Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all checks
  python validate_cli.py

  # Quick validation (skip integration tests)
  python validate_cli.py --quick

  # Generate detailed report
  python validate_cli.py --report

  # Run and save report
  python validate_cli.py --report --output my_report.json
"""
    )

    parser.add_argument('--quick', action='store_true',
                       help='Quick validation (skip integration tests)')
    parser.add_argument('--report', action='store_true',
                       help='Generate and save validation report')
    parser.add_argument('--output', type=str,
                       help='Output filename for report')

    args = parser.parse_args()

    # Create and run validation
    validator = ValidationCLI()
    validator.run_all_checks(quick=args.quick)
    validator.show_results()
    validator.show_summary()

    if args.report:
        validator.save_report(args.output)

    # Exit with appropriate code
    failed = sum(1 for c in validator.checks if c.status == "failed")
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
