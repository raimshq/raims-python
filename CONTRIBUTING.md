# Contributing

Read `AGENTS.md`, README, and the [maintenance guide](docs/maintenance.md).
Preserve JSON names, public signatures, numeric precision, credential isolation,
and the distinction between an accepted result and a completed operation.

## Complete validation

From the SDK root, using Python 3.10 or later, prepare the tools on the first
run and then run the same gate without the preparation option:

```text
python scripts/check.py --prepare-tools
python scripts/check.py
```

The command uses the canonical validator from the sibling Developer Toolkit
checkout. It recreates suites and consumers in `.tmp`, checks generation,
compatibility, lint, types, and regressions, builds wheel and sdist, and validates
a clean wheel installation. The pip-audit scan checks the runtime dependencies
actually installed, including transitive dependencies. Tools have pinned
versions and hashes. The cache is separated by Python minor version.

The wheel is installed in a new virtual environment that does not inherit the
tool packages. First, the gate installs only the wheel and its declared
dependencies and exercises operations and webhooks. It then adds only the
suite tools, pinned by version and hash, and reruns the tests in that
environment. A fixture package without the HTTPX dependency must be rejected
before validation can pass.

The suite uses configuration and plugins controlled by the gate and discards
`PYTEST_*` variables inherited from the workstation. The report must confirm
setup, execution, and teardown for every test, without partial selection,
skip, or xfail. Exit code zero alone does not approve a run. Source and wheel
tests must execute the same set of cases.

The gate requires interpreter optimization level zero and enabled assertions.
Run without `-O` or `-OO`. If `PYTHONOPTIMIZE` enables optimization, remove that
setting from the process before validation. Controlled subprocesses use
`PYTHONOPTIMIZE=0`, and materialized scripts reject optimized execution before
their checks. The report records this state. This requirement applies to
engineering validation.

Without the Toolkit or prepared tools, execution fails and identifies the
missing dependency. A partial check does not approve the SDK. To choose a new
results directory, use `--output` with a path inside
`C:\server\raims\.tmp\raims-python-sdk`. Sources must remain stable until the
run finishes. Reports and artifacts remain in that directory.

## Generation and compatibility

From the SDK root, using Python 3.10 or later:

```text
python scripts/generate.py --check
python scripts/check-compatibility.py
python -m ruff check --config pyproject.toml --no-cache .
python -m mypy --cache-dir ../.tmp/raims-python-sdk/mypy-cache src/raims
```

The generator uses only the pinned contract and does not access the network.
After updating the source, run `python scripts/generate.py` and review the
generated files. Do not manually edit generated services, models, inputs,
constants, or metadata.

`contracts/python-api.json` is the independent baseline for the library's public
symbols. OpenAPI generation does not change it. The check allows new symbols
and rejects changes to definitions already recorded. Signatures, annotations,
and values require review, even when a change is intended to be compatible.
The baseline also records inherited `TypedDict` field requirements, dataclass
options, method binding, property accessors, and base classes. Symbols are
resolved by module and imports, preserving classes that share a name.
To deliberately accept a new baseline, run
`python scripts/check-compatibility.py --write` and review the diff.

Virtual environments, tools, tests, simulators, and reports must remain
exclusively in `C:\server\raims\.tmp\raims-python-sdk`, outside the repository.
Keep the validation suite there and run it with the SDK source on PYTHONPATH.
During validation, set `PYTHONDONTWRITEBYTECODE=1` or point `PYTHONPYCACHEPREFIX`
to the same temporary directory. Do not use the real API: even Sandbox calls
can trigger external communications and integrations.

Validation must cover every operation and success status in the contract,
synchronous and asynchronous clients, consumer-visible types, precision,
null and omission, errors, per-request options, empty and cyclic pagination,
idempotency, read retries, the absence of write retries, webhooks, TLS,
redirects, timeouts, response limits, and resource cleanup. Test the minimum
Python version and the latest supported version. Use fake transport and local
receivers with cleanup in `finally`.

## Distribution

```text
python -m build --no-isolation --outdir ../.tmp/raims-python-sdk/dist
python -m twine check ../.tmp/raims-python-sdk/dist/*
```

Inspect the wheel and sdist. Install the wheel in a clean environment outside
the checkout and validate imports, types, transport, and the embedded contract.
The wheel must contain only the package, distribution metadata, and license.
The sdist also includes the public sources needed for maintenance and
generation. Neither may contain tests, caches, environments, evidence, or
private configuration. Do not write build artifacts to the repository root.

## Review

Review every modified and new file, `git diff --check`, `git diff`, and
`git diff --cached`. Leave the work uncommitted and unstaged. Do not add
credentials, temporary URLs, customer data, or references to other brands as
inspiration. Preserve mandatory attribution and licenses. Human-facing text
follows the workspace's humanizer skill.

Publishing on PyPI, creating a remote, pushing, releasing, and publishing
documentation require separate authorization. Successful local validation
does not publish the SDK.

The `templates/ci/validate.yml` template prepares `Validate Python SDK` for
`raimshq/raims-python` on authorized CodeBuild runners, using Python 3.10 and
3.14. When activated, it validates pushes from the repository and manual runs
without publishing packages. The first GitHub publication has no executable
workflow. Activation depends on the reviewed checkouts being available,
GitHub App access, the runner allowlist, and `RAIMS_PYTHON_TOOLKIT_REF` holding
the immutable Toolkit SHA containing the gate. The local command applies none
of those remote settings.

Before a delivery commit, run the workspace preflight's Commit stage with the
`Raims-Python` profile. Run Deploy before a push, tag, or release. The GitHub
source profile requires complete SAST, dependency auditing, the correct public
destination, and no executable workflows.
