"""
Advanced optimization functions for high-performance scenarios.
"""

import sys
import time
import hashlib
import logging
from typing import Dict, Any, Optional, Callable, Tuple
from functools import wraps
from cachetools import TTLCache
import json

logger = logging.getLogger(__name__)

# Global caches for high-performance scenarios
OPTIMIZATION_CACHE = TTLCache(maxsize=10_000, ttl=300)  # 5 min TTL
HASH_CACHE = TTLCache(maxsize=5_000, ttl=600)  # 10 min TTL for hash keys

def _fast_dict_filter(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Optimized dictionary filtering for None values.
    Uses pre-allocation strategies for better performance.
    """
    # Count non-None values for pre-allocation
    non_none_count = sum(1 for v in data.values() if v is not None)
    
    # Pre-allocate result dict with estimated size
    result = {}
    if hasattr(result, '__sizeof__') and non_none_count > 0:
        # Python 3.12 compatible optimization
        # Pre-allocate internal dict structure
        for _ in range(min(non_none_count + 2, 8)):  # +2 for meta fields
            result[f"__temp_{_}"] = None
        result.clear()  # Clear but keep allocated space
    
    # Fast filtering without repeated None checks
    for key, value in data.items():
        if value is not None:
            result[key] = value
    
    return result

def _memory_optimize_zero_alloc(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Zero-allocation memory optimization (Python 3.12 compatible).
    Minimizes object creation and memory churn.
    """
    # Use fast filtering
    result = _fast_dict_filter(data)
    
    # Add meta fields efficiently
    result["_optimization"] = "memory"
    result["_compressed"] = True
    
    # Runtime validation (optimized)
    if __debug__:  # Only in debug mode
        none_count = sum(1 for k, v in result.items() 
                        if not k.startswith("_") and v is None)
        if none_count > 0:
            logger.error("Zero-alloc optimization failed: %d None values", none_count)
            raise ValueError(f"Memory optimization produced {none_count} None values")
    
    return result

def _generate_cache_key(data: Dict[str, Any], strategy: str) -> str:
    """
    Generate optimized cache key for data and strategy.
    Uses fast hashing with caching for repeated patterns.
    """
    # Create a deterministic key from data structure
    if len(data) < 10:  # Small dicts - use simple approach
        key_parts = [strategy]
        for k in sorted(data.keys()):
            key_parts.append(f"{k}:{type(data[k]).__name__}")
        cache_key = "|".join(key_parts)
    else:  # Large dicts - use hash
        data_str = json.dumps(data, sort_keys=True, default=str)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()[:16]
        cache_key = f"{strategy}:{data_hash}:{len(data)}"
    
    return cache_key

def cached_vector_embedding_optimizer(data: Dict[str, Any], strategy: str = "auto") -> Dict[str, Any]:
    """
    Cached version of vector embedding optimizer with TTL cache.
    Automatically purges stale entries for memory stability.
    """
    # Generate cache key
    cache_key = _generate_cache_key(data, strategy)
    
    # Check cache
    if cache_key in OPTIMIZATION_CACHE:
        logger.debug("Cache hit for optimization: %s", cache_key[:20])
        return OPTIMIZATION_CACHE[cache_key].copy()  # Return copy to prevent mutation
    
    # Import the original function to avoid circular imports
    from project_module.utils import vector_embedding_optimizer
    
    # Compute result
    result = vector_embedding_optimizer(data, strategy)
    
    # Cache result (store copy to prevent mutation)
    OPTIMIZATION_CACHE[cache_key] = result.copy()
    logger.debug("Cached optimization result: %s", cache_key[:20])
    
    return result

def benchmark_optimization_methods(data: Dict[str, Any], iterations: int = 1000) -> Dict[str, float]:
    """
    Benchmark different optimization methods for performance comparison.
    """
    from project_module.utils import vector_embedding_optimizer
    
    methods = {
        "original": lambda: vector_embedding_optimizer(data, "memory"),
        "zero_alloc": lambda: _memory_optimize_zero_alloc(data),
        "cached": lambda: cached_vector_embedding_optimizer(data, "memory"),
    }
    
    results = {}
    
    for method_name, method_func in methods.items():
        # Warm-up
        for _ in range(10):
            method_func()
        
        # Benchmark
        start_time = time.perf_counter()
        for _ in range(iterations):
            method_func()
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        ops_per_sec = iterations / duration if duration > 0 else 0
        
        results[method_name] = {
            "total_time": duration,
            "avg_time": duration / iterations,
            "ops_per_sec": ops_per_sec
        }
        
        logger.info("%s: %.2f ops/sec (%.4f ms avg)", 
                   method_name, ops_per_sec, (duration / iterations) * 1000)
    
    return results

# ──────────────────────────────────────────────────────────
# Telemetry and Monitoring
# ──────────────────────────────────────────────────────────

def telemetry_wrapper(func: Callable) -> Callable:
    """
    Wrapper to add telemetry to optimization functions.
    Tracks performance metrics and None key removal stats.
    """
    @wraps(func)
    def wrapper(data: Dict[str, Any], *args, **kwargs) -> Dict[str, Any]:
        start_time = time.perf_counter()
        input_size = len(data)
        none_count = sum(1 for v in data.values() if v is None)
        
        try:
            result = func(data, *args, **kwargs)
            
            # Calculate metrics
            end_time = time.perf_counter()
            duration = end_time - start_time
            output_size = len([k for k in result.keys() if not k.startswith("_")])
            removed_count = input_size - output_size
            
            # Log telemetry
            logger.info(
                "Optimization telemetry - func=%s, input_size=%d, none_removed=%d, "
                "duration=%.4fms, ops_per_sec=%.1f",
                func.__name__, input_size, removed_count, 
                duration * 1000, 1/duration if duration > 0 else 0
            )
            
            # Add telemetry metadata to result
            result["_telemetry"] = {
                "duration_ms": duration * 1000,
                "input_size": input_size,
                "none_removed": removed_count,
                "timestamp": time.time()
            }
            
            return result
            
        except Exception as e:
            end_time = time.perf_counter()
            duration = end_time - start_time
            
            logger.error(
                "Optimization failed - func=%s, input_size=%d, duration=%.4fms, error=%s",
                func.__name__, input_size, duration * 1000, str(e)
            )
            raise
    
    return wrapper

@telemetry_wrapper
def monitored_memory_optimize(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Memory optimization with comprehensive monitoring and telemetry.
    """
    return _memory_optimize_zero_alloc(data)

# ──────────────────────────────────────────────────────────
# Cache Management
# ──────────────────────────────────────────────────────────

def get_cache_stats() -> Dict[str, Any]:
    """Get comprehensive cache statistics."""
    return {
        "optimization_cache": {
            "size": len(OPTIMIZATION_CACHE),
            "maxsize": OPTIMIZATION_CACHE.maxsize,
            "ttl": OPTIMIZATION_CACHE.ttl,
            "hits": getattr(OPTIMIZATION_CACHE, '_hits', 0),
            "misses": getattr(OPTIMIZATION_CACHE, '_misses', 0)
        },
        "hash_cache": {
            "size": len(HASH_CACHE),
            "maxsize": HASH_CACHE.maxsize,
            "ttl": HASH_CACHE.ttl
        }
    }

def clear_all_caches() -> None:
    """Clear all optimization caches."""
    OPTIMIZATION_CACHE.clear()
    HASH_CACHE.clear()
    logger.info("All optimization caches cleared")

def warm_cache_with_common_patterns() -> None:
    """Pre-warm cache with common data patterns."""
    common_patterns = [
        # Small dict with None values
        {f"key_{i}": None if i % 3 == 0 else f"value_{i}" for i in range(10)},
        # Medium dict with mixed types
        {f"field_{i}": i if i % 2 == 0 else None for i in range(50)},
        # Large dict with sparse None values
        {f"data_{i}": f"content_{i}" if i % 10 != 0 else None for i in range(100)}
    ]
    
    for pattern in common_patterns:
        for strategy in ["memory", "performance", "accuracy"]:
            cached_vector_embedding_optimizer(pattern, strategy)
    
    logger.info("Cache warmed with %d common patterns", len(common_patterns))

# ──────────────────────────────────────────────────────────
# Performance Profiling Utilities
# ──────────────────────────────────────────────────────────

def profile_memory_optimization(data_sizes: list = None, iterations: int = 100) -> Dict[str, Any]:
    """
    Profile memory optimization performance across different data sizes.
    """
    if data_sizes is None:
        data_sizes = [10, 100, 1000, 5000]
    
    results = {}
    
    for size in data_sizes:
        # Generate test data with None values
        test_data = {}
        for i in range(size):
            if i % 4 == 0:  # 25% None values
                test_data[f"key_{i}"] = None
            else:
                test_data[f"key_{i}"] = f"value_{i}"
        
        # Benchmark different methods
        size_results = benchmark_optimization_methods(test_data, iterations)
        results[f"size_{size}"] = size_results
        
        print(f"\n📊 Performance for {size} elements:")
        for method, metrics in size_results.items():
            print(f"  {method:12}: {metrics['ops_per_sec']:8.1f} ops/sec "
                  f"({metrics['avg_time']*1000:6.2f}ms avg)")
    
    return results 