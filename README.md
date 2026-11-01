# Raims Python

Official Python SDK for the Raims public API.

Use the SDK in server applications, with synchronous and asynchronous clients,
typed parameters, read-only responses, cursor pagination, and webhook signature
verification.

## Install from GitHub

Requires Python 3.10 or later. Source code and release notes are available on
[GitHub](https://github.com/raimshq/raims-python/releases). The package is not yet
available on PyPI.

With Git installed, run this command in your application environment:

```text
python -m pip install "git+https://github.com/raimshq/raims-python.git"
```

To update this installation, run the command again with a forced upgrade and
test your integration:

```text
python -m pip install --upgrade --force-reinstall "git+https://github.com/raimshq/raims-python.git"
```

You can also download the source code from the
[current release](https://github.com/raimshq/raims-python/releases/latest),
extract the archive, and install its directory in your application environment:

```text
python -m pip install /path/to/Raims-Python
```

Import the package as `raims`. It uses HTTPX for HTTP transport.
Future updates are not applied automatically.

## First request

```python
import os

from raims import RaimsClient

with RaimsClient(os.environ["RAIMS_API_KEY"]) as raims:
    page = raims.customers.list({"page_size": 20})
    for customer in page:
        process_customer(customer.id)
```

`process_customer` represents your application's processing. The base URL is
`https://api.raims.com` for both Sandbox and Production. The key determines the
company, environment, and permissions. Keep it on the server and out of version
control.

## Create a charge

`customer_id`, `due_date`, and `order_idempotency_key` are values your application
has already defined and persisted for the order. The due date uses Unix seconds
in UTC, and the amount uses integer cents: `15000` represents BRL 150.00.

```python
from raims import RequestOptions

with RaimsClient(os.environ["RAIMS_API_KEY"]) as raims:
    charge = raims.charges.create(
        {
            "customer_id": customer_id,
            "amount_cents": 15000,
            "due_date": due_date,
            "title": "Order 1234",
        },
        options=RequestOptions(idempotency_key=order_idempotency_key),
    )
    response = charge.last_response
    assert response is not None
    request_id = response.request_id
```

The SDK does not generate idempotency keys or retry writes automatically.
If you lose a response, keep the same key and parameters and follow the
endpoint's rules for retrieving or retrying the operation. A `202` response
means processing is pending; retrieve the resource to follow its outcome.

## Asynchronous use

```python
from raims import AsyncRaimsClient

async def load_customers(api_key: str) -> None:
    async with AsyncRaimsClient(api_key) as raims:
        page = await raims.customers.list({"page_size": 50})
        async for customer in page.auto_paging_iter():
            await process_customer_async(customer.id)
```

`process_customer_async` represents your application's asynchronous processing.
Normal iteration over a page accesses only the items already received.
`auto_paging_iter()` retrieves subsequent pages as you consume them.

## Services

| Property | Resources |
| --- | --- |
| `accounts` | Account context, number, fees, and checkout |
| `balances` | Balance and forecast |
| `customers` | Customer creation, retrieval, and deletion |
| `charges` | Charges, payment, documents, and refunds for a charge |
| `payment_links` | Payment links and email delivery requests |
| `refunds` | Refunds and receipts |
| `disputes` | Disputes |
| `statements` | Account statements |
| `withdrawals` | Withdrawals, limits, summary, and automatic settings |
| `withdrawal_destinations` | Withdrawal destinations |
| `webhooks` | Registration, health, pause, test, and secret rotation |
| `webhook_event_types` | Available event types |
| `simulations.charges` | Charge simulations with a Sandbox key |
| `simulations.refunds` | Refund simulations with a Sandbox key |

Services expose `create`, `retrieve`, `update`, `delete`, and `list` according
to the operations available. The [reference](docs/reference.md) describes each
method.

## Documentation

- [Configuration, responses, and documents](docs/usage.md)
- [Pagination](docs/pagination.md)
- [Errors, idempotency, and retries](docs/errors-and-retries.md)
- [Receiving webhooks](docs/webhooks.md)
- [Maintenance and contract](docs/maintenance.md)
- [Contributing](CONTRIBUTING.md) and [security](SECURITY.md)
- [Public API](https://docs.raims.com/en/api)

Distributed under the [MIT license](LICENSE).
