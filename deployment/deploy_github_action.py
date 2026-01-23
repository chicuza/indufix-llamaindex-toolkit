"""Simplified CI/CD deployment script for GitHub Actions.

This script is called from GitHub Actions workflow to deploy to LangSmith.
It uses environment variables from GitHub Secrets.

Usage:
    python deploy_github_action.py \\
        --name my-deployment \\
        --repo owner/repo \\
        --branch main \\
        --config toolkit.toml \\
        --wait
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Import deployment modules
sys.path.insert(0, str(Path(__file__).parent))

from langsmith_deploy import LangSmithDeployClient, ResourceSpec
from exceptions import DeploymentError, DeploymentTimeoutError

def main():
    """Main deployment function for GitHub Actions."""
    parser = argparse.ArgumentParser(description='Deploy to LangSmith from GitHub Actions')
    parser.add_argument('--name', required=True, help='Deployment name')
    parser.add_argument('--repo', required=True, help='GitHub repository (owner/repo)')
    parser.add_argument('--branch', default='main', help='Git branch to deploy')
    parser.add_argument('--config', default='langgraph.json', help='LangGraph config file path')
    parser.add_argument('--wait', action='store_true', help='Wait for deployment to complete')
    parser.add_argument('--wait-timeout', type=int, default=1800,
                       help='Wait timeout in seconds (default: 1800 = 30 minutes)')

    args = parser.parse_args()

    # Get credentials from environment (set by GitHub Secrets)
    api_key = os.environ.get('LANGSMITH_API_KEY')
    workspace_id = os.environ.get('WORKSPACE_ID')
    integration_id = os.environ.get('INTEGRATION_ID')
    llama_api_key = os.environ.get('LLAMA_CLOUD_API_KEY')
    anthropic_api_key = os.environ.get('ANTHROPIC_API_KEY')
    openai_api_key = os.environ.get('OPENAI_API_KEY')

    # Validate required environment variables
    print("=" * 70)
    print("DEPLOYMENT VALIDATION")
    print("=" * 70)

    missing = []
    if not api_key:
        missing.append('LANGSMITH_API_KEY')
    if not workspace_id:
        missing.append('WORKSPACE_ID')
    if not integration_id:
        missing.append('INTEGRATION_ID')

    if missing:
        print("ERROR: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nThese must be set as GitHub Secrets.")
        print("See: DEPLOYMENT_WORKFLOW_PLAN.md Phase 2")
        sys.exit(1)

    print(f"LANGSMITH_API_KEY: {'set' if api_key else 'MISSING'}")
    print(f"WORKSPACE_ID: {workspace_id[:20]}..." if workspace_id else "MISSING")
    print(f"INTEGRATION_ID: {integration_id[:20]}..." if integration_id else "MISSING")
    print(f"LLAMA_CLOUD_API_KEY: {'set' if llama_api_key else 'not set'}")
    print(f"ANTHROPIC_API_KEY: {'set' if anthropic_api_key else 'not set'}")
    print(f"OPENAI_API_KEY: {'set' if openai_api_key else 'not set'}")
    print("=" * 70)

    # Create LangSmith client
    try:
        client = LangSmithDeployClient(
            api_key=api_key,
            workspace_id=workspace_id
        )
        print("Client initialized successfully")
    except Exception as e:
        print(f"ERROR: Failed to initialize client: {e}")
        sys.exit(1)

    # Prepare secrets for deployment
    secrets = {}
    if llama_api_key:
        secrets['LLAMA_CLOUD_API_KEY'] = llama_api_key
    if anthropic_api_key:
        secrets['ANTHROPIC_API_KEY'] = anthropic_api_key
    if openai_api_key:
        secrets['OPENAI_API_KEY'] = openai_api_key

    # Build GitHub repository URL
    repo_url = f"https://github.com/{args.repo}"

    print("\n" + "=" * 70)
    print("DEPLOYMENT CONFIGURATION")
    print("=" * 70)
    print(f"Name: {args.name}")
    print(f"Repository: {repo_url}")
    print(f"Branch: {args.branch}")
    print(f"Config file: {args.config}")
    print(f"Secrets configured: {len(secrets)}")
    print(f"Wait for completion: {args.wait}")
    if args.wait:
        print(f"Wait timeout: {args.wait_timeout}s ({args.wait_timeout // 60} minutes)")
    print("=" * 70)

    try:
        # Check if deployment already exists
        print("\nChecking for existing deployment...")
        deployments = client.list_deployments()
        existing = next((d for d in deployments if d['name'] == args.name), None)

        if existing:
            deployment_id = existing['id']
            print(f"Found existing deployment: {deployment_id}")
            print("Updating deployment (creates new revision)...")

            deployment = client.update_deployment(
                deployment_id=deployment_id,
                branch=args.branch,
                secrets=secrets if secrets else None
            )
            print("Deployment updated successfully")
        else:
            print("No existing deployment found")
            print("Creating new deployment...")

            deployment = client.create_deployment(
                name=args.name,
                source='github',
                repo_url=repo_url,
                branch=args.branch,
                config_path=args.config,
                integration_id=integration_id,
                secrets=secrets,
                deployment_type='dev',  # Use 'dev' for free tier
                build_on_push=True
            )
            print("Deployment created successfully")

        deployment_id = deployment['id']
        revision_id = deployment.get('latest_revision_id')

        print("\n" + "=" * 70)
        print("DEPLOYMENT SUBMITTED")
        print("=" * 70)
        print(f"Deployment ID: {deployment_id}")
        print(f"Revision ID: {revision_id}")
        print("=" * 70)

        # Wait for deployment if requested
        if args.wait and revision_id:
            print("\n" + "=" * 70)
            print("WAITING FOR DEPLOYMENT TO COMPLETE")
            print("=" * 70)
            print(f"This may take 15-30 minutes...")
            print(f"Timeout: {args.wait_timeout}s")
            print("=" * 70)

            success = client.wait_for_revision_deployed(
                deployment_id=deployment_id,
                revision_id=revision_id,
                timeout=args.wait_timeout,
                poll_interval=60  # Check every 60 seconds
            )

            if success:
                # Get final deployment info
                final_deployment = client.get_deployment(deployment_id)
                deployment_url = final_deployment.get('url')

                # Save deployment info to file
                deployment_info = {
                    'deployment_id': deployment_id,
                    'revision_id': revision_id,
                    'name': args.name,
                    'url': deployment_url,
                    'status': 'deployed',
                    'branch': args.branch,
                    'config_path': args.config
                }

                output_file = Path('.deployment.json')
                with open(output_file, 'w') as f:
                    json.dump(deployment_info, f, indent=2)

                print("\n" + "=" * 70)
                print("DEPLOYMENT SUCCESS")
                print("=" * 70)
                print(f"Deployment URL: {deployment_url}")
                print(f"Health endpoint: {deployment_url}/ok")
                print(f"MCP endpoint: {deployment_url}/mcp")
                print(f"\nDeployment info saved to: {output_file.absolute()}")
                print("=" * 70)

                # Set GitHub Actions output if running in CI
                github_output = os.environ.get('GITHUB_OUTPUT')
                if github_output:
                    with open(github_output, 'a') as f:
                        f.write(f"deployment_url={deployment_url}\n")
                        f.write(f"deployment_id={deployment_id}\n")

                sys.exit(0)

        elif not revision_id:
            print("\nWARNING: No revision ID returned")
            print("Deployment may not have triggered a build")
            print("Check LangSmith UI for status")
            sys.exit(0)

        else:
            print("\nDeployment submitted successfully")
            print("Not waiting for completion (--wait not specified)")
            print(f"Monitor status at: https://smith.langchain.com/deployments/{deployment_id}")
            sys.exit(0)

    except DeploymentError as e:
        print("\n" + "=" * 70)
        print("DEPLOYMENT FAILED")
        print("=" * 70)
        print(f"Error: {e}")
        print("\nTroubleshooting steps:")
        print("1. Check LangSmith deployment logs")
        print("2. Verify GitHub integration is connected")
        print("3. Check repository permissions")
        print("4. Validate config file syntax")
        print("=" * 70)
        sys.exit(1)

    except DeploymentTimeoutError as e:
        print("\n" + "=" * 70)
        print("DEPLOYMENT TIMEOUT")
        print("=" * 70)
        print(f"Error: {e}")
        print("\nDeployment may still be in progress.")
        print("Check status at:")
        print(f"  https://smith.langchain.com/deployments/{deployment_id}")
        print("=" * 70)
        sys.exit(1)

    except Exception as e:
        print("\n" + "=" * 70)
        print("UNEXPECTED ERROR")
        print("=" * 70)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        sys.exit(1)

if __name__ == '__main__':
    main()
