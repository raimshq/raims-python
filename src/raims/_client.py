from __future__ import annotations

import asyncio
import ipaddress
import json
import random
import re
import time
from collections.abc import Mapping
from contextvars import ContextVar
from dataclasses import dataclass
from email.utils import parsedate_to_datetime
from types import TracebackType
from typing import Any, TypeVar
from urllib.parse import quote, urlencode, urlsplit

import httpx

from . import _errors as errors
from . import services
from ._options import (
    RequestDiagnostics,
    RequestObserver,
    RequestOptions,
    validate_retries,
    validate_timeout,
    visible_ascii,
)
from ._pagination import ApiList, AsyncApiList
from ._response import LastResponse
from ._validation import CONTRACT, hydrate, parse_json, serialize_params, validate_response
from ._version import __version__ as VERSION

_MAX_RESPONSE_BYTES = 16 * 1024 * 1024
_RETRY_STATUSES = {408, 429, 500, 502, 503, 504}
_SyncClientT = TypeVar("_SyncClientT", bound="RaimsClient")
_AsyncClientT = TypeVar("_AsyncClientT", bound="AsyncRaimsClient")


def _api_base(value: str) -> str:
    if not isinstance(value, str) or re.search(r"[\x00-\x20\x7f\\]", value):
        raise ValueError("api_base must be an HTTPS origin without credentials or a path.")
    try:
        url = urlsplit(value)
        hostname = url.hostname
        port = url.port
    except ValueError:
        raise ValueError("api_base is invalid.") from None
    loopback = hostname == "localhost"
    try:
        loopback = loopback or ipaddress.ip_address(hostname or "").is_loopback
    except ValueError:
        pass
    if (
        not hostname
        or url.username is not None
        or url.password is not None
        or url.path not in ("", "/")
        or url.query
        or url.fragment
        or "?" in value
        or "#" in value
        or (url.scheme != "https" and not (url.scheme == "http" and loopback))
        or port == 0
    ):
        raise ValueError(
            "api_base requires HTTPS without credentials, path, query or fragment; HTTP is allowed only on loopback."
        )
    return value.rstrip("/")


def _retry_delay(attempt: int, response: LastResponse | None) -> float | None:
    delay = min(2.0, 0.5 * 2**attempt) * random.uniform(0.5, 1.0)
    header = response.retry_after if response else None
    if header:
        try:
            if re.fullmatch(r"[0-9]+", header.strip()):
                wanted = float(header)
            else:
                wanted = parsedate_to_datetime(header).timestamp() - time.time()
            if wanted > 30:
                return None
            delay = max(delay, wanted)
        except (ValueError, TypeError, OverflowError):
            pass
    return delay


@dataclass
class _Prepared:
    operation: dict[str, Any]
    path_params: dict[str, str]
    params: dict[str, Any]
    options: RequestOptions
    url: str
    headers: dict[str, str]
    body: bytes | None
    timeout: float
    retries: int


class _ClientBase:
    def __init__(
        self,
        api_key: str,
        *,
        api_base: str,
        timeout: float,
        connect_timeout: float,
        max_network_retries: int,
        request_observer: RequestObserver | None,
    ) -> None:
        self._api_key = visible_ascii(api_key, 4096, "api_key")
        self._base = _api_base(api_base)
        self._timeout = validate_timeout(timeout)
        self._connect_timeout = validate_timeout(connect_timeout)
        self._retries = validate_retries(max_network_retries)
        if request_observer is not None and not callable(request_observer):
            raise ValueError("request_observer must be callable.")
        self._observer = request_observer
        self._notifying: ContextVar[bool] = ContextVar("raims_observer", default=False)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} version={VERSION}>"

    def _prepare(
        self,
        operation_id: str,
        path_params: dict[str, str],
        params: Mapping[str, Any] | None,
        options: RequestOptions | None,
    ) -> _Prepared:
        operation = CONTRACT["operations"][operation_id]
        if options is not None and not isinstance(options, RequestOptions):
            raise ValueError("options must be a RequestOptions instance.")
        options = options or RequestOptions()
        if options.idempotency_key is not None and not operation["idempotency"]:
            raise ValueError("This operation does not accept an idempotency key.")
        path = operation["path"]
        if set(path_params) != set(operation["pathParams"]):
            raise ValueError("The operation received invalid path parameters.")
        for name, value in path_params.items():
            if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", value):
                raise ValueError("Resource identifiers must be non-empty URL-safe strings.")
            path = path.replace("{" + name + "}", quote(value, safe=""))
        if params is None:
            if operation.get("body_required"):
                raise ValueError("This operation requires request parameters.")
            snapshot: dict[str, Any] = {}
        elif isinstance(params, Mapping):
            snapshot = json.loads(serialize_params(params))
        else:
            raise ValueError("params must be a mapping of JSON field names to values.")
        if (
            snapshot.get("after") is not None
            and snapshot.get("before") is not None
            and operation["paginated"]
        ):
            raise ValueError("after and before cannot be used together.")
        headers = {
            "Authorization": "Bearer " + (options.api_key or self._api_key),
            "Accept": "application/json",
            "User-Agent": "raims-python/" + VERSION,
        }
        if options.idempotency_key is not None:
            headers["Idempotency-Key"] = options.idempotency_key
        body = None
        if operation["body"]:
            body = serialize_params(snapshot)
            if operation.get("maxBodyBytes") is not None and len(body) > operation["maxBodyBytes"]:
                raise ValueError("Request body exceeds the published size limit.")
            headers["Content-Type"] = "application/json"
        else:
            query: list[tuple[str, str]] = []
            for name, value in snapshot.items():
                if name not in operation["query"]:
                    raise ValueError(
                        "This operation received an unsupported query parameter or body."
                    )
                if value is None:
                    continue
                for item in value if isinstance(value, list) else [value]:
                    if type(item) not in (str, int, float, bool):
                        raise ValueError("Query values must be scalars or lists of scalars.")
                    query.append((name, str(item).lower() if isinstance(item, bool) else str(item)))
            if query:
                path += "?" + urlencode(query)
        retries = (
            options.max_network_retries
            if options.max_network_retries is not None
            else self._retries
        )
        return _Prepared(
            operation,
            dict(path_params),
            snapshot,
            options,
            self._base + path,
            headers,
            body,
            options.timeout if options.timeout is not None else self._timeout,
            retries if operation["method"] in ("GET", "HEAD") else 0,
        )

    def _http_request(self, prepared: _Prepared) -> httpx.Request:
        timeout = httpx.Timeout(
            prepared.timeout, connect=min(prepared.timeout, self._connect_timeout)
        )
        return httpx.Request(
            prepared.operation["method"],
            prepared.url,
            headers=prepared.headers,
            content=prepared.body,
            extensions={"timeout": timeout.as_dict()},
        )

    def _notify(
        self,
        prepared: _Prepared,
        attempt: int,
        start: float,
        response: LastResponse | None,
        delay: float | None,
    ) -> None:
        if self._observer is None or self._notifying.get():
            return
        token = self._notifying.set(True)
        try:
            self._observer(
                RequestDiagnostics(
                    prepared.operation["id"],
                    prepared.operation["method"],
                    prepared.operation["path"],
                    attempt + 1,
                    (time.perf_counter() - start) * 1000,
                    response.status_code if response else None,
                    response.request_id if response else None,
                    delay is not None,
                    delay * 1000 if delay is not None else None,
                )
            )
        except Exception:  # noqa: BLE001, S110
            pass  # Observer failures must not change the result of financial requests.
        finally:
            self._notifying.reset(token)

    def _interpret(self, prepared: _Prepared, response: LastResponse, *, asynchronous: bool) -> Any:
        status = response.status_code
        if 300 <= status < 400:
            raise errors.UnexpectedResponseError(
                "The API returned a redirect; redirects are not followed.", last_response=response
            )
        if not 200 <= status < 300:
            api_error = None
            try:
                data = parse_json(response.body)
                if isinstance(data, dict) and isinstance(data.get("error"), dict):
                    api_error = data["error"]
            except (ValueError, UnicodeError, RecursionError):
                pass
            category = {
                400: errors.InvalidRequestError,
                405: errors.InvalidRequestError,
                413: errors.InvalidRequestError,
                415: errors.InvalidRequestError,
                422: errors.InvalidRequestError,
                401: errors.AuthenticationError,
                403: errors.PermissionError,
                404: errors.NotFoundError,
                409: errors.ConflictError,
                429: errors.RateLimitError,
            }.get(status, errors.ApiError)
            raise category(
                f"The API request failed with HTTP {status}.",
                last_response=response,
                api_error=api_error,
            )
        responses = prepared.operation["responses"]
        if str(status) not in responses:
            raise errors.UnexpectedResponseError(
                "The API returned an undocumented success status.", last_response=response
            )
        schema = responses[str(status)]
        if schema is None:
            if response.body:
                raise errors.UnexpectedResponseError(
                    "The API returned a body for an empty response.", last_response=response
                )
            return None
        content_type = response.headers.get("content-type")
        if content_type and not re.match(
            r"application/(?:[a-z0-9.+-]+\+)?json(?:\s*;|$)", content_type, re.IGNORECASE
        ):
            raise errors.UnexpectedResponseError(
                "The API returned a non-JSON success response.", last_response=response
            )
        try:
            data = parse_json(response.body)
        except (ValueError, UnicodeError, RecursionError):
            raise errors.UnexpectedResponseError(
                "The API returned invalid JSON.", last_response=response
            ) from None
        validate_response(data, schema, response)
        resource = hydrate(data, schema, response)
        if prepared.operation["paginated"]:
            page_type = AsyncApiList if asynchronous else ApiList
            return page_type(
                resource,
                self,
                prepared.operation["id"],
                prepared.path_params,
                prepared.params,
                prepared.options,
            )
        return resource

    def _check_size(self, size: int, status: int, headers: Mapping[str, str]) -> None:
        if size > _MAX_RESPONSE_BYTES:
            raise errors.UnexpectedResponseError(
                "The API response exceeds the supported size.",
                last_response=LastResponse(status, headers, b""),
            )


@dataclass(frozen=True)
class Simulations:
    charges: services.SimulationChargesService
    refunds: services.SimulationRefundsService


@dataclass(frozen=True)
class AsyncSimulations:
    charges: services.AsyncSimulationChargesService
    refunds: services.AsyncSimulationRefundsService


class RaimsClient(_ClientBase):
    def __init__(
        self,
        api_key: str,
        *,
        api_base: str = "https://api.raims.com",
        timeout: float = 80.0,
        connect_timeout: float = 10.0,
        max_network_retries: int = 0,
        transport: httpx.BaseTransport | None = None,
        request_observer: RequestObserver | None = None,
    ) -> None:
        super().__init__(
            api_key,
            api_base=api_base,
            timeout=timeout,
            connect_timeout=connect_timeout,
            max_network_retries=max_network_retries,
            request_observer=request_observer,
        )
        self._http = httpx.Client(transport=transport, trust_env=False, follow_redirects=False)
        self.accounts = services.AccountsService(self)
        self.balances = services.BalancesService(self)
        self.customers = services.CustomersService(self)
        self.charges = services.ChargesService(self)
        self.payment_links = services.PaymentLinksService(self)
        self.refunds = services.RefundsService(self)
        self.disputes = services.DisputesService(self)
        self.statements = services.StatementsService(self)
        self.withdrawals = services.WithdrawalsService(self)
        self.withdrawal_destinations = services.WithdrawalDestinationsService(self)
        self.webhooks = services.WebhooksService(self)
        self.webhook_event_types = services.WebhookEventTypesService(self)
        self.simulations = Simulations(
            services.SimulationChargesService(self), services.SimulationRefundsService(self)
        )

    def _request(
        self,
        operation_id: str,
        *,
        path_params: dict[str, str],
        params: Mapping[str, Any] | None,
        options: RequestOptions | None,
    ) -> Any:
        if self._http.is_closed:
            raise RuntimeError("The API client is closed.")
        prepared = self._prepare(operation_id, path_params, params, options)
        for attempt in range(prepared.retries + 1):
            start = time.perf_counter()
            info = None
            try:
                response = self._http.send(
                    self._http_request(prepared), stream=True, follow_redirects=False
                )
                info = LastResponse(response.status_code, response.headers, b"")
                try:
                    chunks = bytearray()
                    for chunk in response.iter_bytes():
                        self._check_size(
                            len(chunks) + len(chunk), response.status_code, response.headers
                        )
                        chunks.extend(chunk)
                    info = LastResponse(response.status_code, response.headers, bytes(chunks))
                finally:
                    response.close()
            except httpx.DecodingError:
                self._notify(prepared, attempt, start, info, None)
                raise errors.UnexpectedResponseError(
                    "The API returned invalid compressed content.", last_response=info
                ) from None
            except httpx.TransportError:
                delay = _retry_delay(attempt, info) if attempt < prepared.retries else None
                self._notify(prepared, attempt, start, info, delay)
                if delay is None:
                    raise errors.ConnectionError(
                        "The API connection failed or timed out.", last_response=info
                    ) from None
                time.sleep(delay)
                continue
            except errors.UnexpectedResponseError as exc:
                self._notify(prepared, attempt, start, exc.last_response, None)
                raise
            delay = (
                _retry_delay(attempt, info)
                if attempt < prepared.retries and info.status_code in _RETRY_STATUSES
                else None
            )
            self._notify(prepared, attempt, start, info, delay)
            if delay is not None:
                time.sleep(delay)
                continue
            return self._interpret(prepared, info, asynchronous=False)
        raise AssertionError("Unreachable retry state.")

    def close(self) -> None:
        self._http.close()

    def __enter__(self: _SyncClientT) -> _SyncClientT:  # noqa: PYI019
        self._http.__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._http.__exit__(exc_type, exc_value, traceback)


class AsyncRaimsClient(_ClientBase):
    def __init__(
        self,
        api_key: str,
        *,
        api_base: str = "https://api.raims.com",
        timeout: float = 80.0,
        connect_timeout: float = 10.0,
        max_network_retries: int = 0,
        transport: httpx.AsyncBaseTransport | None = None,
        request_observer: RequestObserver | None = None,
    ) -> None:
        super().__init__(
            api_key,
            api_base=api_base,
            timeout=timeout,
            connect_timeout=connect_timeout,
            max_network_retries=max_network_retries,
            request_observer=request_observer,
        )
        self._http = httpx.AsyncClient(transport=transport, trust_env=False, follow_redirects=False)
        self.accounts = services.AsyncAccountsService(self)
        self.balances = services.AsyncBalancesService(self)
        self.customers = services.AsyncCustomersService(self)
        self.charges = services.AsyncChargesService(self)
        self.payment_links = services.AsyncPaymentLinksService(self)
        self.refunds = services.AsyncRefundsService(self)
        self.disputes = services.AsyncDisputesService(self)
        self.statements = services.AsyncStatementsService(self)
        self.withdrawals = services.AsyncWithdrawalsService(self)
        self.withdrawal_destinations = services.AsyncWithdrawalDestinationsService(self)
        self.webhooks = services.AsyncWebhooksService(self)
        self.webhook_event_types = services.AsyncWebhookEventTypesService(self)
        self.simulations = AsyncSimulations(
            services.AsyncSimulationChargesService(self),
            services.AsyncSimulationRefundsService(self),
        )

    async def _request(
        self,
        operation_id: str,
        *,
        path_params: dict[str, str],
        params: Mapping[str, Any] | None,
        options: RequestOptions | None,
    ) -> Any:
        if self._http.is_closed:
            raise RuntimeError("The API client is closed.")
        prepared = self._prepare(operation_id, path_params, params, options)
        for attempt in range(prepared.retries + 1):
            start = time.perf_counter()
            info = None
            try:
                response = await self._http.send(
                    self._http_request(prepared), stream=True, follow_redirects=False
                )
                info = LastResponse(response.status_code, response.headers, b"")
                try:
                    chunks = bytearray()
                    async for chunk in response.aiter_bytes():
                        self._check_size(
                            len(chunks) + len(chunk), response.status_code, response.headers
                        )
                        chunks.extend(chunk)
                    info = LastResponse(response.status_code, response.headers, bytes(chunks))
                finally:
                    await response.aclose()
            except httpx.DecodingError:
                self._notify(prepared, attempt, start, info, None)
                raise errors.UnexpectedResponseError(
                    "The API returned invalid compressed content.", last_response=info
                ) from None
            except httpx.TransportError:
                delay = _retry_delay(attempt, info) if attempt < prepared.retries else None
                self._notify(prepared, attempt, start, info, delay)
                if delay is None:
                    raise errors.ConnectionError(
                        "The API connection failed or timed out.", last_response=info
                    ) from None
                await asyncio.sleep(delay)
                continue
            except errors.UnexpectedResponseError as exc:
                self._notify(prepared, attempt, start, exc.last_response, None)
                raise
            delay = (
                _retry_delay(attempt, info)
                if attempt < prepared.retries and info.status_code in _RETRY_STATUSES
                else None
            )
            self._notify(prepared, attempt, start, info, delay)
            if delay is not None:
                await asyncio.sleep(delay)
                continue
            return self._interpret(prepared, info, asynchronous=True)
        raise AssertionError("Unreachable retry state.")

    async def close(self) -> None:
        await self._http.aclose()

    async def aclose(self) -> None:
        await self.close()

    async def __aenter__(self: _AsyncClientT) -> _AsyncClientT:  # noqa: PYI019
        await self._http.__aenter__()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self._http.__aexit__(exc_type, exc_value, traceback)
