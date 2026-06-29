"""immobilier-notaires-client — Python client for immobilier.notaires.fr.

Quick start::

    from notaires_immo import NotairesClient, PropertyType, TransactionType

    with NotairesClient() as client:
        for listing in client.iter_search(
            departements=["56"],
            property_types=[PropertyType.MAISON],
            transaction_types=[TransactionType.VENTE],
            surface_min=80,
        ):
            print(listing.commune, listing.price_eur)
"""

from .client import NotairesClient
from .enums import DpeClass, PropertyType, TernaryFlag, TransactionType
from .exceptions import (
    ApiBadRequest,
    ApiSchemaError,
    NotairesError,
    NotFound,
    RateLimited,
)
from .models import Contact, Listing, ListingDetail, Photo, SearchResult
from .params import SearchParams

__version__ = "0.1.0"

__all__ = [
    "NotairesClient",
    "SearchParams",
    # enums
    "PropertyType",
    "TransactionType",
    "TernaryFlag",
    "DpeClass",
    # models
    "SearchResult",
    "Listing",
    "ListingDetail",
    "Contact",
    "Photo",
    # exceptions
    "NotairesError",
    "ApiBadRequest",
    "NotFound",
    "RateLimited",
    "ApiSchemaError",
    "__version__",
]
