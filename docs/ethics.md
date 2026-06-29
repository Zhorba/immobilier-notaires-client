# Responsible use

This library talks to an **undocumented, public, unauthenticated** endpoint that
the immobilier.notaires.fr website uses internally. With that comes responsibility.

## Not affiliated

This project is **not affiliated with, authorized by, or endorsed by** the Notaires
de France, the Conseil Supérieur du Notariat, or immobilier.notaires.fr. "Notaires
de France" and related marks belong to their owners.

## Respect the source

- **Read the site's Terms of Service** before using this in anything beyond personal
  experimentation, and comply with them. Using an undocumented endpoint may be
  against those terms; that responsibility is the user's.
- **The endpoint can change or vanish without notice.** Do not build anything that
  assumes long-term stability without monitoring.

## Be polite (defaults this library enforces)

- **Rate limit.** Default to a low request rate (≤ ~1 request/second) and a single
  connection. Don't parallelize aggressively.
- **Honest `User-Agent`.** Identify the client and link its repository, so the
  operator can see what's hitting them and contact the maintainers.
- **Fetch only what you need.** Push filters (`departements`, `typeBiens`,
  `surfaceMin`, `prixMax`, …) into the query server-side instead of downloading
  everything and filtering locally.
- **Cache / schedule sensibly.** For monitoring use cases, a once-daily batch is
  almost always enough. Don't poll in tight loops.

## Personal data

Listing contacts include notary-office negotiator names, phone numbers and emails
(publicly listed on the site). Treat them as personal data:

- Don't redistribute scraped contact details in bulk.
- Comply with GDPR and local law for any storage or processing.
- The redacted samples in [`samples/`](./samples) have contact PII replaced with
  placeholders on purpose — **do not** commit un-redacted personal data to this repo.

## If asked to stop

If the site operator requests it, stop. Open an issue so maintainers can respond
(e.g. add a notice, adjust defaults, or archive the project).
