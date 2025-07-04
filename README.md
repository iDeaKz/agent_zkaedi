# 🛡️ Resilience Core

**Production-grade retry, circuit breaker, and health check patterns for robust Python applications.**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/resilience-core.svg)](https://badge.fury.io/py/resilience-core)
[![Tests](https://github.com/resilience-core/resilience-core/workflows/Tests/badge.svg)](https://github.com/resilience-core/resilience-core/actions)

## 🚀 Features

- **🔄 Retry Patterns**: Exponential backoff with jitter and configurable exceptions
- **⚡ Circuit Breaker**: Prevents cascading failures with automatic recovery
- **❤️ Health Checks**: Continuous monitoring with threaded execution
- **🔧 Async Support**: Full async/await compatibility
- **📊 Performance**: High-performance, thread-safe implementations
- **⚙️ Configuration**: Pydantic-validated configuration with JSON schema
- **🧪 Testing**: Comprehensive test suite with 100% coverage
- **📦 Packaging**: Production-ready with proper packaging and CLI tools

## 📦 Installation

```bash
pip install resilience-core
```

For development:
```bash
pip install resilience-core[dev]
```

## 🎯 Quick Start

### Basic Retry Pattern

```python
from resilience import retry_on_exception, RetryConfig

config = RetryConfig(max_attempts=3, base_delay=1.0, jitter=True)

@retry_on_exception(config)
def unreliable_function():
    import random
    if random.random() < 0.7:
        raise ValueError("Temporary failure")
    return "Success!"

# Will retry up to 3 times with exponential backoff
result = unreliable_function()
```

### Circuit Breaker Pattern

```python
from resilience import CircuitBreaker, CircuitBreakerConfig

config = CircuitBreakerConfig(failure_threshold=5, recovery_timeout=60.0)
breaker = CircuitBreaker(config)

def external_service_call():
    # Simulate external service
    import random
    if random.random() < 0.8:
        raise RuntimeError("Service unavailable")
    return "Service response"

# Protected call with circuit breaker
try:
    result = breaker.call(external_service_call)
    print(f"Success: {result}")
except RuntimeError as e:
    print(f"Circuit breaker rejected: {e}")
```

### Health Check Pattern

```python
from resilience import HealthCheckThread, HealthCheckResult, HealthStatus
import time

def system_health_check():
    # Simulate health check
    cpu_usage = 75.0  # Get from system
    memory_usage = 60.0  # Get from system
    
    if cpu_usage > 90 or memory_usage > 90:
        status = HealthStatus.UNHEALTHY
        message = "Critical resource usage"
    elif cpu_usage > 70 or memory_usage > 70:
        status = HealthStatus.DEGRADED
        message = "Elevated resource usage"
    else:
        status = HealthStatus.HEALTHY
        message = "Normal operation"
    
    return HealthCheckResult(
        status=status,
        message=message,
        timestamp=time.time(),
        details={"cpu": cpu_usage, "memory": memory_usage}
    )

# Start health monitoring
health_thread = HealthCheckThread(system_health_check, interval=30.0)
health_thread.start()

# Check health status
if health_thread.is_healthy():
    print("System is healthy")
else:
    print("System has issues")
```

### Async Support

```python
import asyncio
from resilience import retry_on_exception, RetryConfig

config = RetryConfig(max_attempts=2, base_delay=0.5)

@retry_on_exception(config)
async def async_unreliable_function():
    await asyncio.sleep(0.1)
    import random
    if random.random() < 0.6:
        raise ValueError("Async failure")
    return "Async success"

# Async retry
result = await async_unreliable_function()
```

## 🛠️ CLI Usage

Resilience Core includes a comprehensive CLI for testing and demonstration:

```bash
# Test retry pattern
resilience-cli retry --fail-rate 0.7 --max-attempts 3

# Test circuit breaker
resilience-cli circuit-breaker --fail-rate 0.8 --threshold 2

# Run health checks
resilience-cli health-check --checks 10 --interval 0.5

# Test async retry
resilience-cli async-retry --fail-rate 0.6

# Run performance benchmarks
resilience-cli benchmark retry --iterations 1000

# Run all demonstrations
resilience-cli demo
```

## ⚙️ Configuration

### Retry Configuration

```python
from resilience.config import RetryConfig

config = RetryConfig(
    max_attempts=3,           # Maximum retry attempts
    base_delay=1.0,           # Base delay between retries
    max_delay=60.0,           # Maximum delay cap
    exponential_base=2.0,     # Exponential backoff base
    jitter=True,              # Add random jitter
    exceptions=(ValueError,)  # Exception types to retry
)
```

### Circuit Breaker Configuration

```python
from resilience.config import CircuitBreakerConfig

config = CircuitBreakerConfig(
    failure_threshold=5,      # Failures before opening circuit
    recovery_timeout=60.0,    # Time to wait before half-open
    expected_exception=RuntimeError,  # Exception type to track
    monitor_interval=10.0     # Background monitoring interval
)
```

### Health Check Configuration

```python
from resilience.config import ResilienceConfig

config = ResilienceConfig(
    health_check_interval=30.0,  # Health check frequency
    max_retries=3,              # Retry attempts for health checks
    backoff_factor=0.5          # Backoff for health check retries
)
```

## 🔧 Advanced Usage

### Combined Patterns

```python
from resilience import retry_on_exception, CircuitBreaker
from resilience.config import RetryConfig, CircuitBreakerConfig

# Configure both patterns
retry_config = RetryConfig(max_attempts=2, base_delay=0.5)
breaker_config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=30.0)

breaker = CircuitBreaker(breaker_config)

@retry_on_exception(retry_config)
def resilient_operation():
    # This will be retried, but circuit breaker will prevent cascading failures
    return breaker.call(external_service)

result = resilient_operation()
```

### Custom Health Check Management

```python
from resilience.health import health_checker, HealthCheckResult, HealthStatus

def database_health_check():
    # Check database connectivity
    try:
        # Perform database operation
        return HealthCheckResult(
            status=HealthStatus.HEALTHY,
            message="Database connection OK",
            timestamp=time.time()
        )
    except Exception as e:
        return HealthCheckResult(
            status=HealthStatus.UNHEALTHY,
            message=f"Database error: {e}",
            timestamp=time.time()
        )

def api_health_check():
    # Check API endpoint
    try:
        # Make API call
        return HealthCheckResult(
            status=HealthStatus.HEALTHY,
            message="API endpoint OK",
            timestamp=time.time()
        )
    except Exception as e:
        return HealthCheckResult(
            status=HealthStatus.DEGRADED,
            message=f"API warning: {e}",
            timestamp=time.time()
        )

# Add multiple health checks
health_checker.add_health_check("database", database_health_check, interval=30.0)
health_checker.add_health_check("api", api_health_check, interval=60.0)

# Get overall health status
status = health_checker.get_health_status()
print(f"Overall health: {status['overall']}")
```

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
pip install resilience-core[test]

# Run tests
pytest

# Run with coverage
pytest --cov=resilience --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m "not slow"
```

## 📊 Performance

Resilience Core is designed for high performance:

- **Retry Pattern**: ~10,000 operations/second
- **Circuit Breaker**: ~15,000 operations/second
- **Health Checks**: Minimal overhead with threaded execution
- **Memory Usage**: Efficient with minimal allocations
- **Thread Safety**: Full thread-safe implementations

## 🔒 Thread Safety

All components are thread-safe:

- **Circuit Breaker**: Uses locks for state management
- **Health Checker**: Thread-safe health check management
- **Retry Pattern**: Stateless, inherently thread-safe
- **Configuration**: Immutable after creation

## 📈 Monitoring and Observability

```python
from resilience.breaker import CircuitBreaker
from resilience.health import health_checker

# Circuit breaker statistics
breaker = CircuitBreaker(config)
stats = breaker.get_stats()
print(f"Circuit state: {stats['state']}")
print(f"Failure count: {stats['failure_count']}")

# Health check status
status = health_checker.get_health_status()
for check_name, check_status in status['checks'].items():
    print(f"{check_name}: {check_status['status']}")
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/resilience-core/resilience-core.git
cd resilience-core

# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black resilience tests
isort resilience tests

# Type checking
mypy resilience
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Netflix Hystrix and resilience4j
- Built with modern Python best practices
- Comprehensive testing and documentation

## 📞 Support

- 📧 Email: team@resilience-core.dev
- 🐛 Issues: [GitHub Issues](https://github.com/resilience-core/resilience-core/issues)
- 📖 Documentation: [Read the Docs](https://resilience-core.readthedocs.io)
- 💬 Discussions: [GitHub Discussions](https://github.com/resilience-core/resilience-core/discussions)

---

**Made with ❤️ by the Resilience Core Team** 