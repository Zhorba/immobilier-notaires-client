"""API contract tests — assert that captured fixtures still match the documented schema.

These tests are the canary for upstream API drift.  If they fail after refreshing
fixtures (``scripts/record_fixtures.py``), open an ``api_drift`` issue and update
the field reference docs.  They do NOT hit the network.
"""


# ---------------------------------------------------------------------------
# Search response
# ---------------------------------------------------------------------------

REQUIRED_ENVELOPE_KEYS = {"annonceResumeDto", "page", "nbPages", "parPage"}

REQUIRED_LISTING_KEYS = {
    "annonceId", "bienId", "reference", "crpcen",
    "prixAffiche", "surface", "communeNom", "codePostal",
    "inseeDepartement", "typeBien", "typeTransaction",
}


def test_search_envelope_keys(search_payload):
    missing = REQUIRED_ENVELOPE_KEYS - search_payload.keys()
    assert not missing, f"Search envelope missing keys: {missing}"


def test_search_listing_keys(search_payload):
    for listing in search_payload["annonceResumeDto"]:
        missing = REQUIRED_LISTING_KEYS - listing.keys()
        assert not missing, f"Listing summary missing keys: {missing}"


def test_search_types(search_payload):
    assert isinstance(search_payload["page"], int)
    assert isinstance(search_payload["nbPages"], int)
    assert isinstance(search_payload["annonceResumeDto"], list)


# ---------------------------------------------------------------------------
# Detail response
# ---------------------------------------------------------------------------

REQUIRED_DETAIL_KEYS = {"id", "vente", "bien"}
REQUIRED_VENTE_KEYS = {"prix", "emoluments", "multimedias", "descriptions"}
REQUIRED_BIEN_KEYS = {"id", "typeBien"}


def test_detail_top_level_keys(detail_payload):
    missing = REQUIRED_DETAIL_KEYS - detail_payload.keys()
    assert not missing, f"Detail response missing keys: {missing}"


def test_detail_vente_keys(detail_payload):
    vente = detail_payload.get("vente", {})
    missing = REQUIRED_VENTE_KEYS - vente.keys()
    assert not missing, f"vente block missing keys: {missing}"


def test_detail_bien_keys(detail_payload):
    bien = detail_payload.get("bien", {})
    missing = REQUIRED_BIEN_KEYS - bien.keys()
    assert not missing, f"bien block missing keys: {missing}"


def _prop_block(bien: dict) -> dict:
    """Resolve the nested property sub-block from a bien dict."""
    from notaires_immo.models import _BIEN_TYPE_TO_KEY
    type_code = bien.get("typeBien", "")
    key = _BIEN_TYPE_TO_KEY.get(type_code, type_code.lower())
    return bien.get(key, {})


def test_detail_prop_block_has_gps(detail_payload):
    bien = detail_payload["bien"]
    prop = _prop_block(bien)
    assert "coordonneesExactesW84" in prop, "GPS block missing from property block"
    gps = prop["coordonneesExactesW84"]
    assert "coordonneeX" in gps
    assert "coordonneeY" in gps


def test_detail_descriptions_have_fr(detail_payload):
    descriptions = detail_payload["vente"].get("descriptions", [])
    assert any(d.get("langue") == "fr" for d in descriptions), \
        "No French description found in detail response"


def test_detail_amenity_flags_present(detail_payload):
    bien = detail_payload["bien"]
    prop = _prop_block(bien)
    for flag in ("bordMer", "vueMer", "piscine", "terrasse"):
        assert flag in prop, f"Amenity flag '{flag}' missing from property block"


# ---------------------------------------------------------------------------
# Contacts response
# ---------------------------------------------------------------------------

REQUIRED_CONTACT_KEYS = {"id", "nom", "codePostal", "ville", "telephone"}


def test_contacts_keys(contacts_payload):
    missing = REQUIRED_CONTACT_KEYS - contacts_payload.keys()
    assert not missing, f"Contacts response missing keys: {missing}"


def test_contacts_no_email(contacts_payload):
    """The /contacts endpoint intentionally excludes email; use detail for that."""
    assert "mail" not in contacts_payload, \
        "Unexpected 'mail' field in contacts response — update docs if this changed"
