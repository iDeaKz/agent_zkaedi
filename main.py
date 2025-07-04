"""
Resilience Core Demo Launcher.

Demonstrates the resilience patterns in action.
"""

import asyncio
import time
import random
from resilience import retry_on_exception, ResilienceConfig
from resilience.config import RetryConfig, CircuitBreakerConfig
from resilience.breaker import CircuitBreaker
from resilience.health import HealthCheckResult, HealthStatus

def demo_retry_pattern():
    """Demonstrate retry pattern with exponential backoff."""
    print("Demo: Retry Pattern")
    print("=" * 50)
    
    config = RetryConfig(max_attempts=3, base_delay=0.5, jitter=True)
    
    @retry_on_exception(config)
    def might_fail():
        if random.random() < 0.7:
            raise ValueError("Unstable operation!")
        return "Success!"
    
    print("Attempting operation with 70% failure rate...")
    try:
        result = might_fail()
        print(f"✅ Result: {result}")
    except Exception as e:
        print(f"❌ Final failure: {e}")
    print()

def demo_circuit_breaker():
    """Demonstrate circuit breaker pattern."""
    print("Demo: Circuit Breaker Pattern")
    print("=" * 50)
    
    config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=2.0)
    breaker = CircuitBreaker(config)
    
    def unreliable_service():
        if random.random() < 0.8:
            raise RuntimeError("Service temporarily unavailable")
        return "Service response"
    
    print("Testing unreliable service with circuit breaker...")
    
    for i in range(5):
        try:
            result = breaker.call(unreliable_service)
            print(f"✅ Call {i+1}: {result}")
        except RuntimeError as e:
            print(f"❌ Call {i+1}: Circuit breaker rejected - {e}")
        except Exception as e:
            print(f"⚠️  Call {i+1}: Service failed - {e}")
        
        time.sleep(0.5)
    
    print(f"Circuit state: {breaker.get_state().value}")
    print()

def demo_health_check():
    """Demonstrate health check pattern."""
    print("Demo: Health Check Pattern")
    print("=" * 50)
    
    def system_health_check():
        # Simulate system health check
        cpu_usage = random.uniform(0, 100)
        memory_usage = random.uniform(0, 100)
        
        if cpu_usage > 90 or memory_usage > 90:
            status = HealthStatus.UNHEALTHY
            message = f"High resource usage: CPU {cpu_usage:.1f}%, Memory {memory_usage:.1f}%"
        elif cpu_usage > 70 or memory_usage > 70:
            status = HealthStatus.DEGRADED
            message = f"Elevated resource usage: CPU {cpu_usage:.1f}%, Memory {memory_usage:.1f}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"Normal operation: CPU {cpu_usage:.1f}%, Memory {memory_usage:.1f}%"
        
        return HealthCheckResult(
            status=status,
            message=message,
            timestamp=time.time(),
            details={
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage
            }
        )
    
    print("Running health checks...")
    for i in range(3):
        result = system_health_check()
        status_emoji = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.DEGRADED: "⚠️",
            HealthStatus.UNHEALTHY: "❌"
        }
        print(f"{status_emoji[result.status]} Check {i+1}: {result.message}")
        time.sleep(1)
    print()

async def demo_async_resilience():
    """Demonstrate async resilience patterns."""
    print("🚀 Demo: Async Resilience Patterns")
    print("=" * 50)
    
    config = RetryConfig(max_attempts=2, base_delay=0.3)
    
    @retry_on_exception(config)
    async def async_might_fail():
        await asyncio.sleep(0.1)  # Simulate async work
        if random.random() < 0.6:
            raise ValueError("Async operation failed!")
        return "Async success!"
    
    print("Testing async operation with retry...")
    try:
        result = await async_might_fail()
        print(f"✅ Async result: {result}")
    except Exception as e:
        print(f"❌ Async failure: {e}")
    print()

def demo_integration():
    """Demonstrate integration of multiple resilience patterns."""
    print("🔗 Demo: Integrated Resilience Patterns")
    print("=" * 50)
    
    # Configure patterns
    retry_config = RetryConfig(max_attempts=2, base_delay=0.2)
    breaker_config = CircuitBreakerConfig(failure_threshold=3, recovery_timeout=1.0)
    
    breaker = CircuitBreaker(breaker_config)
    
    @retry_on_exception(retry_config)
    def resilient_operation():
        if random.random() < 0.7:
            raise RuntimeError("Operation failed")
        return "Operation successful"
    
    print("Testing integrated resilience (retry + circuit breaker)...")
    
    for i in range(6):
        try:
            result = breaker.call(resilient_operation)
            print(f"✅ Attempt {i+1}: {result}")
        except RuntimeError as e:
            print(f"❌ Attempt {i+1}: Circuit breaker rejected - {e}")
        except Exception as e:
            print(f"⚠️  Attempt {i+1}: Operation failed - {e}")
        
        time.sleep(0.3)
    
    print(f"Final circuit state: {breaker.get_state().value}")
    print()

def main():
    """Run all resilience pattern demonstrations."""
    print("Resilience Core - Pattern Demonstrations")
    print("=" * 60)
    print()
    
    # Run synchronous demos
    demo_retry_pattern()
    demo_circuit_breaker()
    demo_health_check()
    demo_integration()
    
    # Run async demo
    asyncio.run(demo_async_resilience())
    
    print("🎉 All demonstrations completed!")
    print("\n💡 Key Takeaways:")
    print("• Retry patterns handle temporary failures with exponential backoff")
    print("• Circuit breakers prevent cascading failures")
    print("• Health checks provide continuous system monitoring")
    print("• Patterns work together for robust system design")
    print("• Both sync and async functions are supported")

if __name__ == "__main__":
    main() 