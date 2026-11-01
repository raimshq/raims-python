# Configuration and responses

## Clients

```python
from raims import RaimsClient, RequestOptions

with RaimsClient(
    api_key,
    timeout=80.0,
    connect_timeout=10.0,
    max_network_retries=0,
) as raims:
    customer = raims.customers.retrieve(
        customer_id,
        options=RequestOptions(timeout=60.0),
    )
```

Each instance keeps its own credential and reuses connections. Use `with` to
close the synchronous client or `async with` for the asynchronous client.
You can also call `close()` explicitly; use `await` on the asynchronous client.
The context managers also enter and exit a custom transport's context,
preserving an application exception when one occurs. `close()` closes the
transport supplied to the client. Use one asynchronous instance per event loop
lifecycle.

| Option | Default | Effect |
| --- | --- | --- |
| `api_key` | Required | Bearer credential |
| `api_base` | `https://api.raims.com` | HTTPS origin without a path, query, or credentials |
| `timeout` | `80.0` | Network timeout for each stage of an attempt, in seconds |
| `connect_timeout` | `10.0` | Connection timeout, capped by `timeout` |
| `max_network_retries` | `0` | Zero to five additional retries for reads only |
| `transport` | HTTPX transport | Synchronous `BaseTransport` or asynchronous `AsyncBaseTransport` |
| `request_observer` | Disabled | Synchronous callback with metadata for each attempt |

Timeouts must be greater than zero and no more than 300 seconds. The HTTPX
timeout limits connection establishment, waiting for a pool connection,
sending, and read inactivity. It is not a total deadline for receiving a
streamed response. Retries add the timeouts and waiting intervals of each attempt.

HTTP is accepted only on loopback for development. The origin receives the
credential: configure only destinations controlled by your organization.
The default transport verifies TLS, does not follow redirects, and does not
use proxies implicitly defined by process environment variables. For specific
network settings, supply an HTTPX transport configured by your application.

Per-request options are `api_key`, `idempotency_key`, `timeout`, and
`max_network_retries`, supplied through `RequestOptions`. A request-specific key
does not change the client's credential for later calls. Arbitrary headers,
environment selection, and OAuth are not part of this SDK version.
A custom transport must preserve TLS verification and must not retry writes.
HTTPX transport exceptions become `ConnectionError`; application exceptions
keep their original type.

## Responses and types

```python
charge = raims.charges.retrieve(charge_id)
amount = charge.amount_cents
same_amount = charge["amount_cents"]

data = charge.to_dict()
response = charge.last_response
assert response is not None
status = response.status_code
request_id = response.request_id
```

Models in `raims.models` provide annotated properties for your editor.
Inputs in `raims.types` are `TypedDict` definitions; calls also accept ordinary
dictionaries. Named public enum values are in `raims.enum_values`. They are
generated from the contract and have types compatible with operation literal
parameters.

Resources and nested objects are read-only; received lists become tuples.
`to_dict()` returns a copy containing dictionaries and lists. Future fields
and new enum values are preserved. Missing optional fields remain absent:
use `"field" in resource` or `resource.get("field")` when needed.
Static analysis checks known attributes and rejects assignments to model
properties. To consume a new field not yet described by the installed version,
use mapping access and validate its type in your application. Pagination
metadata also has types generated from the contract.

Integers are read without rounding, including integral JSON representations
such as `1.0` and `1e0`. Fractions are preserved as `decimal.Decimal` and rejected
in integer fields. The SDK does not convert cents to currency units or change
dates, states, or business rules.

The SDK checks required fields, types, and nullability before constructing a
model. An incompatible structure raises `UnexpectedResponseError`. Response
bodies are limited to 16 MiB. `202` does not start automatic polling; a `204`
response without a body returns `None`.

Excessively nested responses are also rejected with `UnexpectedResponseError`,
including when the nesting is in a new field not yet described by the models.

`last_response` contains the status, headers, original bytes decoded by the
transport, Request-Id, `idempotency_replayed`, and `retry_after`. Request-Id takes
precedence over the X-Request-Id alias. Nested objects do not represent another
request and have no response metadata of their own.

Default debug representations hide the data. `to_dict()`, `last_response.body`,
headers, and explicitly accessed fields may contain personal data, secrets, or
temporary URLs. Control access to those values and how your application logs them.

## Omission and null

```python
raims.charges.update(charge_id, {"title": "Updated order"})
raims.charges.update(charge_id, {"description": None})
raims.customers.update(customer_id, {"metadata": {}})
```

Omitting a field and sending `None` produce different requests. The SDK preserves
`None`, `False`, zero, empty text, and empty maps in JSON. Their meaning depends
on the endpoint: for charges, `description=None` clears the description; an
empty metadata map does not mean clear everything. To remove payment-link
redirect URLs, use the corresponding `clear_*` fields defined in the contract.

## Diagnostics

`request_observer` receives `RequestDiagnostics` with the operation, method,
parameterized path, attempt number, duration, status, Request-Id, and retry
decision. The path contains neither resource IDs nor a query. Credentials,
bodies, and parameters are not sent to the callback. The SDK does not emit its
own telemetry. Observer exceptions are isolated; a call made by the observer
does not recursively notify the same observer.

## Documents and images

`charges.retrieve_receipt`, `charges.retrieve_boleto`, and
`refunds.retrieve_receipt` return `FinancialDocument`, with `url` and
`expires_at`. Download the temporary URL in a separate GET, without Authorization,
cookies, or an API key, and without changing its parameters. Do not log the URL.
If it expires, retrieve it again through the authenticated endpoint.

`accounts.create_checkout_logo_upload` and
`accounts.create_checkout_favicon_upload` prepare the upload. PUT the bytes to
`upload_url` separately, with the exact Content-Type and Content-Length, without
a Bearer credential, cookies, or redirects. Then apply the ID through
`accounts.update_checkout_settings`. The SDK does not upload the file or
download external URLs through its authenticated transport.
