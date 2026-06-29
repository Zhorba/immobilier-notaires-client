"""Export search results to a CSV file.

Usage:
    python examples/export_csv.py --dept 56 --out listings.csv
"""

import argparse
import csv
import sys

from notaires_immo import NotairesClient, PropertyType, TransactionType


FIELDS = [
    "annonce_id", "commune", "postal_code", "property_type", "transaction_type",
    "price_eur", "living_area_m2", "land_area_m2", "rooms", "bedrooms",
    "photo_count", "listing_url_fr",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dept", default="56")
    parser.add_argument("--out", default="-", help="Output file (default: stdout)")
    parser.add_argument("--max", type=int, default=200)
    args = parser.parse_args()

    out = open(args.out, "w", newline="", encoding="utf-8") if args.out != "-" else sys.stdout

    writer = csv.DictWriter(out, fieldnames=FIELDS)
    writer.writeheader()

    client = NotairesClient()
    count = 0

    for listing in client.iter_search(
        departements=[args.dept],
        property_types=[PropertyType.MAISON],
        transaction_types=[TransactionType.VENTE],
        per_page=100,
    ):
        writer.writerow({f: getattr(listing, f) for f in FIELDS})
        count += 1
        if count >= args.max:
            break

    if out is not sys.stdout:
        out.close()
        print(f"Wrote {count} rows to {args.out}")


if __name__ == "__main__":
    main()
