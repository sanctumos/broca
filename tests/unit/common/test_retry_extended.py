"""Extended unit tests for common retry utilities."""

from unittest.mock import patch

import pytest

from common.retry import RetryConfig, exponential_backoff, is_retryable_exception


@pytest.mark.unit
def test_retry_config_initialization():
    """Test RetryConfig initialization."""
    config = RetryConfig(max_retries=5, initial_delay=1.0, max_delay=60.0)
    assert config.max_retries == 5
    assert config.initial_delay == 1.0
    assert config.max_delay == 60.0


@pytest.mark.unit
def test_retry_config_default_values():
    """Test RetryConfig default values."""
    config = RetryConfig()
    assert config.max_retries == 3
    assert config.initial_delay == 1.0
    assert config.max_delay == 60.0


@pytest.mark.unit
def test_retry_config_validation():
    """Test RetryConfig validation."""
    with pytest.raises(ValueError):
        RetryConfig(max_retries=-1)

    with pytest.raises(ValueError):
        RetryConfig(initial_delay=-1.0)

    with pytest.raises(ValueError):
        RetryConfig(max_delay=0.0)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_success_first_try():
    """Test exponential_backoff with success on first try."""
    call_count = 0

    @exponential_backoff(max_retries=3, initial_delay=0.1)
    async def test_func():
        nonlocal call_count
        call_count += 1
        return "success"

    result = await test_func()
    assert result == "success"
    assert call_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_success_after_retries():
    """Test exponential_backoff with success after retries."""
    call_count = 0

    @exponential_backoff(max_retries=3, initial_delay=0.1)
    async def test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Temporary failure")
        return "success"

    result = await test_func()
    assert result == "success"
    assert call_count == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_max_retries_exceeded():
    """Test exponential_backoff with max retries exceeded."""
    call_count = 0

    @exponential_backoff(max_retries=2, initial_delay=0.1)
    async def test_func():
        nonlocal call_count
        call_count += 1
        raise Exception("Persistent failure")

    with pytest.raises(Exception, match="Persistent failure"):
        await test_func()

    assert call_count == 3  # Initial call + 2 retries


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_custom_exception():
    """Test exponential_backoff with custom exception."""
    call_count = 0

    @exponential_backoff(max_retries=2, initial_delay=0.1)
    async def test_func():
        nonlocal call_count
        call_count += 1
        raise ValueError("Custom error")

    with pytest.raises(ValueError, match="Custom error"):
        await test_func()

    assert call_count == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_delay_calculation():
    """Test exponential_backoff delay calculation."""
    call_count = 0

    @exponential_backoff(max_retries=3, initial_delay=0.1)
    async def test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Temporary failure")
        return "success"

    with patch("asyncio.sleep") as mock_sleep:
        await test_func()
        assert mock_sleep.call_count == 2  # Two delays before success
        # Check that delays are increasing exponentially
        assert mock_sleep.call_args_list[0][0][0] == 0.1
        assert mock_sleep.call_args_list[1][0][0] == 0.2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_max_delay():
    """Test exponential_backoff with max delay limit."""
    call_count = 0

    @exponential_backoff(max_retries=5, initial_delay=1.0, max_delay=2.0)
    async def test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 4:
            raise Exception("Temporary failure")
        return "success"

    with patch("asyncio.sleep") as mock_sleep:
        await test_func()
        # Check that delays are capped at max_delay
        for call in mock_sleep.call_args_list:
            assert call[0][0] <= 2.0


@pytest.mark.unit
def test_is_retryable_exception_default():
    """Test is_retryable_exception with default behavior."""
    # Most exceptions should be retryable by default
    assert is_retryable_exception(Exception()) is True
    assert is_retryable_exception(ValueError()) is True
    assert is_retryable_exception(RuntimeError()) is True


@pytest.mark.unit
def test_is_retryable_exception_with_custom_check():
    """Test is_retryable_exception with custom check function."""

    def custom_check(exc):
        return isinstance(exc, ValueError)

    assert is_retryable_exception(ValueError(), custom_check) is True
    assert is_retryable_exception(Exception(), custom_check) is False


@pytest.mark.unit
def test_is_retryable_exception_with_none():
    """Test is_retryable_exception with None exception."""
    assert is_retryable_exception(None) is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_zero_retries():
    """Test exponential_backoff with zero retries."""
    call_count = 0

    @exponential_backoff(max_retries=0, initial_delay=0.1)
    async def test_func():
        nonlocal call_count
        call_count += 1
        raise Exception("Failure")

    with pytest.raises(Exception, match="Failure"):
        await test_func()

    assert call_count == 1  # Only initial call, no retries


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_zero_delay():
    """Test exponential_backoff with zero delay."""
    call_count = 0

    @exponential_backoff(max_retries=2, initial_delay=0.0)
    async def test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise Exception("Temporary failure")
        return "success"

    with patch("asyncio.sleep") as mock_sleep:
        await test_func()
        # Should still call sleep even with zero delay
        assert mock_sleep.call_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_async_function():
    """Test exponential_backoff with async function."""
    call_count = 0

    @exponential_backoff(max_retries=2, initial_delay=0.1)
    async def async_test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise Exception("Temporary failure")
        return "success"

    result = await async_test_func()
    assert result == "success"
    assert call_count == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_sync_function():
    """Test exponential_backoff with sync function."""
    call_count = 0

    @exponential_backoff(max_retries=2, initial_delay=0.1)
    def sync_test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise Exception("Temporary failure")
        return "success"

    result = await sync_test_func()
    assert result == "success"
    assert call_count == 2


@pytest.mark.unit
def test_retry_config_with_negative_values():
    """Test RetryConfig with negative values."""
    with pytest.raises(ValueError):
        RetryConfig(max_retries=-1)

    with pytest.raises(ValueError):
        RetryConfig(initial_delay=-0.1)

    with pytest.raises(ValueError):
        RetryConfig(max_delay=-1.0)


@pytest.mark.unit
def test_retry_config_with_zero_values():
    """Test RetryConfig with zero values."""
    config = RetryConfig(max_retries=0, initial_delay=0.0, max_delay=0.0)
    assert config.max_retries == 0
    assert config.initial_delay == 0.0
    assert config.max_delay == 0.0
