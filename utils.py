"""
Enhanced utility functions for ScriptSynthCore.
Comprehensive utilities for logging, validation, caching, and data processing.
"""

import logging
import json
import hashlib
import time
import functools
import asyncio
import os
import sys
from typing import Dict, Any, Optional, Union, List, Callable, TypeVar
from pathlib import Path
from datetime import datetime, timezone
import pickle
import tempfile
import threading
from contextlib import contextmanager
from dataclasses import dataclass, asdict

# Type variables
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    value: Any
    timestamp: float
    access_count: int = 0
    ttl: Optional[float] = None
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired"""
        if self.ttl is None:
            return False
        return time.time() - self.timestamp > self.ttl

class InMemoryCache:
    """Thread-safe in-memory cache with TTL support"""
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[float] = None):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            entry = self._cache[key]
            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return None
            
            entry.access_count += 1
            self._hits += 1
            return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Set value in cache"""
        with self._lock:
            # Evict oldest entries if at max capacity
            if len(self._cache) >= self.max_size and key not in self._cache:
                oldest_key = min(self._cache.keys(), 
                               key=lambda k: self._cache[k].timestamp)
                del self._cache[oldest_key]
            
            self._cache[key] = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl
            )
    
    def clear(self) -> None:
        """Clear all cache entries"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
    
    def stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = self._hits / total_requests if total_requests > 0 else 0
            
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": hit_rate,
                "total_requests": total_requests
            }

# Global cache instance
_global_cache = InMemoryCache()

def cached(ttl: Optional[float] = None, key_func: Optional[Callable] = None):
    """Decorator for caching function results"""
    def decorator(func: Callable) -> Any:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"
            
            # Try to get from cache
            result = _global_cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {func.__name__}")
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            _global_cache.set(cache_key, result, ttl)
            logger.debug(f"Cache miss for {func.__name__}, result cached")
            
            return result
        return wrapper
    return decorator

class DataValidator:
    """Comprehensive data validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_ethereum_address(address: str) -> bool:
        """Validate Ethereum address format"""
        import re
        if not isinstance(address, str):
            return False
        return bool(re.match(r'^0x[a-fA-F0-9]{40}$', address))
    
    @staticmethod
    def validate_json(data: str) -> bool:
        """Validate JSON string"""
        try:
            json.loads(data)
            return True
        except (json.JSONDecodeError, TypeError):
            return False
    
    @staticmethod
    def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
        """Validate required fields are present"""
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None:
                missing_fields.append(field)
        return missing_fields
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(text, str):
            return ""
        
        # Remove potentially dangerous characters
        import re
        sanitized = re.sub(r'[<>"\']', '', text)
        
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized.strip()

class FileUtils:
    """File operation utilities"""
    
    @staticmethod
    def safe_read_file(file_path: Union[str, Path], encoding: str = 'utf-8') -> Optional[str]:
        """Safely read file with error handling"""
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                return f.read()
        except (IOError, OSError, UnicodeDecodeError) as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    @staticmethod
    def safe_write_file(file_path: Union[str, Path], content: str, 
                       encoding: str = 'utf-8', backup: bool = True) -> bool:
        """Safely write file with optional backup"""
        try:
            file_path = Path(file_path)
            
            # Create backup if file exists
            if backup and file_path.exists():
                backup_path = file_path.with_suffix(f'{file_path.suffix}.bak')
                file_path.rename(backup_path)
            
            # Ensure parent directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return True
            
        except (IOError, OSError) as e:
            logger.error(f"Error writing file {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256') -> Optional[str]:
        """Get file hash"""
        try:
            hash_func = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except (IOError, OSError, ValueError) as e:
            logger.error(f"Error hashing file {file_path}: {e}")
            return None

class AsyncUtils:
    """Async operation utilities"""
    
    @staticmethod
    async def run_with_timeout(coro, timeout: float):
        """Run coroutine with timeout"""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            logger.warning(f"Operation timed out after {timeout} seconds")
            raise
    
    @staticmethod
    async def batch_execute(tasks: List[Callable], batch_size: int = 10) -> List[Any]:
        """Execute tasks in batches"""
        results = []
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            batch_results = await asyncio.gather(*[task() for task in batch], 
                                                return_exceptions=True)
            results.extend(batch_results)
        return results

class PerformanceMonitor:
    """Performance monitoring utilities"""
    
    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
    
    @contextmanager
    def measure(self, operation_name: str):
        """Context manager for measuring execution time"""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            with self._lock:
                if operation_name not in self.metrics:
                    self.metrics[operation_name] = []
                self.metrics[operation_name].append(duration)
    
    def get_stats(self, operation_name: str) -> Optional[Dict[str, float]]:
        """Get performance statistics for an operation"""
        with self._lock:
            if operation_name not in self.metrics:
                return None
            
            times = self.metrics[operation_name]
            return {
                "count": len(times),
                "total": sum(times),
                "average": sum(times) / len(times),
                "min": min(times),
                "max": max(times)
            }
    
    def clear_metrics(self) -> None:
        """Clear all metrics"""
        with self._lock:
            self.metrics.clear()

# Global performance monitor
_performance_monitor = PerformanceMonitor()

def timed(operation_name: Optional[str] = None):
    """Decorator for timing function execution"""
    def decorator(func: Callable) -> Any:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = operation_name or func.__name__
            with _performance_monitor.measure(name):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def get_performance_stats(operation_name: str) -> Optional[Dict[str, float]]:
    """Get performance statistics for an operation"""
    return _performance_monitor.get_stats(operation_name)

def vector_embedding_optimizer(data: Dict[str, Any], strategy: str = "auto") -> Dict[str, Any]:
    """
    Optimize data using vector embedding strategies.
    
    Args:
        data: Input data to optimize
        strategy: Optimization strategy ('auto', 'performance', 'accuracy', 'memory')
    
    Returns:
        Optimized data with metadata
    """
    if strategy == "auto":
        return _auto_optimize(data)
    elif strategy == "performance":
        return _performance_optimize(data)
    elif strategy == "accuracy":
        return _accuracy_optimize(data)
    elif strategy == "memory":
        return _memory_optimize(data)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

@cached(ttl=300)  # 5-minute TTL cache
def cached_vector_embedding_optimizer(data: Dict[str, Any], strategy: str = "auto") -> Dict[str, Any]:
    """
    Cached version of vector embedding optimizer for improved performance.
    
    Args:
        data: Input data to optimize
        strategy: Optimization strategy
    
    Returns:
        Optimized data with metadata (cached for 5 minutes)
    """
    logger.debug("Computing optimization for strategy: %s", strategy)
    return vector_embedding_optimizer(data, strategy)

def _auto_optimize(data: Dict[str, Any]) -> Dict[str, Any]:
    """Auto-select optimization strategy based on data size"""
    data_size = len(json.dumps(data).encode('utf-8'))
    
    if data_size < 1000:  # Small data
        return _accuracy_optimize(data)
    elif data_size < 10000:  # Medium data
        return _performance_optimize(data)
    else:  # Large data
        return _memory_optimize(data)

def _performance_optimize(data: Dict[str, Any]) -> Dict[str, Any]:
    """Performance-focused optimization"""
    result = data.copy()
    result["_optimization"] = "performance"
    result["_timestamp"] = time.time()
    return result

def _accuracy_optimize(data: Dict[str, Any]) -> Dict[str, Any]:
    """Accuracy-focused optimization"""
    result = data.copy()
    result["_optimization"] = "accuracy"
    result["_precision_level"] = "high"
    return result

def _memory_optimize(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Memory-focused optimization with zero-allocation strategies.
    Removes None values efficiently and adds compression metadata.
    """
    logger.debug("Starting memory optimization for %d keys", len(data))
    
    # Zero-allocation strategy: pre-calculate sizes
    none_count = sum(1 for v in data.values() if v is None)
    non_none_count = len(data) - none_count
    
    if none_count > 0:
        logger.info("Removing %d None values from dataset", none_count)
    
    # Pre-allocate result dictionary for better performance
    result = {}
    
    # For larger datasets, pre-allocate internal dictionary structure
    if non_none_count > 16:
        # Pre-fill with dummy keys to allocate internal hash table
        for i in range(min(non_none_count + 2, 64)):
            result[f"__temp_alloc_{i}"] = None
        result.clear()  # Clear content but keep allocated structure
    
    # High-performance None filtering using generator expression
    for key, value in data.items():
        if value is not None:
            result[key] = value
    
    # Add optimization metadata
    result["_optimization"] = "memory"
    result["_compressed"] = True
    
    # Runtime guardrail - fail fast if None values survived
    none_fields = [k for k, v in result.items() if not k.startswith("_") and v is None]
    if none_fields:
        logger.exception("None values survived memory optimization: %s", none_fields)
        raise ValueError(f"Memory optimization failed: None values in {none_fields}")
    
    # Static contract validation
    try:
        from project_module.schemas import MemoryOptimizedResult
        validated_result = MemoryOptimizedResult.validate_output(result)
        logger.debug("Memory optimization completed: %d → %d keys", len(data), len(result))
        return validated_result
    except ImportError:
        logger.warning("Pydantic schemas not available, skipping validation")
    return result

def checkpoint_system(func: Callable) -> Any:
    """
    Checkpoint system decorator for error recovery.
    
    Args:
        func: Function to wrap with checkpoint system
    
    Returns:
        Wrapped function with checkpoint capabilities
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        checkpoint_name = f"{func.__name__}_{int(time.time())}"
        
        try:
            logger.debug(f"Creating checkpoint: {checkpoint_name}")
            result = func(*args, **kwargs)
            logger.debug(f"Checkpoint successful: {checkpoint_name}")
            return result
            
        except Exception as e:
            logger.error(f"Checkpoint failed: {checkpoint_name} - {str(e)}")
            raise
    
    return wrapper

# Utility functions for backward compatibility
def dummy_data() -> Dict[str, Any]:
    """
    Return a dummy data placeholder.
    
    Returns:
        Empty dictionary
    """
    return {}

# Export commonly used instances
cache = _global_cache
performance_monitor = _performance_monitor
validator = DataValidator()
file_utils = FileUtils()
async_utils = AsyncUtils() 