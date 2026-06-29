"""Tests for from_api() model parsing against captured fixtures."""

from datetime import date

from notaires_immo.enums import DpeClass, PropertyType, TernaryFlag, TransactionType
from notaires_immo.models import Contact, Listing, ListingDetail, SearchResult


class TestSearchResult:
    def test_parses_envelope(self, search_payload):
        result = SearchResult.from_api(search_payload)
        assert result.page == 1
        assert result.total_pages == 1263
        assert result.total == 1263
        assert len(result.listings) == 1

    def test_raw_preserved(self, search_payload):
        result = SearchResult.from_api(search_payload)
        assert result.raw is search_payload


class TestListing:
    def test_core_fields(self, search_payload):
        listing = Listing.from_api(search_payload["annonceResumeDto"][0])
        assert listing.annonce_id == 2022988
        assert listing.commune == "Plumelin"
        assert listing.postal_code == "56500"
        assert listing.dept_code == "56"
        assert listing.price_eur == 220000
        assert listing.price_total_eur == 230080
        assert listing.emoluments_eur == 10080
        assert listing.living_area_m2 == 81.68
        assert listing.land_area_m2 == 756
        assert listing.rooms == 5
        assert listing.bedrooms == 3

    def test_enums(self, search_payload):
        listing = Listing.from_api(search_payload["annonceResumeDto"][0])
        assert listing.property_type is PropertyType.MAISON
        assert listing.transaction_type is TransactionType.VENTE

    def test_dates(self, search_payload):
        listing = Listing.from_api(search_payload["annonceResumeDto"][0])
        assert listing.date_created is not None
        assert listing.date_created.year == 2026
        assert listing.dpe_date == date(2026, 6, 15)

    def test_urls(self, search_payload):
        listing = Listing.from_api(search_payload["annonceResumeDto"][0])
        assert listing.listing_url_fr and "2022988" in listing.listing_url_fr
        assert listing.photo_url and "media.immobilier.notaires.fr" in listing.photo_url
        assert listing.photo_count == 9

    def test_raw_preserved(self, search_payload):
        raw = search_payload["annonceResumeDto"][0]
        listing = Listing.from_api(raw)
        assert listing.raw is raw

    def test_unknown_property_type_tolerated(self):
        raw = {**_minimal_listing_raw(), "typeBien": "FUTURE_CODE"}
        listing = Listing.from_api(raw)
        assert listing.property_type.value == "FUTURE_CODE"
        assert listing.property_type is not PropertyType.MAISON


class TestListingDetail:
    def test_core_fields(self, detail_payload):
        detail = ListingDetail.from_api(detail_payload)
        assert detail.annonce_id == 2022988
        assert detail.property_type is PropertyType.MAISON
        assert detail.transaction_type is TransactionType.VENTE
        assert detail.price_eur == 220000
        assert detail.living_area_m2 == 81.68
        assert detail.land_area_m2 == 756
        assert detail.rooms == 5
        assert detail.bedrooms == 3

    def test_gps(self, detail_payload):
        detail = ListingDetail.from_api(detail_payload)
        assert detail.gps_lon == pytest.approx(-2.89623, rel=1e-3)
        assert detail.gps_lat == pytest.approx(47.8706, rel=1e-3)

    def test_dpe(self, detail_payload):
        detail = ListingDetail.from_api(detail_payload)
        assert detail.dpe_class is DpeClass.D
        assert detail.dpe_consumption == 194
        assert detail.ges_class is DpeClass.B
        assert detail.ges_emission == 7
        assert detail.energy_cost_min == 1420
        assert detail.energy_cost_max == 1922
        assert detail.dpe_date == date(2026, 6, 15)

    def test_costs(self, detail_payload):
        detail = ListingDetail.from_api(detail_payload)
        assert detail.taxe_fonciere == 909

    def test_ternary_flags(self, detail_payload):
        detail = ListingDetail.from_api(detail_payload)
        assert detail.sea_front is TernaryFlag.INCONNU
        assert detail.sea_view is TernaryFlag.INCONNU
        assert detail.pool is TernaryFlag.INCONNU
        assert detail.terrace is TernaryFlag.OUI

    def test_description(self, detail_payload):
        detail = ListingDetail.from_api(detail_payload)
        assert detail.description_fr and "PLUMELIN" in detail.description_fr
        assert detail.description_short_fr and "756" in detail.description_short_fr

    def test_photos(self, detail_payload):
        detail = ListingDetail.from_api(detail_payload)
        assert len(detail.photos) == 1
        assert detail.photos[0].is_main is True
        assert detail.photos[0].url_vga and "VGA" in detail.photos[0].url_vga

    def test_contact(self, detail_payload):
        detail = ListingDetail.from_api(detail_payload)
        assert detail.contact is not None
        assert detail.contact.city == "Locmine"
        assert detail.contact.email == "nego@example.notaires.fr"

    def test_raw_preserved(self, detail_payload):
        detail = ListingDetail.from_api(detail_payload)
        assert detail.raw is detail_payload


class TestContact:
    def test_contacts_endpoint(self, contacts_payload):
        contact = Contact.from_api(contacts_payload)
        assert contact.city == "Locmine"
        assert contact.postal_code == "56500"
        assert contact.email is None  # not present in contacts endpoint

    def test_gps(self, contacts_payload):
        contact = Contact.from_api(contacts_payload)
        assert contact.gps_lon == pytest.approx(-2.84145, rel=1e-3)
        assert contact.gps_lat == pytest.approx(47.87994, rel=1e-3)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

import pytest  # noqa: E402 (import at bottom for clarity)


def _minimal_listing_raw() -> dict:
    """Minimal valid raw dict for a Listing."""
    return {
        "annonceId": 1,
        "bienId": 2,
        "reference": "00000-1",
        "crpcen": "00000",
        "statut": "LIGNE",
        "prixAffiche": 100000,
        "surface": 80.0,
        "communeNom": "Test",
        "codePostal": "56000",
        "inseeDepartement": "56",
        "typeBien": "MAI",
        "typeTransaction": "VENTE",
    }
