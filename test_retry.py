"""Tests for retry utilities with exponential backoff."""

import asyncio
import logging
from unittest.mock import patch

from common.retry import (
    CircuitBreaker,
    CircuitBreakerError,
    RetryConfig,
    exponential_backoff,
    is_rate_limit_exception,
    is_retryable_exception,
)


async def test_exponential_backoff_success():
    """Test exponential backoff with successful function."""
    call_count = 0

    async def successful_func():
        nonlocal call_count
        call_count += 1
        return "success"

    result = await exponential_backoff(successful_func, RetryConfig(max_retries=3))
    assert result == "success"
    assert call_count == 1


async def test_exponential_backoff_retry():
    """Test exponential backoff with retryable failures."""
    call_count = 0

    async def failing_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("Connection failed")
        return "success"

    result = await exponential_backoff(failing_func, RetryConfig(max_retries=3))
    assert result == "success"
    assert call_count == 3


async def test_exponential_backoff_max_retries():
    """Test exponential backoff exhausting retries."""
    call_count = 0

    async def always_failing_func():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("Always fails")

    try:
        await exponential_backoff(always_failing_func, RetryConfig(max_retries=2))
        raise AssertionError("Should have raised exception")
    except ConnectionError as e:
        assert str(e) == "Always fails"
        assert call_count == 3  # Initial + 2 retries


async def test_circuit_breaker():
    """Test circuit breaker functionality."""
    breaker = CircuitBreaker(failure_threshold=2, timeout=1.0)

    # Should allow execution initially
    assert breaker.can_execute() is True

    # Record failures
    breaker.record_failure()
    breaker.record_failure()

    # Should block execution after threshold
    assert breaker.can_execute() is False

    # Wait for timeout
    await asyncio.sleep(1.1)

    # Should allow execution again (half-open)
    assert breaker.can_execute() is True

    # Record success
    breaker.record_success()

    # Should be closed again
    assert breaker.can_execute() is True


async def test_circuit_breaker_with_retry():
    """Test circuit breaker integration with retry logic."""
    breaker = CircuitBreaker(failure_threshold=1, timeout=0.1)
    call_count = 0

    async def failing_func():
        nonlocal call_count
        call_count += 1
        raise ConnectionError("Connection failed")

    # First call should fail and open circuit breaker
    try:
        await exponential_backoff(
            failing_func,
            RetryConfig(max_retries=1),
            circuit_breaker=breaker,
        )
        raise AssertionError("Should have raised exception")
    except ConnectionError:
        pass

    # Second call should be blocked by circuit breaker
    try:
        await exponential_backoff(
            failing_func,
            RetryConfig(max_retries=1),
            circuit_breaker=breaker,
        )
        raise AssertionError("Should have raised CircuitBreakerError")
    except CircuitBreakerError:
        pass

    # Wait for circuit breaker timeout
    await asyncio.sleep(0.2)

    # Should work again
    call_count = 0
    try:
        await exponential_backoff(
            failing_func,
            RetryConfig(max_retries=1),
            circuit_breaker=breaker,
        )
        raise AssertionError("Should have raised exception")
    except ConnectionError:
        pass


def test_is_retryable_exception():
    """Test retryable exception detection."""
    assert is_retryable_exception(ConnectionError("Connection failed")) is True
    assert is_retryable_exception(TimeoutError("Timeout")) is True
    assert is_retryable_exception(ValueError("Invalid value")) is False


def test_is_rate_limit_exception():
    """Test rate limit exception detection."""

    class RateLimitError(Exception):
        pass

    class TooManyRequestsError(Exception):
        pass

    assert is_rate_limit_exception(RateLimitError("Rate limit exceeded")) is True
    assert is_rate_limit_exception(TooManyRequestsError("Too many requests")) is True
    assert is_rate_limit_exception(ConnectionError("Connection failed")) is False


async def test_retry_with_jitter():
    """Test that retry delays include jitter."""
    call_count = 0
    delays = []

    async def failing_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ConnectionError("Connection failed")
        return "success"

    # Mock asyncio.sleep to capture delays
    with patch("asyncio.sleep") as mock_sleep:

        async def mock_sleep_func(delay):
            delays.append(delay)

        mock_sleep.side_effect = mock_sleep_func

        await exponential_backoff(
            failing_func,
            RetryConfig(max_retries=1, base_delay=1.0, jitter=True),
        )

        # Should have one delay
        assert len(delays) == 1
        # Delay should be between 0.5 and 1.5 (base_delay with jitter)
        assert 0.5 <= delays[0] <= 1.5


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run tests
    asyncio.run(test_exponential_backoff_success())
    asyncio.run(test_exponential_backoff_retry())
    asyncio.run(test_exponential_backoff_max_retries())
    asyncio.run(test_circuit_breaker())
    asyncio.run(test_circuit_breaker_with_retry())
    test_is_retryable_exception()
    test_is_rate_limit_exception()
    asyncio.run(test_retry_with_jitter())

    print("All retry tests passed!")
