# Contributing to immobilier-notaires-client

Thank you for taking the time to contribute. This document explains how to set
up a development environment, run the test suite, record new API fixtures, and
submit changes.

---

## Table of contents

1. [Prerequisites](#prerequisites)
2. [Development setup](#development-setup)
3. [Running tests](#running-tests)
4. [Code quality](#code-quality)
5. [Recording / refreshing fixtures](#recording--refreshing-fixtures)
6. [Adding a new property type or field](#adding-a-new-property-type-or-field)
7. [Submitting a pull request](#submitting-a-pull-request)
8. [Good first issues](#good-first-issues)

---

## Prerequisites

- Python 3.11 or 3.12
- `git`

---

## Development setup

```bash
git clone https://github.com/Zhorba/immobilier-notaires-client.git
cd immobilier-notaires-client

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -e ".[dev]"
```

The `[dev]` extra installs pytest, pytest-httpx, ruff, mypy, and click.

---

## Running tests

The full suite runs **offline** against committed fixtures — no API key, no
network required.

```bash
pytest                              # run everything
pytest -v                           # verbose
pytest tests/test_models.py -v      # single file
pytest -m live                      # live network smoke-tests (opt-in, needs internet)
```

CI runs `pytest` (no `-m live` flag) so network tests are never required to
pass in a PR.

Expected output on a clean install: **52 tests, 0 failures**.

---

## Code quality

```bash
ruff check src tests        # lint
ruff format src tests       # auto-format
mypy src                    # type-check
```

All three must be clean before a PR is merged. CI enforces this automatically.

To run them all at once:

```bash
ruff check src tests && ruff format --check src tests && mypy src
```

Optional: install pre-commit hooks to run these automatically before every
`git commit`:

```bash
pip install pre-commit
pre-commit install
```

---

## Recording / refreshing fixtures

Fixtures live in `tests/fixtures/` and are **committed to the repo** so the
test suite never needs a network connection. They should be refreshed when:

- The API returns a new required field.
- A `test_contract.py` assertion starts failing against a live response.
- You are adding a new property type and need a matching fixture.

### Steps

1. **Search** for a listing of the target type to get an `annonceId`:

   ```bash
   notaires search --dept 56 --type MAI --per-page 1 --format json
   # note the "annonce_id" value in the output
   ```

2. **Fetch and redact** the three payloads. The helper script does this for you:

   ```bash
   python scripts/record_fixtures.py --annonce-id <ID> --dept 56
   ```

   The script fetches real responses, strips personal data (phone, email,
   negotiator name, exact address), and writes the three JSON files to
   `tests/fixtures/`.

3. **Run the tests** to confirm the new fixtures pass all contract assertions:

   ```bash
   pytest tests/test_contract.py -v
   ```

4. **Commit** the updated fixtures alongside any model/enum changes.

> **Privacy note:** Before committing, confirm that the fixture files contain
> no personal data. Negotiator phone numbers, emails, and exact street
> addresses must be redacted (replaced with `"REDACTED"` or `null`). See
> [`docs/ethics.md`](docs/ethics.md) for the full policy.

---

## Adding a new property type or field

### New property type (e.g. `PRK` — parking)

1. Add the member to `PropertyType` in `src/notaires_immo/enums.py`.
2. Add the `"PRK": "parking"` entry to `_BIEN_TYPE_TO_KEY` in
   `src/notaires_immo/models.py`.
3. Record a fixture for this type (see above) and save it as
   `tests/fixtures/detail-prk-response.json`.
4. Add a `conftest.py` fixture loading the new file.
5. Add contract assertions to `tests/test_contract.py`.

### New field in an existing model

1. Add the typed attribute to the dataclass in `models.py`.
2. Map it in `from_api()`.
3. Add or update the corresponding assertion in `test_models.py` or
   `test_contract.py`.
4. Update [`docs/fields-reference.md`](docs/fields-reference.md).

---

## Submitting a pull request

1. Fork the repo and create a branch: `git checkout -b feat/my-change`.
2. Make your changes; ensure `pytest`, `ruff`, and `mypy` all pass.
3. Open a PR against `main`. Fill in the PR template.
4. A maintainer will review within a few days.

**Commit message convention** (Conventional Commits):

```
feat: add AsyncNotairesClient
fix: handle missing typeBien in detail response
docs: add ethics section on contact PII
test: cover unknown DpeClass code in fixture
```

PRs are squash-merged so the commit title is what lands in `CHANGELOG.md`.

---

## Good first issues

Look for the `good first issue` label on GitHub. Current candidates:

- Add a fixture + enum member for a new `typeBien` code (e.g. `PRK`).
- Write `examples/export_csv.py`.
- Document a `geo-consultation` endpoint in `docs/api-reference.md`.
- Widen a `SearchParams` validation test for an edge case.
- Add a French translation of the README.
