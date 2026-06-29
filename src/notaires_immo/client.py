"""Main client: NotairesClient."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import httpx

from .http import _make_client, get_json
from .models import Contact, Listing, ListingDetail, SearchResult
from .pagination import iter_page_numbers
from .params import SearchParams
from .ratelimit import RateLimiter

_SEARCH_PATH = "/inotr-www-annonces/v1/annonces"
_DETAIL_PATH = "/inotr-www-annonces/v1/annonces/{annonce_id}"
_CONTACTS_PATH = "/inotr-www-annonces-contacts/v1/annonces/{annonce_id}/contacts"


class NotairesClient:
    """Polite, typed client for the immobilier.notaires.fr public API.

    Usage::

        from notaires_immo import NotairesClient, PropertyType, TransactionType

        client = NotairesClient()
        for listing in client.iter_search(
            departements=["56"],
            property_types=[PropertyType.MAISON],
            transaction_types=[TransactionType.VENTE],
            surface_min=80,
            price_max=300_000,
        ):
            print(listing.commune, listing.price_eur)

    :param min_delay: Minimum seconds between requests (default 1.1).
        Pass ``0`` to disable throttling (not recommended).
    :param timeout: HTTP timeout in seconds.
    :param http_client: Inject a custom ``httpx.Client`` (e.g. for testing).
    """

    def __init__(
        self,
        *,
        min_delay: float = 1.1,
        timeout: float = 20.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._http = http_client or _make_client(timeout)
        self._limiter = RateLimiter(min_delay)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def search(
        self,
        *,
        departements: list[str] | None = None,
        property_types: list[Any] | None = None,
        transaction_types: list[Any] | None = None,
        surface_min: int | None = None,
        surface_max: int | None = None,
        price_min: int | None = None,
        price_max: int | None = None,
        rooms_min: int | None = None,
        rooms_max: int | None = None,
        per_page: int = 100,
        page: int = 1,
        perimetre: int = 0,
    ) -> SearchResult:
        """Fetch one page of listings matching the given filters.

        :returns: :class:`SearchResult` with ``.listings``, ``.total``,
            ``.total_pages``.
        """
        params = SearchParams(
            departements=departements,
            property_types=property_types,
            transaction_types=transaction_types,
            surface_min=surface_min,
            surface_max=surface_max,
            price_min=price_min,
            price_max=price_max,
            rooms_min=rooms_min,
            rooms_max=rooms_max,
            per_page=per_page,
            page=page,
            perimetre=perimetre,
        )
        return self._search_page(params)

    def iter_search(
        self,
        *,
        departements: list[str] | None = None,
        property_types: list[Any] | None = None,
        transaction_types: list[Any] | None = None,
        surface_min: int | None = None,
        surface_max: int | None = None,
        price_min: int | None = None,
        price_max: int | None = None,
        rooms_min: int | None = None,
        rooms_max: int | None = None,
        per_page: int = 100,
        perimetre: int = 0,
    ) -> Iterator[Listing]:
        """Lazily yield all listings matching the filters, auto-paginating.

        Rate-limited — respects ``min_delay`` between pages.
        """
        params = SearchParams(
            departements=departements,
            property_types=property_types,
            transaction_types=transaction_types,
            surface_min=surface_min,
            surface_max=surface_max,
            price_min=price_min,
            price_max=price_max,
            rooms_min=rooms_min,
            rooms_max=rooms_max,
            per_page=per_page,
            page=1,
            perimetre=perimetre,
        )
        first = self._search_page(params)
        yield from first.listings
        for page_num in iter_page_numbers(2, first.total_pages):
            params.page = page_num
            result = self._search_page(params)
            yield from result.listings

    def get_detail(self, annonce_id: int) -> ListingDetail:
        """Fetch the full record for one listing.

        Includes long description, exact GPS, DPE, amenity flags (sea view,
        pool, …), all photos at every resolution, and the negotiator contact
        with email.
        """
        path = _DETAIL_PATH.format(annonce_id=annonce_id)
        self._limiter.wait()
        raw = get_json(self._http, path)
        return ListingDetail.from_api(raw)

    def get_contacts(self, annonce_id: int) -> Contact:
        """Fetch the negotiator contact for a listing.

        Note: unlike the detail endpoint, this response does **not** include
        the email address.  Use ``get_detail()`` when you need the email.
        """
        path = _CONTACTS_PATH.format(annonce_id=annonce_id)
        self._limiter.wait()
        raw = get_json(self._http, path)
        return Contact.from_api(raw)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _search_page(self, params: SearchParams) -> SearchResult:
        self._limiter.wait()
        raw = get_json(
            self._http,
            _SEARCH_PATH,
            params=params.to_query(),
            referer=params.to_referer(),
        )
        return SearchResult.from_api(raw)

    # Context manager support (closes the underlying httpx.Client)
    def __enter__(self) -> "NotairesClient":
        return self

    def __exit__(self, *_: object) -> None:
        self._http.close()
