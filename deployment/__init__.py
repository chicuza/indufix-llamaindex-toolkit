"""Deployment automation tools for LangSmith Cloud.

This package provides Python wrappers for the Control Plane API,
enabling programmatic deployment management without using the UI.
"""

from .langsmith_deploy import LangSmithDeployClient
from .exceptions import (
    DeploymentError,
    DeploymentTimeoutError,
    DeploymentNotFoundError,
    InvalidConfigError
)

__all__ = [
    "LangSmithDeployClient",
    "DeploymentError",
    "DeploymentTimeoutError",
    "DeploymentNotFoundError",
    "InvalidConfigError"
]

__version__ = "1.0.0"
