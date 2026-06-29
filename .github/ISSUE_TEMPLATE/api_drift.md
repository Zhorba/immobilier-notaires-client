---
name: API drift
about: The notaires.fr API changed and the library needs updating
labels: api-drift
---

## What changed

<!-- Describe the API change you observed: new field, renamed key, new enum value, etc. -->

## How you detected it

- [ ] `test_contract.py` assertion failed after refreshing fixtures
- [ ] A `from_api()` call raised `ApiSchemaError`
- [ ] An enum returned `UNKNOWN(…)` for a value that should be mapped
- [ ] Other: <!-- describe -->

## Affected endpoint

- [ ] Search (`/v1/annonces`)
- [ ] Detail (`/v1/annonces/{id}`)
- [ ] Contacts (`/v1/annonces/{id}/contacts`)

## Raw evidence

```json
// Paste the relevant fragment of the API response here (redact PII first)
```

## Suggested fix

<!-- Optional: what model/enum change would resolve this. -->
