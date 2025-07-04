"""
Configuration management for Resilience Core.

Provides validated configuration classes using Pydantic for type safety.
"""

from pydantic import BaseModel, ConfigDict, field_validator
from typing import Any, Optional

class ResilienceConfig(BaseModel):
    """Configuration for resilience patterns with validation."""
    
    model_config = ConfigDict(str_strip_whitespace=True)

    max_retries: int = 3
    backoff_factor: float = 0.5
    health_check_interval: float = 60.0
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    jitter: bool = True
    max_delay: float = 300.0

    @field_validator("max_retries", mode="before")
    def validate_max_retries(cls, v: Any) -> int:
        if not isinstance(v, int) or v < 0:
            raise ValueError("max_retries must be non-negative integer")
        return v

    @field_validator("backoff_factor", mode="before")
    def validate_backoff_factor(cls, v: Any) -> float:
        val = float(v)
        if val < 0:
            raise ValueError("backoff_factor must be non-negative")
        return val

    @field_validator("health_check_interval", mode="before")
    def validate_health_interval(cls, v: Any) -> float:
        val = float(v)
        if val <= 0:
            raise ValueError("health_check_interval must be positive")
        return val

    @field_validator("failure_threshold", mode="before")
    def validate_failure_threshold(cls, v: Any) -> int:
        if not isinstance(v, int) or v <= 0:
            raise ValueError("failure_threshold must be positive integer")
        return v

    @field_validator("recovery_timeout", mode="before")
    def validate_recovery_timeout(cls, v: Any) -> float:
        val = float(v)
        if val <= 0:
            raise ValueError("recovery_timeout must be positive")
        return val

    @field_validator("max_delay", mode="before")
    def validate_max_delay(cls, v: Any) -> float:
        val = float(v)
        if val <= 0:
            raise ValueError("max_delay must be positive")
        return val

class RetryConfig(BaseModel):
    """Specific configuration for retry patterns."""
    
    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    exceptions: tuple = (Exception,)

    @field_validator("max_attempts", mode="before")
    def validate_max_attempts(cls, v: Any) -> int:
        if not isinstance(v, int) or v <= 0:
            raise ValueError("max_attempts must be positive integer")
        return v

    @field_validator("base_delay", mode="before")
    def validate_base_delay(cls, v: Any) -> float:
        val = float(v)
        if val < 0:
            raise ValueError("base_delay must be non-negative")
        return val

    @field_validator("max_delay", mode="before")
    def validate_max_delay(cls, v: Any) -> float:
        val = float(v)
        if val <= 0:
            raise ValueError("max_delay must be positive")
        return val

    @field_validator("exponential_base", mode="before")
    def validate_exponential_base(cls, v: Any) -> float:
        val = float(v)
        if val <= 0:
            raise ValueError("exponential_base must be positive")
        return val

class CircuitBreakerConfig(BaseModel):
    """Specific configuration for circuit breaker patterns."""
    
    failure_threshold: int = 5
    recovery_timeout: float = 60.0
    expected_exception: type = Exception
    monitor_interval: float = 10.0

    @field_validator("failure_threshold", mode="before")
    def validate_failure_threshold(cls, v: Any) -> int:
        if not isinstance(v, int) or v <= 0:
            raise ValueError("failure_threshold must be positive integer")
        return v

    @field_validator("recovery_timeout", mode="before")
    def validate_recovery_timeout(cls, v: Any) -> float:
        val = float(v)
        if val <= 0:
            raise ValueError("recovery_timeout must be positive")
        return val

    @field_validator("monitor_interval", mode="before")
    def validate_monitor_interval(cls, v: Any) -> float:
        val = float(v)
        if val <= 0:
            raise ValueError("monitor_interval must be positive")
        return val 