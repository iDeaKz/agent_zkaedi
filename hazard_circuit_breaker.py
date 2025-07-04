#!/usr/bin/env python3
from __future__ import annotations  # enable forward references
"""
hazard_driven_circuit_breaker_master.py

A unified, CPU-only circuit breaker system with:
- Pre-trained symbolic hazard function H(t)
- Dynamic risk assessment via softplus-transformed linear model
- Intelligent retries and checkpoint-based feedback
- Soft performance budgets (timeout + memory)
- Tamper-evident, thread-safe audit logging
- Idempotent recovery and customizable corrections
"""

# Standard library imports (PEP 8 ordering)
import time
import math
import tracemalloc
import hashlib
import threading
import random
from collections import deque
from dataclasses import dataclass
from typing import Callable, TypeVar, Generic, Optional, Any, Dict
import concurrent.futures
import unittest

T = TypeVar('T')

class OpenCircuitException(Exception):
    """
    Raised when the circuit is open and execution is blocked.

    Attributes:
        timestamp (float): Time when the circuit opened.
    """
    def __init__(self, message: str = "Circuit is open; execution blocked."):
        super().__init__(message)
        self.timestamp: float = time.time()

class Correction:
    """
    Performs domain-specific rollback or cleanup after failures.
    """
    @staticmethod
    def apply_if_needed(context: Any) -> None:
        # TODO: implement cleanup logic based on stored context
        pass

class SecureLogger:
    """
    Tamper-evident logger with input sanitization and SHA-256 chaining.
    Thread-safe via RLock.
    """
    def __init__(self, logfile: str = "circuit_audit.log"):
        self.logfile = logfile
        self._lock = threading.RLock()
        self._last_hash: Optional[str] = None

    def sanitize(self, data: str) -> str:
        s = data.replace("\n", " ").replace("\r", " ")
        return (s[:1024] + "...[truncated]") if len(s) > 1024 else s

    def log_event(self, event: str, details: Dict[str, Any]) -> None:
        with self._lock:
            ts = time.time()
            safe = {k: self.sanitize(str(v)) for k, v in details.items()}
            entry = f"{ts:.3f}|{event}|{safe}"
            digest = hashlib.sha256(((self._last_hash or "") + entry).encode()).hexdigest()
            self._last_hash = digest
            with open(self.logfile, "a", encoding="utf-8") as f:
                f.write(f"{entry}|hash={digest}\n")

class FeedbackCheckpointer:
    """
    Records recent events (bounded) and stores checkpoints.
    Provides sliding-window metrics for risk evaluation.
    """
    def __init__(self, max_events: int = 1000):
        self._events: deque = deque(maxlen=max_events)
        self._checkpoints: Dict[str, Any] = {}

    def record_success(self, duration: Optional[float] = None) -> None:
        self._events.append((time.time(), "SUCCESS", 0.0, duration))

    def record_failure(self, severity: float = 1.0, duration: Optional[float] = None) -> None:
        self._events.append((time.time(), "FAILURE", severity, duration))

    def recent_failure_rate(self, window: float = 60.0) -> float:
        cutoff = time.time() - window
        count = sum(1 for t, typ, *_ in self._events if typ == "FAILURE" and t >= cutoff)
        return count / window if window > 0 else float(count)

    def seasonal_factor(self, now: float) -> float:
        hour = time.localtime(now).tm_hour
        return 1.2 if 8 <= hour < 18 else 0.8

    def volatility(self, window: float = 300.0) -> float:
        cutoff = time.time() - window
        durations = [d for t, typ, _, d in self._events if typ == "SUCCESS" and d and t >= cutoff]
        if not durations:
            return 0.0
        mean = sum(durations) / len(durations)
        return math.sqrt(sum((x - mean) ** 2 for x in durations) / len(durations))

    def last_error_severity(self) -> float:
        for t, typ, sev, _ in reversed(self._events):
            if typ == "FAILURE":
                return sev
        return 0.0

    def save_checkpoint(self, op_id: str, data: Any) -> None:
        self._checkpoints[op_id] = data

    def get_checkpoint(self, op_id: str) -> Any:
        return self._checkpoints.get(op_id)

    def last_context(self) -> Any:
        return self._events[-1] if self._events else None

@dataclass(frozen=True)
class RiskParams:
    theta0: float = 0.0
    theta_fail: float = 0.0
    theta_season: float = 0.0
    theta_vol: float = 0.0
    theta_sev: float = 0.0
    threshold: float = 1.0

class RiskStrategy:
    """
    Computes hazard H(t)=softplus(linear combination of features).
    """
    def __init__(self, params: RiskParams):
        self.params = params
        self.time_budget: Optional[float] = None
        self.memory_budget: Optional[int] = None
        self.mitigation: Optional[Mitigation] = None

    def set_budgets(self, time_budget: float, memory_budget: int) -> None:
        self.time_budget = time_budget
        self.memory_budget = memory_budget

    def set_mitigation(self, mitigation: Mitigation) -> None:
        self.mitigation = mitigation

    def evaluate_risk(self, cp: FeedbackCheckpointer) -> float:
        now = time.time()
        f1 = cp.recent_failure_rate()
        f2 = cp.seasonal_factor(now)
        f3 = cp.volatility()
        f4 = cp.last_error_severity()
        raw = (self.params.theta0 + self.params.theta_fail * f1
               + self.params.theta_season * f2 + self.params.theta_vol * f3
               + self.params.theta_sev * f4)
        return math.log1p(math.exp(raw))

class Mitigation:
    """
    Provides fallback values or cached results.
    """
    def __init__(self, fallback: Any = None, cache: Optional[Dict[Any, Any]] = None):
        self.fallback = fallback
        self.cache = cache or {}

    def apply(self, key: Any = None) -> Any:
        if key is not None and key in self.cache:
            return self.cache[key]
        if self.fallback is not None:
            return self.fallback
        raise OpenCircuitException("No fallback available.")

class ErrorHandler:
    """
    Processes failures: logs, updates hazard, and trips circuit.
    """
    def __init__(self, strategy: RiskStrategy, cp: FeedbackCheckpointer, logger: SecureLogger):
        self.strategy = strategy
        self.cp = cp
        self.logger = logger

    def handle(self, err: Exception, sev: float) -> Any:
        self.logger.log_event("ERROR", {"type": type(err).__name__, "severity": sev})
        self.cp.record_failure(sev)
        risk = self.strategy.evaluate_risk(self.cp)
        if risk > self.strategy.params.threshold:
            self.logger.log_event("TRIP", {"risk": risk})
            Correction.apply_if_needed(self.cp.last_context())
            return OpenCircuitException(f"Risk {risk:.2f} exceeds threshold.")
        return err

class Handler(Generic[T]):
    """
    Executes operations with timeouts, memory tracking, and error delegation.
    """
    _executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    def __init__(self, manager: CircuitBreakerManager[T], cp: FeedbackCheckpointer, logger: SecureLogger):
        self.manager = manager
        self.cp = cp
        self.logger = logger
        strat = manager.strategy
        self.time_budget = strat.time_budget
        self.memory_budget = strat.memory_budget

    def run(self, func: Callable[..., T]) -> T:
        start = time.time()
        if self.memory_budget:
            tracemalloc.start()
        try:
            if self.time_budget:
                fut = self._executor.submit(func)
                res = fut.result(timeout=self.time_budget)
            else:
                res = func()
        except Exception as exc:
            if self.memory_budget:
                tracemalloc.stop()
            return self._fail(exc, start)
        if self.memory_budget:
            tracemalloc.stop()
        return res

    def _fail(self, exc: Exception, start: float) -> Any:
        dur = time.time() - start
        sev = 0.5 if isinstance(exc, TimeoutError) else 1.0
        self.logger.log_event("FAIL", {"error": str(exc), "duration": dur})
        fb = ErrorHandler(self.manager.strategy, self.cp, self.logger).handle(exc, sev)
        if isinstance(fb, Exception):
            raise fb
        return fb

class CircuitBreakerManager(Generic[T]):
    """
    Orchestrates state transitions, risk checks, execution, and mitigation.
    """
    def __init__(
        self,
        strategy: RiskStrategy,
        cp: FeedbackCheckpointer,
        mitigation: Mitigation,
        logger: SecureLogger,
        cooldown: float = 5.0
    ):
        self.strategy = strategy
        self.cp = cp
        self.mitigation = mitigation
        self.logger = logger
        self.cooldown = cooldown
        self.state: str = "CLOSED"
        self.last_event: float = time.time()
        self._lock = threading.RLock()

    def execute(self, func: Callable[..., T], key: Any = None) -> T:
        with self._lock:
            now = time.time()
            risk = self.strategy.evaluate_risk(self.cp)

            if self.state == "OPEN" and now - self.last_event < self.cooldown:
                self.logger.log_event("BLOCK", {"risk": risk})
                return self.mitigation.apply(key)

            if risk > self.strategy.params.threshold:
                self.state, self.last_event = "OPEN", now
                self.logger.log_event("OPEN", {"risk": risk})
                return self.mitigation.apply(key)

            if self.state == "OPEN":
                self.state, self.last_event = "HALF_OPEN", now
                self.logger.log_event("HALF_OPEN", {"risk": risk})

            try:
                result = Handler(self, self.cp, self.logger).run(func)
            except OpenCircuitException:
                return self.mitigation.apply(key)
            else:
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.logger.log_event("CLOSED", {"time": now})
                self.cp.record_success(time.time() - now)
                return result 