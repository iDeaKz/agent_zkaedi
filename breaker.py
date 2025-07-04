"""
Circuit breaker patterns for fault tolerance.

Provides circuit breaker implementation with configurable failure thresholds.
"""

import threading
import time
import logging
from typing import Callable, Any, TypeVar, Optional
from enum import Enum
from .config import CircuitBreakerConfig

logger = logging.getLogger(__name__)
T = TypeVar('T')

class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered

class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    
    Prevents cascading failures by temporarily stopping requests to failing services.
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.last_success_time = time.time()
        self._lock = threading.Lock()
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_monitoring = threading.Event()

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            RuntimeError: If circuit breaker is open
            Exception: Original function exception
        """
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to half-open state")
            else:
                raise RuntimeError("Circuit breaker is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e
    
    async def call_async(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute async function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            RuntimeError: If circuit breaker is open
            Exception: Original function exception
        """
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker transitioning to half-open state")
            else:
                raise RuntimeError("Circuit breaker is OPEN")
        
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self) -> None:
        """Handle successful execution."""
        with self._lock:
            self.failure_count = 0
            self.last_success_time = time.time()
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                logger.info("Circuit breaker closed after successful recovery")
    
    def _on_failure(self) -> None:
        """Handle failed execution."""
        with self._lock:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def get_state(self) -> CircuitState:
        """Get current circuit breaker state."""
        with self._lock:
            return self.state
    
    def get_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics."""
        with self._lock:
            return {
                "state": self.state.value,
                "failure_count": self.failure_count,
                "last_failure_time": self.last_failure_time,
                "last_success_time": self.last_success_time,
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout
            }
    
    def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.last_failure_time = 0.0
            self.last_success_time = time.time()
            logger.info("Circuit breaker reset to closed state")
    
    def start_monitoring(self) -> None:
        """Start background monitoring thread."""
        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._stop_monitoring.clear()
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()
            logger.info("Circuit breaker monitoring started")
    
    def stop_monitoring(self) -> None:
        """Stop background monitoring thread."""
        self._stop_monitoring.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
            logger.info("Circuit breaker monitoring stopped")
    
    def _monitor_loop(self) -> None:
        """Background monitoring loop."""
        while not self._stop_monitoring.is_set():
            try:
                # Check if circuit breaker should transition from open to half-open
                if self.state == CircuitState.OPEN:
                    if time.time() - self.last_failure_time >= self.config.recovery_timeout:
                        with self._lock:
                            self.state = CircuitState.HALF_OPEN
                        logger.info("Circuit breaker automatically transitioning to half-open state")
                
                time.sleep(self.config.monitor_interval)
            except Exception as e:
                logger.error(f"Circuit breaker monitoring error: {e}")
                time.sleep(self.config.monitor_interval)

def circuit_breaker(config: CircuitBreakerConfig):
    """
    Circuit breaker decorator.
    
    Args:
        config: Circuit breaker configuration
        
    Returns:
        Decorated function with circuit breaker protection
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        breaker = CircuitBreaker(config)
        
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            return breaker.call(func, *args, **kwargs)
        
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            return await breaker.call_async(func, *args, **kwargs)
        
        # Return appropriate wrapper based on function type
        import asyncio
        from functools import wraps
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator 