#!/usr/bin/env python3
"""Deployment Environment Verification Script

This script verifies that all required environment variables are correctly
set in the deployed LangGraph application on LangSmith Cloud.

Usage:
    # Check deployment environment
    python verify_deployment_env.py --deployment-url https://your-deployment.us.langgraph.app

    # Check with custom API key
    python verify_deployment_env.py --deployment-url https://your-deployment.us.langgraph.app --api-key YOUR_KEY

    # Verbose mode
    python verify_deployment_env.py --deployment-url https://your-deployment.us.langgraph.app -v
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("ERROR: requests module not found. Install with: pip install requests")
    sys.exit(1)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Required environment variables for deployment
REQUIRED_ENV_VARS = {
    'ANTHROPIC_API_KEY': 'Required for Claude LLM integration',
    'LLAMA_CLOUD_API_KEY': 'Required for LlamaIndex toolkit',
}

RECOMMENDED_ENV_VARS = {
    'LANGSMITH_API_KEY': 'Enables LangSmith tracing and observability',
    'LANGCHAIN_TRACING_V2': 'Enables LangChain tracing (should be "true")',
    'LANGCHAIN_PROJECT': 'LangSmith project name for organizing traces',
    'LANGCHAIN_ENDPOINT': 'LangSmith API endpoint',
}

OPTIONAL_ENV_VARS = {
    'OPENAI_API_KEY': 'Optional OpenAI API key for GPT models',
    'LANGCHAIN_API_KEY': 'Alternative to LANGSMITH_API_KEY',
}


class DeploymentVerifier:
    """Verifies deployment configuration and environment variables."""

    def __init__(self, deployment_url: str, api_key: Optional[str] = None):
        """Initialize verifier.

        Args:
            deployment_url: Base URL of deployed application
            api_key: Optional API key for authentication
        """
        self.deployment_url = deployment_url.rstrip('/')
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        self.session = requests.Session()

        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })

    def check_health(self) -> Tuple[bool, str]:
        """Check deployment health endpoint.

        Returns:
            Tuple of (success, message)
        """
        logger.info("Checking deployment health...")

        health_url = urljoin(self.deployment_url, '/ok')

        try:
            response = self.session.get(health_url, timeout=10)

            if response.status_code == 200:
                logger.info("Health check: PASSED")
                return True, "Deployment is healthy"
            else:
                logger.warning(f"Health check: FAILED (status {response.status_code})")
                return False, f"Health endpoint returned status {response.status_code}"

        except requests.exceptions.RequestException as e:
            logger.error(f"Health check: FAILED ({e})")
            return False, f"Health check failed: {e}"

    def check_info_endpoint(self) -> Tuple[bool, Optional[Dict]]:
        """Check deployment info endpoint.

        Returns:
            Tuple of (success, info_data)
        """
        logger.info("Checking deployment info endpoint...")

        info_url = urljoin(self.deployment_url, '/info')

        try:
            response = self.session.get(info_url, timeout=10)

            if response.status_code == 200:
                info_data = response.json()
                logger.info("Info endpoint: ACCESSIBLE")
                return True, info_data
            else:
                logger.warning(f"Info endpoint: FAILED (status {response.status_code})")
                return False, None

        except requests.exceptions.RequestException as e:
            logger.error(f"Info endpoint: FAILED ({e})")
            return False, None
        except json.JSONDecodeError as e:
            logger.error(f"Info endpoint: Invalid JSON ({e})")
            return False, None

    def test_mcp_tools(self) -> Tuple[bool, Optional[List[str]]]:
        """Test MCP (Model Context Protocol) tools endpoint.

        Returns:
            Tuple of (success, list of tool names)
        """
        logger.info("Testing MCP tools endpoint...")

        # Try to invoke the graph to list tools
        invoke_url = urljoin(self.deployment_url, '/runs/stream')

        try:
            # Create a simple test request
            payload = {
                "input": {
                    "messages": [
                        {
                            "role": "user",
                            "content": "What tools do you have available?"
                        }
                    ]
                },
                "config": {},
                "stream_mode": ["values"]
            }

            response = self.session.post(
                invoke_url,
                json=payload,
                timeout=30,
                stream=True
            )

            if response.status_code == 200:
                logger.info("MCP endpoint: ACCESSIBLE")
                # Parse streaming response
                tools_found = []
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8').replace('data: ', ''))
                            # Look for tool information in response
                            if 'tool' in str(data).lower():
                                tools_found.append("Tool detected in response")
                        except:
                            continue

                return True, tools_found if tools_found else ["Response received"]
            else:
                logger.warning(f"MCP endpoint: FAILED (status {response.status_code})")
                return False, None

        except requests.exceptions.RequestException as e:
            logger.error(f"MCP endpoint: FAILED ({e})")
            return False, None

    def verify_environment_variables(self) -> Dict[str, Dict[str, bool]]:
        """Verify environment variables through indirect testing.

        Note: Direct env var access is not available in deployment,
        so we verify through functionality testing.

        Returns:
            Dictionary with verification results
        """
        logger.info("Verifying environment variables through functionality...")

        results = {
            'required': {},
            'recommended': {},
            'optional': {}
        }

        # We can't directly check env vars in deployment,
        # but we can infer from functionality

        # Test 1: Health check (basic functionality)
        health_ok, _ = self.check_health()

        # Test 2: Info endpoint (deployment info)
        info_ok, info_data = self.check_info_endpoint()

        # Test 3: MCP tools (ANTHROPIC_API_KEY and LLAMA_CLOUD_API_KEY needed)
        mcp_ok, tools = self.test_mcp_tools()

        # Infer environment variable status
        if mcp_ok and health_ok:
            results['required']['ANTHROPIC_API_KEY'] = True
            results['required']['LLAMA_CLOUD_API_KEY'] = True
        else:
            results['required']['ANTHROPIC_API_KEY'] = False
            results['required']['LLAMA_CLOUD_API_KEY'] = False

        # We can't verify tracing vars directly, mark as unknown
        results['recommended']['LANGSMITH_API_KEY'] = None  # Unknown
        results['recommended']['LANGCHAIN_TRACING_V2'] = None  # Unknown
        results['recommended']['LANGCHAIN_PROJECT'] = None  # Unknown
        results['recommended']['LANGCHAIN_ENDPOINT'] = None  # Unknown

        results['optional']['OPENAI_API_KEY'] = None  # Unknown
        results['optional']['LANGCHAIN_API_KEY'] = None  # Unknown

        return results

    def generate_report(self) -> str:
        """Generate comprehensive verification report.

        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 70)
        report.append("DEPLOYMENT ENVIRONMENT VERIFICATION REPORT")
        report.append("=" * 70)
        report.append(f"Deployment URL: {self.deployment_url}")
        report.append("")

        # Health check
        report.append("1. HEALTH CHECK")
        report.append("-" * 70)
        health_ok, health_msg = self.check_health()
        report.append(f"   Status: {'PASS' if health_ok else 'FAIL'}")
        report.append(f"   Message: {health_msg}")
        report.append("")

        # Info endpoint
        report.append("2. INFO ENDPOINT")
        report.append("-" * 70)
        info_ok, info_data = self.check_info_endpoint()
        report.append(f"   Status: {'PASS' if info_ok else 'FAIL'}")
        if info_data:
            report.append(f"   Data: {json.dumps(info_data, indent=2)}")
        report.append("")

        # MCP tools
        report.append("3. MCP TOOLS ENDPOINT")
        report.append("-" * 70)
        mcp_ok, tools = self.test_mcp_tools()
        report.append(f"   Status: {'PASS' if mcp_ok else 'FAIL'}")
        if tools:
            report.append(f"   Tools: {', '.join(tools)}")
        report.append("")

        # Environment variables
        report.append("4. ENVIRONMENT VARIABLES (Inferred)")
        report.append("-" * 70)
        env_results = self.verify_environment_variables()

        report.append("   Required Variables:")
        for var, status in env_results['required'].items():
            status_str = "SET" if status else "MISSING"
            symbol = "✓" if status else "✗"
            report.append(f"     {symbol} {var}: {status_str}")
            if var in REQUIRED_ENV_VARS:
                report.append(f"        {REQUIRED_ENV_VARS[var]}")

        report.append("")
        report.append("   Recommended Variables:")
        for var, status in env_results['recommended'].items():
            status_str = "SET" if status else ("UNKNOWN" if status is None else "MISSING")
            symbol = "✓" if status else ("?" if status is None else "✗")
            report.append(f"     {symbol} {var}: {status_str}")
            if var in RECOMMENDED_ENV_VARS:
                report.append(f"        {RECOMMENDED_ENV_VARS[var]}")

        report.append("")
        report.append("   Optional Variables:")
        for var, status in env_results['optional'].items():
            status_str = "SET" if status else ("UNKNOWN" if status is None else "MISSING")
            symbol = "✓" if status else ("?" if status is None else "✗")
            report.append(f"     {symbol} {var}: {status_str}")
            if var in OPTIONAL_ENV_VARS:
                report.append(f"        {OPTIONAL_ENV_VARS[var]}")

        report.append("")
        report.append("=" * 70)
        report.append("OVERALL STATUS")
        report.append("=" * 70)

        overall_pass = health_ok and mcp_ok
        if overall_pass:
            report.append("   ✓ PASS - Deployment is functioning correctly")
            report.append("   All required functionality is working")
        else:
            report.append("   ✗ FAIL - Deployment has issues")
            report.append("   Check the details above for specific failures")

        report.append("")
        report.append("Note: Environment variables cannot be directly inspected in deployment.")
        report.append("      Status is inferred from functionality tests.")
        report.append("      Check GitHub Secrets configuration if issues are found.")
        report.append("")
        report.append("=" * 70)

        return "\n".join(report)


def main():
    """Main verification function."""
    parser = argparse.ArgumentParser(
        description='Verify LangGraph deployment environment and configuration',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--deployment-url',
        required=True,
        help='Deployment URL (e.g., https://your-deployment.us.langgraph.app)'
    )
    parser.add_argument(
        '--api-key',
        help='API key for authentication (default: uses ANTHROPIC_API_KEY env var)'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Create verifier
    verifier = DeploymentVerifier(
        deployment_url=args.deployment_url,
        api_key=args.api_key
    )

    # Generate and print report
    report = verifier.generate_report()
    print(report)

    # Exit with appropriate code
    health_ok, _ = verifier.check_health()
    mcp_ok, _ = verifier.test_mcp_tools()

    if health_ok and mcp_ok:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == '__main__':
    main()
