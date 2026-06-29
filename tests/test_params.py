"""Tests for SearchParams query building and validation."""

import pytest

from notaires_immo.enums import PropertyType, TransactionType
from notaires_immo.exceptions import ApiBadRequest
from notaires_immo.params import SearchParams


def test_required_par_page_included():
    q = SearchParams().to_query()
    assert "parPage" in q
    assert q["parPage"] == "100"


def test_page_default_is_one():
    q = SearchParams().to_query()
    assert q["page"] == "1"


def test_departements_comma_joined():
    q = SearchParams(departements=["44", "56"]).to_query()
    assert q["departements"] == "44,56"


def test_single_department():
    q = SearchParams(departements=["56"]).to_query()
    assert q["departements"] == "56"


def test_property_types_use_api_values():
    q = SearchParams(property_types=[PropertyType.MAISON, PropertyType.APPARTEMENT]).to_query()
    assert q["typeBiens"] == "MAI,APP"


def test_transaction_types():
    q = SearchParams(
        transaction_types=[TransactionType.VENTE, TransactionType.VNI]
    ).to_query()
    assert q["typeTransactions"] == "VENTE,VNI"


def test_surface_filters():
    q = SearchParams(surface_min=80, surface_max=200).to_query()
    assert q["surfaceMin"] == "80"
    assert q["surfaceMax"] == "200"


def test_price_filters():
    q = SearchParams(price_min=50_000, price_max=300_000).to_query()
    assert q["prixMin"] == "50000"
    assert q["prixMax"] == "300000"


def test_rooms_filters():
    q = SearchParams(rooms_min=3, rooms_max=6).to_query()
    assert q["nbPiecesMin"] == "3"
    assert q["nbPiecesMax"] == "6"


def test_omits_none_filters():
    q = SearchParams().to_query()
    for key in ("departements", "typeBiens", "typeTransactions",
                "surfaceMin", "surfaceMax", "prixMin", "prixMax"):
        assert key not in q


def test_invalid_per_page_raises():
    with pytest.raises(ApiBadRequest):
        SearchParams(per_page=0).validate()


def test_invalid_page_raises():
    with pytest.raises(ApiBadRequest):
        SearchParams(page=0).validate()


def test_surface_min_gt_max_raises():
    with pytest.raises(ApiBadRequest):
        SearchParams(surface_min=200, surface_max=80).validate()


def test_price_min_gt_max_raises():
    with pytest.raises(ApiBadRequest):
        SearchParams(price_min=400_000, price_max=100_000).validate()


def test_referer_includes_department():
    p = SearchParams(departements=["56"], property_types=[PropertyType.MAISON])
    referer = p.to_referer()
    assert "departement=56" in referer
    assert "typeBien=MAI" in referer


def test_extra_params_passed_through():
    q = SearchParams(extra={"foo": "bar"}).to_query()
    assert q["foo"] == "bar"
