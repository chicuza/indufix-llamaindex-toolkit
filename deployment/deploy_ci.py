#!/usr/bin/env python3
"""CI/CD orchestration script for LangSmith Cloud deployments.

This script is designed to be called from GitHub Actions (or other CI/CD systems)
to automate deployment to LangSmith Cloud using the Control Plane API.

Official Pattern:
1. Create or update deployment
2. Get latest_revision_id from response
3. Poll revision status until DEPLOYED or FAILED
4. Return appropriate exit code

Usage:
    python deploy_ci.py --env dev --config deployment/deploy_config.yaml
    python deploy_ci.py --env prod --config deployment/deploy_config_prod.yaml --wait
"""

import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

from langsmith_deploy import LangSmithDeployClient
from exceptions import (
    DeploymentError,
    DeploymentTimeoutError,
    DeploymentNotFoundError,
    APIError
)

# Configure logging for CI/CD
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str) -> Dict[str, Any]:
    """Load deployment configuration from YAML file.

    Args:
        config_path: Path to YAML config file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config is invalid YAML
    """
    config_file = Path(config_path)

    if not config_file.exists():
        logger.error(f"Config file not found: {config_path}")
        sys.exit(2)  # Exit code 2 = Configuration error

    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {config_path}")
            return config
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in config file: {e}")
        sys.exit(2)


def substitute_env_vars(value: str) -> str:
    """Substitute environment variables in string.

    Supports ${VAR_NAME} format.

    Args:
        value: String with potential env var references

    Returns:
        String with env vars substituted

    Raises:
        ValueError: If required env var is not set
    """
    if not isinstance(value, str):
        return value

    if value.startswith('${') and value.endswith('}'):
        env_var = value[2:-1]
        env_value = os.getenv(env_var)

        if env_value is None:
            logger.error(f"Required environment variable not set: {env_var}")
            sys.exit(2)

        return env_value

    return value


def process_secrets(secrets_config: Dict[str, str]) -> Dict[str, str]:
    """Process secrets configuration with env var substitution.

    Args:
        secrets_config: Secrets from config file

    Returns:
        Processed secrets dictionary
    """
    processed = {}

    for key, value in secrets_config.items():
        processed[key] = substitute_env_vars(value)

    logger.info(f"Processed {len(processed)} secret(s)")
    return processed


def create_or_update_deployment(
    client: LangSmithDeployClient,
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """Create new deployment or update existing one.

    Implements idempotent deployment: checks if deployment exists,
    updates if found, creates if not found.

    Args:
        client: LangSmith deployment client
        config: Deployment configuration

    Returns:
        Deployment object with id and latest_revision_id
    """
    deployment_config = config.get('deployment', {})
    secrets_config = config.get('secrets', {})
    resource_spec_config = config.get('resource_spec')

    name = deployment_config.get('name')
    source = deployment_config.get('source', 'github')

    if not name:
        logger.error("Deployment name is required in config")
        sys.exit(2)

    logger.info(f"Deployment name: {name}")
    logger.info(f"Source type: {source}")

    # Process secrets
    secrets = process_secrets(secrets_config) if secrets_config else None

    # Check if deployment already exists
    logger.info("Checking for existing deployment...")
    try:
        deployments = client.list_deployments()
        existing = next((d for d in deployments if d['name'] == name), None)

        if existing:
            deployment_id = existing['id']
            logger.info(f"Found existing deployment: {deployment_id}")
            logger.info("Updating deployment (creates new revision)...")

            # Update deployment
            deployment = client.update_deployment(
                deployment_id=deployment_id,
                branch=deployment_config.get('branch'),
                image_uri=deployment_config.get('image_uri'),
                secrets=secrets
            )

            logger.info("Deployment updated successfully")
            return deployment

        else:
            logger.info("No existing deployment found, creating new one...")

            # Create new deployment
            try:
                deployment = client.create_deployment(
                    name=name,
                    source=source,
                    repo_url=deployment_config.get('repo_url'),
                    branch=deployment_config.get('branch', 'main'),
                    config_path=deployment_config.get('config_path', 'langgraph.json'),
                    image_uri=deployment_config.get('image_uri'),
                    secrets=secrets,
                    deployment_type=deployment_config.get('type', 'dev')
                )

                logger.info("Deployment created successfully")
                return deployment

            except APIError as create_error:
                # Handle 409 Conflict - deployment likely exists but wasn't listed
                if create_error.status_code == 409:
                    logger.warning("Got 409 Conflict - project/deployment may already exist")
                    logger.info("Attempting to find and update existing deployment...")

                    # Try to get all deployments using pagination (API max limit is 100)
                    try:
                        all_deployments = []
                        offset = 0
                        limit = 100

                        while True:
                            batch = client.list_deployments(limit=limit, offset=offset)
                            all_deployments.extend(batch)

                            if len(batch) < limit:
                                break  # No more deployments
                            offset += limit

                        logger.info(f"Found {len(all_deployments)} total deployment(s)")
                        existing = next((d for d in all_deployments if d['name'] == name), None)

                        if existing:
                            deployment_id = existing['id']
                            logger.info(f"Found deployment: {deployment_id}")
                            logger.info("Updating deployment...")

                            deployment = client.update_deployment(
                                deployment_id=deployment_id,
                                branch=deployment_config.get('branch'),
                                image_uri=deployment_config.get('image_uri'),
                                secrets=secrets
                            )

                            logger.info("Deployment updated successfully")
                            return deployment
                        else:
                            logger.error(f"Could not find deployment '{name}' even with 409 conflict")
                            logger.error("This may indicate a project exists but deployment was deleted")
                            logger.error("Please delete the LangSmith project manually or use a different name")
                            raise create_error
                    except Exception as recovery_error:
                        logger.error(f"Recovery attempt failed: {recovery_error}")
                        raise create_error
                else:
                    raise create_error

    except APIError as e:
        logger.error(f"API error: {e}")
        if e.status_code == 401 or e.status_code == 403:
            logger.error("Authentication failed. Check your LANGSMITH_API_KEY and WORKSPACE_ID")
            sys.exit(3)  # Exit code 3 = Authentication error
        sys.exit(1)  # Exit code 1 = General error


def wait_for_deployment_ready(
    client: LangSmithDeployClient,
    deployment: Dict[str, Any],
    timeout: int = 1800
) -> bool:
    """Wait for deployment revision to reach DEPLOYED status.

    Uses the official pattern: poll revision status, not deployment health.

    Args:
        client: LangSmith deployment client
        deployment: Deployment object
        timeout: Maximum seconds to wait

    Returns:
        True if deployment succeeded

    Raises:
        SystemExit: On deployment failure or timeout
    """
    deployment_id = deployment.get('id')
    latest_revision_id = deployment.get('latest_revision_id')

    if not latest_revision_id:
        logger.warning("No revision ID in deployment response")
        logger.warning("Deployment may not have triggered a build")
        return True

    logger.info("=" * 60)
    logger.info("WAITING FOR DEPLOYMENT TO COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Deployment ID: {deployment_id}")
    logger.info(f"Revision ID: {latest_revision_id}")
    logger.info(f"Timeout: {timeout} seconds ({timeout // 60} minutes)")
    logger.info("=" * 60)

    try:
        # Use official pattern: wait for revision status
        success = client.wait_for_revision_deployed(
            deployment_id=deployment_id,
            revision_id=latest_revision_id,
            timeout=timeout
        )

        if success:
            logger.info("=" * 60)
            logger.info("DEPLOYMENT SUCCESSFUL!")
            logger.info("=" * 60)

            # Get final deployment details
            final_deployment = client.get_deployment(deployment_id)
            deployment_url = final_deployment.get('url')

            if deployment_url:
                logger.info(f"Deployment URL: {deployment_url}")
                logger.info(f"Health endpoint: {deployment_url}/ok")

            return True

    except DeploymentError as e:
        logger.error("=" * 60)
        logger.error("DEPLOYMENT FAILED")
        logger.error("=" * 60)
        logger.error(f"Error: {e}")
        logger.error("Check LangSmith UI for detailed build logs")
        sys.exit(1)  # Exit code 1 = Deployment failed

    except DeploymentTimeoutError as e:
        logger.error("=" * 60)
        logger.error("DEPLOYMENT TIMEOUT")
        logger.error("=" * 60)
        logger.error(f"Error: {e}")
        logger.error("Deployment may still be in progress")
        logger.error("Check LangSmith UI for current status")
        sys.exit(5)  # Exit code 5 = Timeout

    return False


def main():
    """Main CI/CD orchestration function."""
    parser = argparse.ArgumentParser(
        description='Deploy LangGraph application to LangSmith Cloud',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy dev environment with waiting
  python deploy_ci.py --env dev --config deploy_config.yaml --wait

  # Deploy prod environment without waiting
  python deploy_ci.py --env prod --config deploy_config_prod.yaml

  # Deploy with custom timeout
  python deploy_ci.py --env dev --config deploy_config.yaml --wait --timeout 3600
        """
    )

    parser.add_argument('--env', required=True, choices=['dev', 'prod'],
                        help='Deployment environment')
    parser.add_argument('--config', required=True,
                        help='Path to deployment config YAML file')
    parser.add_argument('--wait', action='store_true',
                        help='Wait for deployment to complete')
    parser.add_argument('--timeout', type=int, default=1800,
                        help='Timeout in seconds for waiting (default: 1800 = 30 minutes)')

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("LangSmith Cloud Deployment - CI/CD Orchestrator")
    logger.info("=" * 60)
    logger.info(f"Environment: {args.env}")
    logger.info(f"Config file: {args.config}")
    logger.info(f"Wait for completion: {args.wait}")
    logger.info("=" * 60)

    # Load configuration
    config = load_config(args.config)

    # Initialize client from environment variables
    try:
        client = LangSmithDeployClient.from_env()
        logger.info("Client initialized successfully")
    except ValueError as e:
        logger.error(f"Client initialization failed: {e}")
        logger.error("Required environment variables:")
        logger.error("  - LANGSMITH_API_KEY")
        logger.error("  - WORKSPACE_ID")
        logger.error("  - INTEGRATION_ID (for GitHub deployments)")
        sys.exit(2)  # Exit code 2 = Configuration error

    # Create or update deployment
    deployment = create_or_update_deployment(client, config)

    # Wait for deployment if requested
    if args.wait:
        wait_for_deployment_ready(client, deployment, timeout=args.timeout)
    else:
        logger.info("Deployment submitted successfully")
        logger.info("Use --wait flag to monitor deployment progress")

    logger.info("=" * 60)
    logger.info("CI/CD ORCHESTRATION COMPLETE")
    logger.info("=" * 60)

    sys.exit(0)  # Exit code 0 = Success


if __name__ == '__main__':
    main()
