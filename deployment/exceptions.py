"""Custom exceptions for deployment automation."""


class DeploymentError(Exception):
    """Base exception for deployment-related errors."""
    pass


class DeploymentTimeoutError(DeploymentError):
    """Raised when deployment exceeds timeout waiting for healthy status."""
    pass


class DeploymentNotFoundError(DeploymentError):
    """Raised when deployment ID not found."""
    pass


class InvalidConfigError(DeploymentError):
    """Raised when configuration is invalid."""
    pass


class APIError(DeploymentError):
    """Raised when Control Plane API returns an error."""

    def __init__(self, message, status_code=None, response_body=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
