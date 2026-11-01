# Raims Python SDK

Read README, CONTRIBUTING, and docs/maintenance.md before changing the SDK.

- Repository descriptions and Markdown documentation must be in English.
  Preserve public identifiers, commands, URLs, and contractual meaning.
- Keep internal TODO lists, backlogs, and roadmaps out of this public repository
  and its packages. Track operational work in the private workspace backlog
  maintained outside Git. Do not publish its contents, location, or links.
- Python 3.10 or later; package `raims`, clients `RaimsClient` and
  `AsyncRaimsClient`, with snake_case services and methods.
- Consume only the public contract pinned in contracts, with its revision and
  SHA-256 verified. Do not import private contracts or host implementation code.
- scripts/generate.py generates services, models, inputs, constants, HTTP
  metadata, and docs/reference.md. Do not edit those outputs manually.
- Keep English reference wording in docs/reference.en.json, keyed by the exact
  public source text. Generation must reject missing translations; do not edit
  the pinned OpenAPI or omit descriptions to change the documentation language.
- Preserve JSON names, integer cents, Unix timestamps, omission and null,
  future fields, and pending results. Do not generate idempotency keys or retry
  writes automatically. Configurable retries apply only to reads.
- The API key determines the company and environment. Do not offer environment
  selection, OAuth, or arbitrary headers. The transport does not follow
  redirects, download external URLs, or upload files. Keep TLS verification on.
- Diagnostics contain only metadata, without resource IDs, query parameters,
  credentials, or payloads. Default object representations do not expose data.
- Tests, simulators, tools, virtual environments, builds, and evidence belong
  exclusively in C:\server\raims\.tmp\raims-python-sdk.
  Never version them or include them in a distribution.
- Check offline generation, types, the complete contract, synchronous and
  asynchronous transport, webhooks, and wheel/sdist before finishing. Use
  isolated dependencies; do not call the real API during validation.
- The first distribution publishes source code and a release on GitHub. CI
  remains in `templates/ci/validate.yml`, without an executable workflow at
  this stage.
- Before committing or publishing, run the Commit and Deploy preflight stages
  with the Raims-Python profile. Preserve SAST and runtime dependency auditing.
- Leave changes uncommitted and unstaged. Creating a remote, pushing, releasing,
  publishing on PyPI, and publishing documentation require their own authorization.
- Describe Raims features directly and preserve mandatory licenses and
  attribution for incorporated code. Apply the humanizer skill to prose.
