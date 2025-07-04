"""
Retry patterns with exponential backoff and jitter.

Provides configurable retry decorators for robust function execution.
"""

import time
import random
import logging
from typing import Callable, Any, TypeVar, Union
from functools import wraps
from .config import ResilienceConfig, RetryConfig

logger = logging.getLogger(__name__)
T = TypeVar('T')

def retry_on_exception(config: Union[ResilienceConfig, RetryConfig]) -> Callable:
    """
    Retry decorator with exponential backoff and jitter.
    
    Args:
        config: Configuration for retry behavior
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            attempts = 0
            last_exception = None
            
            # Get max attempts from config
            max_attempts = getattr(config, 'max_attempts', getattr(config, 'max_retries', 3))
            
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except config.exceptions as exc:
                    last_exception = exc
                    attempts += 1
                    
                    if attempts > max_attempts:
                        logger.error(f"{func.__name__} failed after {attempts} attempts: {exc}")
                        raise last_exception
                    
                    # Calculate delay with exponential backoff
                    if isinstance(config, RetryConfig):
                        delay = min(
                            config.base_delay * (config.exponential_base ** (attempts - 1)),
                            config.max_delay
                        )
                    else:
                        delay = min(
                            config.backoff_factor * (2 ** (attempts - 1)),
                            config.max_delay
                        )
                    
                    # Add jitter if enabled
                    if config.jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Retry {attempts}/{max_attempts} in {delay:.2f}s for {func.__name__}: {exc}")
                    time.sleep(delay)
            
            raise last_exception
        
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            attempts = 0
            last_exception = None
            
            # Get max attempts from config
            max_attempts = getattr(config, 'max_attempts', getattr(config, 'max_retries', 3))
            
            while attempts < max_attempts:
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except config.exceptions as exc:
                    last_exception = exc
                    attempts += 1
                    
                    if attempts > max_attempts:
                        logger.error(f"{func.__name__} failed after {attempts} attempts: {exc}")
                        raise last_exception
                    
                    # Calculate delay with exponential backoff
                    if isinstance(config, RetryConfig):
                        delay = min(
                            config.base_delay * (config.exponential_base ** (attempts - 1)),
                            config.max_delay
                        )
                    else:
                        delay = min(
                            config.backoff_factor * (2 ** (attempts - 1)),
                            config.max_delay
                        )
                    
                    # Add jitter if enabled
                    if config.jitter:
                        delay *= (0.5 + random.random() * 0.5)
                    
                    logger.warning(f"Retry {attempts}/{max_attempts} in {delay:.2f}s for {func.__name__}: {exc}")
                    await asyncio.sleep(delay)
            
            raise last_exception
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper
    
    return decorator

def retry_with_custom_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Retry decorator with custom backoff parameters.
    
    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay between retries
        max_delay: Maximum delay cap
        exponential_base: Base for exponential backoff
        jitter: Whether to add random jitter
        exceptions: Exception types to retry on
        
    Returns:
        Decorated function with retry logic
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exponential_base=exponential_base,
        jitter=jitter,
        exceptions=exceptions
    )
    return retry_on_exception(config) 