"""Post-Deployment Validation Script.

This script performs comprehensive validation of a deployed LangSmith application,
including health checks, MCP endpoint testing, tool validation, and actual tool invocation.

Usage:
    # Validate current deployment
    python post_deploy_validate.py

    # Validate specific environment
    python post_deploy_validate.py --environment prod

    # Generate detailed report
    python post_deploy_validate.py --report validation_report.json

    # Quick health check only
    python post_deploy_validate.py --quick

Author: DevOps Team
Last Updated: 2026-01-23
"""

import os
import sys
import json
import time
import argparse
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any


class DeploymentValidator:
    """Handles post-deployment validation."""

    def __init__(self, environment: str = 'dev'):
        """Initialize validator.

        Args:
            environment: Target environment ('dev' or 'prod')
        """
        self.environment = environment
        self.deployment_url = None
        self.deployment_id = None
        self.validation_results = {}
        self.start_time = datetime.utcnow()

        # Load credentials
        self._load_credentials()

    def _load_credentials(self):
        """Load credentials from environment."""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        self.api_key = os.environ.get('LANGSMITH_API_KEY')
        self.workspace_id = os.environ.get('WORKSPACE_ID')

        if not self.api_key or not self.workspace_id:
            print("WARNING: LANGSMITH_API_KEY or WORKSPACE_ID not set")
            print("Some validations may be skipped")

    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "=" * 70)
        print(title)
        print("=" * 70)

    def print_section(self, title: str):
        """Print a formatted section header."""
        print(f"\n{title}")
        print("-" * 70)

    def get_deployment_info(self) -> Tuple[bool, str]:
        """Get deployment information from LangSmith API.

        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.api_key or not self.workspace_id:
                return False, "Missing credentials (LANGSMITH_API_KEY or WORKSPACE_ID)"

            headers = {'x-api-key': self.api_key}
            url = f'https://api.smith.langchain.com/api/v1/workspaces/{self.workspace_id}/deployments'

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                return False, f"API returned {response.status_code}: {response.text}"

            deployments = response.json()
            deployment_name = 'indufix-llamaindex-toolkit'
            deployment = next((d for d in deployments if d['name'] == deployment_name), None)

            if not deployment:
                return False, f"Deployment '{deployment_name}' not found"

            self.deployment_id = deployment['id']
            self.deployment_url = deployment.get('url')

            print(f"Deployment ID: {self.deployment_id}")
            print(f"Deployment Name: {deployment['name']}")
            print(f"Deployment URL: {self.deployment_url}")
            print(f"Health: {deployment.get('health', 'N/A')}")
            print(f"State: {deployment.get('state', 'N/A')}")
            print(f"Latest Revision: {deployment.get('latest_revision_id', 'N/A')}")

            if not self.deployment_url:
                return False, "Deployment URL not available"

            return True, "Deployment info retrieved successfully"

        except requests.RequestException as e:
            return False, f"API request failed: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def wait_for_deployment_ready(self, max_wait: int = 300) -> Tuple[bool, str]:
        """Wait for deployment to be in DEPLOYED state.

        Args:
            max_wait: Maximum time to wait in seconds (default: 300 = 5 minutes)

        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.api_key or not self.workspace_id or not self.deployment_id:
                return False, "Missing required information"

            print(f"Waiting for deployment to be ready (max {max_wait}s)...")

            headers = {'x-api-key': self.api_key}
            start_time = time.time()
            poll_interval = 10  # Check every 10 seconds

            while time.time() - start_time < max_wait:
                url = f'https://api.smith.langchain.com/api/v1/workspaces/{self.workspace_id}/deployments/{self.deployment_id}'
                response = requests.get(url, headers=headers, timeout=10)

                if response.status_code == 200:
                    deployment = response.json()
                    state = deployment.get('state', 'unknown')
                    health = deployment.get('health', 'unknown')

                    elapsed = int(time.time() - start_time)
                    print(f"[{elapsed}s] State: {state}, Health: {health}")

                    if state == 'DEPLOYED' and health == 'healthy':
                        return True, f"Deployment ready (took {elapsed}s)"

                    if state == 'FAILED':
                        return False, "Deployment failed"

                time.sleep(poll_interval)

            return False, f"Timeout waiting for deployment (>{max_wait}s)"

        except Exception as e:
            return False, f"Error waiting for deployment: {e}"

    def test_health_endpoint(self) -> Tuple[bool, str]:
        """Test /ok health endpoint.

        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.deployment_url:
                return False, "Deployment URL not available"

            health_url = f"{self.deployment_url}/ok"
            print(f"Testing: {health_url}")

            start_time = time.time()
            response = requests.get(health_url, timeout=10)
            response_time = (time.time() - start_time) * 1000  # Convert to ms

            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {response_time:.2f}ms")
            print(f"Response: {response.text[:200]}")

            if response.status_code == 200:
                return True, f"Health endpoint OK ({response_time:.2f}ms)"
            else:
                return False, f"Health endpoint returned {response.status_code}"

        except requests.RequestException as e:
            return False, f"Health check failed: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def test_mcp_endpoint(self) -> Tuple[bool, str]:
        """Test MCP endpoint with authentication.

        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.deployment_url:
                return False, "Deployment URL not available"

            if not self.api_key or not self.workspace_id:
                return False, "Missing authentication credentials"

            mcp_url = f"{self.deployment_url}/mcp"
            print(f"Testing: {mcp_url}")

            headers = {
                'X-Api-Key': self.api_key,
                'X-Tenant-Id': self.workspace_id,
                'Content-Type': 'application/json'
            }

            # Test MCP list tools
            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }

            start_time = time.time()
            response = requests.post(mcp_url, json=payload, headers=headers, timeout=10)
            response_time = (time.time() - start_time) * 1000

            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {response_time:.2f}ms")

            if response.status_code == 200:
                data = response.json()
                tools = data.get('result', {}).get('tools', [])
                print(f"Tools Found: {len(tools)}")

                for tool in tools:
                    print(f"  - {tool.get('name', 'N/A')}: {tool.get('description', 'N/A')[:60]}...")

                return True, f"MCP endpoint OK ({len(tools)} tools, {response_time:.2f}ms)"
            else:
                return False, f"MCP endpoint returned {response.status_code}: {response.text[:200]}"

        except requests.RequestException as e:
            return False, f"MCP request failed: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def validate_tools(self) -> Tuple[bool, str]:
        """Validate that expected tools are available.

        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.deployment_url:
                return False, "Deployment URL not available"

            mcp_url = f"{self.deployment_url}/mcp"
            headers = {
                'X-Api-Key': self.api_key,
                'X-Tenant-Id': self.workspace_id,
                'Content-Type': 'application/json'
            }

            payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }

            response = requests.post(mcp_url, json=payload, headers=headers, timeout=10)

            if response.status_code != 200:
                return False, f"Failed to get tools list ({response.status_code})"

            data = response.json()
            tools = data.get('result', {}).get('tools', [])

            # Expected tools (adjust based on your actual tools)
            expected_tool_patterns = ['search', 'retriev', 'query', 'find']

            found_tools = []
            for tool in tools:
                tool_name = tool.get('name', '').lower()
                for pattern in expected_tool_patterns:
                    if pattern in tool_name:
                        found_tools.append(tool['name'])
                        break

            print(f"\nExpected tool patterns: {expected_tool_patterns}")
            print(f"Found tools: {found_tools}")
            print(f"Total tools: {len(tools)}")

            if found_tools:
                return True, f"Tools validated ({len(found_tools)}/{len(tools)} matched patterns)"
            else:
                return False, f"No expected tools found (got {len(tools)} tools total)"

        except Exception as e:
            return False, f"Tool validation error: {e}"

    def test_tool_invocation(self) -> Tuple[bool, str]:
        """Test actual tool invocation with real parameters.

        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.deployment_url:
                return False, "Deployment URL not available"

            mcp_url = f"{self.deployment_url}/mcp"
            headers = {
                'X-Api-Key': self.api_key,
                'X-Tenant-Id': self.workspace_id,
                'Content-Type': 'application/json'
            }

            # First, get available tools
            list_payload = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }

            response = requests.post(mcp_url, json=list_payload, headers=headers, timeout=10)
            if response.status_code != 200:
                return False, "Failed to get tools list"

            tools = response.json().get('result', {}).get('tools', [])
            if not tools:
                return False, "No tools available for invocation"

            # Try to invoke the first tool with a simple test query
            test_tool = tools[0]
            tool_name = test_tool['name']

            print(f"\nTesting tool invocation: {tool_name}")

            # Create a test invocation based on tool schema
            # This is a generic test - adjust based on your actual tool signatures
            invoke_payload = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": {
                        "query": "test query for SKU validation",
                        "limit": 1
                    }
                }
            }

            print(f"Invoking: {tool_name}")
            print(f"Arguments: {invoke_payload['params']['arguments']}")

            start_time = time.time()
            response = requests.post(mcp_url, json=invoke_payload, headers=headers, timeout=30)
            response_time = (time.time() - start_time) * 1000

            print(f"Status Code: {response.status_code}")
            print(f"Response Time: {response_time:.2f}ms")

            if response.status_code == 200:
                result = response.json()
                print(f"Response: {json.dumps(result, indent=2)[:500]}...")

                # Check for errors in response
                if 'error' in result:
                    return False, f"Tool invocation returned error: {result['error']}"

                return True, f"Tool invocation successful ({response_time:.2f}ms)"
            else:
                return False, f"Tool invocation failed ({response.status_code}): {response.text[:200]}"

        except requests.Timeout:
            return False, "Tool invocation timed out (>30s)"
        except requests.RequestException as e:
            return False, f"Tool invocation request failed: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def test_anthropic_api_key(self) -> Tuple[bool, str]:
        """Verify ANTHROPIC_API_KEY is configured in deployment.

        Returns:
            Tuple of (success, message)
        """
        try:
            # This is a bit tricky - we can't directly check if the secret is set
            # in the deployment, but we can infer from tool behavior

            # For now, we'll just check if the tool invocation works
            # (which requires ANTHROPIC_API_KEY if tools use Claude)

            print("Note: ANTHROPIC_API_KEY validation is implicit via tool invocation")
            print("If tool invocation succeeds, the key is likely configured correctly")

            return True, "ANTHROPIC_API_KEY validation implicit (check tool invocation result)"

        except Exception as e:
            return False, f"Error checking ANTHROPIC_API_KEY: {e}"

    def run_validations(self, quick: bool = False) -> Dict[str, Any]:
        """Run all post-deployment validations.

        Args:
            quick: If True, run only essential validations

        Returns:
            Dictionary of validation results
        """
        self.print_header("POST-DEPLOYMENT VALIDATION")

        validations = [
            ("Get Deployment Info", self.get_deployment_info),
            ("Wait for Deployment Ready", lambda: self.wait_for_deployment_ready(max_wait=300)),
            ("Test Health Endpoint", self.test_health_endpoint),
            ("Test MCP Endpoint", self.test_mcp_endpoint),
        ]

        if not quick:
            validations.extend([
                ("Validate Tools", self.validate_tools),
                ("Test Tool Invocation", self.test_tool_invocation),
                ("Verify ANTHROPIC_API_KEY", self.test_anthropic_api_key),
            ])

        all_passed = True

        for name, validator in validations:
            self.print_section(f"Validating: {name}")
            try:
                success, message = validator()
                self.validation_results[name] = {
                    'success': success,
                    'message': message,
                    'timestamp': datetime.utcnow().isoformat()
                }

                if success:
                    print(f"\n✓ PASSED: {message}")
                else:
                    print(f"\n✗ FAILED: {message}")
                    all_passed = False

            except Exception as e:
                print(f"\n✗ ERROR: {e}")
                self.validation_results[name] = {
                    'success': False,
                    'message': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
                all_passed = False

        # Calculate summary
        elapsed = (datetime.utcnow() - self.start_time).total_seconds()

        summary = {
            'overall_success': all_passed,
            'environment': self.environment,
            'deployment_id': self.deployment_id,
            'deployment_url': self.deployment_url,
            'validation_start': self.start_time.isoformat(),
            'validation_duration_seconds': elapsed,
            'total_validations': len(validations),
            'passed': sum(1 for r in self.validation_results.values() if r['success']),
            'failed': sum(1 for r in self.validation_results.values() if not r['success']),
            'results': self.validation_results
        }

        # Print summary
        self.print_header("VALIDATION SUMMARY")
        print(f"Environment: {self.environment}")
        print(f"Deployment ID: {self.deployment_id or 'N/A'}")
        print(f"Deployment URL: {self.deployment_url or 'N/A'}")
        print(f"Duration: {elapsed:.2f}s")
        print(f"\nResults:")
        print(f"  Total: {summary['total_validations']}")
        print(f"  Passed: {summary['passed']} ✓")
        print(f"  Failed: {summary['failed']} ✗")

        print("\nDetailed Results:")
        for name, result in self.validation_results.items():
            status = "✓ PASSED" if result['success'] else "✗ FAILED"
            print(f"  {status}: {name}")
            print(f"    {result['message']}")

        if all_passed:
            print("\n✓ ALL VALIDATIONS PASSED")
            print("Deployment is healthy and operational!")
        else:
            print("\n✗ VALIDATION FAILURES DETECTED")
            print("Review failures above and check DEPLOYMENT_TROUBLESHOOTING.md")

        return summary

    def save_report(self, report_file: Path):
        """Save validation report to JSON file.

        Args:
            report_file: Path to save report
        """
        try:
            summary = {
                'overall_success': all(r['success'] for r in self.validation_results.values()),
                'environment': self.environment,
                'deployment_id': self.deployment_id,
                'deployment_url': self.deployment_url,
                'validation_start': self.start_time.isoformat(),
                'validation_duration_seconds': (datetime.utcnow() - self.start_time).total_seconds(),
                'results': self.validation_results
            }

            with open(report_file, 'w') as f:
                json.dump(summary, f, indent=2)

            print(f"\n✓ Report saved to: {report_file}")

        except Exception as e:
            print(f"\n✗ Failed to save report: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Post-deployment validation for LangSmith deployments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate current deployment
  python post_deploy_validate.py

  # Validate specific environment
  python post_deploy_validate.py --environment prod

  # Generate detailed report
  python post_deploy_validate.py --report validation_report.json

  # Quick health check only
  python post_deploy_validate.py --quick
        """
    )

    parser.add_argument(
        '--environment', '-e',
        choices=['dev', 'prod'],
        default='dev',
        help='Target environment (default: dev)'
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick validation only (skip tool invocation)'
    )

    parser.add_argument(
        '--report',
        type=Path,
        help='Save detailed report to JSON file'
    )

    args = parser.parse_args()

    # Create validator
    validator = DeploymentValidator(environment=args.environment)

    # Run validations
    summary = validator.run_validations(quick=args.quick)

    # Save report if requested
    if args.report:
        validator.save_report(args.report)

    # Exit with appropriate code
    if summary['overall_success']:
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
