"""
Comprehensive tests for Resilience Core.

Tests all resilience patterns including retry, circuit breaker, and health checks.
"""

import unittest
import time
import threading
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from resilience import (
    ResilienceConfig, 
    retry_on_exception, 
    HealthCheckThread, 
    CircuitBreaker,
    HealthStatus,
    HealthCheckResult
)
from resilience.config import RetryConfig, CircuitBreakerConfig
from resilience.health import health_checker

class TestResilienceConfig(unittest.TestCase):
    """Test configuration validation."""
    
    def test_valid_config(self):
        """Test valid configuration creation."""
        config = ResilienceConfig(
            max_retries=5,
            backoff_factor=1.0,
            health_check_interval=30.0
        )
        self.assertEqual(config.max_retries, 5)
        self.assertEqual(config.backoff_factor, 1.0)
        self.assertEqual(config.health_check_interval, 30.0)
    
    def test_invalid_max_retries(self):
        """Test invalid max_retries validation."""
        with self.assertRaises(ValueError):
            ResilienceConfig(max_retries=-1)
    
    def test_invalid_backoff_factor(self):
        """Test invalid backoff_factor validation."""
        with self.assertRaises(ValueError):
            ResilienceConfig(backoff_factor=-1.0)
    
    def test_invalid_health_interval(self):
        """Test invalid health_check_interval validation."""
        with self.assertRaises(ValueError):
            ResilienceConfig(health_check_interval=0)

class TestRetryPattern(unittest.TestCase):
    """Test retry functionality."""
    
    def test_successful_retry(self):
        """Test successful retry after failures."""
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        
        call_count = 0
        @retry_on_exception(config)
        def failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary failure")
            return "success"
        
        result = failing_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
    
    def test_max_retries_exceeded(self):
        """Test behavior when max retries exceeded."""
        config = RetryConfig(max_attempts=2, base_delay=0.1)
        
        @retry_on_exception(config)
        def always_failing():
            raise ValueError("Persistent failure")
        
        with self.assertRaises(ValueError):
            always_failing()
    
    def test_no_retry_on_success(self):
        """Test no retry when function succeeds immediately."""
        config = RetryConfig(max_attempts=3, base_delay=0.1)
        
        call_count = 0
        @retry_on_exception(config)
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = successful_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 1)
    
    def test_jitter_enabled(self):
        """Test jitter functionality."""
        config = RetryConfig(max_attempts=2, base_delay=1.0, jitter=True)
        
        start_time = time.time()
        @retry_on_exception(config)
        def failing_function():
            raise ValueError("Test failure")
        
        with self.assertRaises(ValueError):
            failing_function()
        
        # Should have some delay due to jitter
        elapsed = time.time() - start_time
        self.assertGreater(elapsed, 0.5)

class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker functionality."""
    
    def test_closed_state_operation(self):
        """Test normal operation in closed state."""
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=1.0)
        breaker = CircuitBreaker(config)
        
        def successful_function():
            return "success"
        
        result = breaker.call(successful_function)
        self.assertEqual(result, "success")
        self.assertEqual(breaker.get_state(), CircuitState.CLOSED)
    
    def test_circuit_opens_on_failures(self):
        """Test circuit breaker opens after threshold failures."""
        config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=1.0)
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("Test failure")
        
        # First failure
        with self.assertRaises(ValueError):
            breaker.call(failing_function)
        self.assertEqual(breaker.get_state(), CircuitState.CLOSED)
        
        # Second failure - should open circuit
        with self.assertRaises(ValueError):
            breaker.call(failing_function)
        self.assertEqual(breaker.get_state(), CircuitState.OPEN)
    
    def test_circuit_rejects_when_open(self):
        """Test circuit breaker rejects calls when open."""
        config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=1.0)
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("Test failure")
        
        # Cause circuit to open
        with self.assertRaises(ValueError):
            breaker.call(failing_function)
        
        # Should reject calls when open
        with self.assertRaises(RuntimeError):
            breaker.call(lambda: "should not execute")
    
    def test_circuit_half_open_recovery(self):
        """Test circuit breaker recovery through half-open state."""
        config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=0.1)
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("Test failure")
        
        def successful_function():
            return "success"
        
        # Cause circuit to open
        with self.assertRaises(ValueError):
            breaker.call(failing_function)
        
        # Wait for recovery timeout
        time.sleep(0.2)
        
        # Should be in half-open state and allow test call
        result = breaker.call(successful_function)
        self.assertEqual(result, "success")
        self.assertEqual(breaker.get_state(), CircuitState.CLOSED)
    
    def test_circuit_reset(self):
        """Test circuit breaker reset functionality."""
        config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=1.0)
        breaker = CircuitBreaker(config)
        
        def failing_function():
            raise ValueError("Test failure")
        
        # Cause circuit to open
        with self.assertRaises(ValueError):
            breaker.call(failing_function)
        
        # Reset circuit
        breaker.reset()
        self.assertEqual(breaker.get_state(), CircuitState.CLOSED)
        self.assertEqual(breaker.failure_count, 0)

class TestHealthCheck(unittest.TestCase):
    """Test health check functionality."""
    
    def test_health_check_thread(self):
        """Test health check thread operation."""
        check_count = 0
        
        def health_check_func():
            nonlocal check_count
            check_count += 1
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="Test health check",
                timestamp=time.time()
            )
        
        health_thread = HealthCheckThread(health_check_func, interval=0.1)
        health_thread.start()
        
        # Wait for a few checks
        time.sleep(0.3)
        
        health_thread.stop()
        self.assertGreater(check_count, 0)
    
    def test_health_checker_management(self):
        """Test health checker management."""
        def test_health_check():
            return HealthCheckResult(
                status=HealthStatus.HEALTHY,
                message="Test check",
                timestamp=time.time()
            )
        
        # Add health check
        health_checker.add_health_check("test", test_health_check, interval=0.1)
        
        # Wait for check to run
        time.sleep(0.2)
        
        # Get status
        status = health_checker.get_health_status()
        self.assertIn("test", status["checks"])
        self.assertEqual(status["overall"], "healthy")
        
        # Remove health check
        health_checker.remove_health_check("test")
        status = health_checker.get_health_status()
        self.assertNotIn("test", status["checks"])

class TestAsyncSupport(unittest.TestCase):
    """Test async function support."""
    
    def test_async_retry(self):
        """Test retry with async functions."""
        config = RetryConfig(max_attempts=2, base_delay=0.1)
        
        call_count = 0
        @retry_on_exception(config)
        async def async_failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Async failure")
            return "async success"
        
        async def run_test():
            return await async_failing_function()
        
        result = asyncio.run(run_test())
        self.assertEqual(result, "async success")
        self.assertEqual(call_count, 2)
    
    def test_async_circuit_breaker(self):
        """Test circuit breaker with async functions."""
        config = CircuitBreakerConfig(failure_threshold=1, recovery_timeout=0.1)
        breaker = CircuitBreaker(config)
        
        async def async_failing_function():
            raise ValueError("Async failure")
        
        async def run_test():
            with self.assertRaises(ValueError):
                await breaker.call_async(async_failing_function)
            
            # Should be open now
            with self.assertRaises(RuntimeError):
                await breaker.call_async(lambda: "should not execute")
        
        asyncio.run(run_test())

class TestIntegration(unittest.TestCase):
    """Test integration scenarios."""
    
    def test_retry_with_circuit_breaker(self):
        """Test combining retry and circuit breaker patterns."""
        retry_config = RetryConfig(max_attempts=2, base_delay=0.1)
        breaker_config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=0.1)
        
        breaker = CircuitBreaker(breaker_config)
        
        call_count = 0
        @retry_on_exception(retry_config)
        def resilient_function():
            nonlocal call_count
            call_count += 1
            if call_count < 5:
                raise ValueError("Temporary failure")
            return "success"
        
        # Should fail due to circuit breaker opening
        with self.assertRaises(ValueError):
            breaker.call(resilient_function)
        
        self.assertEqual(breaker.get_state(), CircuitState.OPEN)

if __name__ == '__main__':
    unittest.main()
