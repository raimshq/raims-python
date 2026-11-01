# TODO

- [ ] Activate the CI prepared in `templates/ci/validate.yml` after the reviewed
  checkouts have been published with authorization. Verify the repository,
  GitHub App access, the existing CodeBuild runner allowlist, and
  `RAIMS_PYTHON_TOOLKIT_REF` with the full SHA of the Toolkit containing the
  Python gate. Confirm the Python 3.10 and 3.14 jobs for the same commit before
  making the package available. The first GitHub delivery publishes sources
  without an executable workflow. PyPI and remote runner configuration remain
  separate steps.

- [ ] Python SDK availability: after confirming its name, version, and
  distribution on PyPI, update README and create the BR/EN guide in
  `raims-developer-docs/content/docs/integracoes/sdk-python`. Explain its purpose,
  when to suggest Python, access from the integrations section, installation,
  Python 3.10+, server use, keys and permissions, the credential's environment,
  synchronous/asynchronous clients, pagination, idempotency, the absence of
  write retries, pending responses, documents, and webhooks. Regenerate the
  public catalog consumed by `Raims-Chat` and validate AI retrieval and guidance
  in Portuguese and English. Do not advertise installation from PyPI until
  distribution there is confirmed. GitHub installation is documented in README.
  The current library does not require a new context contract or query tools;
  reassess that conclusion when preparing the guides. Complete this item only
  after validating sources, catalogs, and answers.
- [ ] Changelog for the first Python SDK distribution: publish a note in
  `raims-developer-docs/content/docs/changelog/post` with the actual availability
  date, requirements, installation, and a link to the updated guide. Include
  typing, pagination, error handling, idempotency, and the retry limits actually
  available. A local implementation does not authorize a public announcement.
