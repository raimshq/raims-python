# Receive webhooks

Authenticate the original body before interpreting the event:

```python
from raims import SignatureVerificationError, Webhook

try:
    event = Webhook.construct_event(raw_body, received_headers, webhook_secret)
except SignatureVerificationError:
    reject_request()
else:
    persist_event_atomically(event)
```

`raw_body` contains the bytes received by the server. `received_headers` is a
map with `webhook-id`, `webhook-timestamp`, and `webhook-signature`.
`reject_request` and `persist_event_atomically` belong to your application.
Do not reserialize JSON: whitespace, Unicode, and line breaks are part of
the signature.

Use the `secret_key` received when creating or rotating the webhook, stored
in a vault. It differs from the API Bearer key and is not returned by later
retrieval requests.

`construct_event` authenticates headers, timestamp, and signature before
decoding a JSON object. `verify_signature` authenticates without interpreting
the body. Neither validates the event's business rules.

The protocol uses HMAC-SHA256 with Raims' Base62 secret. Header names are
case-insensitive. Lists containing one value are accepted; duplicate or
ambiguous headers are rejected. During rotation, the header may contain
multiple `v1=` signatures separated by commas. A signature matching the
configured secret authenticates the delivery.

The default tolerance is 300 seconds in both the past and the future. Keep
the clock synchronized. `tolerance=0` requires the same second; it does not
disable the protection. `now` lets you inject an integer timestamp for local
verification.

A signature does not prevent duplicate valid deliveries. Before acknowledging
a request over HTTP, check the type, environment, and resource, and persist
the work durably, atomically, and with deduplication. The body `id` identifies
the event; `webhook-id` identifies the delivery. If persistence fails, return an
HTTP failure. Process business effects idempotently. The event's `created_at`
uses ISO 8601 and is not the attempt header's Unix timestamp.

Consult the [receiving guide](https://docs.raims.com/en/integracoes/webhooks/receber-eventos)
for events and delivery conditions.
