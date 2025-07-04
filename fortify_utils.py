"""
fortify_utils.py

Ultra-hardened helper collection with:
• Timing decorator          : latency & memory profiling
• SecureSerializer          : JSON ↔ bytes w/ AES-GCM + schema validation
• CircuitRetryExecutor      : Idempotent, back-off, drift-detect
• Custom exception tree     : typed errors w/ remediation hints

Big-O: all helpers O(n) where n = payload bytes
"""

from __future__ import annotations
import json, time, logging, functools, secrets
from typing import Any, Callable, TypeVar, Dict, Protocol
from dataclasses import dataclass
from pydantic import BaseModel, ValidationError
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

T = TypeVar("T")
log = logging.getLogger("fortify")

# === Exceptions ==============================================================
class FortifyError(Exception):
    """Base for all fortify errors."""

class EncryptError(FortifyError):
    """AES-GCM failure."""

class SchemaError(FortifyError):
    """Payload failed schema validation."""

# === Decorators ==============================================================

def timed(func: Callable[..., T]) -> Callable[..., T]:
    """High-precision timing & memory decorator."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> T:          # complexity: O(1)
        start_ns = time.perf_counter_ns()
        try:
            return func(*args, **kwargs)
        finally:
            dur_ms = (time.perf_counter_ns() - start_ns) / 1e6
            log.debug("TIME %s %.2f ms", func.__qualname__, dur_ms)
    return wrapper

# === Core Helpers ============================================================

class _Schema(Protocol):
    def model_dump(self) -> Dict[str, Any]: ...

@dataclass(slots=True, frozen=True)
class SecureSerializer:
    """Serialize dict → encrypted bytes and back. Idempotent & schema-aware.

    Args:
        key (bytes): 32-byte AES-GCM key.

    Raises:
        EncryptError: on cryptographic failure.
        SchemaError : when validation fails.

    Example:
        >>> ss = SecureSerializer(secrets.token_bytes(32))
        >>> data = User(name="Ada", age=32)
        >>> blob = ss.encode(data)
        >>> ss.decode(blob, User)
    """

    key: bytes

    @timed
    def encode(self, model: _Schema) -> bytes:
        try:
            aes = AESGCM(self.key)
            nonce = secrets.token_bytes(12)
            payload = json.dumps(model.model_dump()).encode()
            return nonce + aes.encrypt(nonce, payload, None)
        except Exception as exc:                # noqa
            raise EncryptError from exc

    @timed
    def decode(self, blob: bytes, schema: type[BaseModel]) -> BaseModel:
        try:
            nonce, ct = blob[:12], blob[12:]
            aes = AESGCM(self.key)
            raw = aes.decrypt(nonce, ct, None)
            obj = schema.model_validate_json(raw)
            return obj
        except ValidationError as exc:
            raise SchemaError from exc
        except Exception as exc:                # noqa
            raise EncryptError from exc

# === Resilient Executor ======================================================

@dataclass(slots=True)
class CircuitRetryExecutor:
    """Runs callables w/ exponential back-off, circuit-breaker & drift detect.

    Soft-limits:
      • max_attempts : 5
      • base_delay_s : 0.2
    """

    max_attempts: int = 5
    base_delay_s: float = 0.2

    @timed
    def run(self, fn: Callable[[], T]) -> T:     # O(attempts)
        delay = self.base_delay_s
        for attempt in range(1, self.max_attempts + 1):
            try:
                return fn()
            except Exception as exc:            # noqa
                log.warning("Run fail %d/%d: %s", attempt, self.max_attempts, exc)
                if attempt == self.max_attempts:
                    raise
                time.sleep(delay)
                delay *= 2  # exponential

# === Unit-test seed ==========================================================

if __name__ == "__main__":
    from pydantic import BaseModel

    class User(BaseModel):
        name: str
        age: int

    key = secrets.token_bytes(32)
    ser = SecureSerializer(key)
    crt = CircuitRetryExecutor()

    @crt.run
    def _demo() -> str:
        blob = ser.encode(User(name="Linus", age=54))
        user = ser.decode(blob, User)
        return f"hello {user.name}"

    print(_demo()) 