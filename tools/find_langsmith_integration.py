#!/usr/bin/env python3
"""
LangSmith GitHub Integration Finder

This CLI tool helps you find your LangSmith GitHub integration ID needed for
deploying applications from GitHub repositories.

Usage:
    python find_langsmith_integration.py              # List all integrations
    python find_langsmith_integration.py --github     # Show only GitHub integrations
    python find_langsmith_integration.py --set-env    # Export INTEGRATION_ID to .env

Environment Variables Required:
    LANGSMITH_API_KEY   - Your LangSmith API key
    WORKSPACE_ID        - Your LangSmith workspace/organization ID

Example:
    export LANGSMITH_API_KEY="lsv2_pt_..."
    export WORKSPACE_ID="your-org-id"
    python find_langsmith_integration.py --github
"""

import argparse
import json
import os
import sys
from typing import Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @staticmethod
    def disable():
        """Disable colors for non-TTY environments"""
        Colors.HEADER = ''
        Colors.OKBLUE = ''
        Colors.OKCYAN = ''
        Colors.OKGREEN = ''
        Colors.WARNING = ''
        Colors.FAIL = ''
        Colors.ENDC = ''
        Colors.BOLD = ''
        Colors.UNDERLINE = ''


# Disable colors on Windows unless explicitly supported
if os.name == 'nt' and not os.environ.get('FORCE_COLOR'):
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        Colors.disable()


class LangSmithIntegrationFinder:
    """Client for finding LangSmith integrations via Control Plane API"""

    BASE_URL = "https://api.host.langchain.com"
    INTEGRATIONS_ENDPOINT = "/v2/integrations"

    def __init__(self, api_key: str, workspace_id: Optional[str] = None):
        """
        Initialize the integration finder.

        Args:
            api_key: LangSmith API key
            workspace_id: Optional workspace/organization ID
        """
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "LangSmith-Integration-Finder/1.0"
        }

    def get_integrations(self) -> List[Dict]:
        """
        Fetch all integrations from LangSmith Control Plane API.

        Returns:
            List of integration dictionaries

        Raises:
            HTTPError: If API request fails
            URLError: If network connection fails
        """
        url = f"{self.BASE_URL}{self.INTEGRATIONS_ENDPOINT}"

        # Add workspace_id as query parameter if provided
        if self.workspace_id:
            url += f"?workspace_id={self.workspace_id}"

        request = Request(url, headers=self.headers)

        try:
            with urlopen(request, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))

                # Handle different response formats
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict):
                    # API might return {"integrations": [...]}
                    return data.get('integrations', data.get('data', []))
                else:
                    return []

        except HTTPError as e:
            error_body = e.read().decode('utf-8') if e.fp else 'No error details'
            raise HTTPError(
                e.url, e.code, f"API request failed: {e.reason}\nDetails: {error_body}",
                e.hdrs, e.fp
            )

    def filter_github_integrations(self, integrations: List[Dict]) -> List[Dict]:
        """
        Filter integrations to show only GitHub-related ones.

        Args:
            integrations: List of all integrations

        Returns:
            List of GitHub integrations
        """
        github_providers = {'github', 'github_app', 'github_oauth'}

        return [
            integration for integration in integrations
            if integration.get('provider', '').lower() in github_providers
            or integration.get('type', '').lower() in github_providers
            or 'github' in integration.get('name', '').lower()
        ]


def print_header(text: str):
    """Print a formatted header"""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{text}{Colors.ENDC}")
    print("=" * len(text))


def print_success(text: str):
    """Print a success message"""
    print(f"{Colors.OKGREEN}{text}{Colors.ENDC}")


def print_warning(text: str):
    """Print a warning message"""
    print(f"{Colors.WARNING}{text}{Colors.ENDC}")


def print_error(text: str):
    """Print an error message"""
    print(f"{Colors.FAIL}ERROR: {text}{Colors.ENDC}", file=sys.stderr)


def print_info(text: str):
    """Print an info message"""
    print(f"{Colors.OKCYAN}{text}{Colors.ENDC}")


def format_integration_table(integrations: List[Dict]) -> str:
    """
    Format integrations as a readable table.

    Args:
        integrations: List of integration dictionaries

    Returns:
        Formatted table string
    """
    if not integrations:
        return "No integrations found."

    # Calculate column widths
    headers = ["ID", "Provider", "Type", "Status", "Name"]
    rows = []

    for integration in integrations:
        row = [
            str(integration.get('id', 'N/A'))[:36],
            str(integration.get('provider', 'N/A'))[:20],
            str(integration.get('type', 'N/A'))[:20],
            str(integration.get('status', 'N/A'))[:15],
            str(integration.get('name', 'N/A'))[:30]
        ]
        rows.append(row)

    # Calculate max width for each column
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    # Build table
    separator = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"
    header_row = "| " + " | ".join(
        headers[i].ljust(col_widths[i]) for i in range(len(headers))
    ) + " |"

    table_lines = [separator, header_row, separator]

    for row in rows:
        table_lines.append(
            "| " + " | ".join(
                row[i].ljust(col_widths[i]) for i in range(len(row))
            ) + " |"
        )

    table_lines.append(separator)

    return "\n".join(table_lines)


def print_github_integration_details(integrations: List[Dict]):
    """
    Print detailed information about GitHub integrations.

    Args:
        integrations: List of GitHub integrations
    """
    if not integrations:
        print_warning("\nNo GitHub integrations found!")
        print("\nTo create a GitHub integration:")
        print("1. Visit: https://smith.langchain.com/settings/integrations")
        print("2. Click 'Add Integration' or 'Connect GitHub'")
        print("3. Follow the GitHub OAuth flow to authorize LangSmith")
        print("4. Run this script again to get your INTEGRATION_ID")
        return

    print_success(f"\nFound {len(integrations)} GitHub integration(s)!")

    for i, integration in enumerate(integrations, 1):
        print(f"\n{Colors.BOLD}GitHub Integration #{i}:{Colors.ENDC}")
        print(f"  Integration ID: {Colors.OKGREEN}{integration.get('id')}{Colors.ENDC}")
        print(f"  Provider:       {integration.get('provider', 'N/A')}")
        print(f"  Type:           {integration.get('type', 'N/A')}")
        print(f"  Status:         {integration.get('status', 'N/A')}")
        print(f"  Name:           {integration.get('name', 'N/A')}")

        if integration.get('created_at'):
            print(f"  Created:        {integration.get('created_at')}")

    # Show copy-paste ready format
    if len(integrations) == 1:
        integration_id = integrations[0].get('id')
        print_header("\nReady to Use")
        print(f"\nAdd this to your GitHub repository secrets:")
        print(f"{Colors.BOLD}INTEGRATION_ID{Colors.ENDC} = {Colors.OKGREEN}{integration_id}{Colors.ENDC}")
        print(f"\nOr export to your environment:")
        print(f"{Colors.OKCYAN}export INTEGRATION_ID=\"{integration_id}\"{Colors.ENDC}")
    else:
        print_warning("\nMultiple GitHub integrations found. Use the ID that matches your deployment target.")


def save_to_env_file(integration_id: str, env_path: str = ".env") -> bool:
    """
    Save INTEGRATION_ID to .env file.

    Args:
        integration_id: The integration ID to save
        env_path: Path to .env file

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read existing .env if it exists
        env_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_lines = f.readlines()

        # Check if INTEGRATION_ID already exists
        integration_id_exists = False
        for i, line in enumerate(env_lines):
            if line.strip().startswith('INTEGRATION_ID='):
                env_lines[i] = f'INTEGRATION_ID="{integration_id}"\n'
                integration_id_exists = True
                break

        # Add INTEGRATION_ID if it doesn't exist
        if not integration_id_exists:
            env_lines.append(f'INTEGRATION_ID="{integration_id}"\n')

        # Write back to .env
        with open(env_path, 'w') as f:
            f.writelines(env_lines)

        return True
    except Exception as e:
        print_error(f"Failed to write to {env_path}: {e}")
        return False


def validate_environment() -> tuple[Optional[str], Optional[str]]:
    """
    Validate required environment variables.

    Returns:
        Tuple of (api_key, workspace_id)

    Raises:
        SystemExit: If required environment variables are missing
    """
    api_key = os.environ.get('LANGSMITH_API_KEY')
    workspace_id = os.environ.get('WORKSPACE_ID')

    missing = []
    if not api_key:
        missing.append('LANGSMITH_API_KEY')
    if not workspace_id:
        missing.append('WORKSPACE_ID')

    if missing:
        print_error("Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nSet them using:")
        if 'LANGSMITH_API_KEY' in missing:
            print('  export LANGSMITH_API_KEY="lsv2_pt_..."')
        if 'WORKSPACE_ID' in missing:
            print('  export WORKSPACE_ID="your-workspace-id"')
        print("\nGet your API key from: https://smith.langchain.com/settings")
        sys.exit(1)

    return api_key, workspace_id


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Find LangSmith GitHub integration ID for deployments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                    List all integrations
  %(prog)s --github           Show only GitHub integrations
  %(prog)s --set-env          Export INTEGRATION_ID to .env file
  %(prog)s --json             Output as JSON

For more information, visit:
  https://smith.langchain.com/settings/integrations
        """
    )

    parser.add_argument(
        '--github',
        action='store_true',
        help='Show only GitHub integrations'
    )

    parser.add_argument(
        '--set-env',
        action='store_true',
        help='Save INTEGRATION_ID to .env file (requires single GitHub integration)'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    parser.add_argument(
        '--env-file',
        default='.env',
        help='Path to .env file (default: .env)'
    )

    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )

    args = parser.parse_args()

    # Disable colors if requested
    if args.no_color or args.json:
        Colors.disable()

    # Validate environment
    api_key, workspace_id = validate_environment()

    # Initialize client
    try:
        print_info("Fetching integrations from LangSmith Control Plane API...")
        client = LangSmithIntegrationFinder(api_key, workspace_id)
        integrations = client.get_integrations()

        # Filter for GitHub if requested
        if args.github:
            integrations = client.filter_github_integrations(integrations)

        # JSON output
        if args.json:
            print(json.dumps(integrations, indent=2))
            return

        # Table output
        print_header("LangSmith Integrations")
        print(format_integration_table(integrations))

        # GitHub-specific details
        if args.github or any(
            'github' in str(i.get('provider', '')).lower() or
            'github' in str(i.get('type', '')).lower()
            for i in integrations
        ):
            github_integrations = client.filter_github_integrations(integrations)
            print_github_integration_details(github_integrations)

            # Save to .env if requested
            if args.set_env:
                if len(github_integrations) == 1:
                    integration_id = github_integrations[0].get('id')
                    if save_to_env_file(integration_id, args.env_file):
                        print_success(f"\nINTEGRATION_ID saved to {args.env_file}")
                    else:
                        sys.exit(1)
                elif len(github_integrations) == 0:
                    print_error("No GitHub integration found. Cannot save to .env")
                    sys.exit(1)
                else:
                    print_error("Multiple GitHub integrations found. Specify which one to use:")
                    for i, integration in enumerate(github_integrations, 1):
                        print(f"  {i}. {integration.get('id')} - {integration.get('name')}")
                    sys.exit(1)

        print()  # Empty line at end

    except HTTPError as e:
        print_error(f"API request failed with status {e.code}")
        print(f"URL: {e.url}")
        print(f"Reason: {e.reason}")
        if e.code == 401:
            print("\nYour LANGSMITH_API_KEY may be invalid or expired.")
            print("Get a new one from: https://smith.langchain.com/settings")
        elif e.code == 403:
            print("\nYou don't have permission to access integrations.")
            print("Check your WORKSPACE_ID and API key permissions.")
        elif e.code == 404:
            print("\nIntegrations endpoint not found.")
            print("The API structure may have changed. Contact LangSmith support.")
        sys.exit(1)

    except URLError as e:
        print_error(f"Network error: {e.reason}")
        print("Check your internet connection and try again.")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(130)

    except Exception as e:
        print_error(f"Unexpected error: {e}")
        if '--debug' in sys.argv:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()
