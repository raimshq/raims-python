from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType


@dataclass(frozen=True)
class LastResponse:
    status_code: int
    headers: Mapping[str, str] = field(repr=False)
    body: bytes = field(repr=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "headers", MappingProxyType({k.lower(): v for k, v in self.headers.items()})
        )

    @property
    def request_id(self) -> str | None:
        return self.headers.get("request-id")

    @property
    def idempotency_replayed(self) -> bool:
        return self.headers.get("idempotency-replayed", "").lower() == "true"

    @property
    def retry_after(self) -> str | None:
        return self.headers.get("retry-after")
