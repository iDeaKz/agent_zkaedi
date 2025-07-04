"""
Resilience Core Command Line Interface.

Provides CLI access to resilience patterns for testing and demonstration.
"""

import argparse
import asyncio
import time
import random
import json
from typing import Optional
from resilience import retry_on_exception, ResilienceConfig
from resilience.config import RetryConfig, CircuitBreakerConfig
from resilience.breaker import CircuitBreaker
from resilience.health import HealthCheckResult, HealthStatus

def simulate_retry(fail_rate: float, max_attempts: int = 3, base_delay: float = 1.0):
    """Simulate retry pattern with configurable failure rate."""
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        jitter=True
    )
    
    @retry_on_exception(config)
    def simulate():
        if random.random() < fail_rate:
            raise RuntimeError("Simulated failure")
        return "Completed successfully"
    
    print(f"🔄 Simulating retry with {fail_rate*100:.0f}% failure rate...")
    start_time = time.time()
    
    try:
        result = simulate()
        elapsed = time.time() - start_time
        print(f"✅ {result} (took {elapsed:.2f}s)")
        return True
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Failed after {max_attempts} attempts: {e} (took {elapsed:.2f}s)")
        return False

def simulate_circuit_breaker(fail_rate: float, failure_threshold: int = 3, recovery_timeout: float = 5.0):
    """Simulate circuit breaker pattern."""
    config = CircuitBreakerConfig(
        failure_threshold=failure_threshold,
        recovery_timeout=recovery_timeout
    )
    breaker = CircuitBreaker(config)
    
    def unreliable_service():
        if random.random() < fail_rate:
            raise RuntimeError("Service unavailable")
        return "Service response"
    
    print(f"⚡ Simulating circuit breaker with {fail_rate*100:.0f}% failure rate...")
    print(f"   Failure threshold: {failure_threshold}, Recovery timeout: {recovery_timeout}s")
    
    results = []
    for i in range(10):
        try:
            result = breaker.call(unreliable_service)
            results.append(f"✅ Call {i+1}: {result}")
        except RuntimeError as e:
            results.append(f"❌ Call {i+1}: Circuit breaker rejected - {e}")
        except Exception as e:
            results.append(f"⚠️  Call {i+1}: Service failed - {e}")
        
        time.sleep(0.5)
    
    # Print results
    for result in results:
        print(f"   {result}")
    
    print(f"   Final circuit state: {breaker.get_state().value}")
    return breaker.get_stats()

def simulate_health_check(checks: int = 5, interval: float = 1.0):
    """Simulate health check pattern."""
    def health_check():
        cpu_usage = random.uniform(0, 100)
        memory_usage = random.uniform(0, 100)
        
        if cpu_usage > 90 or memory_usage > 90:
            status = HealthStatus.UNHEALTHY
            message = f"Critical: CPU {cpu_usage:.1f}%, Memory {memory_usage:.1f}%"
        elif cpu_usage > 70 or memory_usage > 70:
            status = HealthStatus.DEGRADED
            message = f"Warning: CPU {cpu_usage:.1f}%, Memory {memory_usage:.1f}%"
        else:
            status = HealthStatus.HEALTHY
            message = f"Normal: CPU {cpu_usage:.1f}%, Memory {memory_usage:.1f}%"
        
        return HealthCheckResult(
            status=status,
            message=message,
            timestamp=time.time(),
            details={
                "cpu_usage": cpu_usage,
                "memory_usage": memory_usage
            }
        )
    
    print(f"❤️  Running {checks} health checks with {interval}s interval...")
    
    results = []
    for i in range(checks):
        result = health_check()
        status_emoji = {
            HealthStatus.HEALTHY: "✅",
            HealthStatus.DEGRADED: "⚠️",
            HealthStatus.UNHEALTHY: "❌"
        }
        print(f"   {status_emoji[result.status]} Check {i+1}: {result.message}")
        results.append({
            "check": i + 1,
            "status": result.status.value,
            "message": result.message,
            "timestamp": result.timestamp,
            "details": result.details
        })
        
        if i < checks - 1:
            time.sleep(interval)
    
    return results

async def simulate_async_retry(fail_rate: float, max_attempts: int = 2):
    """Simulate async retry pattern."""
    config = RetryConfig(max_attempts=max_attempts, base_delay=0.5)
    
    @retry_on_exception(config)
    async def async_simulate():
        await asyncio.sleep(0.1)  # Simulate async work
        if random.random() < fail_rate:
            raise RuntimeError("Async operation failed")
        return "Async operation completed"
    
    print(f"🚀 Simulating async retry with {fail_rate*100:.0f}% failure rate...")
    start_time = time.time()
    
    try:
        result = await async_simulate()
        elapsed = time.time() - start_time
        print(f"✅ {result} (took {elapsed:.2f}s)")
        return True
    except Exception as e:
        elapsed = time.time() - start_time
        print(f"❌ Async operation failed: {e} (took {elapsed:.2f}s)")
        return False

def run_benchmark(pattern: str, iterations: int = 100):
    """Run performance benchmark for resilience patterns."""
    print(f"📊 Running benchmark for {pattern} pattern ({iterations} iterations)...")
    
    if pattern == "retry":
        config = RetryConfig(max_attempts=2, base_delay=0.01)
        
        @retry_on_exception(config)
        def benchmark_func():
            if random.random() < 0.3:
                raise RuntimeError("Benchmark failure")
            return "success"
        
        start_time = time.time()
        successes = 0
        for i in range(iterations):
            try:
                benchmark_func()
                successes += 1
            except:
                pass
        elapsed = time.time() - start_time
        
    elif pattern == "circuit_breaker":
        config = CircuitBreakerConfig(failure_threshold=5, recovery_timeout=0.1)
        breaker = CircuitBreaker(config)
        
        def benchmark_func():
            if random.random() < 0.2:
                raise RuntimeError("Benchmark failure")
            return "success"
        
        start_time = time.time()
        successes = 0
        for i in range(iterations):
            try:
                breaker.call(benchmark_func)
                successes += 1
            except:
                pass
        elapsed = time.time() - start_time
    
    else:
        print(f"❌ Unknown pattern: {pattern}")
        return
    
    success_rate = (successes / iterations) * 100
    ops_per_sec = iterations / max(elapsed, 0.001)  # Prevent division by zero
    
    print(f"   Success rate: {success_rate:.1f}%")
    print(f"   Operations/sec: {ops_per_sec:.0f}")
    print(f"   Total time: {elapsed:.2f}s")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Resilience Core CLI - Test and demonstrate resilience patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s retry --fail-rate 0.7
  %(prog)s circuit-breaker --fail-rate 0.8 --threshold 2
  %(prog)s health-check --checks 10 --interval 0.5
  %(prog)s async-retry --fail-rate 0.6
  %(prog)s benchmark retry --iterations 1000
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Retry command
    retry_parser = subparsers.add_parser('retry', help='Test retry pattern')
    retry_parser.add_argument('--fail-rate', type=float, default=0.5, 
                             help='Failure rate (0.0-1.0, default: 0.5)')
    retry_parser.add_argument('--max-attempts', type=int, default=3,
                             help='Maximum retry attempts (default: 3)')
    retry_parser.add_argument('--base-delay', type=float, default=1.0,
                             help='Base delay between retries (default: 1.0)')
    
    # Circuit breaker command
    cb_parser = subparsers.add_parser('circuit-breaker', help='Test circuit breaker pattern')
    cb_parser.add_argument('--fail-rate', type=float, default=0.7,
                          help='Failure rate (0.0-1.0, default: 0.7)')
    cb_parser.add_argument('--threshold', type=int, default=3,
                          help='Failure threshold (default: 3)')
    cb_parser.add_argument('--recovery-timeout', type=float, default=5.0,
                          help='Recovery timeout in seconds (default: 5.0)')
    
    # Health check command
    health_parser = subparsers.add_parser('health-check', help='Test health check pattern')
    health_parser.add_argument('--checks', type=int, default=5,
                              help='Number of health checks (default: 5)')
    health_parser.add_argument('--interval', type=float, default=1.0,
                              help='Interval between checks (default: 1.0)')
    
    # Async retry command
    async_parser = subparsers.add_parser('async-retry', help='Test async retry pattern')
    async_parser.add_argument('--fail-rate', type=float, default=0.6,
                             help='Failure rate (0.0-1.0, default: 0.6)')
    async_parser.add_argument('--max-attempts', type=int, default=2,
                             help='Maximum retry attempts (default: 2)')
    
    # Benchmark command
    benchmark_parser = subparsers.add_parser('benchmark', help='Run performance benchmarks')
    benchmark_parser.add_argument('pattern', choices=['retry', 'circuit_breaker'],
                                 help='Pattern to benchmark')
    benchmark_parser.add_argument('--iterations', type=int, default=100,
                                 help='Number of iterations (default: 100)')
    
    # Demo command
    subparsers.add_parser('demo', help='Run all demonstrations')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print("🎯 Resilience Core CLI")
    print("=" * 50)
    
    if args.command == 'retry':
        simulate_retry(args.fail_rate, args.max_attempts, args.base_delay)
    
    elif args.command == 'circuit-breaker':
        simulate_circuit_breaker(args.fail_rate, args.threshold, args.recovery_timeout)
    
    elif args.command == 'health-check':
        simulate_health_check(args.checks, args.interval)
    
    elif args.command == 'async-retry':
        asyncio.run(simulate_async_retry(args.fail_rate, args.max_attempts))
    
    elif args.command == 'benchmark':
        run_benchmark(args.pattern, args.iterations)
    
    elif args.command == 'demo':
        print("Running all demonstrations...")
        print()
        
        simulate_retry(0.6)
        print()
        simulate_circuit_breaker(0.7)
        print()
        simulate_health_check(3, 0.5)
        print()
        asyncio.run(simulate_async_retry(0.5))
        print()
        run_benchmark('retry', 50)
        print()
        run_benchmark('circuit_breaker', 50)
    
    print("\n✨ CLI operation completed!")

if __name__ == "__main__":
    main() 