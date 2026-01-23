"""LangSmith Cloud Deployment Client - Control Plane API Wrapper.

This module provides a Python wrapper for the LangSmith Control Plane API,
enabling programmatic deployment management without using the web UI.

Example usage:
    >>> from deployment import LangSmithDeployClient
    >>> client = LangSmithDeployClient.from_env()
    >>> deployment = client.create_deployment(
    ...     name="my-agent",
    ...     repo_url="https://github.com/user/repo",
    ...     branch="main"
    ... )
    >>> print(deployment["id"])
"""

import os
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    DeploymentError,
    DeploymentTimeoutError,
    DeploymentNotFoundError,
    APIError
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ResourceSpec:
    """Resource specification for deployment."""
    min_scale: int = 1
    max_scale: int = 1
    cpu: int = 1
    memory_mb: int = 1024

    def to_dict(self) -> dict:
        return {
            "min_scale": self.min_scale,
            "max_scale": self.max_scale,
            "cpu": self.cpu,
            "memory_mb": self.memory_mb
        }


class LangSmithDeployClient:
    """Client for LangSmith Cloud Deployment via Control Plane API.

    This client wraps the Control Plane REST API, providing Python methods
    for creating, updating, and managing deployments programmatically.

    Attributes:
        api_key: LangSmith API key
        workspace_id: LangSmith workspace/tenant ID
        base_url: Control Plane API base URL
    """

    DEFAULT_BASE_URL = "https://api.host.langchain.com"
    DEFAULT_TIMEOUT = 30
    DEFAULT_WAIT_TIMEOUT = 600  # 10 minutes

    def __init__(
        self,
        api_key: str,
        workspace_id: str,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT
    ):
        """Initialize LangSmith Deploy Client.

        Args:
            api_key: LangSmith API key (lsv2_sk_...)
            workspace_id: Workspace/tenant ID
            base_url: Control Plane API URL (defaults to US region)
            timeout: Default timeout for API requests in seconds
        """
        self.api_key = api_key
        self.workspace_id = workspace_id
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.timeout = timeout

        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PATCH", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    @classmethod
    def from_env(cls, **kwargs) -> "LangSmithDeployClient":
        """Create client from environment variables.

        Reads LANGSMITH_API_KEY and WORKSPACE_ID from environment.

        Returns:
            Configured LangSmithDeployClient instance

        Raises:
            ValueError: If required environment variables are missing
        """
        api_key = os.getenv("LANGSMITH_API_KEY")
        workspace_id = os.getenv("WORKSPACE_ID")

        if not api_key:
            raise ValueError("LANGSMITH_API_KEY environment variable not set")
        if not workspace_id:
            raise ValueError("WORKSPACE_ID environment variable not set")

        return cls(api_key=api_key, workspace_id=workspace_id, **kwargs)

    def _headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "X-Api-Key": self.api_key,
            "X-Tenant-Id": self.workspace_id,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def _request(
        self,
        method: str,
        endpoint: str,
        json: Optional[dict] = None,
        params: Optional[dict] = None
    ) -> dict:
        """Make HTTP request to Control Plane API.

        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint path
            json: JSON body for request
            params: Query parameters

        Returns:
            Response JSON as dict

        Raises:
            APIError: If API returns error status
        """
        url = f"{self.base_url}{endpoint}"

        logger.debug(f"{method} {url}")
        if json:
            logger.debug(f"Request body: {json}")

        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=self._headers(),
                json=json,
                params=params,
                timeout=self.timeout
            )

            # Log response
            logger.debug(f"Response status: {response.status_code}")

            # Handle errors
            if response.status_code >= 400:
                error_msg = f"{method} {endpoint} failed with status {response.status_code}"
                try:
                    error_body = response.json()
                    error_msg += f": {error_body}"
                except:
                    error_msg += f": {response.text[:200]}"

                raise APIError(
                    error_msg,
                    status_code=response.status_code,
                    response_body=response.text
                )

            # Return JSON response
            return response.json()

        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}")

    # ==================== DEPLOYMENT MANAGEMENT ====================

    def create_deployment(
        self,
        name: str,
        source: str = "github",
        repo_url: Optional[str] = None,
        branch: str = "main",
        config_path: str = "langgraph.json",
        integration_id: Optional[str] = None,
        image_uri: Optional[str] = None,
        secrets: Optional[Dict[str, str]] = None,
        resource_spec: Optional[ResourceSpec] = None,
        deployment_type: str = "dev",
        build_on_push: bool = False,
        dry_run: bool = False
    ) -> dict:
        """Create a new deployment.

        Args:
            name: Deployment name
            source: Deployment source ("github" or "external_docker")
            repo_url: GitHub repository URL (required if source=github)
            branch: Git branch to deploy (default: main)
            config_path: Path to langgraph.json in repo
            integration_id: GitHub integration ID (from env if not provided)
            image_uri: Docker image URI (required if source=external_docker)
            secrets: Dictionary of secret name -> value
            resource_spec: Resource allocation spec
            deployment_type: "dev" or "prod"
            build_on_push: Auto-build on git push
            dry_run: If True, print what would be created without executing

        Returns:
            Deployment object dict with id, name, url, status, etc.

        Raises:
            InvalidConfigError: If required parameters missing
            APIError: If API request fails
        """
        # Validation
        if source == "github" and not repo_url:
            raise ValueError("repo_url required for GitHub deployments")
        if source == "external_docker" and not image_uri:
            raise ValueError("image_uri required for Docker deployments")

        # Get integration ID from env if not provided
        if source == "github" and not integration_id:
            integration_id = os.getenv("INTEGRATION_ID")
            if not integration_id:
                raise ValueError("integration_id or INTEGRATION_ID env var required")

        # Build request body
        request_body = {
            "name": name,
            "source": source
        }

        # Source config
        if source == "github":
            request_body["source_config"] = {
                "integration_id": integration_id,
                "repo_url": repo_url,
                "deployment_type": deployment_type,
                "build_on_push": build_on_push
            }
            if resource_spec:
                request_body["source_config"]["resource_spec"] = resource_spec.to_dict()

        # Source revision config
        if source == "github":
            request_body["source_revision_config"] = {
                "repo_ref": branch,
                "langgraph_config_path": config_path
            }
        elif source == "external_docker":
            request_body["source_revision_config"] = {
                "image_uri": image_uri
            }

        # Secrets
        if secrets:
            request_body["secrets"] = [
                {"name": k, "value": v} for k, v in secrets.items()
            ]

        # Dry run
        if dry_run:
            logger.info("DRY RUN - Would create deployment:")
            logger.info(f"Request: {request_body}")
            return {"dry_run": True, "request": request_body}

        # Create deployment
        logger.info(f"Creating deployment '{name}'...")
        deployment = self._request("POST", "/v2/deployments", json=request_body)

        deployment_id = deployment.get('id')
        latest_revision_id = deployment.get('latest_revision_id')

        logger.info(f"SUCCESS: Deployment created: {deployment_id}")
        if latest_revision_id:
            logger.info(f"Latest revision ID: {latest_revision_id}")
            logger.info(f"Use wait_for_revision_deployed() to monitor deployment progress")

        return deployment

    def list_deployments(self, limit: int = 100, offset: int = 0) -> List[dict]:
        """List all deployments in workspace.

        Args:
            limit: Maximum number of deployments to return
            offset: Offset for pagination

        Returns:
            List of deployment dicts
        """
        logger.info("Listing deployments...")
        params = {"limit": limit, "offset": offset}
        response = self._request("GET", "/v2/deployments", params=params)

        deployments = response.get("deployments", [])
        logger.info(f"Found {len(deployments)} deployment(s)")
        return deployments

    def get_deployment(self, deployment_id: str) -> dict:
        """Get deployment details by ID.

        Args:
            deployment_id: Deployment ID

        Returns:
            Deployment object dict

        Raises:
            DeploymentNotFoundError: If deployment not found
        """
        logger.info(f"Getting deployment {deployment_id}...")
        try:
            deployment = self._request("GET", f"/v2/deployments/{deployment_id}")
            return deployment
        except APIError as e:
            if e.status_code == 404:
                raise DeploymentNotFoundError(f"Deployment {deployment_id} not found")
            raise

    def update_deployment(
        self,
        deployment_id: str,
        branch: Optional[str] = None,
        image_uri: Optional[str] = None,
        secrets: Optional[Dict[str, str]] = None,
        dry_run: bool = False
    ) -> dict:
        """Update deployment (creates new revision).

        Args:
            deployment_id: Deployment ID to update
            branch: New git branch (if GitHub deployment)
            image_uri: New Docker image URI (if Docker deployment)
            secrets: Updated secrets
            dry_run: Preview changes without applying

        Returns:
            Updated deployment object
        """
        update_body = {}

        if branch:
            update_body["source_revision_config"] = {
                "repo_ref": branch
            }

        if image_uri:
            update_body["source_revision_config"] = {
                "image_uri": image_uri
            }

        if secrets:
            update_body["secrets"] = [
                {"name": k, "value": v} for k, v in secrets.items()
            ]

        if dry_run:
            logger.info("DRY RUN - Would update deployment:")
            logger.info(f"Update: {update_body}")
            return {"dry_run": True, "update": update_body}

        logger.info(f"Updating deployment {deployment_id}...")
        deployment = self._request(
            "PATCH",
            f"/v2/deployments/{deployment_id}",
            json=update_body
        )

        latest_revision_id = deployment.get('latest_revision_id')

        logger.info(f"SUCCESS: Deployment updated")
        if latest_revision_id:
            logger.info(f"New revision ID: {latest_revision_id}")
            logger.info(f"Use wait_for_revision_deployed() to monitor deployment progress")

        return deployment

    def delete_deployment(self, deployment_id: str, confirm: bool = False) -> bool:
        """Delete a deployment.

        Args:
            deployment_id: Deployment ID to delete
            confirm: Must be True to actually delete

        Returns:
            True if deleted successfully

        Raises:
            ValueError: If confirm is False
        """
        if not confirm:
            raise ValueError("Must pass confirm=True to delete deployment")

        logger.warning(f"Deleting deployment {deployment_id}...")
        self._request("DELETE", f"/v2/deployments/{deployment_id}")

        logger.info(f"✅ Deployment deleted")
        return True

    # ==================== STATUS & MONITORING ====================

    def get_deployment_status(self, deployment_id: str) -> dict:
        """Get current deployment status.

        Args:
            deployment_id: Deployment ID

        Returns:
            Status dict with state, health, url, etc.
        """
        deployment = self.get_deployment(deployment_id)
        return {
            "id": deployment.get("id"),
            "name": deployment.get("name"),
            "state": deployment.get("state"),
            "health": deployment.get("health"),
            "url": deployment.get("url"),
            "updated_at": deployment.get("updated_at")
        }

    def wait_for_deployment(
        self,
        deployment_id: str,
        timeout: int = DEFAULT_WAIT_TIMEOUT,
        poll_interval: int = 10
    ) -> bool:
        """Wait for deployment to become healthy.

        Args:
            deployment_id: Deployment ID
            timeout: Maximum seconds to wait
            poll_interval: Seconds between status checks

        Returns:
            True if deployment became healthy

        Raises:
            DeploymentTimeoutError: If timeout exceeded
        """
        logger.info(f"Waiting for deployment {deployment_id} to become healthy...")
        start_time = time.time()

        while time.time() - start_time < timeout:
            status = self.get_deployment_status(deployment_id)

            logger.info(f"Status: {status.get('state')} / {status.get('health')}")

            if status.get("health") == "healthy":
                logger.info(f"✅ Deployment is healthy! URL: {status.get('url')}")
                return True

            if status.get("state") in ["failed", "error"]:
                raise DeploymentError(f"Deployment failed: {status}")

            time.sleep(poll_interval)

        raise DeploymentTimeoutError(
            f"Deployment did not become healthy within {timeout} seconds"
        )

    # ==================== REVISIONS ====================

    def list_revisions(self, deployment_id: str) -> List[dict]:
        """List all revisions for a deployment.

        Args:
            deployment_id: Deployment ID

        Returns:
            List of revision dicts
        """
        logger.info(f"Listing revisions for deployment {deployment_id}...")
        response = self._request("GET", f"/v2/deployments/{deployment_id}/revisions")

        revisions = response.get("revisions", [])
        logger.info(f"Found {len(revisions)} revision(s)")
        return revisions

    def redeploy_revision(self, deployment_id: str, revision_id: str) -> dict:
        """Redeploy a specific revision.

        Args:
            deployment_id: Deployment ID
            revision_id: Revision ID to redeploy

        Returns:
            Updated deployment object
        """
        logger.info(f"Redeploying revision {revision_id}...")
        deployment = self._request(
            "POST",
            f"/v2/deployments/{deployment_id}/revisions/{revision_id}/redeploy"
        )

        logger.info(f"✅ Revision redeployed")
        return deployment

    def get_revision_status(self, deployment_id: str, revision_id: str) -> dict:
        """Get status of a specific revision.

        This is the official pattern for deployment monitoring. Poll this endpoint
        to check if a revision has reached DEPLOYED status.

        Args:
            deployment_id: Deployment ID
            revision_id: Revision ID

        Returns:
            Revision object with status field

        Raises:
            DeploymentNotFoundError: If deployment or revision not found
        """
        logger.debug(f"Getting revision {revision_id} status...")
        try:
            revision = self._request(
                "GET",
                f"/v2/deployments/{deployment_id}/revisions/{revision_id}"
            )
            return revision
        except APIError as e:
            if e.status_code == 404:
                raise DeploymentNotFoundError(
                    f"Revision {revision_id} not found in deployment {deployment_id}"
                )
            raise

    def wait_for_revision_deployed(
        self,
        deployment_id: str,
        revision_id: str,
        timeout: int = 1800,  # 30 minutes default (builds can take time)
        poll_interval: int = 60  # Official pattern: 60 second intervals
    ) -> bool:
        """Wait for revision to reach DEPLOYED status (official pattern).

        This is the CORRECT way to monitor deployments according to official
        LangSmith patterns. Poll the revision status, not the deployment health.

        Args:
            deployment_id: Deployment ID
            revision_id: Revision ID to monitor
            timeout: Maximum seconds to wait (default: 30 minutes)
            poll_interval: Seconds between status checks (default: 60)

        Returns:
            True if revision reached DEPLOYED status

        Raises:
            DeploymentError: If revision fails
            DeploymentTimeoutError: If timeout exceeded

        Official Status Flow:
            PENDING → BUILDING → DEPLOYING → DEPLOYED
            or PENDING → FAILED_*
        """
        logger.info(f"Waiting for revision {revision_id} to deploy...")
        logger.info(f"Timeout: {timeout}s, Poll interval: {poll_interval}s")

        start_time = time.time()
        last_status = None

        while time.time() - start_time < timeout:
            try:
                revision = self.get_revision_status(deployment_id, revision_id)
                status = revision.get("status", "UNKNOWN")

                # Only log when status changes
                if status != last_status:
                    elapsed = int(time.time() - start_time)
                    logger.info(f"Revision status: {status} (elapsed: {elapsed}s)")
                    last_status = status

                # Check for success
                if status == "DEPLOYED":
                    logger.info(f"SUCCESS: Revision deployed successfully!")
                    deployment = self.get_deployment(deployment_id)
                    if deployment.get("url"):
                        logger.info(f"Deployment URL: {deployment['url']}")
                    return True

                # Check for failure states (all FAILED_* statuses)
                if "FAILED" in status:
                    error_details = revision.get("error_message", "No error details available")
                    raise DeploymentError(
                        f"Revision deployment failed with status '{status}': {error_details}"
                    )

                # Sleep before next poll
                time.sleep(poll_interval)

            except DeploymentNotFoundError:
                # Revision might not exist yet immediately after creation
                logger.debug(f"Revision not found yet, will retry...")
                time.sleep(poll_interval)
            except APIError as e:
                # Log API errors but continue polling
                logger.warning(f"API error while polling: {e}")
                time.sleep(poll_interval)

        # Timeout exceeded
        raise DeploymentTimeoutError(
            f"Revision {revision_id} did not reach DEPLOYED status within {timeout} seconds. "
            f"Last status: {last_status}"
        )

    def rollback_to_previous(self, deployment_id: str) -> dict:
        """Rollback deployment to the previous successful revision.

        Args:
            deployment_id: Deployment ID

        Returns:
            Updated deployment object after rollback

        Raises:
            DeploymentError: If no previous revision to rollback to
        """
        logger.warning(f"Rolling back deployment {deployment_id}...")

        # Get revision history
        revisions = self.list_revisions(deployment_id)

        if len(revisions) < 2:
            raise DeploymentError(
                "No previous revision to rollback to (only one revision exists)"
            )

        # Find the last DEPLOYED revision (skip current revision)
        deployed_revisions = [
            r for r in revisions
            if r.get("status") == "DEPLOYED"
        ]

        if len(deployed_revisions) < 2:
            raise DeploymentError(
                "No previous successful revision found to rollback to"
            )

        # Get the second most recent deployed revision
        previous_revision = deployed_revisions[1]
        previous_revision_id = previous_revision["id"]

        logger.info(f"Rolling back to revision: {previous_revision_id}")
        logger.info(f"Previous revision status: {previous_revision.get('status')}")

        # Redeploy the previous revision
        deployment = self.redeploy_revision(deployment_id, previous_revision_id)

        logger.info(f"SUCCESS: Rollback initiated")
        return deployment

    # ==================== CONVENIENCE METHODS ====================

    def create_github_deployment(
        self,
        name: str,
        repo_url: str,
        branch: str = "main",
        **kwargs
    ) -> dict:
        """Convenience method for GitHub deployments.

        Args:
            name: Deployment name
            repo_url: GitHub repository URL
            branch: Git branch
            **kwargs: Additional arguments for create_deployment

        Returns:
            Deployment object
        """
        return self.create_deployment(
            name=name,
            source="github",
            repo_url=repo_url,
            branch=branch,
            **kwargs
        )

    def create_docker_deployment(
        self,
        name: str,
        image_uri: str,
        **kwargs
    ) -> dict:
        """Convenience method for Docker registry deployments.

        Args:
            name: Deployment name
            image_uri: Docker image URI (e.g., docker.io/user/image:tag)
            **kwargs: Additional arguments for create_deployment

        Returns:
            Deployment object
        """
        return self.create_deployment(
            name=name,
            source="external_docker",
            image_uri=image_uri,
            **kwargs
        )
