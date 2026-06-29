# Changelog

All notable changes to this project will be documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning: [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

---

## [0.1.0] — 2026-06-29

### Added

- `NotairesClient` with `search()`, `iter_search()`, `get_detail()`, and
  `get_contacts()` methods.
- `SearchParams` dataclass for validated, typed query building.
- Typed models: `Listing`, `ListingDetail`, `Contact`, `Photo`, `SearchResult`.
- Enums: `PropertyType` (MAI/APP/TER/IMM/GAR/DIV), `TransactionType`
  (VENTE/VNI/VAE/LOCATION), `TernaryFlag` (OUI/NON/INCONNU), `DpeClass` (A–G).
- Ternary flag convenience properties: `.is_yes`, `.is_no`, `.is_known`.
- All models expose `.raw` for forward-compatible access to unmapped fields.
- Unknown enum codes tolerated via `_missing_` (returns an `UNKNOWN(…)` member
  rather than raising `ValueError`).
- Rate limiter (default 1.1 s between requests, configurable).
- Retry / exponential backoff on 429 and 5xx responses.
- Polite defaults: honest `User-Agent`, correct `Referer` header.
- CLI: `notaires search` with `--format json/csv/table` and `--all-pages`.
- 52 offline tests (params, models, pagination, API contract canaries).
- Full API documentation: `docs/api-reference.md`, `docs/fields-reference.md`,
  `docs/ethics.md`, and redacted sample responses under `docs/samples/`.
- MIT license.

[Unreleased]: https://github.com/Zhorba/immobilier-notaires-client/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/Zhorba/immobilier-notaires-client/releases/tag/v0.1.0
