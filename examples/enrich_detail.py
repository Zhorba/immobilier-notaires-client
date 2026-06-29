"""Fetch detail + contacts for the first N listings from a search.

Shows GPS coordinates, DPE class, and sea-view flag — fields only available
in the detail endpoint.

Usage:
    python examples/enrich_detail.py --dept 56 --n 5
"""

import argparse
import time

from notaires_immo import NotairesClient, PropertyType, TransactionType, TernaryFlag


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dept", default="56")
    parser.add_argument("--n", type=int, default=5, help="Number of listings to enrich")
    args = parser.parse_args()

    client = NotairesClient(min_delay=1.5)   # extra polite for two calls per listing

    count = 0
    for listing in client.iter_search(
        departements=[args.dept],
        property_types=[PropertyType.MAISON],
        transaction_types=[TransactionType.VENTE],
        per_page=20,
    ):
        detail = client.get_detail(listing.annonce_id)

        sea = "🌊" if detail.sea_view is TernaryFlag.OUI else "  "
        pool = "🏊" if detail.pool is TernaryFlag.OUI else "  "
        gps = f"{detail.gps_lat:.5f},{detail.gps_lon:.5f}" if detail.gps_lat else "no GPS"
        dpe = detail.dpe_class.value if detail.dpe_class else "?"

        print(
            f"{sea}{pool} {listing.annonce_id}  {listing.commune:<20}  "
            f"{listing.price_eur:>10,.0f} €  DPE:{dpe}  GPS:{gps}"
        )

        count += 1
        if count >= args.n:
            break

    print(f"\nEnriched {count} listings.")


if __name__ == "__main__":
    main()
