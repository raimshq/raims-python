from __future__ import annotations

import math
import re
from collections.abc import Callable
from dataclasses import dataclass, field


def visible_ascii(value: str, maximum: int, label: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(
        r"[\x21-\x7e]{1," + str(maximum) + "}", value
    ):
        raise ValueError(f"{label} must contain visible ASCII characters without spaces.")
    return value


def validate_timeout(value: float) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not 0 < value <= 300
    ):
        raise ValueError("timeout must be greater than zero and at most 300 seconds.")
    return float(value)


def validate_retries(value: int) -> int:
    if type(value) is not int or not 0 <= value <= 5:
        raise ValueError("max_network_retries must be an integer between zero and five.")
    return value


@dataclass(frozen=True)
class RequestOptions:
    api_key: str | None = field(default=None, repr=False)
    idempotency_key: str | None = field(default=None, repr=False)
    timeout: float | None = None
    max_network_retries: int | None = None

    def __post_init__(self) -> None:
        if self.api_key is not None:
            visible_ascii(self.api_key, 4096, "api_key")
        if self.idempotency_key is not None:
            visible_ascii(self.idempotency_key, 255, "idempotency_key")
        if self.timeout is not None:
            validate_timeout(self.timeout)
        if self.max_network_retries is not None:
            validate_retries(self.max_network_retries)


@dataclass(frozen=True)
class RequestDiagnostics:
    operation_id: str
    method: str
    path: str
    attempt: int
    duration_ms: float
    status_code: int | None
    request_id: str | None
    will_retry: bool
    retry_delay_ms: float | None


RequestObserver = Callable[[RequestDiagnostics], None]
