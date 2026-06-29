"""Typed models for API responses.

Each model is a frozen dataclass with a ``from_api(dict)`` classmethod that parses
the raw API payload.  Unknown or additional fields are preserved in ``.raw`` so that
upstream API changes never cause silent data loss — you can always reach into ``.raw``
while waiting for the library to be updated.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from .enums import DpeClass, PropertyType, TernaryFlag, TransactionType
from .exceptions import ApiSchemaError


def _str(d: dict[str, Any], key: str) -> str:
    v = d.get(key)
    if v is None:
        raise ApiSchemaError(f"Missing required field '{key}'", raw=d)
    return str(v)


def _opt_str(d: dict[str, Any], key: str) -> str | None:
    v = d.get(key)
    return str(v) if v is not None else None


def _int(d: dict[str, Any], key: str) -> int:
    v = d.get(key)
    if v is None:
        raise ApiSchemaError(f"Missing required field '{key}'", raw=d)
    return int(v)


def _opt_int(d: dict[str, Any], key: str) -> int | None:
    v = d.get(key)
    return int(v) if v is not None else None


def _opt_float(d: dict[str, Any], key: str) -> float | None:
    v = d.get(key)
    return float(v) if v is not None else None


def _dt(d: dict[str, Any], key: str) -> datetime | None:
    v = d.get(key)
    if not v:
        return None
    text = str(v)
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _date(d: dict[str, Any], key: str) -> date | None:
    v = d.get(key)
    if not v:
        return None
    try:
        return date.fromisoformat(str(v)[:10])
    except ValueError:
        return None


def _ternary(d: dict[str, Any], key: str) -> TernaryFlag:
    return TernaryFlag(d.get(key, "INCONNU"))


# Maps typeBien code → key name used inside the bien block
_BIEN_TYPE_TO_KEY: dict[str, str] = {
    "MAI": "maison",
    "APP": "appartement",
    "TER": "terrain",
    "IMM": "immeuble",
    "GAR": "garage",
    "DIV": "divers",
}


def _nested(d: dict[str, Any], *keys: str) -> Any:
    v: Any = d
    for k in keys:
        if not isinstance(v, dict):
            return None
        v = v.get(k)
    return v


@dataclass(frozen=True)
class Photo:
    url_vga: str | None
    url_highest: str | None
    is_main: bool
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> "Photo":
        return cls(
            url_vga=_nested(d, "vga", "url"),
            url_highest=_opt_str(d, "urlHighestResolution"),
            is_main=d.get("photoPrincipale") == "OUI",
            raw=d,
        )


@dataclass(frozen=True)
class Contact:
    """Negotiator contact.  ``email`` is only populated from the detail endpoint,
    not from the dedicated contacts endpoint."""

    contact_id: int | None
    name: str | None
    address: str | None
    postal_code: str | None
    city: str | None
    phone: str | None
    email: str | None
    gps_lon: float | None
    gps_lat: float | None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> "Contact":
        return cls(
            contact_id=_opt_int(d, "id"),
            name=_opt_str(d, "nom"),
            address=_opt_str(d, "adresse4"),
            postal_code=_opt_str(d, "codePostal"),
            city=_opt_str(d, "ville"),
            phone=_opt_str(d, "telephone"),
            email=_opt_str(d, "mail"),
            gps_lon=_nested(d, "coordonneesW84", "coordonneeX"),
            gps_lat=_nested(d, "coordonneesW84", "coordonneeY"),
            raw=d,
        )


@dataclass(frozen=True)
class Listing:
    """One listing summary as returned by the search endpoint."""

    annonce_id: int
    bien_id: int
    reference: str
    crpcen: str
    status: str
    date_created: datetime | None
    date_updated: datetime | None
    # price
    price_eur: int
    price_total_eur: int
    emoluments_eur: int
    emoluments_pct: float | None
    # property
    property_type: PropertyType
    transaction_type: TransactionType
    living_area_m2: float | None
    land_area_m2: int | None
    rooms: int | None
    bedrooms: int | None
    # location
    commune: str
    locality: str
    postal_code: str
    insee_commune: str
    dept_code: str
    dept_name: str
    region_name: str
    # media & extras
    description_fr: str | None
    photo_url: str | None
    photo_count: int
    listing_url_fr: str | None
    listing_url_en: str | None
    phone: str | None
    dpe_date: date | None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> "Listing":
        return cls(
            annonce_id=_int(d, "annonceId"),
            bien_id=_int(d, "bienId"),
            reference=_str(d, "reference"),
            crpcen=_str(d, "crpcen"),
            status=d.get("statut", ""),
            date_created=_dt(d, "dateCreation"),
            date_updated=_dt(d, "dateMaj"),
            price_eur=_int(d, "prixAffiche"),
            price_total_eur=d.get("prixTotal") or d.get("prixAffiche") or 0,
            emoluments_eur=d.get("emoluments") or 0,
            emoluments_pct=_opt_float(d, "pourcentageEmoluments"),
            property_type=PropertyType(d.get("typeBien", "")),
            transaction_type=TransactionType(d.get("typeTransaction", "")),
            living_area_m2=_opt_float(d, "surface"),
            land_area_m2=_opt_int(d, "surfaceTerrain"),
            rooms=_opt_int(d, "nbPieces"),
            bedrooms=_opt_int(d, "nbChambres"),
            commune=_str(d, "communeNom"),
            locality=d.get("localiteNom") or d.get("communeNom") or "",
            postal_code=_str(d, "codePostal"),
            insee_commune=d.get("inseeCommune") or "",
            dept_code=_str(d, "inseeDepartement"),
            dept_name=d.get("departementNom") or "",
            region_name=d.get("regionNom") or "",
            description_fr=_opt_str(d, "descriptionFr"),
            photo_url=_opt_str(d, "urlPhotoPrincipale"),
            photo_count=d.get("nbPhoto") or 0,
            listing_url_fr=_opt_str(d, "urlDetailAnnonceFr"),
            listing_url_en=_opt_str(d, "urlDetailAnnonceEn"),
            phone=_opt_str(d, "telephone"),
            dpe_date=_date(d, "dateRealisationDpe"),
            raw=d,
        )


@dataclass(frozen=True)
class ListingDetail:
    """Full listing record from the detail endpoint.

    Includes long description, exact GPS, all amenity flags (sea view, pool, DPE…)
    and the negotiator contact with email.
    """

    annonce_id: int
    status: str
    property_type: PropertyType
    transaction_type: TransactionType
    crpcen: str
    office_id: int | None
    # price (from vente block)
    price_eur: int | None
    emoluments_eur: int | None
    date_created: datetime | None
    date_updated: datetime | None
    reference: str | None
    # media
    photos: list[Photo]
    description_fr: str | None
    description_short_fr: str | None
    # property (from bien.* block)
    commune: str | None
    postal_code: str | None
    dept_code: str | None
    gps_lon: float | None
    gps_lat: float | None
    living_area_m2: float | None
    land_area_m2: int | None
    rooms: int | None
    bedrooms: int | None
    bathrooms: int | None
    # energy
    dpe_class: DpeClass | None
    dpe_consumption: int | None
    ges_class: DpeClass | None
    ges_emission: int | None
    dpe_date: date | None
    energy_cost_min: int | None
    energy_cost_max: int | None
    # costs
    taxe_fonciere: int | None
    # location quality (key scoring signals)
    sea_front: TernaryFlag
    sea_view: TernaryFlag
    feet_in_water: TernaryFlag
    pool: TernaryFlag
    terrace: TernaryFlag
    garden: TernaryFlag
    fireplace: TernaryFlag
    panoramic_view: TernaryFlag
    countryside: TernaryFlag
    # contact
    contact: Contact | None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> "ListingDetail":
        vente: dict[str, Any] = d.get("vente") or {}
        bien: dict[str, Any] = d.get("bien") or {}

        # The property sub-block key is the full word, not the code abbreviation.
        type_code = bien.get("typeBien") or ""
        prop_key = _BIEN_TYPE_TO_KEY.get(type_code, type_code.lower())
        prop_block: dict[str, Any] = bien.get(prop_key) or {}

        # Photos from vente.multimedias
        photos = [Photo.from_api(m) for m in (vente.get("multimedias") or [])]

        # Full description from vente.descriptions (prefer 'fr')
        desc_fr = desc_short_fr = None
        for desc in vente.get("descriptions") or []:
            if desc.get("langue") == "fr":
                desc_fr = _opt_str(desc, "descLongue")
                desc_short_fr = _opt_str(desc, "descCourte")
                break

        # GPS from coordonneesExactesW84
        gps = prop_block.get("coordonneesExactesW84") or {}

        contact_raw = d.get("contact")
        contact = Contact.from_api(contact_raw) if contact_raw else None

        dpe_raw = _opt_str(prop_block, "consommationClasse")
        ges_raw = _opt_str(prop_block, "emissionGesClasse")

        return cls(
            annonce_id=_int(d, "id"),
            status=d.get("status") or d.get("statut") or "",
            property_type=PropertyType(bien.get("typeBien") or ""),
            transaction_type=TransactionType(d.get("typeTransaction") or ""),
            crpcen=d.get("crpcen") or "",
            office_id=_opt_int(d, "idOffice"),
            price_eur=_opt_int(vente, "prix"),
            emoluments_eur=_opt_int(vente, "emoluments"),
            date_created=_dt(vente, "dateCreation"),
            date_updated=_dt(vente, "dateMaj"),
            reference=_opt_str(vente, "reference"),
            photos=photos,
            description_fr=desc_fr,
            description_short_fr=desc_short_fr,
            commune=_opt_str(prop_block, "communeNom"),
            postal_code=_opt_str(prop_block, "codePostal"),
            dept_code=_opt_str(prop_block, "inseeDepartement"),
            gps_lon=gps.get("coordonneeX"),
            gps_lat=gps.get("coordonneeY"),
            living_area_m2=_opt_float(prop_block, "surfaceHabitable"),
            land_area_m2=_opt_int(prop_block, "surfaceTerrain"),
            rooms=_opt_int(prop_block, "nbPieces"),
            bedrooms=_opt_int(prop_block, "nbChambres"),
            bathrooms=_opt_int(prop_block, "nbSdb"),
            dpe_class=DpeClass(dpe_raw) if dpe_raw else None,
            dpe_consumption=_opt_int(prop_block, "consommation"),
            ges_class=DpeClass(ges_raw) if ges_raw else None,
            ges_emission=_opt_int(prop_block, "emissionGes"),
            dpe_date=_date(prop_block, "dateRealisationDpe"),
            energy_cost_min=_opt_int(prop_block, "depensesEnergieMin"),
            energy_cost_max=_opt_int(prop_block, "depensesEnergieMax"),
            taxe_fonciere=_opt_int(prop_block, "taxeFonciere"),
            sea_front=_ternary(prop_block, "bordMer"),
            sea_view=_ternary(prop_block, "vueMer"),
            feet_in_water=_ternary(prop_block, "piedsDansEau"),
            pool=_ternary(prop_block, "piscine"),
            terrace=_ternary(prop_block, "terrasse"),
            garden=_ternary(prop_block, "jardin"),
            fireplace=_ternary(prop_block, "cheminee"),
            panoramic_view=_ternary(prop_block, "vuePanoramique"),
            countryside=_ternary(prop_block, "pleineCampagne"),
            contact=contact,
            raw=d,
        )


@dataclass(frozen=True)
class SearchResult:
    """Paginated response from the search endpoint."""

    listings: list[Listing]
    page: int
    total_pages: int
    per_page: int
    total: int
    server_time: datetime | None
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, d: dict[str, Any]) -> "SearchResult":
        if "annonceResumeDto" not in d:
            raise ApiSchemaError("Missing 'annonceResumeDto' in search response", raw=d)
        return cls(
            listings=[Listing.from_api(item) for item in d["annonceResumeDto"]],
            page=_int(d, "page"),
            total_pages=_int(d, "nbPages"),
            per_page=_int(d, "parPage"),
            total=d.get("nbTotalAnnonces") or 0,
            server_time=_dt(d, "dateServeur"),
            raw=d,
        )
