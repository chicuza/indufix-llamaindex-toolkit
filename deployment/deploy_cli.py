"""Command-Line Interface for LangSmith Deployment Automation.

Usage:
    python deploy_cli.py create --name my-agent --repo https://github.com/user/repo
    python deploy_cli.py list
    python deploy_cli.py status DEPLOYMENT_ID
    python deploy_cli.py update DEPLOYMENT_ID --branch dev
    python deploy_cli.py delete DEPLOYMENT_ID --confirm
    python deploy_cli.py apply -f deploy_config.yaml
"""

import sys
import os
import argparse
import json
import yaml
from pathlib import Path
from typing import Optional

from .langsmith_deploy import LangSmithDeployClient, ResourceSpec
from .exceptions import DeploymentError


def create_deployment(args):
    """Create new deployment."""
    client = LangSmithDeployClient.from_env()

    # Parse resource spec if provided
    resource_spec = None
    if args.cpu or args.memory:
        resource_spec = ResourceSpec(
            min_scale=args.min_scale,
            max_scale=args.max_scale,
            cpu=args.cpu or 1,
            memory_mb=args.memory or 1024
        )

    # Parse secrets
    secrets = {}
    if args.secret:
        for secret in args.secret:
            name, value = secret.split("=", 1)
            secrets[name] = value

    try:
        deployment = client.create_deployment(
            name=args.name,
            source=args.source,
            repo_url=args.repo,
            branch=args.branch,
            image_uri=args.image,
            config_path=args.config,
            secrets=secrets,
            resource_spec=resource_spec,
            deployment_type=args.type,
            build_on_push=args.build_on_push,
            dry_run=args.dry_run
        )

        if args.dry_run:
            print(json.dumps(deployment, indent=2))
        else:
            print(f"✅ Deployment created: {deployment['id']}")
            print(f"   Name: {deployment['name']}")
            print(f"   URL: {deployment.get('url', 'Pending...')}")

            if args.wait:
                print("\nWaiting for deployment to become healthy...")
                client.wait_for_deployment(deployment['id'], timeout=args.wait_timeout)

    except DeploymentError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def list_deployments(args):
    """List all deployments."""
    client = LangSmithDeployClient.from_env()

    try:
        deployments = client.list_deployments(limit=args.limit)

        if args.json:
            print(json.dumps(deployments, indent=2))
        else:
            print(f"Found {len(deployments)} deployment(s):\n")
            for dep in deployments:
                print(f"ID:     {dep['id']}")
                print(f"Name:   {dep['name']}")
                print(f"Status: {dep.get('state', 'unknown')} / {dep.get('health', 'unknown')}")
                print(f"URL:    {dep.get('url', 'N/A')}")
                print()

    except DeploymentError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def get_status(args):
    """Get deployment status."""
    client = LangSmithDeployClient.from_env()

    try:
        status = client.get_deployment_status(args.deployment_id)

        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"Deployment: {status['name']} ({status['id']})")
            print(f"State:      {status['state']}")
            print(f"Health:     {status['health']}")
            print(f"URL:        {status.get('url', 'N/A')}")
            print(f"Updated:    {status.get('updated_at', 'N/A')}")

    except DeploymentError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def update_deployment(args):
    """Update existing deployment."""
    client = LangSmithDeployClient.from_env()

    # Parse secrets
    secrets = {}
    if args.secret:
        for secret in args.secret:
            name, value = secret.split("=", 1)
            secrets[name] = value

    try:
        deployment = client.update_deployment(
            deployment_id=args.deployment_id,
            branch=args.branch,
            image_uri=args.image,
            secrets=secrets if secrets else None,
            dry_run=args.dry_run
        )

        if args.dry_run:
            print(json.dumps(deployment, indent=2))
        else:
            print(f"✅ Deployment updated: {deployment['id']}")

            if args.wait:
                print("\nWaiting for deployment to become healthy...")
                client.wait_for_deployment(deployment['id'], timeout=args.wait_timeout)

    except DeploymentError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def delete_deployment(args):
    """Delete deployment."""
    client = LangSmithDeployClient.from_env()

    if not args.confirm:
        print("❌ Error: Must pass --confirm to delete deployment", file=sys.stderr)
        sys.exit(1)

    try:
        client.delete_deployment(args.deployment_id, confirm=True)
        print(f"✅ Deployment {args.deployment_id} deleted")

    except DeploymentError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def apply_config(args):
    """Apply deployment from YAML config file."""
    client = LangSmithDeployClient.from_env()

    try:
        # Load config file
        config_path = Path(args.file)
        if not config_path.exists():
            print(f"❌ Error: Config file not found: {args.file}", file=sys.stderr)
            sys.exit(1)

        with open(config_path) as f:
            if args.file.endswith('.yaml') or args.file.endswith('.yml'):
                config = yaml.safe_load(f)
            else:
                config = json.load(f)

        # Extract deployment config
        deployment_config = config.get('deployment', {})
        secrets_config = config.get('secrets', {})

        # Resolve environment variables in secrets
        for key, value in secrets_config.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                env_var = value[2:-1]
                secrets_config[key] = os.environ.get(env_var, '')

        # Create or update deployment
        name = deployment_config.get('name')
        if not name:
            print("❌ Error: 'name' required in config", file=sys.stderr)
            sys.exit(1)

        # Check if deployment exists
        deployments = client.list_deployments()
        existing = next((d for d in deployments if d['name'] == name), None)

        if existing:
            print(f"Deployment '{name}' exists, updating...")
            deployment = client.update_deployment(
                deployment_id=existing['id'],
                branch=deployment_config.get('branch'),
                image_uri=deployment_config.get('image_uri'),
                secrets=secrets_config,
                dry_run=args.dry_run
            )
        else:
            print(f"Creating new deployment '{name}'...")
            deployment = client.create_deployment(
                name=name,
                source=deployment_config.get('source', 'github'),
                repo_url=deployment_config.get('repo_url'),
                branch=deployment_config.get('branch', 'main'),
                config_path=deployment_config.get('config_path', 'langgraph.json'),
                image_uri=deployment_config.get('image_uri'),
                secrets=secrets_config,
                deployment_type=deployment_config.get('type', 'dev'),
                dry_run=args.dry_run
            )

        if args.dry_run:
            print(json.dumps(deployment, indent=2))
        else:
            print(f"✅ Deployment applied: {deployment['id']}")

    except DeploymentError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading config: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LangSmith Cloud Deployment CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create new deployment')
    create_parser.add_argument('--name', required=True, help='Deployment name')
    create_parser.add_argument('--source', default='github', choices=['github', 'external_docker'],
                               help='Deployment source')
    create_parser.add_argument('--repo', help='GitHub repository URL')
    create_parser.add_argument('--branch', default='main', help='Git branch (default: main)')
    create_parser.add_argument('--image', help='Docker image URI (for external_docker source)')
    create_parser.add_argument('--config', default='langgraph.json', help='LangGraph config path')
    create_parser.add_argument('--type', default='dev', choices=['dev', 'prod'], help='Deployment type')
    create_parser.add_argument('--secret', action='append', help='Secret in format NAME=VALUE (can specify multiple)')
    create_parser.add_argument('--min-scale', type=int, default=1, help='Minimum scale')
    create_parser.add_argument('--max-scale', type=int, default=1, help='Maximum scale')
    create_parser.add_argument('--cpu', type=int, help='CPU allocation')
    create_parser.add_argument('--memory', type=int, help='Memory in MB')
    create_parser.add_argument('--build-on-push', action='store_true', help='Auto-build on git push')
    create_parser.add_argument('--wait', action='store_true', help='Wait for deployment to become healthy')
    create_parser.add_argument('--wait-timeout', type=int, default=600, help='Wait timeout in seconds')
    create_parser.add_argument('--dry-run', action='store_true', help='Preview without creating')
    create_parser.set_defaults(func=create_deployment)

    # List command
    list_parser = subparsers.add_parser('list', help='List deployments')
    list_parser.add_argument('--limit', type=int, default=100, help='Maximum deployments to list')
    list_parser.add_argument('--json', action='store_true', help='Output as JSON')
    list_parser.set_defaults(func=list_deployments)

    # Status command
    status_parser = subparsers.add_parser('status', help='Get deployment status')
    status_parser.add_argument('deployment_id', help='Deployment ID')
    status_parser.add_argument('--json', action='store_true', help='Output as JSON')
    status_parser.set_defaults(func=get_status)

    # Update command
    update_parser = subparsers.add_parser('update', help='Update deployment')
    update_parser.add_argument('deployment_id', help='Deployment ID')
    update_parser.add_argument('--branch', help='New git branch')
    update_parser.add_argument('--image', help='New Docker image URI')
    update_parser.add_argument('--secret', action='append', help='Secret in format NAME=VALUE')
    update_parser.add_argument('--wait', action='store_true', help='Wait for deployment to become healthy')
    update_parser.add_argument('--wait-timeout', type=int, default=600, help='Wait timeout in seconds')
    update_parser.add_argument('--dry-run', action='store_true', help='Preview without updating')
    update_parser.set_defaults(func=update_deployment)

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete deployment')
    delete_parser.add_argument('deployment_id', help='Deployment ID')
    delete_parser.add_argument('--confirm', action='store_true', required=True, help='Confirm deletion')
    delete_parser.set_defaults(func=delete_deployment)

    # Apply command
    apply_parser = subparsers.add_parser('apply', help='Apply deployment from config file')
    apply_parser.add_argument('-f', '--file', required=True, help='Config file path (YAML or JSON)')
    apply_parser.add_argument('--dry-run', action='store_true', help='Preview without applying')
    apply_parser.set_defaults(func=apply_config)

    # Parse and execute
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
