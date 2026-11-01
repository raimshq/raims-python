from __future__ import annotations

from collections.abc import Iterator, Mapping
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from ._response import LastResponse


def thaw(value: Any) -> Any:
    if isinstance(value, ApiResource):
        return value.to_dict()
    if isinstance(value, Mapping):
        return {k: thaw(v) for k, v in value.items()}
    if isinstance(value, tuple):
        return [thaw(v) for v in value]
    return value


class ApiResource(Mapping[str, Any]):
    """Read-only response data with explicit access to the received fields."""

    _data: Mapping[str, Any]
    _last_response: LastResponse | None

    def __init__(
        self, data: Mapping[str, Any], *, last_response: LastResponse | None = None
    ) -> None:
        object.__setattr__(self, "_data", MappingProxyType(dict(data)))
        object.__setattr__(self, "_last_response", last_response)

    def _get_field(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(name) from None

    if not TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any:
            return self._get_field(name)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("API resources are read-only.")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("API resources are read-only.")

    def __getitem__(self, name: str) -> Any:
        return self._data[name]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __repr__(self) -> str:
        return f"<{type(self).__name__}>"

    @property
    def last_response(self) -> LastResponse | None:
        return self._last_response

    def to_dict(self) -> dict[str, Any]:
        return {key: thaw(value) for key, value in self._data.items()}
