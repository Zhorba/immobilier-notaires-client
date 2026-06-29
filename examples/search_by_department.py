"""Search listings in a department and print a summary table.

Usage:
    python examples/search_by_department.py
    python examples/search_by_department.py --dept 29 --max 50
"""

import argparse

from notaires_immo import NotairesClient, PropertyType, TransactionType


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dept", default="56", help="Department code (default: 56)")
    parser.add_argument("--max", type=int, default=20, help="Max listings to fetch")
    args = parser.parse_args()

    client = NotairesClient()

    print(f"Searching dept {args.dept} — up to {args.max} houses for sale …\n")

    count = 0
    for listing in client.iter_search(
        departements=[args.dept],
        property_types=[PropertyType.MAISON],
        transaction_types=[TransactionType.VENTE],
        per_page=20,
    ):
        print(
            f"  {listing.annonce_id:>10}  {listing.commune:<20}  "
            f"{listing.price_eur:>10,.0f} €  {listing.living_area_m2 or '?':>5} m²  "
            f"{listing.rooms or '?'} pièces"
        )
        count += 1
        if count >= args.max:
            break

    print(f"\n{count} listings printed.")


if __name__ == "__main__":
    main()
