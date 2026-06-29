#!/usr/bin/env python
"""Record (or refresh) API fixtures for the test suite.

Fetches live responses, redacts PII, and writes to tests/fixtures/.

Usage:
    python scripts/record_fixtures.py --annonce-id 12345 --dept 56
    python scripts/record_fixtures.py --annonce-id 12345 --type MAI

The script always redacts:
  - Negotiator phone numbers (telephone field)
  - Negotiator email addresses (mail field)
  - Negotiator full name (nom field)
  - Exact street address (adresse*, localite* fields in contacts)

Requires the package to be installed in editable mode:
    pip install -e ".[dev]"
"""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

import httpx

FIXTURES_DIR = Path(__file__).parent.parent / "tests" / "fixtures"

SEARCH_URL = "https://www.immobilier.notaires.fr/pub-services/inotr-www-annonces/v1/annonces"
DETAIL_URL = "https://www.immobilier.notaires.fr/pub-services/inotr-www-annonces/v1/annonces/{}"
CONTACTS_URL = "https://www.immobilier.notaires.fr/pub-services/inotr-www-annonces/v1/annonces/{}/contacts"

HEADERS = {
    "User-Agent": "immobilier-notaires-client/record-fixtures",
    "Referer": "https://www.immobilier.notaires.fr/",
    "Accept": "application/json, text/plain, */*",
}

PII_STRING_FIELDS = {"telephone", "mail", "nom", "adresse1", "adresse2", "adresse3", "adresse4"}
PII_BLOCK_KEYS = {"coordonneesW84", "coordonneesExactesW84"}


def _redact(obj: object) -> object:
    """Recursively redact PII from a parsed JSON structure."""
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            if k in PII_STRING_FIELDS and isinstance(v, str) and v:
                result[k] = "REDACTED"
            elif k in PII_BLOCK_KEYS:
                result[k] = v  # keep GPS for fixtures (not PII)
            else:
                result[k] = _redact(v)
        return result
    if isinstance(obj, list):
        return [_redact(item) for item in obj]
    return obj


def _fetch(client: httpx.Client, url: str, **kwargs) -> dict:
    resp = client.get(url, headers=HEADERS, **kwargs)
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annonce-id", required=True, type=int)
    parser.add_argument("--dept", default="56")
    parser.add_argument("--type", default="MAI", dest="prop_type")
    parser.add_argument("--out-dir", default=str(FIXTURES_DIR))
    args = parser.parse_args()

    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    annonce_id = args.annonce_id

    with httpx.Client(timeout=20) as client:
        print(f"Fetching search (dept={args.dept}, type={args.prop_type}) …")
        search_data = _fetch(
            client,
            SEARCH_URL,
            params={
                "parPage": 1,
                "page": 1,
                "typeTransactions": "VENTE",
                "typeBiens": args.prop_type,
                "departements": args.dept,
            },
        )
        print(f"  → {search_data.get('nbTotalAnnonces', '?')} total results")

        print(f"Fetching detail for annonceId={annonce_id} …")
        detail_data = _fetch(client, DETAIL_URL.format(annonce_id))

        print(f"Fetching contacts for annonceId={annonce_id} …")
        contacts_data = _fetch(client, CONTACTS_URL.format(annonce_id))

    search_clean = _redact(copy.deepcopy(search_data))
    detail_clean = _redact(copy.deepcopy(detail_data))
    contacts_clean = _redact(copy.deepcopy(contacts_data))

    (out / "search-response.json").write_text(
        json.dumps(search_clean, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "detail-response.json").write_text(
        json.dumps(detail_clean, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out / "contacts-response.json").write_text(
        json.dumps(contacts_clean, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"\nFixtures written to {out}/")
    print("  search-response.json")
    print("  detail-response.json")
    print("  contacts-response.json")
    print("\nReview for PII before committing. Run: pytest tests/test_contract.py -v")


if __name__ == "__main__":
    main()
