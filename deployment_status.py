"""Deployment Status Dashboard.

This script provides a real-time dashboard showing the current deployment status,
environment configuration, health metrics, and recent errors/warnings.

Usage:
    # Show current status
    python deployment_status.py

    # Show specific environment
    python deployment_status.py --environment prod

    # Continuous monitoring (refresh every 30s)
    python deployment_status.py --watch --interval 30

    # Save baseline for rollback
    python deployment_status.py --save-baseline

    # Verify rollback was successful
    python deployment_status.py --verify-rollback

Author: DevOps Team
Last Updated: 2026-01-23
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

try:
    import requests
except ImportError:
    print("ERROR: Missing required package")
    print("Install with: pip install requests")
    sys.exit(1)


class DeploymentStatusDashboard:
    """Displays deployment status and health information."""

    def __init__(self, environment: str = 'dev'):
        """Initialize dashboard.

        Args:
            environment: Target environment ('dev' or 'prod')
        """
        self.environment = environment
        self.api_key = None
        self.workspace_id = None
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
            print("Load from .env file or set environment variables")

    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "=" * 70)
        print(title.center(70))
        print("=" * 70)

    def print_section(self, title: str):
        """Print a formatted section header."""
        print(f"\n{title}")
        print("-" * 70)

    def get_deployment_status(self) -> Optional[Dict[str, Any]]:
        """Get current deployment status from LangSmith API.

        Returns:
            Deployment info dict or None if error
        """
        try:
            if not self.api_key or not self.workspace_id:
                print("ERROR: Missing credentials")
                return None

            headers = {'x-api-key': self.api_key}
            url = f'https://api.smith.langchain.com/api/v1/workspaces/{self.workspace_id}/deployments'

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"ERROR: API returned {response.status_code}")
                return None

            deployments = response.json()
            deployment_name = 'indufix-llamaindex-toolkit'
            deployment = next((d for d in deployments if d['name'] == deployment_name), None)

            if not deployment:
                print(f"ERROR: Deployment '{deployment_name}' not found")
                return None

            return deployment

        except requests.RequestException as e:
            print(f"ERROR: API request failed: {e}")
            return None
        except Exception as e:
            print(f"ERROR: {e}")
            return None

    def get_revision_info(self, deployment_id: str, revision_id: str) -> Optional[Dict[str, Any]]:
        """Get revision information.

        Args:
            deployment_id: Deployment ID
            revision_id: Revision ID

        Returns:
            Revision info dict or None if error
        """
        try:
            headers = {'x-api-key': self.api_key}
            url = f'https://api.smith.langchain.com/api/v1/workspaces/{self.workspace_id}/deployments/{deployment_id}/revisions/{revision_id}'

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                return None

        except Exception:
            return None

    def test_health_endpoint(self, deployment_url: str) -> Dict[str, Any]:
        """Test deployment health endpoint.

        Args:
            deployment_url: Base URL of deployment

        Returns:
            Health check results
        """
        try:
            health_url = f"{deployment_url}/ok"
            start_time = time.time()
            response = requests.get(health_url, timeout=10)
            response_time = (time.time() - start_time) * 1000

            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time_ms': response_time,
                'response': response.text[:200]
            }

        except requests.Timeout:
            return {
                'success': False,
                'error': 'Timeout (>10s)'
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }

    def test_mcp_endpoint(self, deployment_url: str) -> Dict[str, Any]:
        """Test MCP endpoint.

        Args:
            deployment_url: Base URL of deployment

        Returns:
            MCP test results
        """
        try:
            mcp_url = f"{deployment_url}/mcp"
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

            start_time = time.time()
            response = requests.post(mcp_url, json=payload, headers=headers, timeout=10)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                data = response.json()
                tools = data.get('result', {}).get('tools', [])
                return {
                    'success': True,
                    'status_code': response.status_code,
                    'response_time_ms': response_time,
                    'tool_count': len(tools),
                    'tools': [t.get('name') for t in tools]
                }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text[:200]
                }

        except requests.Timeout:
            return {
                'success': False,
                'error': 'Timeout (>10s)'
            }
        except requests.RequestException as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_environment_variables(self) -> List[str]:
        """Get configured environment variables.

        Returns:
            List of environment variable names
        """
        env_vars = []

        # Check for expected environment variables
        expected_vars = [
            'LANGSMITH_API_KEY',
            'WORKSPACE_ID',
            'LLAMA_CLOUD_API_KEY',
            'ANTHROPIC_API_KEY',
            'OPENAI_API_KEY',
            'LANGCHAIN_TRACING_V2',
            'LANGCHAIN_PROJECT',
        ]

        for var in expected_vars:
            if os.environ.get(var):
                env_vars.append(var)

        return env_vars

    def format_timestamp(self, timestamp_str: Optional[str]) -> str:
        """Format ISO timestamp to human-readable format.

        Args:
            timestamp_str: ISO format timestamp string

        Returns:
            Formatted timestamp
        """
        if not timestamp_str:
            return "N/A"

        try:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            now = datetime.now(dt.tzinfo)
            delta = now - dt

            if delta < timedelta(minutes=1):
                return f"{int(delta.total_seconds())}s ago"
            elif delta < timedelta(hours=1):
                return f"{int(delta.total_seconds() / 60)}m ago"
            elif delta < timedelta(days=1):
                return f"{int(delta.total_seconds() / 3600)}h ago"
            else:
                return f"{int(delta.days)}d ago"

        except Exception:
            return timestamp_str

    def display_status(self):
        """Display current deployment status dashboard."""
        self.print_header(f"DEPLOYMENT STATUS DASHBOARD - {self.environment.upper()}")

        # Get deployment info
        deployment = self.get_deployment_status()

        if not deployment:
            print("\n✗ Unable to retrieve deployment status")
            print("Check credentials and network connection")
            return

        # Basic deployment info
        self.print_section("DEPLOYMENT INFORMATION")
        print(f"Name:           {deployment.get('name', 'N/A')}")
        print(f"ID:             {deployment.get('id', 'N/A')}")
        print(f"Environment:    {self.environment}")
        print(f"State:          {deployment.get('state', 'N/A')}")
        print(f"Health:         {deployment.get('health', 'N/A')}")
        print(f"URL:            {deployment.get('url', 'N/A')}")

        # Revision info
        revision_id = deployment.get('latest_revision_id')
        if revision_id:
            print(f"Latest Revision: {revision_id}")

            revision = self.get_revision_info(deployment['id'], revision_id)
            if revision:
                print(f"Revision State:  {revision.get('state', 'N/A')}")
                created_at = revision.get('created_at')
                print(f"Created:         {self.format_timestamp(created_at)}")

        # Health checks
        deployment_url = deployment.get('url')
        if deployment_url:
            self.print_section("HEALTH CHECKS")

            # Test /ok endpoint
            print("Testing health endpoint...")
            health_result = self.test_health_endpoint(deployment_url)

            if health_result.get('success'):
                print(f"  ✓ Health endpoint: OK ({health_result['response_time_ms']:.2f}ms)")
            else:
                error = health_result.get('error', 'Unknown error')
                print(f"  ✗ Health endpoint: FAILED ({error})")

            # Test MCP endpoint
            print("\nTesting MCP endpoint...")
            mcp_result = self.test_mcp_endpoint(deployment_url)

            if mcp_result.get('success'):
                tool_count = mcp_result['tool_count']
                response_time = mcp_result['response_time_ms']
                print(f"  ✓ MCP endpoint: OK ({tool_count} tools, {response_time:.2f}ms)")
                if mcp_result.get('tools'):
                    print(f"\n  Available tools:")
                    for tool in mcp_result['tools']:
                        print(f"    - {tool}")
            else:
                error = mcp_result.get('error', 'Unknown error')
                print(f"  ✗ MCP endpoint: FAILED ({error})")

        # Environment variables
        self.print_section("ENVIRONMENT VARIABLES")
        env_vars = self.get_environment_variables()

        if env_vars:
            print("Configured variables (from local environment):")
            for var in env_vars:
                # Show first/last few chars only for security
                value = os.environ.get(var, '')
                if len(value) > 20:
                    masked = f"{value[:8]}...{value[-8:]}"
                else:
                    masked = "***"
                print(f"  ✓ {var}: {masked}")
        else:
            print("No environment variables detected in local environment")

        # Deployment metrics
        self.print_section("METRICS SUMMARY")

        # Calculate uptime if deployment is healthy
        if deployment.get('health') == 'healthy':
            print(f"Status:          ✓ HEALTHY")
        else:
            print(f"Status:          ✗ {deployment.get('health', 'UNKNOWN').upper()}")

        # Recent activity
        self.print_section("RECENT ACTIVITY")
        print(f"Last updated:    {self.format_timestamp(deployment.get('updated_at'))}")
        print(f"Created:         {self.format_timestamp(deployment.get('created_at'))}")

        # Quick actions
        self.print_section("QUICK ACTIONS")
        print("Monitor in LangSmith UI:")
        print(f"  https://smith.langchain.com/deployments/{deployment.get('id', '')}")
        print("\nRun validation:")
        print(f"  python post_deploy_validate.py --environment {self.environment}")
        print("\nView logs:")
        print(f"  Check LangSmith UI for deployment logs")

        print("\n" + "=" * 70)
        print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

    def save_baseline(self):
        """Save current deployment state as baseline for rollback."""
        deployment = self.get_deployment_status()

        if not deployment:
            print("ERROR: Cannot save baseline (deployment not found)")
            return False

        baseline = {
            'timestamp': datetime.utcnow().isoformat(),
            'environment': self.environment,
            'deployment_id': deployment['id'],
            'deployment_name': deployment['name'],
            'deployment_url': deployment.get('url'),
            'state': deployment.get('state'),
            'health': deployment.get('health'),
            'latest_revision_id': deployment.get('latest_revision_id'),
        }

        baseline_file = Path('rollback_baseline.json')
        with open(baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)

        self.print_header("BASELINE SAVED")
        print(f"Baseline saved to: {baseline_file.absolute()}")
        print(f"\nDeployment: {baseline['deployment_name']}")
        print(f"State: {baseline['state']}")
        print(f"Health: {baseline['health']}")
        print(f"Revision: {baseline['latest_revision_id']}")
        print(f"\nUse this baseline for rollback if needed")

        return True

    def verify_rollback(self):
        """Verify rollback was successful."""
        baseline_file = Path('rollback_baseline.json')

        if not baseline_file.exists():
            print("ERROR: No baseline file found")
            print("Run with --save-baseline to create a baseline first")
            return False

        with open(baseline_file) as f:
            baseline = json.load(f)

        current = self.get_deployment_status()

        if not current:
            print("ERROR: Cannot verify rollback (deployment not found)")
            return False

        self.print_header("ROLLBACK VERIFICATION")

        print("BASELINE (before rollback):")
        print(f"  State: {baseline.get('state')}")
        print(f"  Health: {baseline.get('health')}")
        print(f"  Revision: {baseline.get('latest_revision_id')}")

        print("\nCURRENT (after rollback):")
        print(f"  State: {current.get('state')}")
        print(f"  Health: {current.get('health')}")
        print(f"  Revision: {current.get('latest_revision_id')}")

        # Check if rollback was successful
        if current.get('state') == 'DEPLOYED' and current.get('health') == 'healthy':
            print("\n✓ Rollback verification PASSED")
            print("Deployment is healthy")
            return True
        else:
            print("\n✗ Rollback verification FAILED")
            print(f"Current state: {current.get('state')}")
            print(f"Current health: {current.get('health')}")
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Deployment status dashboard for LangSmith deployments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show current status
  python deployment_status.py

  # Show specific environment
  python deployment_status.py --environment prod

  # Continuous monitoring (refresh every 30s)
  python deployment_status.py --watch --interval 30

  # Save baseline for rollback
  python deployment_status.py --save-baseline

  # Verify rollback was successful
  python deployment_status.py --verify-rollback
        """
    )

    parser.add_argument(
        '--environment', '-e',
        choices=['dev', 'prod'],
        default='dev',
        help='Target environment (default: dev)'
    )

    parser.add_argument(
        '--watch',
        action='store_true',
        help='Continuous monitoring mode (refresh periodically)'
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='Refresh interval in seconds for watch mode (default: 30)'
    )

    parser.add_argument(
        '--save-baseline',
        action='store_true',
        help='Save current deployment state as baseline for rollback'
    )

    parser.add_argument(
        '--verify-rollback',
        action='store_true',
        help='Verify rollback was successful'
    )

    args = parser.parse_args()

    # Create dashboard
    dashboard = DeploymentStatusDashboard(environment=args.environment)

    # Handle special actions
    if args.save_baseline:
        return 0 if dashboard.save_baseline() else 1

    if args.verify_rollback:
        return 0 if dashboard.verify_rollback() else 1

    # Display status
    if args.watch:
        try:
            while True:
                # Clear screen (works on Windows and Unix)
                os.system('cls' if os.name == 'nt' else 'clear')
                dashboard.display_status()
                print(f"\nRefreshing in {args.interval}s... (Ctrl+C to stop)")
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped")
            return 0
    else:
        dashboard.display_status()
        return 0


if __name__ == '__main__':
    sys.exit(main())
