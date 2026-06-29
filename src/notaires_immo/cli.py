"""Command-line interface: ``notaires search ...``

Requires the ``cli`` extra: ``pip install immobilier-notaires-client[cli]``
"""

from __future__ import annotations

import json
import sys

try:
    import click
except ImportError:  # pragma: no cover
    print(
        "The CLI requires the 'cli' extra:\n"
        "  pip install immobilier-notaires-client[cli]",
        file=sys.stderr,
    )
    sys.exit(1)

from .client import NotairesClient
from .enums import PropertyType, TransactionType


@click.group()
def main() -> None:
    """immobilier-notaires-client — query the notaires.fr listings API."""


@main.command()
@click.option("--dept", "-d", multiple=True, help="INSEE dept code(s), e.g. 56")
@click.option(
    "--type",
    "-t",
    "prop_types",
    multiple=True,
    type=click.Choice([pt.value for pt in PropertyType if not pt.name.startswith("UNKNOWN")]),
    help="Property type(s). Default: all.",
)
@click.option(
    "--transaction",
    multiple=True,
    type=click.Choice([tt.value for tt in TransactionType if not tt.name.startswith("UNKNOWN")]),
    default=("VENTE",),
    show_default=True,
    help="Transaction type(s).",
)
@click.option("--surface-min", type=int, default=None, help="Min living area (m²).")
@click.option("--surface-max", type=int, default=None, help="Max living area (m²).")
@click.option("--price-min", type=int, default=None, help="Min price (€).")
@click.option("--price-max", type=int, default=None, help="Max price (€).")
@click.option("--rooms-min", type=int, default=None, help="Min rooms.")
@click.option("--per-page", type=int, default=100, show_default=True)
@click.option("--page", type=int, default=1, show_default=True, help="Single page to fetch.")
@click.option("--all-pages", is_flag=True, help="Fetch all pages (auto-paginate).")
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["json", "csv", "table"]),
    default="json",
    show_default=True,
)
@click.option("--min-delay", type=float, default=1.1, show_default=True,
              help="Seconds between requests.")
def search(
    dept: tuple[str, ...],
    prop_types: tuple[str, ...],
    transaction: tuple[str, ...],
    surface_min: int | None,
    surface_max: int | None,
    price_min: int | None,
    price_max: int | None,
    rooms_min: int | None,
    per_page: int,
    page: int,
    all_pages: bool,
    fmt: str,
    min_delay: float,
) -> None:
    """Search listings and print results."""
    property_types = [PropertyType(t) for t in prop_types] if prop_types else None
    transaction_types = [TransactionType(t) for t in transaction]

    client = NotairesClient(min_delay=min_delay)
    rows = []

    if all_pages:
        for listing in client.iter_search(
            departements=list(dept) or None,
            property_types=property_types,
            transaction_types=transaction_types,
            surface_min=surface_min,
            surface_max=surface_max,
            price_min=price_min,
            price_max=price_max,
            rooms_min=rooms_min,
            per_page=per_page,
        ):
            rows.append(listing)
    else:
        result = client.search(
            departements=list(dept) or None,
            property_types=property_types,
            transaction_types=transaction_types,
            surface_min=surface_min,
            surface_max=surface_max,
            price_min=price_min,
            price_max=price_max,
            rooms_min=rooms_min,
            per_page=per_page,
            page=page,
        )
        click.echo(
            f"Page {result.page}/{result.total_pages} — {result.total} listings total",
            err=True,
        )
        rows = result.listings

    if fmt == "json":
        out = [r.raw for r in rows]
        click.echo(json.dumps(out, ensure_ascii=False, indent=2))
    elif fmt == "csv":
        import csv as _csv
        writer = _csv.writer(sys.stdout)
        writer.writerow([
            "annonce_id", "commune", "postal_code", "dept_code",
            "price_eur", "living_area_m2", "land_area_m2",
            "rooms", "bedrooms", "property_type", "transaction_type",
            "listing_url_fr",
        ])
        for r in rows:
            writer.writerow([
                r.annonce_id, r.commune, r.postal_code, r.dept_code,
                r.price_eur, r.living_area_m2, r.land_area_m2,
                r.rooms, r.bedrooms, r.property_type.value, r.transaction_type.value,
                r.listing_url_fr,
            ])
    else:  # table
        click.echo(
            f"{'ID':>10}  {'Commune':<20}  {'CP':>6}  {'Prix €':>10}  "
            f"{'m²':>6}  {'Terrain':>8}  {'Pièces':>7}"
        )
        click.echo("-" * 75)
        for r in rows:
            click.echo(
                f"{r.annonce_id:>10}  {r.commune:<20}  {r.postal_code:>6}  "
                f"{r.price_eur:>10,}  {r.living_area_m2 or '':>6}  "
                f"{r.land_area_m2 or '':>8}  {r.rooms or '':>7}"
            )
