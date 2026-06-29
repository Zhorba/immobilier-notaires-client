# immobilier-notaires-client

A small, typed Python client for the **public listings API of
[immobilier.notaires.fr](https://www.immobilier.notaires.fr)** — the official
property portal of the Notaires de France.

> ⚠️ **Unofficial & early.** This wraps an *undocumented* (but public, no-auth) JSON
> API used by the site's own frontend. Not affiliated with or endorsed by the
> Notaires de France. The endpoint can change without notice. Please read
> [docs/ethics.md](docs/ethics.md) before using it.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![CI](https://github.com/Zhorba/immobilier-notaires-client/actions/workflows/ci.yml/badge.svg)](https://github.com/Zhorba/immobilier-notaires-client/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue)](pyproject.toml)

## Status

| Milestone | State |
|-----------|-------|
| M0 — API documentation & fixtures | ✅ Done |
| M1 — Core client (52 tests) | ✅ Done |
| M2 — CI, CONTRIBUTING, examples | ✅ Done |
| M3 — PyPI release | ⏳ Planned |
| M4 — Detail enrichment helpers | ⏳ Planned |
| M5 — Async client | ⏳ Planned |

## Install

```bash
pip install git+https://github.com/Zhorba/immobilier-notaires-client.git
```

PyPI release coming soon (M3).

## Documentation

- **[docs/api-reference.md](docs/api-reference.md)** — endpoints, query params,
  pagination, enums, headers.
- **[docs/fields-reference.md](docs/fields-reference.md)** — exhaustive field
  dictionary (search summaries + full detail record).
- **[docs/ethics.md](docs/ethics.md)** — responsible use, rate limiting, ToS, GDPR.
- **[docs/samples/](docs/samples/)** — captured (redacted) real responses you can
  test against.

## The API in 30 seconds

No auth. One `GET` returns a page of listings:

```
GET https://www.immobilier.notaires.fr/pub-services/inotr-www-annonces/v1/annonces
    ?page=1&parPage=100&departements=56&typeBiens=MAI&typeTransactions=VENTE
```

```jsonc
{
  "annonceResumeDto": [ { "annonceId": 2022988, "prixAffiche": 220000,
                          "surface": 81.68, "communeNom": "Plumelin", "...": "..." } ],
  "page": 1, "nbPages": 13, "nbTotalAnnonces": 1263
}
```

Full per-listing data (description, GPS, DPE, sea-view/pool flags, contact) comes
from the detail endpoint `…/annonces/{annonceId}`. See
[docs/api-reference.md](docs/api-reference.md).

## Planned client API (not yet released)

```python
from notaires_immo import NotairesClient, PropertyType, TransactionType

client = NotairesClient()  # polite defaults: rate-limited, honest UA, Referer set

for listing in client.iter_search(
    departements=["56"],
    property_types=[PropertyType.MAISON],
    transaction_types=[TransactionType.VENTE],
    surface_min=80,
    price_max=300_000,
):
    print(listing.commune, listing.price_eur, listing.living_area_m2)
```

## Contributing

Contributions welcome — especially confirming/extending the enums and fields.
See [CONTRIBUTING.md](CONTRIBUTING.md) (incl. how to record a fixture). Be a good
citizen of the upstream API: [docs/ethics.md](docs/ethics.md).

## License

[MIT](LICENSE).
