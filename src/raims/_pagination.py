from __future__ import annotations

from collections.abc import AsyncIterator, Iterator, Mapping
from typing import Any, Generic, TypeVar, cast

from ._errors import UnexpectedResponseError
from ._resource import ApiResource
from ._response import LastResponse
from .models import PageInfo

T = TypeVar("T")


class _Page(Generic[T]):
    def __init__(
        self,
        resource: ApiResource,
        client: Any,
        operation_id: str,
        path_params: dict[str, str],
        params: Mapping[str, Any],
        options: Any,
    ) -> None:
        self._resource = resource
        self._client = client
        self._operation_id = operation_id
        self._path_params = dict(path_params)
        self._params = dict(params)
        self._options = options

    @property
    def list(self) -> tuple[T, ...]:
        return self._resource["list"]

    @property
    def page(self) -> PageInfo:
        return cast(PageInfo, self._resource["page"])

    @property
    def last_response(self) -> LastResponse | None:
        return self._resource.last_response

    def to_dict(self) -> dict[str, Any]:
        return self._resource.to_dict()

    def __len__(self) -> int:
        return len(self.list)

    def __iter__(self) -> Iterator[T]:
        return iter(self.list)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} items={len(self)}>"

    def _navigation(self, forward: bool) -> dict[str, Any] | None:
        flag, cursor_field, key, opposite = (
            ("has_next", "next_after", "after", "before")
            if forward
            else ("has_previous", "previous_before", "before", "after")
        )
        if not self.page[flag]:
            return None
        cursor = self.page[cursor_field]
        if not isinstance(cursor, str) or not cursor or cursor == self._params.get(key):
            raise UnexpectedResponseError(
                "Pagination returned a missing or repeated cursor.",
                last_response=self.last_response,
            )
        params = dict(self._params)
        params.pop(opposite, None)
        params[key] = cursor
        return params


class ApiList(_Page[T]):
    def next_page(self) -> ApiList[T] | None:
        return self._load(True)

    def previous_page(self) -> ApiList[T] | None:
        return self._load(False)

    def _load(self, forward: bool) -> ApiList[T] | None:
        params = self._navigation(forward)
        if params is None:
            return None
        return self._client._request(
            self._operation_id, path_params=self._path_params, params=params, options=self._options
        )

    def auto_paging_iter(self) -> Iterator[T]:
        current: ApiList[T] | None = self
        seen = {self._params["after"]} if self._params.get("after") else set()
        while current is not None:
            yield from current.list
            params = current._navigation(True)
            if params is None:
                return
            cursor = params["after"]
            if cursor in seen:
                raise UnexpectedResponseError(
                    "Pagination returned a repeated cursor.", last_response=current.last_response
                )
            seen.add(cursor)
            current = current.next_page()


class AsyncApiList(_Page[T]):
    async def next_page(self) -> AsyncApiList[T] | None:
        return await self._load(True)

    async def previous_page(self) -> AsyncApiList[T] | None:
        return await self._load(False)

    async def _load(self, forward: bool) -> AsyncApiList[T] | None:
        params = self._navigation(forward)
        if params is None:
            return None
        return await self._client._request(
            self._operation_id, path_params=self._path_params, params=params, options=self._options
        )

    async def auto_paging_iter(self) -> AsyncIterator[T]:
        current: AsyncApiList[T] | None = self
        seen = {self._params["after"]} if self._params.get("after") else set()
        while current is not None:
            for item in current.list:
                yield item
            params = current._navigation(True)
            if params is None:
                return
            cursor = params["after"]
            if cursor in seen:
                raise UnexpectedResponseError(
                    "Pagination returned a repeated cursor.", last_response=current.last_response
                )
            seen.add(cursor)
            current = await current.next_page()
