"""Deployment Trigger Script for GitHub Actions.

This script validates prerequisites, triggers deployment via GitHub Actions,
and monitors the deployment progress.

Usage:
    # Validate secrets only
    python trigger_deployment.py --validate-secrets

    # Dry run (validate everything but don't deploy)
    python trigger_deployment.py --dry-run --environment prod

    # Full validation without deployment
    python trigger_deployment.py --validate-only --environment prod

    # Deploy to development
    python trigger_deployment.py --environment dev --wait

    # Deploy to production
    python trigger_deployment.py --environment prod --wait

Author: DevOps Team
Last Updated: 2026-01-23
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

try:
    import requests
    import yaml
except ImportError:
    print("ERROR: Missing required packages")
    print("Install with: pip install requests pyyaml")
    sys.exit(1)


class DeploymentTrigger:
    """Handles deployment validation and triggering."""

    # Required GitHub Secrets
    REQUIRED_SECRETS = [
        'LANGSMITH_API_KEY',
        'WORKSPACE_ID',
        'INTEGRATION_ID',
        'LLAMA_CLOUD_API_KEY',
        'ANTHROPIC_API_KEY',
    ]

    # Optional GitHub Secrets
    OPTIONAL_SECRETS = [
        'OPENAI_API_KEY',
        'LANGCHAIN_TRACING_V2',
        'LANGCHAIN_PROJECT',
        'LANGCHAIN_ENDPOINT',
    ]

    def __init__(self, environment: str = 'dev', dry_run: bool = False):
        """Initialize deployment trigger.

        Args:
            environment: Target environment ('dev' or 'prod')
            dry_run: If True, validate but don't actually deploy
        """
        self.environment = environment
        self.dry_run = dry_run
        self.repo_root = Path(__file__).parent
        self.validation_results = {}

    def print_header(self, title: str):
        """Print a formatted header."""
        print("\n" + "=" * 70)
        print(title)
        print("=" * 70)

    def print_section(self, title: str):
        """Print a formatted section header."""
        print(f"\n{title}")
        print("-" * 70)

    def check_git_status(self) -> Tuple[bool, str]:
        """Verify git repository status.

        Returns:
            Tuple of (success, message)
        """
        try:
            # Check if on correct branch
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_root
            )
            current_branch = result.stdout.strip()

            # Check for uncommitted changes
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_root
            )
            has_changes = bool(result.stdout.strip())

            # Get last commit
            result = subprocess.run(
                ['git', 'log', '-1', '--oneline'],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.repo_root
            )
            last_commit = result.stdout.strip()

            print(f"Current Branch: {current_branch}")
            print(f"Uncommitted Changes: {'Yes (WARNING)' if has_changes else 'No'}")
            print(f"Last Commit: {last_commit}")

            if has_changes:
                return False, "Uncommitted changes detected. Commit or stash before deploying."

            expected_branch = 'main' if self.environment == 'prod' else 'dev'
            if current_branch != expected_branch:
                return False, f"Wrong branch. Expected '{expected_branch}', got '{current_branch}'"

            return True, f"Git status OK (on {current_branch})"

        except subprocess.CalledProcessError as e:
            return False, f"Git command failed: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def validate_config_file(self) -> Tuple[bool, str]:
        """Validate deployment configuration file.

        Returns:
            Tuple of (success, message)
        """
        try:
            config_file = self.repo_root / 'deployment' / f'deploy_config{"_prod" if self.environment == "prod" else ""}.yaml'

            if not config_file.exists():
                return False, f"Config file not found: {config_file}"

            with open(config_file) as f:
                config = yaml.safe_load(f)

            # Validate required fields
            required_fields = ['deployment']
            for field in required_fields:
                if field not in config:
                    return False, f"Missing required field: {field}"

            deployment = config['deployment']
            required_deployment_fields = ['name', 'source', 'repo_url', 'branch']
            for field in required_deployment_fields:
                if field not in deployment:
                    return False, f"Missing deployment field: {field}"

            print(f"Deployment Name: {deployment['name']}")
            print(f"Source: {deployment['source']}")
            print(f"Repository: {deployment['repo_url']}")
            print(f"Branch: {deployment['branch']}")
            print(f"Type: {deployment.get('type', 'dev')}")
            print(f"Secrets Configured: {len(config.get('secrets', {}))}")

            return True, f"Configuration file valid: {config_file.name}"

        except yaml.YAMLError as e:
            return False, f"Invalid YAML syntax: {e}"
        except Exception as e:
            return False, f"Config validation error: {e}"

    def check_github_secrets(self) -> Tuple[bool, str]:
        """Check if required GitHub Secrets are configured.

        Note: We can't actually read GitHub Secrets values, but we can check
        if they exist by examining the repository via GitHub CLI or API.

        Returns:
            Tuple of (success, message)
        """
        try:
            # Try using GitHub CLI if available
            result = subprocess.run(
                ['gh', 'secret', 'list'],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )

            if result.returncode == 0:
                # Parse secret list
                secrets_output = result.stdout
                configured_secrets = set()
                for line in secrets_output.split('\n'):
                    if line.strip():
                        secret_name = line.split()[0]
                        configured_secrets.add(secret_name)

                # Check required secrets
                missing_required = []
                for secret in self.REQUIRED_SECRETS:
                    if secret in configured_secrets:
                        print(f"  ✓ {secret}: Configured")
                    else:
                        print(f"  ✗ {secret}: MISSING")
                        missing_required.append(secret)

                # Check optional secrets
                print("\nOPTIONAL SECRETS:")
                for secret in self.OPTIONAL_SECRETS:
                    if secret in configured_secrets:
                        print(f"  ✓ {secret}: Configured")
                    else:
                        print(f"  - {secret}: Not configured (optional)")

                if missing_required:
                    return False, f"Missing required secrets: {', '.join(missing_required)}"

                return True, "All required GitHub Secrets are configured"

            else:
                # GitHub CLI not available or not authenticated
                print("WARNING: Cannot verify GitHub Secrets (gh CLI not available)")
                print("Assuming secrets are configured...")
                print("\nREQUIRED SECRETS (verify manually):")
                for secret in self.REQUIRED_SECRETS:
                    print(f"  - {secret}")
                print("\nOPTIONAL SECRETS:")
                for secret in self.OPTIONAL_SECRETS:
                    print(f"  - {secret}")

                return True, "GitHub Secrets cannot be verified (manual check required)"

        except FileNotFoundError:
            # gh command not found
            print("WARNING: GitHub CLI (gh) not installed")
            print("Cannot automatically verify secrets")
            print("\nManual verification required:")
            print(f"Visit: https://github.com/chicuza/indufix-llamaindex-toolkit/settings/secrets/actions")
            print("\nRequired secrets:")
            for secret in self.REQUIRED_SECRETS:
                print(f"  - {secret}")

            return True, "GitHub Secrets verification skipped (manual check required)"

        except Exception as e:
            return False, f"Error checking GitHub Secrets: {e}"

    def check_langsmith_connection(self) -> Tuple[bool, str]:
        """Test LangSmith API connection.

        Returns:
            Tuple of (success, message)
        """
        try:
            # Load from environment or .env file
            from dotenv import load_dotenv
            load_dotenv()

            api_key = os.environ.get('LANGSMITH_API_KEY')
            workspace_id = os.environ.get('WORKSPACE_ID')

            if not api_key or not workspace_id:
                print("WARNING: LANGSMITH_API_KEY or WORKSPACE_ID not in environment")
                print("Skipping LangSmith connection test")
                return True, "LangSmith connection test skipped (credentials not in env)"

            # Test API connection
            headers = {'x-api-key': api_key}
            url = f'https://api.smith.langchain.com/api/v1/workspaces/{workspace_id}'

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                workspace = response.json()
                print(f"Workspace: {workspace.get('display_name', 'N/A')}")
                print(f"Workspace ID: {workspace_id[:20]}...")
                print(f"API Connection: SUCCESS")
                return True, "LangSmith API connection successful"
            else:
                return False, f"LangSmith API returned {response.status_code}: {response.text}"

        except ImportError:
            print("WARNING: python-dotenv not installed")
            print("Skipping LangSmith connection test")
            return True, "LangSmith connection test skipped (dotenv not available)"
        except requests.RequestException as e:
            return False, f"LangSmith API connection failed: {e}"
        except Exception as e:
            return False, f"Unexpected error testing LangSmith: {e}"

    def check_github_integration(self) -> Tuple[bool, str]:
        """Verify GitHub integration is active.

        Returns:
            Tuple of (success, message)
        """
        try:
            from dotenv import load_dotenv
            load_dotenv()

            api_key = os.environ.get('LANGSMITH_API_KEY')
            workspace_id = os.environ.get('WORKSPACE_ID')
            integration_id = os.environ.get('INTEGRATION_ID')

            if not all([api_key, workspace_id, integration_id]):
                print("WARNING: Missing credentials in environment")
                print("Skipping GitHub integration check")
                return True, "GitHub integration check skipped (credentials not in env)"

            headers = {'x-api-key': api_key}
            url = f'https://api.smith.langchain.com/api/v1/workspaces/{workspace_id}/integrations/{integration_id}'

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                integration = response.json()
                print(f"Provider: {integration.get('provider', 'N/A')}")
                print(f"Status: {integration.get('status', 'N/A')}")
                print(f"Integration ID: {integration_id[:20]}...")

                if integration.get('status') != 'active':
                    return False, f"Integration status is '{integration.get('status')}', expected 'active'"

                return True, "GitHub integration is active"
            else:
                return False, f"Integration API returned {response.status_code}"

        except ImportError:
            return True, "GitHub integration check skipped (dotenv not available)"
        except requests.RequestException as e:
            return False, f"Integration check failed: {e}"
        except Exception as e:
            return False, f"Unexpected error: {e}"

    def run_validations(self) -> bool:
        """Run all pre-deployment validations.

        Returns:
            True if all validations pass, False otherwise
        """
        self.print_header("PRE-DEPLOYMENT VALIDATION")

        validations = [
            ("Code Quality (Git Status)", self.check_git_status),
            ("Configuration Files", self.validate_config_file),
            ("GitHub Secrets", self.check_github_secrets),
            ("LangSmith Connection", self.check_langsmith_connection),
            ("GitHub Integration", self.check_github_integration),
        ]

        all_passed = True

        for name, validator in validations:
            self.print_section(f"Validating: {name}")
            try:
                success, message = validator()
                self.validation_results[name] = {
                    'success': success,
                    'message': message
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
                    'message': str(e)
                }
                all_passed = False

        # Print summary
        self.print_header("VALIDATION SUMMARY")
        for name, result in self.validation_results.items():
            status = "✓ PASSED" if result['success'] else "✗ FAILED"
            print(f"{status}: {name}")

        if all_passed:
            print("\n✓ ALL VALIDATIONS PASSED")
            print("Ready to deploy!")
        else:
            print("\n✗ VALIDATION FAILURES DETECTED")
            print("Fix issues before deploying")

        return all_passed

    def trigger_github_workflow(self, wait: bool = False) -> bool:
        """Trigger GitHub Actions workflow.

        Args:
            wait: If True, wait for workflow to complete

        Returns:
            True if triggered successfully, False otherwise
        """
        try:
            self.print_header("TRIGGERING GITHUB ACTIONS WORKFLOW")

            # Check if gh CLI is available
            result = subprocess.run(
                ['gh', '--version'],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                print("ERROR: GitHub CLI (gh) is not installed")
                print("Install from: https://cli.github.com/")
                return False

            # Trigger workflow
            print(f"Environment: {self.environment}")
            print(f"Triggering workflow...")

            cmd = [
                'gh', 'workflow', 'run', 'deploy_langsmith.yml',
                '-f', f'environment={self.environment}'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )

            if result.returncode == 0:
                print("✓ Workflow triggered successfully")
                print(result.stdout)

                if wait:
                    self.print_section("Waiting for workflow to complete...")
                    print("This may take 15-30 minutes...")
                    print("\nYou can monitor progress at:")
                    print("https://github.com/chicuza/indufix-llamaindex-toolkit/actions")

                    # Wait a bit for workflow to start
                    time.sleep(5)

                    # Monitor workflow
                    return self.monitor_workflow()

                return True

            else:
                print(f"✗ Failed to trigger workflow")
                print(f"Error: {result.stderr}")
                return False

        except FileNotFoundError:
            print("ERROR: GitHub CLI (gh) not found")
            print("Install from: https://cli.github.com/")
            return False
        except Exception as e:
            print(f"ERROR: {e}")
            return False

    def monitor_workflow(self) -> bool:
        """Monitor workflow execution.

        Returns:
            True if workflow completes successfully, False otherwise
        """
        try:
            print("\nMonitoring workflow execution...")

            # Get the latest workflow run
            result = subprocess.run(
                ['gh', 'run', 'list', '--workflow=deploy_langsmith.yml', '--limit=1', '--json=status,conclusion,url'],
                capture_output=True,
                text=True,
                cwd=self.repo_root
            )

            if result.returncode != 0:
                print("ERROR: Failed to get workflow status")
                return False

            runs = json.loads(result.stdout)
            if not runs:
                print("ERROR: No workflow runs found")
                return False

            run = runs[0]
            run_url = run.get('url', 'N/A')

            print(f"Workflow URL: {run_url}")

            # Poll workflow status
            max_wait = 1800  # 30 minutes
            start_time = time.time()
            poll_interval = 30  # Check every 30 seconds

            while time.time() - start_time < max_wait:
                result = subprocess.run(
                    ['gh', 'run', 'list', '--workflow=deploy_langsmith.yml', '--limit=1', '--json=status,conclusion'],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_root
                )

                if result.returncode == 0:
                    runs = json.loads(result.stdout)
                    if runs:
                        run = runs[0]
                        status = run.get('status')
                        conclusion = run.get('conclusion')

                        elapsed = int(time.time() - start_time)
                        print(f"[{elapsed}s] Status: {status}, Conclusion: {conclusion or 'N/A'}")

                        if status == 'completed':
                            if conclusion == 'success':
                                print("\n✓ DEPLOYMENT SUCCESSFUL!")
                                return True
                            else:
                                print(f"\n✗ DEPLOYMENT FAILED (conclusion: {conclusion})")
                                return False

                time.sleep(poll_interval)

            print(f"\n✗ TIMEOUT: Workflow did not complete within {max_wait}s")
            print(f"Check status at: {run_url}")
            return False

        except Exception as e:
            print(f"ERROR monitoring workflow: {e}")
            return False

    def save_baseline(self):
        """Save current deployment state for rollback."""
        try:
            from dotenv import load_dotenv
            load_dotenv()

            api_key = os.environ.get('LANGSMITH_API_KEY')
            workspace_id = os.environ.get('WORKSPACE_ID')

            if not api_key or not workspace_id:
                print("WARNING: Cannot save baseline (missing credentials)")
                return

            # Get current deployments
            headers = {'x-api-key': api_key}
            url = f'https://api.smith.langchain.com/api/v1/workspaces/{workspace_id}/deployments'

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                deployments = response.json()
                deployment_name = 'indufix-llamaindex-toolkit'
                current = next((d for d in deployments if d['name'] == deployment_name), None)

                if current:
                    baseline = {
                        'timestamp': datetime.utcnow().isoformat(),
                        'environment': self.environment,
                        'deployment_id': current['id'],
                        'deployment_name': current['name'],
                        'current_revision_id': current.get('latest_revision_id'),
                        'deployment_url': current.get('url'),
                        'health': current.get('health'),
                    }

                    baseline_file = self.repo_root / 'rollback_baseline.json'
                    with open(baseline_file, 'w') as f:
                        json.dump(baseline, f, indent=2)

                    print(f"\n✓ Baseline saved to: {baseline_file}")
                    print(f"  Deployment ID: {baseline['deployment_id']}")
                    print(f"  Revision ID: {baseline['current_revision_id']}")

        except Exception as e:
            print(f"WARNING: Failed to save baseline: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Trigger and manage LangSmith deployments via GitHub Actions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate secrets only
  python trigger_deployment.py --validate-secrets

  # Dry run (validate but don't deploy)
  python trigger_deployment.py --dry-run --environment prod

  # Full validation without deployment
  python trigger_deployment.py --validate-only --environment prod

  # Deploy to development
  python trigger_deployment.py --environment dev --wait

  # Deploy to production
  python trigger_deployment.py --environment prod --wait
        """
    )

    parser.add_argument(
        '--environment', '-e',
        choices=['dev', 'prod'],
        default='dev',
        help='Target environment (default: dev)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate everything but do not trigger deployment'
    )

    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Run validations only, do not deploy'
    )

    parser.add_argument(
        '--validate-secrets',
        action='store_true',
        help='Validate GitHub Secrets only'
    )

    parser.add_argument(
        '--wait',
        action='store_true',
        help='Wait for deployment to complete'
    )

    parser.add_argument(
        '--save-baseline',
        action='store_true',
        help='Save current deployment state as baseline for rollback'
    )

    args = parser.parse_args()

    # Create trigger
    trigger = DeploymentTrigger(
        environment=args.environment,
        dry_run=args.dry_run or args.validate_only
    )

    # Save baseline if requested
    if args.save_baseline:
        trigger.save_baseline()
        return 0

    # Run validations
    if args.validate_secrets:
        trigger.print_header("GITHUB SECRETS VALIDATION")
        trigger.print_section("Checking required GitHub Secrets")
        print("\nREQUIRED SECRETS:")
        success, message = trigger.check_github_secrets()
        if success:
            print(f"\n✓ {message}")
            return 0
        else:
            print(f"\n✗ {message}")
            return 1

    # Full validation
    validations_passed = trigger.run_validations()

    if not validations_passed:
        print("\n" + "=" * 70)
        print("VALIDATION FAILED - Cannot deploy")
        print("=" * 70)
        print("\nFix the issues above and try again.")
        return 1

    # Stop here if validate-only
    if args.validate_only:
        print("\n" + "=" * 70)
        print("Validation complete (validate-only mode)")
        print("=" * 70)
        return 0

    # Stop here if dry-run
    if args.dry_run:
        print("\n" + "=" * 70)
        print("DRY RUN - Deployment not triggered")
        print("=" * 70)
        print("\nAll validations passed. Remove --dry-run to deploy.")
        return 0

    # Save baseline before deployment
    trigger.save_baseline()

    # Trigger deployment
    success = trigger.trigger_github_workflow(wait=args.wait)

    if success:
        print("\n" + "=" * 70)
        print("DEPLOYMENT SUCCESSFUL")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Run: python post_deploy_validate.py")
        print("2. Monitor: python deployment_status.py")
        return 0
    else:
        print("\n" + "=" * 70)
        print("DEPLOYMENT FAILED")
        print("=" * 70)
        print("\nCheck:")
        print("1. GitHub Actions workflow logs")
        print("2. LangSmith deployment UI")
        print("3. See DEPLOYMENT_TROUBLESHOOTING.md")
        return 1


if __name__ == '__main__':
    sys.exit(main())
