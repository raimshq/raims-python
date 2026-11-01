# Security

Report vulnerabilities privately to `security@raims.com`. Do not open a public
discussion containing credentials, personal data, real request or response
bodies, webhook secrets, or temporary URLs. Describe the behavior, affected
version, and a minimal reproduction using fictitious data.

The SDK is intended for the integrator's server. Store keys and secrets in a
vault, use the permissions your integration needs, and keep Python and its
dependencies updated. Check company, environment, authorization, and
idempotency in your application.

Webhook verification authenticates the delivery. The integrator remains
responsible for validating the event, deduplicating it, and persisting the work
before acknowledging it over HTTP.
