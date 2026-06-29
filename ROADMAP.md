# Project plan & roadmap — `immobilier-notaires-client`

A small, typed, **polite-by-default** Python client for the public listings API of
[immobilier.notaires.fr](https://www.immobilier.notaires.fr). This document is the
project's plan of record: vision, scope, architecture, milestones, and how to
contribute to each. It is meant to be read by contributors — if something here is
unclear or stale, a PR fixing it is a great first contribution.

> The API itself is documented in [`docs/api-reference.md`](docs/api-reference.md)
> and [`docs/fields-reference.md`](docs/fields-reference.md). This file is about the
> *software*.

---

## 1. Vision

Be the **first cleanly-licensed, well-tested, pip-installable** Python client for
this API. The existing community projects are unlicensed and unmaintained; the
commercial alternatives are paid aggregators. There is a clear gap for a small MIT
library that does one thing well: turn search criteria into typed listing objects,
responsibly.

**Design values**
- **Typed & predictable.** Dataclasses with real types; no untyped dict soup.
- **Polite by default.** Rate limiting, honest User-Agent, `Referer` — the safe
  behaviour is the default behaviour, not an opt-in.
- **Offline-testable.** The whole suite runs against recorded fixtures with no
  network and no secrets, so contributing is friction-free.
- **No lock-in, no surprises.** Unknown API fields are preserved, never silently
  dropped. The library never hides data from you.
- **Small surface, stable contract.** Few public symbols; semver discipline.

---

## 2. Scope

**In scope**
- Read access to the search, detail, and contacts endpoints.
- Typed models, enums, parameter building/validation.
- Pagination (eager list + lazy generator).
- Rate limiting, retries/backoff, clear exceptions.
- A thin CLI for ad-hoc queries and JSON/CSV export.
- Thorough docs, examples, and tests.

**Out of scope (non-goals)**
- Writing/posting to the site (alerts, favourites) — read-only by design.
- Bypassing anti-bot measures, CAPTCHAs, or auth-gated reference endpoints.
- A scraping framework, a database layer, or a scheduler — this is a client, not a
  pipeline. Downstream apps compose those themselves.
- Bulk redistribution of contact PII (see [`docs/ethics.md`](docs/ethics.md)).

---

## 3. Architecture

```
src/notaires_immo/
├── __init__.py      # public exports: NotairesClient, models, enums, exceptions
├── client.py        # NotairesClient: search / iter_search / get_detail / get_contacts
├── http.py          # session, headers (UA + Referer), retry/backoff
├── ratelimit.py     # token-bucket / min-delay throttle (default ON)
├── params.py        # SearchParams → validated query dict
├── pagination.py    # page → nbPages iteration
├── enums.py         # PropertyType, TransactionType, TernaryFlag, DpeClass
├── models.py        # Listing, ListingDetail, Contact (+ from_api())
├── exceptions.py    # NotairesError hierarchy
└── cli.py           # `notaires search ...`
```

**Layering (one direction, no cycles):**
`enums` → `models` → `params` → `http`/`ratelimit` → `client` → `cli`.

**Public API (target):**

```python
from notaires_immo import NotairesClient, PropertyType, TransactionType

client = NotairesClient()                       # polite defaults

result = client.search(                         # one page → SearchResult
    departements=["56"],
    property_types=[PropertyType.MAISON],
    transaction_types=[TransactionType.VENTE],
    surface_min=80, price_max=300_000,
    page=1, per_page=100,
)
result.total, result.total_pages, result.listings

for listing in client.iter_search(...):         # lazy, auto-paginated, rate-limited
    detail = client.get_detail(listing.annonce_id)   # rich record
    contact = client.get_contacts(listing.annonce_id)
```

- `Listing` / `ListingDetail` / `Contact` are frozen dataclasses with a
  `from_api(dict)` classmethod and a `.raw` escape hatch holding the untouched
  payload (forward-compatible with new API fields).
- Enums are string-valued and tolerant: an unknown code parses to an `UNKNOWN`
  member with the raw value preserved, rather than raising — the API evolves.

---

## 4. Milestones

Each milestone is shippable on its own. Tags follow semver (see §7).

### M0 — Verify & fixtures  ✅ (2026-06-29)
- [x] Reverse-engineer and **document** the API (`docs/api-reference.md`,
      `docs/fields-reference.md`, `docs/ethics.md`).
- [x] Capture redacted sample responses (`docs/samples/`).
- [x] Promote samples into `tests/fixtures/` as the pinned contract fixtures.

### M1 — Core read client  ✅ (2026-06-29)
- [x] `pyproject.toml` (hatchling, PEP 621, MIT, Python ≥3.11, deps: `httpx`).
- [x] `enums.py`, `models.py` with `from_api()` + `.raw`.
- [x] `params.py` — build & validate query (required `parPage`, comma-joins,
      range sanity).
- [x] `http.py` + `ratelimit.py` — session, polite headers, default throttle,
      retry/backoff on 429/5xx.
- [x] `client.py` — `search()`, `iter_search()`, `get_detail()`, `get_contacts()`.
- [x] `exceptions.py` — `NotairesError`, `ApiBadRequest`, `RateLimited`,
      `NotFound`, `ApiSchemaError`.
- [x] `cli.py` — `notaires search` with `--format json/csv/table`, `--all-pages`.
- [x] Tests: `test_params` (16), `test_models` (18), `test_pagination` (6),
      `test_contract` (12) — 52/52 passing, all offline against fixtures.

### M2 — Developer experience & docs  ✅ (2026-06-29)
- [x] `README` polish — badges (CI, Python version, MIT), install instructions.
- [x] `CONTRIBUTING.md` — dev setup, fixture-recording workflow, PR flow,
      commit conventions.
- [x] `CODE_OF_CONDUCT.md`, `CHANGELOG.md` (Keep a Changelog), `SECURITY.md`.
- [x] `examples/` — `search_by_department.py`, `export_csv.py`, `enrich_detail.py`.
- [x] `scripts/record_fixtures.py` — automates live fetch + PII redaction.
- [x] CI (`.github/workflows/ci.yml`): ruff + mypy + pytest on Python 3.11 & 3.12.
- [x] `.pre-commit-config.yaml`; issue templates (`bug`, `feature`, `api_drift`) and
      `PULL_REQUEST_TEMPLATE.md`.
- **Done when:** a new contributor can clone, set up, run tests, and submit a PR
  guided only by repo docs; CI gates PRs.

### M3 — Publish (→ `v0.1.0`/`v0.2.0` on PyPI)
- [ ] Reserve the PyPI name with a skeleton release early (anti-squat).
- [ ] Release workflow: build + publish to PyPI on tag via trusted publishing
      (OIDC, no stored token).
- [ ] Verify `pip install immobilier-notaires-client` from a clean env.
- **Done when:** the package installs from PyPI and imports cleanly.

### M4 — Detail enrichment & helpers (→ `v0.3.0`)
- [ ] Full typed `ListingDetail` incl. amenity/location flags (`bordMer`, `vueMer`,
      `piscine`, DPE, taxe foncière, GPS) and photo-resolution helpers.
- [ ] Geo helpers via `geo-consultation/v1/*` (resolve commune/locality → ids).
- [ ] Convenience: `iter_search_with_detail()` (rate-limited fan-out).
- **Done when:** detail flags are typed and covered by fixtures.

### M5 — Async client (→ `v0.4.0`)
- [ ] `AsyncNotairesClient` mirroring the sync surface, sharing params/models.
- [ ] Async rate limiter; httpx `AsyncClient`.
- **Done when:** async parity tests pass against the same fixtures.

### Backlog (post-1.0 candidates)
Region/department presets; richer filters (DPE class, year built); CLI output
formats (CSV/NDJSON/table); response caching; FR/EN docs; typed enum completion for
all `typeBiens`; optional Pydantic models behind an extra.

**Toward `v1.0.0`:** API stable for two minor cycles, async shipped, docs complete,
CI matrix green, real-world usage validated.

---

## 5. Testing strategy

- **Fixture-first, offline by default.** Record a real response once, redact PII,
  commit under `tests/fixtures/`. CI never hits the network.
- **Contract test** asserts documented fields still exist in fixtures — the canary
  for upstream schema drift. A separate **opt-in live test** (`-m live`, skipped by
  default) probes the real API on demand to detect drift.
- **Pure unit tests** for `params` (query building/validation) and `models`
  (`from_api()` mapping). No mocking of HTTP internals to assert private state.
- `CONTRIBUTING.md` documents the fixture-recording workflow so anyone can add a
  property type or field with a backing fixture.

---

## 6. Contribution model

- **Issues drive work.** Templates: `bug`, `feature`, `api_drift` (for "the API
  changed" reports — high priority).
- **Labels:** `good first issue`, `help wanted`, `api-drift`, `docs`, `enhancement`.
- **Candidate good-first-issues:** add an `APP`/`TER` property-type enum member +
  fixture; add the CSV export example; document a `geo-consultation` endpoint;
  widen a parameter validation test.
- **PR flow:** branch → green CI (ruff + mypy + pytest) → review → squash-merge.
- **Conventional Commits** for messages (feeds `CHANGELOG.md`).
- All contributions abide by `CODE_OF_CONDUCT.md` and the responsible-use stance in
  [`docs/ethics.md`](docs/ethics.md).

---

## 7. Versioning & releases

- **Semantic Versioning.** Pre-1.0: minor = features, patch = fixes; breaking
  changes allowed in minors but called out in `CHANGELOG.md`.
- **Changelog** kept in Keep-a-Changelog format; releases cut from it.
- **Tag → CI publishes to PyPI** (trusted publishing). No manual uploads.
- Python support tracks active CPython releases; dropping a version is a minor bump
  with a changelog note.

---

## 8. Risks & mitigations

| Risk | Mitigation |
|------|-----------|
| Undocumented API changes/breaks | Contract test + `api_drift` issue template + `.raw` passthrough so partial breakage degrades gracefully. |
| Endpoint blocks non-browser traffic | Polite defaults (UA, `Referer`, rate limit); document headers. |
| Legal/ToS concerns | Clear disclaimer, MIT + responsible-use docs, read-only scope, no anti-bot evasion. |
| Maintainer bandwidth | Small surface, offline tests, good-first-issues to grow contributors. |

---

*This roadmap is living. Propose changes via PR.*
