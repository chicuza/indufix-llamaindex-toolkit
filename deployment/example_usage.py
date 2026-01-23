"""Example usage of LangSmith Deployment Client.

This script demonstrates how to use the deployment automation tools.

Usage:
    python example_usage.py
"""

import os
from langsmith_deploy import LangSmithDeployClient, ResourceSpec
from exceptions import DeploymentError


def main():
    """Main example function."""

    # Initialize client from environment variables
    print("Initializing LangSmith Deploy Client...")
    client = LangSmithDeployClient.from_env()

    # Example 1: List existing deployments
    print("\n=== Example 1: List Deployments ===")
    deployments = client.list_deployments()
    print(f"Found {len(deployments)} deployment(s):")
    for dep in deployments:
        print(f"  - {dep['name']} ({dep['id']}): {dep.get('state')}/{dep.get('health')}")

    # Example 2: Create new deployment (GitHub)
    print("\n=== Example 2: Create GitHub Deployment (DRY RUN) ===")
    deployment = client.create_github_deployment(
        name="example-agent",
        repo_url="https://github.com/chicuza/indufix-llamaindex-toolkit",
        branch="main",
        secrets={
            "LLAMA_CLOUD_API_KEY": os.getenv("LLAMA_CLOUD_API_KEY", "placeholder")
        },
        resource_spec=ResourceSpec(
            min_scale=1,
            max_scale=2,
            cpu=1,
            memory_mb=1024
        ),
        deployment_type="dev",
        dry_run=True  # Don't actually create
    )
    print(f"Dry run result: {deployment}")

    # Example 3: Create Docker deployment (DRY RUN)
    print("\n=== Example 3: Create Docker Deployment (DRY RUN) ===")
    deployment = client.create_docker_deployment(
        name="example-docker-agent",
        image_uri="docker.io/username/my-agent:latest",
        secrets={
            "OPENAI_API_KEY": "sk-placeholder"
        },
        dry_run=True
    )
    print(f"Dry run result: {deployment}")

    # Example 4: Get deployment status (if any exists)
    print("\n=== Example 4: Get Deployment Status ===")
    if deployments:
        deployment_id = deployments[0]['id']
        status = client.get_deployment_status(deployment_id)
        print(f"Deployment: {status['name']}")
        print(f"  State:  {status['state']}")
        print(f"  Health: {status['health']}")
        print(f"  URL:    {status.get('url', 'N/A')}")
    else:
        print("No deployments found")

    print("\n=== Examples Complete ===")
    print("\nTo create a real deployment, remove dry_run=True from the create calls")
    print("Or use the CLI: python -m deployment.deploy_cli create --help")


if __name__ == "__main__":
    try:
        main()
    except DeploymentError as e:
        print(f"\n❌ Error: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        exit(1)
