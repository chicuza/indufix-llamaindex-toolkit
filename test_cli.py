#!/usr/bin/env python3
"""Testing CLI for Indufix LlamaIndex Toolkit

Interactive interface for running tests, viewing results, and generating reports.

Usage:
    python test_cli.py                    # Interactive mode
    python test_cli.py --list            # List available tests
    python test_cli.py --all             # Run all tests
    python test_cli.py --test 1          # Run specific test
    python test_cli.py --report          # Generate HTML report
"""

import sys
import os
import argparse
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm, IntPrompt
    from rich.syntax import Syntax
    from rich.markdown import Markdown
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

import requests


class TestSuite:
    """Test suite for MCP server and agent integration"""

    # Test configurations
    TESTS = [
        {
            "id": 1,
            "name": "MCP Health Check",
            "description": "Verify deployment is accessible",
            "category": "connectivity",
            "query": None,
            "endpoint": "/ok"
        },
        {
            "id": 2,
            "name": "MCP Authentication Test",
            "description": "Verify authentication is required",
            "category": "security",
            "query": None,
            "endpoint": "/mcp",
            "expect_403": True
        },
        {
            "id": 3,
            "name": "MCP Tools List",
            "description": "List available MCP tools",
            "category": "mcp",
            "query": {"method": "tools/list", "params": {}},
            "expected_tools": ["indufix_agent"]
        },
        {
            "id": 4,
            "name": "Default Values Query",
            "description": "Get default values for fastener",
            "category": "integration",
            "query": "Buscar valores default para parafuso sextavado M10",
            "expected_keywords": ["material", "acabamento", "aço", "zincado"],
            "should_not_contain": ["Tools are available", "generic"]
        },
        {
            "id": 5,
            "name": "Standard Equivalence Query",
            "description": "Query standard equivalences",
            "category": "integration",
            "query": "Qual a equivalência da norma DIN 933?",
            "expected_keywords": ["ISO", "4017", "equivalente"],
            "should_not_contain": ["Tools are available"]
        },
        {
            "id": 6,
            "name": "Confidence Penalty Query",
            "description": "Query confidence penalties",
            "category": "integration",
            "query": "Qual a penalidade para material inferido como aço carbono?",
            "expected_keywords": ["penalidade", "confiança", "penalty"],
            "should_not_contain": ["Tools are available"]
        },
        {
            "id": 7,
            "name": "Complex Multi-Attribute Query",
            "description": "Complex query with multiple attributes",
            "category": "integration",
            "query": "Para parafuso sextavado M12 faltam material, acabamento e classe. Me dê valores default e penalidades.",
            "expected_keywords": ["material", "acabamento", "classe", "default"],
            "should_not_contain": ["Tools are available"]
        }
    ]

    def __init__(self, deployment_url: str = None, api_key: str = None, workspace_id: str = None):
        self.console = Console() if RICH_AVAILABLE else None
        self.deployment_url = deployment_url or os.getenv(
            "MCP_DEPLOYMENT_URL",
            "https://ndufix-llamaindex-toolkit-m-554ed4cdc4ff5631b895423bc5000927.us.langgraph.app"
        )
        self.api_key = api_key or os.getenv("LANGSMITH_API_KEY")
        self.workspace_id = workspace_id or os.getenv("LANGSMITH_WORKSPACE_ID", "950d802b-125a-45bc-88e4-3d7d0edee182")
        self.results = []

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

    def print_test_info(self, test: Dict):
        """Print test information"""
        if self.console:
            self.console.print(f"\n[bold]Test #{test['id']}: {test['name']}[/bold]")
            self.console.print(f"[dim]{test['description']}[/dim]")
            self.console.print(f"Category: [cyan]{test['category']}[/cyan]")
        else:
            print(f"\nTest #{test['id']}: {test['name']}")
            print(f"Description: {test['description']}")
            print(f"Category: {test['category']}")

    def list_tests(self):
        """List all available tests"""
        self.print_header("Available Tests", f"Total: {len(self.TESTS)} tests")

        if self.console:
            table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
            table.add_column("ID", justify="center", style="cyan", width=6)
            table.add_column("Name", style="green", width=30)
            table.add_column("Description", width=35)
            table.add_column("Category", justify="center", width=15)

            for test in self.TESTS:
                table.add_row(
                    str(test['id']),
                    test['name'],
                    test['description'],
                    test['category']
                )

            self.console.print(table)
        else:
            print("\nID | Name                          | Description                        | Category")
            print("-" * 100)
            for test in self.TESTS:
                print(f"{test['id']:2} | {test['name']:29} | {test['description']:35} | {test['category']}")

    def run_health_check(self, test: Dict) -> Dict[str, Any]:
        """Test 1: Health check"""
        self.print_test_info(test)

        try:
            response = requests.get(f"{self.deployment_url}/ok", timeout=10)

            success = response.status_code == 200
            return {
                "test_id": test['id'],
                "success": success,
                "status_code": response.status_code,
                "response": response.text,
                "message": "Deployment is healthy" if success else f"Unexpected status: {response.status_code}"
            }
        except Exception as e:
            return {
                "test_id": test['id'],
                "success": False,
                "error": str(e),
                "message": f"Failed to connect: {e}"
            }

    def run_auth_test(self, test: Dict) -> Dict[str, Any]:
        """Test 2: Authentication requirement"""
        self.print_test_info(test)

        try:
            # Try without auth
            response = requests.post(
                f"{self.deployment_url}/mcp",
                json={"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1},
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            # Should get 403
            success = response.status_code == 403
            return {
                "test_id": test['id'],
                "success": success,
                "status_code": response.status_code,
                "message": "Authentication properly required" if success else f"Got {response.status_code} instead of 403"
            }
        except Exception as e:
            return {
                "test_id": test['id'],
                "success": False,
                "error": str(e),
                "message": f"Request failed: {e}"
            }

    def run_tools_list(self, test: Dict) -> Dict[str, Any]:
        """Test 3: List MCP tools"""
        self.print_test_info(test)

        if not self.api_key:
            return {
                "test_id": test['id'],
                "success": False,
                "error": "LANGSMITH_API_KEY not set",
                "message": "Set LANGSMITH_API_KEY environment variable"
            }

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

            if response.status_code != 200:
                return {
                    "test_id": test['id'],
                    "success": False,
                    "status_code": response.status_code,
                    "message": f"Request failed with status {response.status_code}"
                }

            result = response.json()
            tools = result.get("result", {}).get("tools", [])
            tool_names = [t.get("name") for t in tools]

            # Check expected tools
            expected = test.get("expected_tools", [])
            found_all = all(name in tool_names for name in expected)

            return {
                "test_id": test['id'],
                "success": found_all and len(tools) > 0,
                "tools_found": tools,
                "tool_names": tool_names,
                "message": f"Found {len(tools)} tool(s): {', '.join(tool_names)}"
            }
        except Exception as e:
            return {
                "test_id": test['id'],
                "success": False,
                "error": str(e),
                "message": f"Request failed: {e}"
            }

    def run_query_test(self, test: Dict) -> Dict[str, Any]:
        """Run a query test"""
        self.print_test_info(test)

        if not self.api_key:
            return {
                "test_id": test['id'],
                "success": False,
                "error": "LANGSMITH_API_KEY not set",
                "message": "Set LANGSMITH_API_KEY environment variable"
            }

        try:
            call_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "indufix_agent",
                    "arguments": {
                        "messages": [{"role": "user", "content": test['query']}]
                    }
                },
                "id": test['id']
            }

            response = requests.post(
                f"{self.deployment_url}/mcp",
                json=call_request,
                headers={
                    "Content-Type": "application/json",
                    "X-Api-Key": self.api_key,
                    "X-Tenant-Id": self.workspace_id
                },
                timeout=60
            )

            if response.status_code != 200:
                return {
                    "test_id": test['id'],
                    "success": False,
                    "status_code": response.status_code,
                    "message": f"Request failed with status {response.status_code}"
                }

            result = response.json()
            content = result.get("result", {}).get("content", [])
            response_text = str(content[0].get("text", "")) if content else str(result)

            # Validate response
            validations = {}

            # Check for expected keywords
            expected_keywords = test.get("expected_keywords", [])
            keywords_found = [kw for kw in expected_keywords if kw.lower() in response_text.lower()]
            validations["has_keywords"] = len(keywords_found) >= 1

            # Check for unwanted content
            should_not_contain = test.get("should_not_contain", [])
            validations["no_generic"] = not any(bad.lower() in response_text.lower() for bad in should_not_contain)

            # Check response length
            validations["adequate_length"] = len(response_text) > 50

            success = all(validations.values())

            return {
                "test_id": test['id'],
                "success": success,
                "query": test['query'],
                "response": response_text,
                "validations": validations,
                "keywords_found": keywords_found,
                "keywords_expected": expected_keywords,
                "message": f"{'Passed' if success else 'Failed'} - {len(keywords_found)}/{len(expected_keywords)} keywords found"
            }
        except Exception as e:
            return {
                "test_id": test['id'],
                "success": False,
                "error": str(e),
                "message": f"Request failed: {e}"
            }

    def run_test(self, test: Dict) -> Dict[str, Any]:
        """Run a single test"""
        if test['category'] == 'connectivity':
            return self.run_health_check(test)
        elif test['category'] == 'security':
            return self.run_auth_test(test)
        elif test['category'] == 'mcp':
            return self.run_tools_list(test)
        elif test['category'] == 'integration':
            return self.run_query_test(test)
        else:
            return {"test_id": test['id'], "success": False, "message": "Unknown test category"}

    def display_result(self, result: Dict[str, Any]):
        """Display test result"""
        if self.console:
            if result['success']:
                self.console.print(f"[green]✓ PASSED[/green] - {result['message']}")
            else:
                self.console.print(f"[red]✗ FAILED[/red] - {result['message']}")

            # Show response preview for query tests
            if 'response' in result and result.get('response'):
                preview = result['response'][:300] + "..." if len(result['response']) > 300 else result['response']
                self.console.print(f"\n[dim]Response preview:[/dim]\n{preview}\n")
        else:
            status = "PASSED" if result['success'] else "FAILED"
            print(f"[{status}] {result['message']}")
            if 'response' in result:
                print(f"Response: {result['response'][:200]}...")

    def run_all_tests(self):
        """Run all tests"""
        self.print_header("Running All Tests", f"{len(self.TESTS)} tests to execute")

        if self.console:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console
            ) as progress:
                task = progress.add_task("Running tests...", total=len(self.TESTS))

                for test in self.TESTS:
                    progress.update(task, description=f"Running: {test['name']}")
                    result = self.run_test(test)
                    self.results.append(result)
                    progress.advance(task)
        else:
            for i, test in enumerate(self.TESTS, 1):
                print(f"\n[{i}/{len(self.TESTS)}] Running: {test['name']}")
                result = self.run_test(test)
                self.results.append(result)
                self.display_result(result)

    def show_summary(self):
        """Show test summary"""
        if not self.results:
            print("No test results to display")
            return

        passed = sum(1 for r in self.results if r.get('success'))
        failed = len(self.results) - passed
        success_rate = (passed / len(self.results)) * 100

        self.print_header("Test Summary", f"{passed}/{len(self.results)} tests passed")

        if self.console:
            table = Table(box=box.ROUNDED, show_header=True, header_style="bold magenta")
            table.add_column("Test", style="cyan", width=35)
            table.add_column("Result", justify="center", width=12)
            table.add_column("Message", width=45)

            for result in self.results:
                test = next(t for t in self.TESTS if t['id'] == result['test_id'])
                status = "[green]✓ PASSED[/green]" if result['success'] else "[red]✗ FAILED[/red]"
                table.add_row(test['name'], status, result['message'])

            self.console.print(table)

            # Summary stats
            stats_table = Table(box=box.SIMPLE, show_header=False)
            stats_table.add_column("Metric", style="bold")
            stats_table.add_column("Value")
            stats_table.add_row("Total Tests", str(len(self.results)))
            stats_table.add_row("Passed", f"[green]{passed}[/green]")
            stats_table.add_row("Failed", f"[red]{failed}[/red]" if failed > 0 else "0")
            stats_table.add_row("Success Rate", f"{success_rate:.1f}%")

            self.console.print("\n")
            self.console.print(stats_table)
        else:
            print("\nTest Results:")
            for result in self.results:
                test = next(t for t in self.TESTS if t['id'] == result['test_id'])
                status = "PASSED" if result['success'] else "FAILED"
                print(f"  [{status}] {test['name']}: {result['message']}")

            print(f"\nTotal: {len(self.results)} | Passed: {passed} | Failed: {failed} | Success Rate: {success_rate:.1f}%")

    def save_report(self, filename: str = None):
        """Save test results to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "deployment_url": self.deployment_url,
            "workspace_id": self.workspace_id,
            "total_tests": len(self.results),
            "passed": sum(1 for r in self.results if r.get('success')),
            "failed": sum(1 for r in self.results if not r.get('success')),
            "tests": self.results
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        if self.console:
            self.console.print(f"\n[green]Report saved:[/green] {filename}")
        else:
            print(f"\nReport saved: {filename}")

        return filename

    def interactive_mode(self):
        """Interactive test selection"""
        while True:
            self.print_header("Interactive Test Mode")

            print("\nOptions:")
            print("  1. List all tests")
            print("  2. Run all tests")
            print("  3. Run specific test")
            print("  4. Run by category")
            print("  5. Show last results")
            print("  6. Save report")
            print("  0. Exit")

            if self.console:
                choice = IntPrompt.ask("\nSelect option", default=0)
            else:
                choice = int(input("\nSelect option [0]: ") or "0")

            if choice == 0:
                break
            elif choice == 1:
                self.list_tests()
            elif choice == 2:
                self.run_all_tests()
                self.show_summary()
            elif choice == 3:
                self.list_tests()
                test_id = IntPrompt.ask("\nEnter test ID") if self.console else int(input("\nEnter test ID: "))
                test = next((t for t in self.TESTS if t['id'] == test_id), None)
                if test:
                    result = self.run_test(test)
                    self.results.append(result)
                    self.display_result(result)
                else:
                    print("Invalid test ID")
            elif choice == 4:
                categories = set(t['category'] for t in self.TESTS)
                print("\nCategories:")
                for cat in categories:
                    print(f"  - {cat}")
                category = input("\nEnter category: ").strip()
                tests = [t for t in self.TESTS if t['category'] == category]
                if tests:
                    for test in tests:
                        result = self.run_test(test)
                        self.results.append(result)
                else:
                    print("No tests found for that category")
            elif choice == 5:
                if self.results:
                    self.show_summary()
                else:
                    print("No results yet. Run some tests first!")
            elif choice == 6:
                if self.results:
                    self.save_report()
                else:
                    print("No results to save. Run tests first!")

            input("\nPress Enter to continue...")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Testing CLI for Indufix LlamaIndex Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python test_cli.py

  # List available tests
  python test_cli.py --list

  # Run all tests
  python test_cli.py --all

  # Run specific test
  python test_cli.py --test 4

  # Run and save report
  python test_cli.py --all --report

  # Specify deployment URL
  python test_cli.py --all --url https://custom-url.app
"""
    )

    parser.add_argument('--list', action='store_true',
                       help='List available tests')
    parser.add_argument('--all', action='store_true',
                       help='Run all tests')
    parser.add_argument('--test', type=int, metavar='ID',
                       help='Run specific test by ID')
    parser.add_argument('--report', action='store_true',
                       help='Generate and save test report')
    parser.add_argument('--url', type=str,
                       help='Deployment URL (default: from env or hardcoded)')
    parser.add_argument('--api-key', type=str,
                       help='LangSmith API key (default: from env)')

    args = parser.parse_args()

    # Create test suite
    suite = TestSuite(deployment_url=args.url, api_key=args.api_key)

    # Execute based on arguments
    if args.list:
        suite.list_tests()
    elif args.all:
        suite.run_all_tests()
        suite.show_summary()
        if args.report:
            suite.save_report()
    elif args.test:
        test = next((t for t in suite.TESTS if t['id'] == args.test), None)
        if test:
            result = suite.run_test(test)
            suite.results.append(result)
            suite.display_result(result)
            suite.show_summary()
        else:
            print(f"Error: Test {args.test} not found")
            return 1
    else:
        # Interactive mode
        suite.interactive_mode()

    return 0


if __name__ == "__main__":
    sys.exit(main())
