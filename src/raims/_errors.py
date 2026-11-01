from __future__ import annotations

from typing import Any

from ._response import LastResponse


class RaimsError(Exception):
    """Base for failures reported by the SDK."""

    def __init__(
        self,
        message: str,
        *,
        last_response: LastResponse | None = None,
        api_error: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.last_response = last_response
        self.api_error = api_error

    @property
    def status_code(self) -> int | None:
        return self.last_response.status_code if self.last_response else None

    @property
    def request_id(self) -> str | None:
        return self.last_response.request_id if self.last_response else None

    @property
    def code(self) -> str | None:
        value = self.api_error.get("code") if self.api_error else None
        return value if isinstance(value, str) else None

    @property
    def retry_after(self) -> str | None:
        return self.last_response.retry_after if self.last_response else None

    def __repr__(self) -> str:
        return f"{type(self).__name__}(status_code={self.status_code!r})"


class ApiError(RaimsError):
    pass


class AuthenticationError(ApiError):
    pass


class PermissionError(ApiError):
    pass


class NotFoundError(ApiError):
    pass


class ConflictError(ApiError):
    pass


class RateLimitError(ApiError):
    pass


class InvalidRequestError(ApiError):
    pass


class ConnectionError(RaimsError):
    pass


class UnexpectedResponseError(RaimsError):
    pass


class SignatureVerificationError(RaimsError):
    pass
