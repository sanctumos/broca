"""
Retry utilities with exponential backoff and jitter.

Copyright (C) 2024 Sanctum OS

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import asyncio
import logging
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: bool = True,
        exponential_base: float = 2.0,
    ):
        """Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            base_delay: Base delay in seconds for first retry
            max_delay: Maximum delay in seconds
            jitter: Whether to add random jitter to delays
            exponential_base: Base for exponential backoff calculation
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter
        self.exponential_base = exponential_base


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """Circuit breaker pattern implementation."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 300.0,
        expected_exception: type[Exception] = Exception,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds before attempting to close circuit
            expected_exception: Exception type to count as failures
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def can_execute(self) -> bool:
        """Check if execution is allowed."""
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            if self.last_failure_time is None:
                return False

            # Check if timeout has passed
            if asyncio.get_event_loop().time() - self.last_failure_time >= self.timeout:
                self.state = "HALF_OPEN"
                return True

            return False

        # HALF_OPEN state
        return True

    def record_success(self):
        """Record a successful execution."""
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Record a failed execution."""
        self.failure_count += 1
        self.last_failure_time = asyncio.get_event_loop().time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"


async def exponential_backoff(
    func: Callable[[], Awaitable[T]],
    config: RetryConfig | None = None,
    circuit_breaker: CircuitBreaker | None = None,
    retry_on_exception: Callable[[Exception], bool] | None = None,
) -> T:
    """Execute function with exponential backoff and optional circuit breaker.

    Args:
        func: Async function to execute
        config: Retry configuration
        circuit_breaker: Optional circuit breaker
        retry_on_exception: Function to determine if exception should be retried

    Returns:
        Result of function execution

    Raises:
        CircuitBreakerError: If circuit breaker is open
        Exception: Last exception if all retries exhausted
    """
    if config is None:
        config = RetryConfig()

    if retry_on_exception is None:

        def retry_on_exception(e):
            return True

    for attempt in range(config.max_retries + 1):
        # Check circuit breaker
        if circuit_breaker and not circuit_breaker.can_execute():
            raise CircuitBreakerError("Circuit breaker is open")

        try:
            result = await func()
            # Record success in circuit breaker
            if circuit_breaker:
                circuit_breaker.record_success()
            return result

        except Exception as e:
            # Check if we should retry this exception
            if not retry_on_exception(e):
                logger.debug(f"Exception not retryable: {type(e).__name__}: {e}")
                raise

            # Record failure in circuit breaker
            if circuit_breaker:
                circuit_breaker.record_failure()

            # If this was the last attempt, raise the exception
            if attempt == config.max_retries:
                logger.error(
                    f"All {config.max_retries} retry attempts exhausted. "
                    f"Last error: {type(e).__name__}: {e}"
                )
                raise

            # Calculate delay with exponential backoff
            delay = min(
                config.base_delay * (config.exponential_base**attempt),
                config.max_delay,
            )

            # Add jitter to prevent thundering herd
            if config.jitter:
                jitter_factor = 0.5 + random.random() * 0.5
                delay *= jitter_factor

            logger.warning(
                f"Attempt {attempt + 1} failed with {type(e).__name__}: {e}. "
                f"Retrying in {delay:.2f} seconds..."
            )

            await asyncio.sleep(delay)


def is_retryable_exception(exception: Exception) -> bool:
    """Determine if an exception should be retried.

    Args:
        exception: Exception to check

    Returns:
        True if exception should be retried
    """
    # Retry on network-related exceptions
    retryable_types = (
        ConnectionError,
        TimeoutError,
        OSError,
    )

    # Check exception type
    if isinstance(exception, retryable_types):
        return True

    # Check exception name for common retryable errors
    exception_name = type(exception).__name__.lower()
    retryable_names = (
        "connectionerror",
        "timeouterror",
        "httperror",
        "requestexception",
        "apierror",
        "serviceunavailable",
        "badgateway",
        "gatewaytimeout",
        "internalservererror",
    )

    return any(name in exception_name for name in retryable_names)


def is_rate_limit_exception(exception: Exception) -> bool:
    """Determine if an exception is rate limit related.

    Args:
        exception: Exception to check

    Returns:
        True if exception is rate limit related
    """
    exception_name = type(exception).__name__.lower()
    exception_str = str(exception).lower()

    rate_limit_names = (
        "ratelimitexceeded",
        "toomanyrequests",
        "quotaexceeded",
        "throttled",
        "ratelimit",
    )

    return any(
        name in exception_name or name in exception_str for name in rate_limit_names
    )


def get_retry_config_for_exception(exception: Exception) -> RetryConfig:
    """Get appropriate retry config based on exception type.

    Args:
        exception: Exception to analyze

    Returns:
        RetryConfig appropriate for the exception type
    """
    if is_rate_limit_exception(exception):
        # Use longer delays for rate limiting
        return RetryConfig(
            max_retries=5,
            base_delay=5.0,
            max_delay=300.0,
            jitter=True,
        )

    # Default retry config
    return RetryConfig(
        max_retries=3,
        base_delay=1.0,
        max_delay=60.0,
        jitter=True,
    )
