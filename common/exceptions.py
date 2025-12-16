"""Common exceptions for broca2.

This module provides a comprehensive exception hierarchy for the Broca application.
All exceptions inherit from BrocaError, which provides context and recoverability information.
"""

from typing import Any


class BrocaError(Exception):
    """Base exception for all Broca errors.
    
    This exception provides:
    - Structured error messages
    - Context information for debugging
    - Recoverability flag for retry logic
    
    Args:
        message: Human-readable error message
        context: Optional dictionary with additional context
        recoverable: Whether this error is recoverable (default: False)
    """

    def __init__(
        self, message: str, context: dict[str, Any] | None = None, recoverable: bool = False
    ):
        """Initialize the exception.
        
        Args:
            message: Human-readable error message
            context: Optional dictionary with additional context information
            recoverable: Whether this error is recoverable (default: False)
        """
        self.message = message
        self.context = context or {}
        self.recoverable = recoverable
        super().__init__(self.message)

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} (context: {context_str})"
        return self.message


class PluginError(BrocaError):
    """Exception raised for plugin-related errors.
    
    This exception is used when:
    - Plugin loading fails
    - Plugin initialization fails
    - Plugin operations fail
    - Plugin configuration is invalid
    """

    def __init__(
        self,
        message: str,
        plugin_name: str | None = None,
        context: dict[str, Any] | None = None,
        recoverable: bool = False,
    ):
        """Initialize plugin error.
        
        Args:
            message: Error message
            plugin_name: Name of the plugin that caused the error
            context: Additional context information
            recoverable: Whether this error is recoverable
        """
        if plugin_name:
            context = context or {}
            context["plugin_name"] = plugin_name
        super().__init__(message, context, recoverable)


class ConfigurationError(BrocaError):
    """Exception raised for configuration errors.
    
    This exception is used when:
    - Configuration files are invalid
    - Required configuration is missing
    - Configuration values are out of range
    """

    def __init__(
        self,
        message: str,
        config_key: str | None = None,
        context: dict[str, Any] | None = None,
        recoverable: bool = True,
    ):
        """Initialize configuration error.
        
        Args:
            message: Error message
            config_key: Configuration key that caused the error
            context: Additional context information
            recoverable: Configuration errors are usually recoverable (default: True)
        """
        if config_key:
            context = context or {}
            context["config_key"] = config_key
        super().__init__(message, context, recoverable)


class DatabaseError(BrocaError):
    """Exception raised for database operation errors.
    
    This exception is used when:
    - Database connections fail
    - SQL queries fail
    - Database transactions fail
    - Database migrations fail
    """

    def __init__(
        self,
        message: str,
        operation: str | None = None,
        context: dict[str, Any] | None = None,
        recoverable: bool = True,
    ):
        """Initialize database error.
        
        Args:
            message: Error message
            operation: Database operation that failed
            context: Additional context information
            recoverable: Database errors may be recoverable (default: True)
        """
        if operation:
            context = context or {}
            context["operation"] = operation
        super().__init__(message, context, recoverable)


class ValidationError(BrocaError):
    """Exception raised for validation errors.
    
    This exception is used when:
    - Input validation fails
    - Data validation fails
    - Schema validation fails
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
        context: dict[str, Any] | None = None,
        recoverable: bool = False,
    ):
        """Initialize validation error.
        
        Args:
            message: Error message
            field: Field that failed validation
            value: Value that failed validation
            context: Additional context information
            recoverable: Validation errors are usually not recoverable (default: False)
        """
        if field:
            context = context or {}
            context["field"] = field
            if value is not None:
                context["value"] = str(value)[:100]  # Limit value length
        super().__init__(message, context, recoverable)


class NetworkError(BrocaError):
    """Exception raised for network/API errors.
    
    This exception is used when:
    - API requests fail
    - Network connections fail
    - Timeouts occur
    - HTTP errors occur
    """

    def __init__(
        self,
        message: str,
        url: str | None = None,
        status_code: int | None = None,
        context: dict[str, Any] | None = None,
        recoverable: bool = True,
    ):
        """Initialize network error.
        
        Args:
            message: Error message
            url: URL that caused the error
            status_code: HTTP status code (if applicable)
            context: Additional context information
            recoverable: Network errors are often recoverable (default: True)
        """
        if url or status_code:
            context = context or {}
            if url:
                context["url"] = url
            if status_code:
                context["status_code"] = status_code
        super().__init__(message, context, recoverable)
