# Contract and maintenance

## Source and organization

The SDK consumes only the public OpenAPI published in
[raimshq/openapi](https://github.com/raimshq/openapi). `contracts/source.json`
pins the immutable revision, URL, SHA-256, HTTP version, deployment identity,
and operation count. The initial snapshot covers 68 operations. Do not use
the private Dashboard contract or endpoints whose publication is unconfirmed.

| Source | Responsibility |
| --- | --- |
| `contracts/openapi.json` | Immutable public snapshot |
| `contracts/service-map.json` | Python service and method names |
| `scripts/generate.py` | Offline generation and output verification |
| `docs/reference.en.json` | English reference translations keyed by exact public source text |
| `scripts/check.py` | Entry point for canonical engineering validation |
| `scripts/check-compatibility.py` | Independent public symbol verification |
| `contracts/python-api.json` | Reviewable library compatibility baseline |
| `src/raims/_generated/contract.json` | Generated HTTP metadata and schemas |
| `src/raims/services.py` | Generated synchronous and asynchronous methods |
| `src/raims/types.py` | Generated TypedDict parameters |
| `src/raims/models.py` | Generated response models |
| `src/raims/enum_values.py` | Generated public enum constants |
| `src/raims/_client.py` | Configuration, transport, retries, and interpretation |
| `src/raims/_validation.py` | Exact JSON, structural validation, and hydration |
| `src/raims/_resource.py` | Read-only responses |
| `src/raims/_pagination.py` | Page navigation and iteration |
| `src/raims/_webhook.py` | Delivery authentication |
| `src/raims/_version.py` | Single version source for the package and client |

Generation checks the origin, revision, and hash, requires API-key authentication,
and covers every operation exactly once. Unrepresentable schemas, external
references, and unpublished operations stop generation. `--check` writes no
files and rejects missing, different, or obsolete outputs.

Reference descriptions are translated through `docs/reference.en.json` without
changing the pinned OpenAPI or generated runtime metadata. Each entry uses the
exact public source text as its key. Update the English entry when that text
changes; a missing translation stops generation before any output is written.

## Update the contract

1. Choose an approved public revision and check its publication manifest.
2. Download the snapshot from its immutable URL and verify the bytes' SHA-256.
3. Update `contracts/source.json` and the method map when needed.
4. Run the generator, review changes to the contract, types, and reference,
   and validate the clients and distribution as described in `CONTRIBUTING.md`.
5. Assess compatibility of signatures, defaults, authentication, environment,
   pagination, errors, idempotency, dates, amounts, and pending results.

The HTTP `/v1` contract and package version have independent lifecycles.
Updating the generator does not authorize incompatible changes or replacing
the snapshot with local operations that have not been published. The generator
rejects compositions that hydration cannot represent faithfully. To accept a
new schema shape, implement and validate both sides in the same delivery.

## Library compatibility

`contracts/python-api.json` records exports, services, signatures, fields,
read-only properties, types, and constants. It is independent of the HTTP
snapshot and is not rewritten by the generator.

Format 2 also records class bases and options, inherited `TypedDict` field
requirements, dataclass options, and the distinction between instance, static,
and class methods. Getters, setters, and deleters are part of property
definitions. Imports and aliases are resolved by module without conflating
classes that share a name.

Run `python scripts/check-compatibility.py` to check the implementation.
New symbols are allowed; changes to existing definitions require explicit
review. Comparison of annotations and signatures is conservative. After
assessing the impact, use `--write` to deliberately update the baseline and
review its diff. Updating the baseline does not remove the effect of an
incompatible change on integrators.

Edit the version only in `src/raims/_version.py`. The build and client User-Agent
use that source. The baseline protects the version export's existence while
allowing its value to change between releases.

## Validation and CI

`python scripts/check.py` uses the workspace adapter
`Developer-Toolkit/scripts/release-preflight/python_sdk.py`. Definitions maintained
in the Toolkit materialize executable files only in `.tmp`; validation does not
depend on tests left by another run. The tool lock pins versions and hashes,
and the report records the validated source, tools, and package results. Use
`--prepare-tools` only to prepare or restore the isolated cache.

The distribution is installed in a new virtual environment, without packages
from the engineering environment or checkout access through `PYTHONPATH`.
Pip resolves the wheel's declared dependencies. Before installing test tools,
a check exercises the synchronous and asynchronous clients' success statuses
and webhook signing using only that environment. The gate then installs the
minimum suite tools from the lock and reruns the tests on the installed package.

Regressions include temporary copies with incompatible public type changes
and a package without the HTTPX dependency. Approval requires the corresponding
checker to detect those changes. The reviewed baseline and SDK sources remain
unchanged during these checks.

Both pytest runs use their own configuration, explicit plugins, and an
environment without inherited `PYTEST_*` options. Every collected test must
complete setup, execution, and teardown successfully. Collection without
execution, deselection, skip, and xfail prevent approval. The report records
executed cases, and validation requires the same coverage in sources and wheel.
Dedicated regressions verify this control with external configuration and
options that would filter tests or collect them without execution.

The launcher, adapter, and materialized scripts require enabled assertions
and optimization level zero. Runs with `-O`, `-OO`, or optimization enabled
through `PYTHONOPTIMIZE` are rejected. The subprocess environment is normalized
to `PYTHONOPTIMIZE=0`, and the report records the interpreter mode. A regression
using a deliberately broken checker proves that optimization cannot turn a
failed canary into an approved result.

The `templates/ci/validate.yml` template prepares the same gate for Python 3.10
and 3.14 on Linux jobs in the existing CodeBuild setup. The
`RAIMS_PYTHON_TOOLKIT_REF` variable must identify the reviewed Toolkit commit by
its full SHA. Validation rejects a missing or mutable reference before requesting
access to the private checkout. Events do not include fork pull-request code.

Remote activation is pending. It requires the repository, published checkouts,
access, variable, and allowlist to be verified through the authorized engineering
process. The template is not an executable workflow in this first source
distribution. It does not change infrastructure or publish to PyPI.

## Initial implementation impact

| Behavior | Source and consumers | Verification |
| --- | --- | --- |
| Python integration | SDK consumes the pinned public contract | Every operation, types, and installation |
| Transport and pagination | Synchronous and asynchronous clients | Isolated HTTP, options, retries, and cursors |
| Webhook reception | Integrator's local helper | Published protocol and original bytes |
| API, CLI, and existing SDKs | No contract or implementation change | Snapshot consumed without changing producers |
| Persistence and migrations | No change | No database or provider writes |
| Support and changelog | SDK guides and TODO items | Confirm public availability before announcing it |

## Support knowledge

The BR/EN integrations guide in `raims-developer-docs` will be responsible for
installation and usage guidance. It must explain purpose, server use,
requirements, confirmed installation, keys, permissions, environment,
pagination, idempotency, pending responses, documents, and webhooks.
Support consumes that guide through the existing catalog, as described in
`Raims-Chat/docs/knowledge-sources.md` in the workspace.

Source code and GitHub installation instructions are in this repository.
PyPI distribution remains pending. Do not publish an installation command
for that registry until availability is confirmed. `TODO.md` records the public
guide, catalog regeneration, AI response validation, and changelog steps.
The library needs no new context fields, permissions, or query tools;
reassess that conclusion if its public scope changes.

## Publication

The first delivery is limited to GitHub, in `raimshq/raims-python`, with matching
library version, tag, and release. The preflight's `public-sdk-source` profile
validates Commit and Deploy, including SAST, dependency auditing, source
integrity, and the remote destination. It does not require runner configuration
when the publication has no executable workflows.

PyPI publication is not configured yet. Before making a version available,
confirm the package name, ownership, version, authorized commit, validation,
and wheel/sdist contents. Configure distribution through the authorized
engineering process without storing tokens in sources or logs. Publication,
creating a remote repository, pushes, and releases require explicit requests.

After publishing, check the version at the destination and perform a clean
installation. Update README and the guides with actual availability. Publish
the changelog note with the effective date through the authorized documentation
process.
