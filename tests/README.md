# Broca2 Test Suite

Comprehensive test suite for the Broca2 message processing system, designed to achieve close to 100% test coverage across unit, integration, and end-to-end testing scenarios.

## 🏗️ Test Structure

```
tests/                      # Main test suite (pytest tests/)
├── unit/                    # Unit tests for individual components
│   ├── runtime/            # Runtime core tests
│   ├── database/           # Database operation tests
│   ├── cli/                # CLI tool tests
│   ├── common/             # Common utility tests
│   └── plugins/            # Plugin system tests (telegram_bot, etc.)
├── integration/            # Integration tests for component interactions
├── e2e/                    # End-to-end tests for complete workflows
├── fixtures/               # Reusable test fixtures
├── utils/                  # Test utilities and helpers
├── conftest.py            # Global pytest configuration
└── __init__.py            # Test package initialization

tests-disabled/             # Tests for disabled/removed plugins (not run by default)
└── unit/plugins/           # fake_plugin, legacy telegram, web_chat
```

## 🚀 Quick Start

### Prerequisites

1. **Python Environment**: Python 3.11+ with virtual environment
2. **Dependencies**: Install test dependencies:
   ```bash
   pip install -r requirements-testing.txt
   ```

### Running Tests

#### Using the Test Runner Script
```bash
# Run all tests
python run_tests.py all

# Run specific test types
python run_tests.py unit
python run_tests.py integration
python run_tests.py e2e

# Run with coverage
python run_tests.py coverage

# Run performance tests
python run_tests.py performance
```

#### Using pytest Directly
```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run end-to-end tests only
pytest tests/e2e/

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/unit/runtime/test_core.py::TestQueueProcessor::test_queue_processor_start
```

## 📋 Test Categories

### Unit Tests (`tests/unit/`)

**Purpose**: Test individual components in isolation

**Coverage**:
- **Runtime Core**: QueueProcessor, AgentClient, PluginManager, MessageFormatter
- **Database Operations**: User, Message, Queue operations
- **CLI Tools**: Bot management, Queue management, User management, Settings
- **Common Utilities**: Configuration, Exceptions, Logging
- **Plugin System**: Base Plugin class, individual plugins

**Key Features**:
- Mock external dependencies
- Test individual methods and functions
- Verify error handling
- Test edge cases

### Integration Tests (`tests/integration/`)

**Purpose**: Test component interactions and workflows with real DB and mocked externals.

**Coverage**:
- **Queue flow** (`test_queue_flow_integration.py`): Real SQLite (temp_db), seed user/message/queue, run QueueProcessor in echo mode, assert message and queue updated.
- **Plugin manager** (`test_plugin_manager_integration.py`): Discover and start the minimal `tests/fixtures/integration_plugin` plugin.
- **Application lifecycle** (`test_application_lifecycle_integration.py`): Application start/stop with mocked Letta and PID, minimal plugin only.

**Key Features**:
- Test component interactions with real database and pool
- Verify data flow from queue through processor to DB
- No live Telegram or Letta; all externals mocked

### End-to-End Tests (`tests/e2e/`)

**Purpose**: Test full system workflows in one process with real DB and mocked externals.

**Coverage**:
- **Full message flow** (`test_message_flow_e2e.py`): Start Application (mocked Letta/PID), seed one message into queue, run app until queue processes it, assert message has response and queue status completed.

**Key Features**:
- Application started and stopped cleanly
- Real database, real queue processor loop
- Externals (Letta, Telegram) mocked; use before trying a live bot

## 🔧 Test Configuration

### pytest Configuration (`pytest.ini`)

- **Async Support**: Automatic asyncio mode
- **Coverage**: 80% minimum coverage requirement
- **Markers**: Custom markers for test categorization
- **Output**: Verbose output with short tracebacks
- **Timeouts**: 300-second timeout for long-running tests

### Test Fixtures (`tests/conftest.py`)

**Global Fixtures**:
- `event_loop`: Session-scoped event loop
- `temp_db`: Temporary database for each test
- `mock_env_vars`: Mock environment variables
- `mock_letta_client`: Mock Letta client
- `mock_telegram_client`: Mock Telegram client
- `mock_plugin_manager`: Mock plugin manager

**Test Data Fixtures**:
- `sample_user_data`: Sample user data
- `sample_message_data`: Sample message data
- `sample_queue_item_data`: Sample queue item data

### Test Utilities (`tests/utils/`)

**Helper Classes**:
- `AsyncTestHelper`: Async testing utilities
- `DatabaseTestHelper`: Database testing utilities
- `MockFactory`: Mock object creation
- `TestDataGenerator`: Test data generation
- `AssertionHelper`: Custom assertions

## 🎯 Test Markers

Use pytest markers to categorize and run specific test types:

```python
@pytest.mark.unit
@pytest.mark.integration
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.async
@pytest.mark.database
@pytest.mark.external
```

**Run tests by marker**:
```bash
pytest -m unit          # Unit tests only
pytest -m integration    # Integration tests only
pytest -m e2e           # End-to-end tests only
pytest -m slow          # Slow tests only
pytest -m async         # Async tests only
pytest -m database      # Database tests only
pytest -m external      # External service tests only
```

## 🔄 Async Testing

**Critical**: This codebase is heavily dependent on asyncio. All tests are designed to prevent hanging:

### Async Test Patterns

```python
@pytest.mark.asyncio
async def test_async_function():
    """Test async function with proper cleanup."""
    # Test implementation
    pass

@pytest_asyncio.fixture
async def async_fixture():
    """Async fixture with proper cleanup."""
    # Setup
    yield resource
    # Cleanup
```

### Async Utilities

- `AsyncTestHelper.run_with_timeout()`: Run coroutines with timeout
- `AsyncTestHelper.wait_for_condition()`: Wait for conditions with timeout
- `AsyncTestHelper.create_async_mock()`: Create properly configured async mocks

## 🗄️ Database Testing

### Database Isolation

Each test gets a clean, isolated database:

```python
@pytest_asyncio.fixture
async def test_db():
    """Provide isolated test database."""
    async with DatabaseTestHelper.temp_database() as db_path:
        yield db_path
```

### Database Utilities

- `DatabaseTestHelper.temp_database()`: Create temporary database
- `DatabaseTestHelper.insert_test_data()`: Insert test data
- `DatabaseTestHelper.get_test_data()`: Retrieve test data

## 🎭 Mocking Strategy

### External Dependencies

All external dependencies are mocked:
- **Letta Client**: Mock agent communication
- **Telegram Client**: Mock Telegram API
- **Database**: Use temporary databases
- **File System**: Mock file operations
- **Network**: Mock HTTP requests

### Mock Factories

```python
# Create common mocks
mock_client = MockFactory.create_letta_client_mock()
mock_plugin = MockFactory.create_plugin_mock()
mock_manager = MockFactory.create_plugin_manager_mock()
```

## 📊 Coverage Reporting

### Coverage Requirements

- **Minimum Coverage**: 80%
- **Target Coverage**: 95%+
- **Critical Components**: 100% coverage for core functionality

### Coverage Reports

```bash
# Generate coverage report
python run_tests.py coverage

# View HTML report
open htmlcov/index.html

# View coverage in terminal
pytest --cov=. --cov-report=term-missing
```

## 🚀 Performance Testing

### Performance Test Categories

- **Message Processing**: Test processing speed and throughput
- **Database Operations**: Test query performance and concurrent operations
- **Plugin System**: Test plugin loading and execution performance
- **System Load**: Test system behavior under high load

### Performance Test Patterns

```python
@pytest.mark.performance
async def test_performance():
    """Performance test with timing."""
    start_time = time.time()
    # Test implementation
    end_time = time.time()
    assert (end_time - start_time) < max_time
```

## 🐛 Error Handling Testing

### Error Scenarios

- **Network Errors**: Connection failures, timeouts
- **Database Errors**: Connection failures, query errors
- **Plugin Errors**: Plugin failures, crashes
- **Validation Errors**: Invalid input data
- **Resource Errors**: Memory, disk, file system errors

### Error Recovery Testing

- **Graceful Degradation**: System continues operating with reduced functionality
- **Retry Mechanisms**: Automatic retry with exponential backoff
- **Fallback Behavior**: Alternative processing paths
- **Error Isolation**: Errors don't cascade to other components

## 🔍 Debugging Tests

### Debug Mode

```bash
# Run tests in debug mode
pytest --log-cli-level=DEBUG

# Run specific test with debug output
pytest -v -s tests/unit/runtime/test_core.py::TestQueueProcessor::test_queue_processor_start
```

### Test Logging

- **Test Setup**: Log test initialization
- **Test Execution**: Log test steps
- **Test Cleanup**: Log cleanup operations
- **Error Details**: Log detailed error information

## 📝 Writing Tests

### Test Naming Convention

```python
def test_component_method_scenario():
    """Test specific scenario for component method."""
    pass

async def test_async_component_method_scenario():
    """Test specific scenario for async component method."""
    pass
```

### Test Structure

```python
@pytest.mark.unit
class TestComponent:
    """Test cases for Component class."""

    @pytest_asyncio.fixture
    async def component(self):
        """Create component instance for testing."""
        return Component()

    @pytest.mark.asyncio
    async def test_component_method_success(self, component):
        """Test successful method execution."""
        # Arrange
        # Act
        # Assert
        pass

    @pytest.mark.asyncio
    async def test_component_method_error(self, component):
        """Test method error handling."""
        # Arrange
        # Act
        # Assert
        pass
```

### Test Data

Use `TestDataGenerator` for consistent test data:

```python
user_data = TestDataGenerator.generate_user_data()
message_data = TestDataGenerator.generate_message_data()
queue_data = TestDataGenerator.generate_queue_item_data()
```

## 🚨 Common Issues

### Async Test Hanging

**Problem**: Tests hang indefinitely
**Solution**: Use `AsyncTestHelper.run_with_timeout()` and proper cleanup

### Database Conflicts

**Problem**: Tests interfere with each other
**Solution**: Use `DatabaseTestHelper.temp_database()` for isolation

### Mock Configuration

**Problem**: Mocks not working correctly
**Solution**: Use `MockFactory` for consistent mock configuration

### Environment Variables

**Problem**: Tests fail due to missing environment variables
**Solution**: Use `mock_env_vars` fixture for consistent environment

## 📚 Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [asyncio Testing Best Practices](https://docs.python.org/3/library/asyncio-dev.html)

## 🤝 Contributing

When adding new tests:

1. **Follow the established patterns**
2. **Use appropriate test markers**
3. **Include both success and error scenarios**
4. **Ensure proper cleanup**
5. **Add docstrings explaining test purpose**
6. **Update this README if adding new test categories**

## 📈 Test Metrics

Track these metrics to ensure test quality:

- **Coverage Percentage**: Aim for 95%+
- **Test Execution Time**: Keep under 5 minutes for full suite
- **Test Reliability**: 100% pass rate on clean runs
- **Test Maintainability**: Easy to understand and modify
- **Test Performance**: Individual tests under 1 second
