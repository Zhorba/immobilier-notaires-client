"""Search parameter building and validation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import PropertyType, TransactionType
from .exceptions import ApiBadRequest

_BASE_SEARCH_URL = (
    "https://www.immobilier.notaires.fr"
    "/fr/annonces-immobilieres-liste"
)


@dataclass
class SearchParams:
    """All parameters accepted by the search endpoint.

    Pass to ``NotairesClient.search()`` or ``iter_search()``.
    """

    departements: list[str] | None = None
    property_types: list[PropertyType] | None = None
    transaction_types: list[TransactionType] | None = None
    surface_min: int | None = None
    surface_max: int | None = None
    price_min: int | None = None
    price_max: int | None = None
    rooms_min: int | None = None
    rooms_max: int | None = None
    # default per_page=100 keeps crawls short; max observed in the wild is 120
    per_page: int = 100
    page: int = 1
    # radius around the locality in km; 0 = exact match only
    perimetre: int = 0
    extra: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.per_page < 1 or self.per_page > 200:
            raise ApiBadRequest("per_page must be between 1 and 200")
        if self.page < 1:
            raise ApiBadRequest("page must be >= 1")
        if self.surface_min is not None and self.surface_max is not None:
            if self.surface_min > self.surface_max:
                raise ApiBadRequest("surface_min must be <= surface_max")
        if self.price_min is not None and self.price_max is not None:
            if self.price_min > self.price_max:
                raise ApiBadRequest("price_min must be <= price_max")
        if self.rooms_min is not None and self.rooms_max is not None:
            if self.rooms_min > self.rooms_max:
                raise ApiBadRequest("rooms_min must be <= rooms_max")

    def to_query(self) -> dict[str, str]:
        """Return the validated query-string dict for the search endpoint."""
        self.validate()
        q: dict[str, str] = {
            "page": str(self.page),
            "parPage": str(self.per_page),
            "offset": "0",
            "perimetre": str(self.perimetre),
        }
        if self.departements:
            q["departements"] = ",".join(self.departements)
        if self.property_types:
            q["typeBiens"] = ",".join(pt.value for pt in self.property_types)
        if self.transaction_types:
            q["typeTransactions"] = ",".join(tt.value for tt in self.transaction_types)
        if self.surface_min is not None:
            q["surfaceMin"] = str(self.surface_min)
        if self.surface_max is not None:
            q["surfaceMax"] = str(self.surface_max)
        if self.price_min is not None:
            q["prixMin"] = str(self.price_min)
        if self.price_max is not None:
            q["prixMax"] = str(self.price_max)
        if self.rooms_min is not None:
            q["nbPiecesMin"] = str(self.rooms_min)
        if self.rooms_max is not None:
            q["nbPiecesMax"] = str(self.rooms_max)
        q.update({k: str(v) for k, v in self.extra.items()})
        return q

    def to_referer(self) -> str:
        """Build the equivalent human listing-page URL for use as Referer."""
        parts: list[str] = []
        if self.departements:
            # the human URL uses singular 'departement'
            parts.append(f"departement={','.join(self.departements)}")
        if self.property_types:
            parts.append(f"typeBien={','.join(pt.value for pt in self.property_types)}")
        if self.transaction_types:
            parts.append(
                f"typeTransaction={','.join(tt.value for tt in self.transaction_types)}"
            )
        if self.surface_min is not None:
            parts.append(f"surfaceMin={self.surface_min}")
        if self.price_max is not None:
            parts.append(f"prixMax={self.price_max}")
        parts.append(f"page={self.page}")
        parts.append(f"parPage={self.per_page}")
        qs = "&".join(parts)
        return f"{_BASE_SEARCH_URL}?{qs}" if qs else _BASE_SEARCH_URL
