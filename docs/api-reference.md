# immobilier.notaires.fr — API reference

> **Unofficial.** This documents the public, unauthenticated JSON API that the
> [immobilier.notaires.fr](https://www.immobilier.notaires.fr) website's own frontend
> calls. It is **not** an officially published or supported API. It can change or
> disappear without notice. This project is not affiliated with or endorsed by the
> Notaires de France. See [ethics.md](./ethics.md) for responsible-use guidance.
>
> Last verified against the live API: **2026-06-29**.

All endpoints are under the host:

```
https://www.immobilier.notaires.fr/pub-services/
```

No API key, cookie, or auth token is required. The endpoints respond to plain
`GET` requests. Send browser-like headers (see [§5](#5-request-headers)) to stay
on the happy path.

---

## 1. Endpoints at a glance

| # | Method | Path | Purpose |
|---|--------|------|---------|
| 1 | `GET` | `inotr-www-annonces/v1/annonces` | **Search** listings (paginated summaries) |
| 2 | `GET` | `inotr-www-annonces/v1/annonces/{annonceId}` | **Detail** of one listing (full record) |
| 3 | `GET` | `inotr-www-annonces-contacts/v1/annonces/{annonceId}/contacts` | Negotiator **contact** for a listing |

Related endpoints seen in the site bundle but not documented here yet (PRs welcome):
`geo-consultation/v1/communes|departements|localites-light` (geo resolution),
`inotr-seo/v1/*` (SEO blocks). The `inotr-ref-annonces/v1/*` reference endpoints
return `403` to anonymous clients.

---

## 2. Search — `GET /inotr-www-annonces/v1/annonces`

Returns a page of listing **summaries** (`annonceResumeDto`) plus a pagination
envelope. This is the primary endpoint.

### 2.1 Query parameters

| Param | Type | Required | Example | Description |
|-------|------|----------|---------|-------------|
| `parPage` | int | **yes** | `100` | Page size. Omitting it returns `400`. |
| `page` | int | recommended | `1` | 1-based page index. |
| `offset` | int | no | `0` | Start offset; normally `0` with paging via `page`. |
| `departements` | string | no | `56` or `44,56` | INSEE department code(s), comma-joined. |
| `typeBiens` | string | no | `MAI` | Property type(s), comma-joined. See [enums](#41-typebiens-property-type). |
| `typeTransactions` | string | no | `VENTE,VNI,VAE` | Transaction kind(s), comma-joined. See [enums](#42-typetransactions). |
| `surfaceMin` | int | no | `80` | Min living area (m²). |
| `surfaceMax` | int | no | `200` | Max living area (m²). |
| `prixMin` | int | no | `50000` | Min price (€). |
| `prixMax` | int | no | `300000` | Max price (€). |
| `nbPiecesMin` | int | no | `3` | Min number of rooms. |
| `nbPiecesMax` | int | no | `6` | Max number of rooms. |
| `perimetre` | int | no | `0` | Search radius (km) around the locality; `0` = exact. |

> Filters are applied **server-side**, so push as much of your query as possible
> into the URL rather than filtering after fetch.

### 2.2 Example

```
GET https://www.immobilier.notaires.fr/pub-services/inotr-www-annonces/v1/annonces
    ?page=1&parPage=100&departements=56&typeBiens=MAI
    &typeTransactions=VENTE&surfaceMin=80&prixMax=300000
```

### 2.3 Response envelope

```jsonc
{
  "annonceResumeDto": [ /* array of listing summaries, see fields-reference.md */ ],
  "urlSeos":          [ /* SEO helper URLs for the result set */ ],
  "page": 1,            // current page (echoes request)
  "nbPages": 13,        // total pages = ceil(nbTotalAnnonces / parPage)
  "parPage": 100,       // echoes request
  "nbTotalAnnonces": 1263, // total matching listings
  "dateServeur": "2026-06-29T08:55:10Z"
}
```

### 2.4 Pagination

`nbTotalAnnonces` is the total match count; `nbPages` is derived from it and your
`parPage`. Loop until the last page:

```
page = 1
loop:
  resp = GET .../annonces?page={page}&parPage=100&...
  yield resp.annonceResumeDto
  if resp.page >= resp.nbPages: break
  page += 1
```

A summary's `annonceId` field is the id used by the **detail** and **contacts**
endpoints (note: distinct from the summary's own `id`).

---

## 3. Detail — `GET /inotr-www-annonces/v1/annonces/{annonceId}`

Returns the **full** record for one listing: long description, all photos at
multiple resolutions, exact GPS, DPE/energy, taxe foncière, every amenity flag
(sea view, pool, fireplace…), and the negotiator contact (with email).

Path id = the `annonceId` from a search summary (e.g. `2022988`).

Top-level shape:

```jsonc
{
  "id": 2022988,
  "status": "LIGNE",
  "typeTransaction": "VENTE",
  "vente":  { /* transaction block: dates, prix, emoluments, photos, descriptions, visite, viager */ },
  "bien":   { "typeBien": "MAI", "maison": { /* polymorphic property block */ } },
  "contact":{ /* negotiator: nom, adresse, mail, telephone, GPS */ },
  "idOffice": 1843,
  "crpcen": "56076"
}
```

> **Polymorphic `bien`:** the nested key matches the type — `bien.maison` for `MAI`,
> `bien.appartement` for `APP`, `bien.terrain` for `TER`, etc. The amenity/DPE fields
> documented in [fields-reference.md](./fields-reference.md#detail--bien) live inside
> that nested object.

See [`samples/detail-response.json`](./samples/detail-response.json) for a full
(redacted) example.

---

## 4. Enums

### 4.1 `typeBiens` (property type)

Empirically confirmed valid codes (counts = dept 56, VENTE, on 2026-06-29):

| Code | Meaning | Sample count |
|------|---------|-------------|
| `MAI` | Maison (house) | 1263 |
| `APP` | Appartement | 254 |
| `TER` | Terrain (land) | 363 |
| `IMM` | Immeuble | 47 |
| `DIV` | Divers (other) | 15 |
| `GAR` | Garage / parking | 7 |

Unrecognized codes return an error envelope rather than results. This list may be
incomplete — see [§6](#6-discovering-more) to verify/extend it.

### 4.2 `typeTransactions`

| Code | Meaning |
|------|---------|
| `VENTE` | Standard sale |
| `VNI` | Vente notariale interactive (online interactive sale) |
| `VAE` | Vente par adjudication / aux enchères (auction) |
| `LOCATION` | Rental |

Combine with commas, e.g. `VENTE,VNI,VAE` for "all sale types." Viager is **not** a
transaction type — it is a flag (`viager`) on the listing.

### 4.3 Ternary flags

Most boolean-ish attributes use a three-state string enum, **not** `true/false`:

```
"OUI"  = yes     "NON" = no     "INCONNU" = unknown / not provided
```

Treat `INCONNU` as "unknown", never as `false`. Other closed vocabularies seen:
`ancienNeuf` ∈ {`ANCIEN`, `NEUF`}, DPE classes ∈ {`A`…`G`}, `redevableEmoluments`
∈ {`ACQUEREUR`, `VENDEUR`, …}.

---

## 5. Request headers

The endpoints work with minimal headers, but to look like the site's own frontend
and avoid being throttled or blocked, send:

```http
Accept: application/json, text/plain, */*
Accept-Language: fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3
Referer: https://www.immobilier.notaires.fr/fr/annonces-immobilieres-liste?...
User-Agent: <honest UA identifying this client + its repo URL>
```

Setting `Referer` to the equivalent human listing page for the same query is cheap
insurance.

---

## 6. Discovering more

The reference (`inotr-ref-annonces`) endpoints are `403` for anonymous clients, so
enums here were derived empirically. To verify or extend any of this:

1. Open [the listing search](https://www.immobilier.notaires.fr/fr/annonces-immobilieres-liste)
   in a browser, open DevTools → Network → filter `Fetch/XHR`.
2. Apply filters; watch the `pub-services/...annonces` request to read the exact
   params the UI sends.
3. Open a listing to capture the detail/contacts requests.

If you confirm a new param, type code, or field, please update
[fields-reference.md](./fields-reference.md) and the
[`samples/`](./samples) and open a PR — see [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## 7. Cross-references

- [fields-reference.md](./fields-reference.md) — exhaustive field dictionary.
- [ethics.md](./ethics.md) — responsible use, rate limiting, ToS.
- [`samples/`](./samples) — captured (redacted) real responses.
</content>
