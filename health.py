"""
Health check patterns for system monitoring.

Provides threaded health check capabilities for continuous monitoring.
"""

import threading
import time
import logging
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Health check status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    """Result of a health check operation."""
    status: HealthStatus
    message: str
    timestamp: float
    details: Optional[Dict[str, Any]] = None

class HealthCheckThread(threading.Thread):
    """
    Threaded health check monitor.
    
    Runs health checks at specified intervals in a background thread.
    """
    
    def __init__(self, check_func: Callable[[], HealthCheckResult], interval: float) -> None:
        super().__init__(daemon=True)
        self.check_func = check_func
        self.interval = interval
        self._stop_event = threading.Event()
        self.check_count = 0
        self.last_result: Optional[HealthCheckResult] = None
        self._lock = threading.Lock()

    def start(self) -> None:
        """Start the health check thread."""
        try:
            super().start()
            logger.info(f"Health check thread started with {self.interval}s interval")
        except RuntimeError as e:
            logger.warning(f"Could not start health check thread: {e}")
            # Fallback to synchronous execution
            for _ in range(3):
                self.check_count += 1
                result = self.check_func()
                self._update_last_result(result)
                time.sleep(self.interval)

    def run(self) -> None:
        """Main health check loop."""
        while not self._stop_event.is_set():
            try:
                self.check_count += 1
                result = self.check_func()
                self._update_last_result(result)
                
                # Log health status changes
                if result.status == HealthStatus.UNHEALTHY:
                    logger.error(f"Health check failed: {result.message}")
                elif result.status == HealthStatus.DEGRADED:
                    logger.warning(f"Health check degraded: {result.message}")
                else:
                    logger.debug(f"Health check passed: {result.message}")
                    
            except Exception as e:
                logger.error(f"Health check error: {e}")
                self._update_last_result(HealthCheckResult(
                    status=HealthStatus.UNHEALTHY,
                    message=f"Health check error: {e}",
                    timestamp=time.time()
                ))
            
            time.sleep(self.interval)

    def stop(self) -> None:
        """Stop the health check thread."""
        self._stop_event.set()
        logger.info("Health check thread stopped")

    def _update_last_result(self, result: HealthCheckResult) -> None:
        """Update the last health check result."""
        with self._lock:
            self.last_result = result

    def get_last_result(self) -> Optional[HealthCheckResult]:
        """Get the last health check result."""
        with self._lock:
            return self.last_result

    def is_healthy(self) -> bool:
        """Check if the system is currently healthy."""
        result = self.get_last_result()
        return result is not None and result.status == HealthStatus.HEALTHY

class HealthChecker:
    """
    Centralized health check management.
    
    Manages multiple health checks and provides aggregated status.
    """
    
    def __init__(self):
        self.health_checks: Dict[str, HealthCheckThread] = {}
        self._lock = threading.Lock()

    def add_health_check(
        self, 
        name: str, 
        check_func: Callable[[], HealthCheckResult], 
        interval: float
    ) -> None:
        """Add a new health check."""
        with self._lock:
            if name in self.health_checks:
                logger.warning(f"Health check '{name}' already exists, replacing")
                self.health_checks[name].stop()
            
            health_check = HealthCheckThread(check_func, interval)
            self.health_checks[name] = health_check
            health_check.start()
            logger.info(f"Added health check '{name}' with {interval}s interval")

    def remove_health_check(self, name: str) -> None:
        """Remove a health check."""
        with self._lock:
            if name in self.health_checks:
                self.health_checks[name].stop()
                del self.health_checks[name]
                logger.info(f"Removed health check '{name}'")

    def get_health_status(self) -> Dict[str, Any]:
        """Get aggregated health status."""
        with self._lock:
            status = {
                "overall": HealthStatus.HEALTHY,
                "checks": {},
                "timestamp": time.time()
            }
            
            for name, health_check in self.health_checks.items():
                result = health_check.get_last_result()
                if result:
                    status["checks"][name] = {
                        "status": result.status.value,
                        "message": result.message,
                        "timestamp": result.timestamp,
                        "details": result.details
                    }
                    
                    # Update overall status
                    if result.status == HealthStatus.UNHEALTHY:
                        status["overall"] = HealthStatus.UNHEALTHY
                    elif result.status == HealthStatus.DEGRADED and status["overall"] == HealthStatus.HEALTHY:
                        status["overall"] = HealthStatus.DEGRADED
                else:
                    status["checks"][name] = {
                        "status": HealthStatus.UNKNOWN.value,
                        "message": "No health check result available",
                        "timestamp": time.time()
                    }
                    if status["overall"] == HealthStatus.HEALTHY:
                        status["overall"] = HealthStatus.UNKNOWN
            
            status["overall"] = status["overall"].value
            return status

    def stop_all(self) -> None:
        """Stop all health checks."""
        with self._lock:
            for health_check in self.health_checks.values():
                health_check.stop()
            self.health_checks.clear()
            logger.info("All health checks stopped")

# Global health checker instance
health_checker = HealthChecker() 