# Errors, idempotency, and retries

## Handle failures

```python
from raims import ApiError, ConnectionError, RateLimitError

try:
    customer = raims.customers.retrieve(customer_id)
except RateLimitError as error:
    retry_after = error.retry_after
    request_id = error.request_id
except ConnectionError:
    handle_uncertain_response()
except ApiError as error:
    status = error.status_code
    code = error.code
```

The handlers represent your application's error handling. Make decisions using
the status and `error.code`; the API's diagnostic messages may change. Complete
details are available in `api_error` and the explicit `last_response` object.
They may contain sensitive data. The `str` and `repr` of errors raised by the
SDK do not include the text or body received.

| Exception | Condition |
| --- | --- |
| `InvalidRequestError` | HTTP 400, 405, 413, 415, or 422 |
| `AuthenticationError` | HTTP 401 |
| `PermissionError` | HTTP 403 |
| `NotFoundError` | HTTP 404 |
| `ConflictError` | HTTP 409 |
| `RateLimitError` | HTTP 429 |
| `ApiError` | Other HTTP failures, including 5xx |
| `ConnectionError` | Timeout or HTTPX transport failure |
| `UnexpectedResponseError` | Redirect, undocumented success, invalid JSON, or invalid structure |
| `SignatureVerificationError` | Webhook authentication failure |

All inherit from `RaimsError`. Invalid arguments use Python's `ValueError` or
`TypeError`. An edge service may return HTML without an error envelope; in that
case, `api_error` and `code` are `None`. The HTTP response remains accessible.

## Idempotency

Supply `RequestOptions(idempotency_key=...)` only for endpoints that declare
support. The key accepts 1 to 255 visible ASCII characters, without spaces.
The SDK sends it exactly as received and does not generate it automatically.
A key supplied to an unsupported operation is rejected before any HTTP request.

Generate and persist the operation's intent identity before executing it.
After losing a response, preserve the key and parameters, including dates
and amounts. Retrieve the resource and consult the
[API policy](https://docs.raims.com/en/api/idempotencia) before deciding whether
to retry. A connection failure does not prove that a write was not processed.
`IDEMPOTENCY_RESULT_UNKNOWN` requires reconciliation; do not replace the key
to repeat the financial intent.

## Read retries

The default is zero. `max_network_retries` accepts up to five additional
attempts for GET/HEAD, on connection failures or HTTP 408, 429, 500, 502, 503,
and 504. The interval uses exponential backoff with jitter between 250 ms and
2 s. `Retry-After` can extend the wait to 30 s; above that, the error is returned
so the application can reschedule the read. The header accepts seconds or an
HTTP date.

POST, PATCH, PUT, and DELETE are never retried automatically, even with
idempotency and retries configured. `202` also does not start another attempt
or automatically retrieve the result.
