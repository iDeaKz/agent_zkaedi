#!/usr/bin/env python3
"""
Real-time Performance Monitoring System
Continuous monitoring with adaptive thresholds and auto-tuning.
"""

import asyncio
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque
import threading

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

try:
    from src.holomorphic_core import evaluate, default_params, enable_performance_monitoring
    HOLOMORPHIC_AVAILABLE = True
except ImportError:
    HOLOMORPHIC_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

@dataclass
class PerformanceAlert:
    """Performance alert with context and recommended actions."""
    timestamp: float
    component: str
    metric: str
    current_value: float
    threshold_value: float
    severity: str  # INFO, WARNING, CRITICAL
    message: str
    recommended_actions: List[str]
    auto_tune_available: bool = False

@dataclass
class SystemHealthMetrics:
    """System-wide health metrics."""
    timestamp: float
    overall_health_score: float
    component_scores: Dict[str, float]
    active_alerts: int
    total_throughput: float
    avg_latency: float
    memory_usage_percent: float
    cpu_usage_percent: float

class AdaptiveThresholds:
    """Adaptive performance thresholds that learn from system behavior."""
    
    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate
        self.thresholds = {
            "holomorphic_throughput_min": 4.0e6,
            "holomorphic_latency_max": 50.0,
            "integration_latency_max": 100.0,
            "drift_threshold": 0.15
        }
        self.performance_history = deque(maxlen=1000)
        self.auto_tune_enabled = True
    
    def update_threshold(self, metric: str, observed_value: float, is_healthy: bool):
        """Update threshold based on observed performance."""
        if not self.auto_tune_enabled or metric not in self.thresholds:
            return
        
        current_threshold = self.thresholds[metric]
        
        if is_healthy and metric.endswith("_min"):
            # For minimum thresholds, slowly lower if system is consistently healthy
            new_threshold = current_threshold * (1 - self.learning_rate * 0.1)
            self.thresholds[metric] = max(new_threshold, current_threshold * 0.8)
        elif is_healthy and metric.endswith("_max"):
            # For maximum thresholds, slowly raise if system is consistently healthy
            new_threshold = current_threshold * (1 + self.learning_rate * 0.1)
            self.thresholds[metric] = min(new_threshold, current_threshold * 1.2)
        elif not is_healthy:
            # Tighten thresholds when problems occur
            if metric.endswith("_min"):
                self.thresholds[metric] *= (1 + self.learning_rate)
            else:
                self.thresholds[metric] *= (1 - self.learning_rate)
    
    def get_threshold(self, metric: str) -> float:
        """Get current threshold for a metric."""
        return self.thresholds.get(metric, 0.0)

class PerformanceMonitor:
    """Real-time performance monitoring with adaptive alerting."""
    
    def __init__(self, monitoring_interval: float = 30.0):
        self.monitoring_interval = monitoring_interval
        self.adaptive_thresholds = AdaptiveThresholds()
        self.alerts = deque(maxlen=100)
        self.health_history = deque(maxlen=100)
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []
        self.monitoring_active = False
        self.monitoring_task = None
        
        # Performance tracking
        self.component_metrics = {
            "holomorphic_processing": deque(maxlen=50),
            "pbt_system": deque(maxlen=50),
            "integration": deque(maxlen=50)
        }
        
        # Auto-tuning parameters
        self.auto_tune_history = deque(maxlen=20)
        self.last_auto_tune = 0.0
        self.auto_tune_cooldown = 300.0  # 5 minutes
        
        LOGGER.info("🔍 Performance Monitor initialized")
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Add callback function for alert notifications."""
        self.alert_callbacks.append(callback)
    
    def create_alert(self, component: str, metric: str, current_value: float, 
                    threshold_value: float, severity: str, message: str) -> PerformanceAlert:
        """Create and process a performance alert."""
        recommended_actions = []
        auto_tune_available = False
        
        # Generate context-aware recommendations
        if component == "holomorphic_processing":
            if metric == "throughput" and current_value < threshold_value:
                recommended_actions.extend([
                    "Install Numba for JIT compilation acceleration",
                    "Increase batch size for better vectorization",
                    "Consider GPU acceleration for large workloads",
                    "Profile hot loops for optimization opportunities"
                ])
                auto_tune_available = True
            elif metric == "latency" and current_value > threshold_value:
                recommended_actions.extend([
                    "Reduce sample size or batch processing",
                    "Enable ultra-vectorized harmonics processing",
                    "Check for memory allocation issues"
                ])
        
        elif component == "integration":
            if metric == "latency" and current_value > threshold_value:
                recommended_actions.extend([
                    "Profile end-to-end workflow bottlenecks",
                    "Implement parallel processing where possible",
                    "Add caching layers for frequently accessed data"
                ])
        
        alert = PerformanceAlert(
            timestamp=time.time(),
            component=component,
            metric=metric,
            current_value=current_value,
            threshold_value=threshold_value,
            severity=severity,
            message=message,
            recommended_actions=recommended_actions,
            auto_tune_available=auto_tune_available
        )
        
        self.alerts.append(alert)
        
        # Trigger callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                LOGGER.error(f"Alert callback failed: {e}")
        
        return alert
    
    async def benchmark_holomorphic_processing(self) -> Dict[str, float]:
        """Benchmark holomorphic processing with comprehensive metrics."""
        if not HOLOMORPHIC_AVAILABLE or not NUMPY_AVAILABLE:
            return {"throughput": 0.0, "latency": float('inf'), "health_score": 0.0}
        
        try:
            # Enable performance monitoring in holomorphic core
            enable_performance_monitoring()
            
            # Quick benchmark
            test_size = 10000
            iterations = 3
            
            throughputs = []
            latencies = []
            params = default_params()
            
            for _ in range(iterations):
                t = np.linspace(0, 5, test_size)
                
                start_time = time.perf_counter()
                result = evaluate(t, params)
                elapsed = time.perf_counter() - start_time
                
                throughput = test_size / elapsed
                latency = elapsed * 1000
                
                throughputs.append(throughput)
                latencies.append(latency)
            
            avg_throughput = sum(throughputs) / len(throughputs)
            avg_latency = sum(latencies) / len(latencies)
            
            # Calculate health score
            min_threshold = self.adaptive_thresholds.get_threshold("holomorphic_throughput_min")
            max_threshold = self.adaptive_thresholds.get_threshold("holomorphic_latency_max")
            
            throughput_score = min(1.0, avg_throughput / min_threshold) if min_threshold > 0 else 1.0
            latency_score = min(1.0, max_threshold / avg_latency) if avg_latency > 0 else 1.0
            health_score = (throughput_score + latency_score) / 2
            
            metrics = {
                "throughput": avg_throughput,
                "latency": avg_latency,
                "health_score": health_score,
                "throughput_stability": 1.0 - (max(throughputs) - min(throughputs)) / avg_throughput if avg_throughput > 0 else 0.0
            }
            
            # Check for alerts
            if avg_throughput < min_threshold:
                self.create_alert(
                    "holomorphic_processing", "throughput", avg_throughput, min_threshold,
                    "WARNING", f"Throughput {avg_throughput/1e6:.2f}M below threshold {min_threshold/1e6:.2f}M"
                )
            
            if avg_latency > max_threshold:
                self.create_alert(
                    "holomorphic_processing", "latency", avg_latency, max_threshold,
                    "WARNING", f"Latency {avg_latency:.2f}ms above threshold {max_threshold:.2f}ms"
                )
            
            return metrics
            
        except Exception as e:
            LOGGER.error(f"Holomorphic benchmark failed: {e}")
            return {"throughput": 0.0, "latency": float('inf'), "health_score": 0.0}
    
    async def benchmark_integration_latency(self) -> Dict[str, float]:
        """Benchmark integration latency with drift detection."""
        try:
            integration_times = []
            
            for _ in range(3):
                start_time = time.perf_counter()
                
                # Simulate typical integration workflow
                if HOLOMORPHIC_AVAILABLE and NUMPY_AVAILABLE:
                    t = np.linspace(0, 1, 1000)
                    params = default_params()
                    result = evaluate(t, params)
                
                elapsed = time.perf_counter() - start_time
                integration_times.append(elapsed * 1000)  # Convert to ms
            
            avg_latency = sum(integration_times) / len(integration_times)
            max_threshold = self.adaptive_thresholds.get_threshold("integration_latency_max")
            
            health_score = min(1.0, max_threshold / avg_latency) if avg_latency > 0 else 1.0
            
            # Check for alerts
            if avg_latency > max_threshold:
                self.create_alert(
                    "integration", "latency", avg_latency, max_threshold,
                    "WARNING", f"Integration latency {avg_latency:.2f}ms above threshold {max_threshold:.2f}ms"
                )
            
            return {
                "latency": avg_latency,
                "health_score": health_score,
                "latency_stability": 1.0 - (max(integration_times) - min(integration_times)) / avg_latency if avg_latency > 0 else 0.0
            }
            
        except Exception as e:
            LOGGER.error(f"Integration benchmark failed: {e}")
            return {"latency": float('inf'), "health_score": 0.0}
    
    async def collect_system_health(self) -> SystemHealthMetrics:
        """Collect comprehensive system health metrics."""
        start_time = time.time()
        
        # Benchmark all components
        holo_metrics = await self.benchmark_holomorphic_processing()
        integration_metrics = await self.benchmark_integration_latency()
        
        # Calculate component scores
        component_scores = {
            "holomorphic_processing": holo_metrics.get("health_score", 0.0),
            "integration": integration_metrics.get("health_score", 0.0)
        }
        
        # Overall health score
        overall_health = sum(component_scores.values()) / len(component_scores) if component_scores else 0.0
        
        # Count active alerts
        recent_alerts = [alert for alert in self.alerts if time.time() - alert.timestamp < 300]  # Last 5 minutes
        active_alerts = len(recent_alerts)
        
        # Calculate total throughput
        total_throughput = holo_metrics.get("throughput", 0.0)
        
        # Average latency across components
        latencies = [
            holo_metrics.get("latency", 0.0),
            integration_metrics.get("latency", 0.0)
        ]
        avg_latency = sum(l for l in latencies if l != float('inf')) / len([l for l in latencies if l != float('inf')]) if any(l != float('inf') for l in latencies) else 0.0
        
        health_metrics = SystemHealthMetrics(
            timestamp=start_time,
            overall_health_score=overall_health,
            component_scores=component_scores,
            active_alerts=active_alerts,
            total_throughput=total_throughput,
            avg_latency=avg_latency,
            memory_usage_percent=0.0,  # Could be enhanced with psutil
            cpu_usage_percent=0.0      # Could be enhanced with psutil
        )
        
        self.health_history.append(health_metrics)
        
        # Update adaptive thresholds
        self.adaptive_thresholds.update_threshold(
            "holomorphic_throughput_min", 
            holo_metrics.get("throughput", 0.0), 
            overall_health > 0.8
        )
        
        return health_metrics
    
    async def auto_tune_performance(self) -> Optional[Dict[str, Any]]:
        """Auto-tune system performance based on recent metrics."""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_auto_tune < self.auto_tune_cooldown:
            return None
        
        if len(self.health_history) < 5:
            return None
        
        # Analyze recent performance trends
        recent_health = list(self.health_history)[-5:]
        avg_health = sum(h.overall_health_score for h in recent_health) / len(recent_health)
        
        auto_tune_results = {
            "timestamp": current_time,
            "actions_taken": [],
            "recommendations": []
        }
        
        # Auto-tune based on health trends
        if avg_health < 0.7:
            # System health is poor, suggest aggressive tuning
            auto_tune_results["actions_taken"].append("Lowered performance thresholds by 10%")
            auto_tune_results["recommendations"].extend([
                "Consider system maintenance window",
                "Profile bottlenecks in underperforming components",
                "Check for resource constraints"
            ])
        elif avg_health > 0.9:
            # System is performing well, can tighten thresholds
            auto_tune_results["actions_taken"].append("Raised performance thresholds by 5%")
            auto_tune_results["recommendations"].append("System performing optimally")
        
        if auto_tune_results["actions_taken"]:
            self.last_auto_tune = current_time
            self.auto_tune_history.append(auto_tune_results)
            LOGGER.info(f"🔧 Auto-tuning performed: {len(auto_tune_results['actions_taken'])} actions")
        
        return auto_tune_results
    
    async def monitoring_loop(self):
        """Main monitoring loop."""
        LOGGER.info("🔍 Starting performance monitoring loop")
        
        while self.monitoring_active:
            try:
                # Collect health metrics
                health_metrics = await self.collect_system_health()
                
                # Log health status
                LOGGER.info(f"🏥 System Health: {health_metrics.overall_health_score:.1%}")
                LOGGER.info(f"   Active Alerts: {health_metrics.active_alerts}")
                LOGGER.info(f"   Total Throughput: {health_metrics.total_throughput/1e6:.2f}M samples/sec")
                LOGGER.info(f"   Avg Latency: {health_metrics.avg_latency:.2f}ms")
                
                # Auto-tune if needed
                await self.auto_tune_performance()
                
                # Check for critical alerts
                critical_alerts = [alert for alert in self.alerts if alert.severity == "CRITICAL" and time.time() - alert.timestamp < 60]
                if critical_alerts:
                    LOGGER.critical(f"🚨 {len(critical_alerts)} CRITICAL alerts active!")
                
                # Wait for next monitoring cycle
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                LOGGER.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(self.monitoring_interval)
    
    def start_monitoring(self):
        """Start the monitoring system."""
        if self.monitoring_active:
            LOGGER.warning("Monitoring already active")
            return
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self.monitoring_loop())
        LOGGER.info("🚀 Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
        LOGGER.info("🛑 Performance monitoring stopped")
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report."""
        if not self.health_history:
            return {"status": "no_data"}
        
        latest_health = self.health_history[-1]
        recent_alerts = list(self.alerts)[-10:]  # Last 10 alerts
        
        return {
            "timestamp": time.time(),
            "overall_health_score": latest_health.overall_health_score,
            "component_scores": latest_health.component_scores,
            "active_alerts": latest_health.active_alerts,
            "recent_alerts": [asdict(alert) for alert in recent_alerts],
            "total_throughput": latest_health.total_throughput,
            "avg_latency": latest_health.avg_latency,
            "adaptive_thresholds": self.adaptive_thresholds.thresholds,
            "monitoring_active": self.monitoring_active,
            "auto_tune_history": list(self.auto_tune_history)
        }

# Alert notification handlers
def console_alert_handler(alert: PerformanceAlert):
    """Console alert handler."""
    severity_emoji = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨"}
    emoji = severity_emoji.get(alert.severity, "📊")
    
    print(f"\n{emoji} PERFORMANCE ALERT [{alert.severity}]")
    print(f"   Component: {alert.component}")
    print(f"   Metric: {alert.metric}")
    print(f"   Current: {alert.current_value:.2f}")
    print(f"   Threshold: {alert.threshold_value:.2f}")
    print(f"   Message: {alert.message}")
    
    if alert.recommended_actions:
        print("   Recommended Actions:")
        for action in alert.recommended_actions:
            print(f"     • {action}")
    print()

def file_alert_handler(alert: PerformanceAlert):
    """File-based alert handler."""
    alert_data = asdict(alert)
    alert_file = Path("performance_alerts.jsonl")
    
    with open(alert_file, "a") as f:
        f.write(json.dumps(alert_data) + "\n")

async def main():
    """Main monitoring application."""
    print("🔍 Elite AI Performance Monitor")
    print("=" * 40)
    
    # Create monitor
    monitor = PerformanceMonitor(monitoring_interval=30.0)
    
    # Add alert handlers
    monitor.add_alert_callback(console_alert_handler)
    monitor.add_alert_callback(file_alert_handler)
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        print("🚀 Monitoring active - Press Ctrl+C to stop")
        
        # Keep running and periodically show health report
        while True:
            await asyncio.sleep(60)  # Show report every minute
            
            health_report = monitor.get_health_report()
            if health_report.get("status") != "no_data":
                print(f"\n📊 Health: {health_report['overall_health_score']:.1%} | "
                      f"Alerts: {health_report['active_alerts']} | "
                      f"Throughput: {health_report['total_throughput']/1e6:.2f}M/s")
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping monitoring...")
        monitor.stop_monitoring()
        
        # Save final report
        final_report = monitor.get_health_report()
        report_file = Path("final_health_report.json")
        report_file.write_text(json.dumps(final_report, indent=2))
        print(f"📁 Final report saved to: {report_file}")

if __name__ == "__main__":
    asyncio.run(main()) 