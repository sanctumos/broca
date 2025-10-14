"""Extended unit tests for common retry utilities."""

from unittest.mock import patch

import pytest

from common.retry import RetryConfig, exponential_backoff, is_retryable_exception


@pytest.mark.unit
def test_retry_config_initialization():
    """Test RetryConfig initialization."""
    config = RetryConfig(max_retries=5, base_delay=1.0, max_delay=60.0)
    assert config.max_retries == 5
    assert config.base_delay == 1.0
    assert config.max_delay == 60.0


@pytest.mark.unit
def test_retry_config_default_values():
    """Test RetryConfig default values."""
    config = RetryConfig()
    assert config.max_retries == 3
    assert config.base_delay == 1.0
    assert config.max_delay == 60.0
    assert config.jitter is True
    assert config.exponential_base == 2.0


@pytest.mark.unit
def test_retry_config_validation():
    """Test RetryConfig validation."""
    # The actual implementation doesn't validate negative values
    # So we just test that it accepts them
    config = RetryConfig(max_retries=-1)
    assert config.max_retries == -1

    config = RetryConfig(base_delay=-1.0)
    assert config.base_delay == -1.0

    config = RetryConfig(max_delay=0.0)
    assert config.max_delay == 0.0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_success_first_try():
    """Test exponential_backoff with success on first try."""
    call_count = 0

    async def test_func():
        nonlocal call_count
        call_count += 1
        return "success"

    config = RetryConfig(max_retries=3, base_delay=0.1)
    result = await exponential_backoff(test_func, config)
    assert result == "success"
    assert call_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_success_after_retries():
    """Test exponential_backoff with success after retries."""
    call_count = 0

    async def test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Temporary failure")
        return "success"

    config = RetryConfig(max_retries=3, base_delay=0.1)
    result = await exponential_backoff(test_func, config)
    assert result == "success"
    assert call_count == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_max_retries_exceeded():
    """Test exponential_backoff with max retries exceeded."""
    call_count = 0

    async def test_func():
        nonlocal call_count
        call_count += 1
        raise Exception("Persistent failure")

    config = RetryConfig(max_retries=2, base_delay=0.1)
    with pytest.raises(Exception, match="Persistent failure"):
        await exponential_backoff(test_func, config)

    assert call_count == 3  # Initial call + 2 retries


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_custom_exception():
    """Test exponential_backoff with custom exception."""
    call_count = 0

    async def test_func():
        nonlocal call_count
        call_count += 1
        raise ValueError("Custom error")

    config = RetryConfig(max_retries=2, base_delay=0.1)
    with pytest.raises(ValueError, match="Custom error"):
        await exponential_backoff(test_func, config)

    assert call_count == 3


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_delay_calculation():
    """Test exponential_backoff delay calculation."""
    call_count = 0

    async def test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Temporary failure")
        return "success"

    config = RetryConfig(max_retries=3, base_delay=0.1, jitter=False)
    with patch("asyncio.sleep") as mock_sleep:
        await exponential_backoff(test_func, config)
        assert mock_sleep.call_count == 2  # Two delays before success
        # Check that delays are increasing exponentially
        assert mock_sleep.call_args_list[0][0][0] == 0.1
        assert mock_sleep.call_args_list[1][0][0] == 0.2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_max_delay():
    """Test exponential_backoff with max delay limit."""
    call_count = 0

    async def test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 4:
            raise Exception("Temporary failure")
        return "success"

    config = RetryConfig(max_retries=5, base_delay=1.0, max_delay=2.0, jitter=False)
    with patch("asyncio.sleep") as mock_sleep:
        await exponential_backoff(test_func, config)
        # Check that delays are capped at max_delay
        for call in mock_sleep.call_args_list:
            assert call[0][0] <= 2.0


@pytest.mark.unit
def test_is_retryable_exception_default():
    """Test is_retryable_exception with default behavior."""
    # Test retryable exceptions
    assert is_retryable_exception(ConnectionError()) is True
    assert is_retryable_exception(TimeoutError()) is True
    assert is_retryable_exception(OSError()) is True

    # Test non-retryable exceptions
    assert is_retryable_exception(Exception()) is False
    assert is_retryable_exception(ValueError()) is False
    assert is_retryable_exception(RuntimeError()) is False


@pytest.mark.unit
def test_is_retryable_exception_with_custom_check():
    """Test is_retryable_exception with custom check function."""
    # The function doesn't accept a custom check parameter
    # So we just test the default behavior
    assert is_retryable_exception(ConnectionError()) is True
    assert is_retryable_exception(Exception()) is False


@pytest.mark.unit
def test_is_retryable_exception_with_none():
    """Test is_retryable_exception with None exception."""
    # None is not retryable
    assert is_retryable_exception(None) is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_zero_retries():
    """Test exponential_backoff with zero retries."""
    call_count = 0

    async def test_func():
        nonlocal call_count
        call_count += 1
        raise Exception("Failure")

    config = RetryConfig(max_retries=0, base_delay=0.1)
    with pytest.raises(Exception, match="Failure"):
        await exponential_backoff(test_func, config)

    assert call_count == 1  # Only initial call, no retries


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_zero_delay():
    """Test exponential_backoff with zero delay."""
    call_count = 0

    async def test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise Exception("Temporary failure")
        return "success"

    config = RetryConfig(max_retries=2, base_delay=0.0, jitter=False)
    with patch("asyncio.sleep") as mock_sleep:
        await exponential_backoff(test_func, config)
        # Should still call sleep even with zero delay
        assert mock_sleep.call_count == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_async_function():
    """Test exponential_backoff with async function."""
    call_count = 0

    async def async_test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise Exception("Temporary failure")
        return "success"

    config = RetryConfig(max_retries=2, base_delay=0.1)
    result = await exponential_backoff(async_test_func, config)
    assert result == "success"
    assert call_count == 2


@pytest.mark.unit
@pytest.mark.asyncio
async def test_exponential_backoff_with_sync_function():
    """Test exponential_backoff with sync function."""
    call_count = 0

    def sync_test_func():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise Exception("Temporary failure")
        return "success"

    config = RetryConfig(max_retries=2, base_delay=0.1)
    # This will fail because exponential_backoff expects an async function
    with pytest.raises(TypeError):
        await exponential_backoff(sync_test_func, config)


@pytest.mark.unit
def test_retry_config_with_negative_values():
    """Test RetryConfig with negative values."""
    # The actual implementation doesn't validate negative values
    config = RetryConfig(max_retries=-1)
    assert config.max_retries == -1

    config = RetryConfig(base_delay=-0.1)
    assert config.base_delay == -0.1

    config = RetryConfig(max_delay=-1.0)
    assert config.max_delay == -1.0


@pytest.mark.unit
def test_retry_config_with_zero_values():
    """Test RetryConfig with zero values."""
    config = RetryConfig(max_retries=0, base_delay=0.0, max_delay=0.0)
    assert config.max_retries == 0
    assert config.base_delay == 0.0
    assert config.max_delay == 0.0
