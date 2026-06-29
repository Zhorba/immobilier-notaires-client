# Field reference

Exhaustive dictionary of fields returned by the API, observed on **2026-06-29**.
Fields are listed with their observed type and meaning. `INCONNU` = "unknown / not
provided" (see [api-reference §4.3](./api-reference.md#43-ternary-flags)). Lists
here may lag the live API — corrections welcome (see [CONTRIBUTING.md](../CONTRIBUTING.md)).

---

## Search — `annonceResumeDto[]`

One object per listing summary.

### Identity & status
| Field | Type | Notes |
|-------|------|-------|
| `id` | int | Summary record id (internal). |
| `annonceId` | int | **Listing id — use this for detail/contacts endpoints.** |
| `bienId` | int | Property (bien) id. |
| `reference` | string | Office reference, e.g. `"56076-1382"`. |
| `crpcen` | string | Notary office CRPCEN code. |
| `partenaire` | int | Partner/source id. |
| `statut` | string | `LIGNE` = online/active. |
| `dateCreation` | ISO datetime | Created. |
| `dateMaj` | ISO datetime | Last updated. |
| `publiable` | enum | `OUI`/`NON`. |

### Price
| Field | Type | Notes |
|-------|------|-------|
| `prixAffiche` | int (€) | Displayed price. |
| `prixTotal` | int (€) | Price incl. notary fees. |
| `emoluments` | int (€) | Notary fees. |
| `pourcentageEmoluments` | float | Fee % (e.g. `4.6`). |
| `redevableEmoluments` | enum | Who pays fees: `ACQUEREUR`/`VENDEUR`. |

### Property basics
| Field | Type | Notes |
|-------|------|-------|
| `typeBien` | enum | `MAI`/`APP`/`TER`/… see api-reference §4.1. |
| `typeTransaction` | enum | `VENTE`/`VNI`/`VAE`/`LOCATION`. |
| `surface` | float (m²) | Living area. |
| `surfaceTerrain` | int (m²) | Land area. |
| `nbPieces` | int | Rooms. |
| `nbChambres` | int | Bedrooms. |
| `typeTerrain` | enum | e.g. `INCONNU`. |
| `ancienNeuf` | enum | `ANCIEN`/`NEUF`. |
| `descriptionFr` | string | Truncated description (full text in detail endpoint). |
| `dateRealisationDpe` | ISO date | DPE assessment date (class is in detail endpoint). |

### Location
| Field | Type | Notes |
|-------|------|-------|
| `localiteNom` | string | Locality (upper-case), e.g. `PLUMELIN`. |
| `communeNom` | string | Commune (title-case), e.g. `Plumelin`. |
| `codePostal` | string | Postal code. |
| `inseeCommune` | string | INSEE commune code. |
| `inseeDepartement` | string | INSEE department code. |
| `departementNom` | string | Department name. |
| `inseeRegion` / `regionNom` | string | Region. |
| `hexaviaLocalite` | string | Internal locality id. |

### Media & contact (summary-level)
| Field | Type | Notes |
|-------|------|-------|
| `urlPhotoPrincipale` | url | Main photo (VGA). |
| `nbPhoto` | int | Photo count. |
| `urlDetailAnnonceFr` | url | Human-readable FR listing page. |
| `urlDetailAnnonceEn` | url | EN listing page. |
| `telephone` | string | Negotiator phone. |

### Auction / sale-state flags
`viager`, `isVniClose`, `modeVente`, `typeAdjudication`, `natureMiseAPrix`,
`origineJudiciaire`, `bienVendu`, `bienRetire`, `bienNonVenduCarence`,
`venteReportee`, `bienNonVenduReserve`, `variation` — mostly `INCONNU` for standard
`VENTE`; relevant for `VAE`/`VNI`.

---

## `urlSeos[]`
SEO helper links describing the result set: `urlSeo`, `nomCommune`, `codePostal`,
`typeTransaction`, `typeBien`, `fourthParam`/`fourthPath` (e.g. `pieces`/`5`).
Not needed for data extraction.

---

## Detail — top level
| Field | Type | Notes |
|-------|------|-------|
| `id` | int | = `annonceId`. |
| `status` | enum | `LIGNE`. |
| `typeTransaction` | enum | |
| `vente` | object | Transaction block (below). |
| `bien` | object | Property block (polymorphic, below). |
| `contact` | object | Negotiator (below). |
| `idOffice` | int | Notary office id. |
| `crpcen` | string | Office CRPCEN. |

### Detail — `vente`
`dateCreation`, `dateMaj`, `dateActivation`, `dateStatut`, `statut`, `reference`,
`referencePartenaire`, `exclusivite`, `origineNegociation`, `partenaire`,
`typeTransaction`, `crpcen`, `publiable`, `prix` (€), `emoluments` (€),
`redevableEmoluments`, plus nested:
- `multimedias[]` — photos, each with `checksum`, `photoPrincipale`, `type`,
  `extension`, `directory`, `ratio`, and per-resolution url objects
  (`qqvga`/`qvga`/`vga`/`xga`) + `urlHighestResolution`.
- `descriptions[]` — `langue`, `descCourte`, `descLongue` (**full description text**).
- `visite` — `typeVisite`, `visiteContact`, `visiteNomContact`.
- `viager` — `viager`, `viagerPeriodiciteRente`, etc.

### Detail — `bien`
`id`, `typeBien`, and **one nested object named after the type** (`maison`,
`appartement`, `terrain`, …). The nested object carries the rich data:

**Location & geo:** `localiteNom`, `communeNom`, `inseeCommune`, `codePostal`,
`inseeDepartement`, `departementNom`, `regionNom`,
`coordonneesExactesW84.{coordonneeX, coordonneeY}` (**exact lon/lat, WGS84**).

**Surfaces & layout:** `surfaceHabitable`, `surfaceTerrain`, `nbPieces`,
`nbChambres`, `nbSdb`, `exposition` (e.g. `S`), `epoqueConstruction`.

**Energy / DPE:** `consommationClasse` (A–G), `consommation` (kWh),
`emissionGesClasse` (A–G), `emissionGes`, `dateRealisationDpe`,
`depensesEnergieMin`/`Max`/`Annee`, `basseConsommation`.

**Costs:** `taxeFonciere` (€).

**Amenity flags (ternary `OUI`/`NON`/`INCONNU` unless noted):**
`cuisine`, `typeCuisine` (e.g. `AMERICAINE`), `terrasse`, `balcon`, `cave`,
`piscine`, `jardin`, `cheminee`, `parquet`, `climatisation`, `dependances`,
`garage`/`stationnement`, `ascenseur`, `accesHandicapes`, `meuble`, `sansVisAVis`,
and many prestige flags (`monumentHistorique`, `domaineChasse`, `parcPaysager`,
`ecurie`, `spa`, `courtTennis`, `architecte`, `salleReception`, …).

**Location-quality flags (useful for scoring):**
`bordMer`, `piedsDansEau`, `vueMer` + `checkVueMer`, `belleVue`, `vuePanoramique`,
`pleineCampagne`, `procheMontagne`, `procheGolf`, `pistes` + `checkPistes`.

**Proximity flags:** `checkBus`, `checkMetro`, `checkTram`, `checkGare`,
`checkAeroport`, `checkEcole`/`ecole`, `checkCommerce`/`commerce` (e.g. `DIST300`).

> The sea-view (`bordMer`, `vueMer`, `piedsDansEau`) and `piscine` flags are the
> ones most useful for buy-side scoring downstream.

### Detail — `contact`
`id`, `nom`, `adresse4`, `codePostal`, `ville`,
`coordonneesW84.{coordonneeX, coordonneeY}`, `telephone`, `mail`.

---

## Contacts — `GET .../annonces/{annonceId}/contacts`
Subset of `detail.contact`, **without `mail`**: `id`, `nom`, `adresse4`,
`codePostal`, `ville`, `coordonneesW84`, `telephone`. Use the detail endpoint if you
need the email.
