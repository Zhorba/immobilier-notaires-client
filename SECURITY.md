# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Report privately by emailing the address listed in `pyproject.toml`
(`project.maintainers`). Include:

1. A description of the vulnerability and its potential impact.
2. Steps to reproduce or a minimal proof-of-concept.
3. Any suggestions for a fix, if you have them.

You will receive an acknowledgement within 72 hours and a fix or mitigation
plan within 14 days.

## Scope

This library is a **read-only HTTP client**. It:

- Makes outbound GET requests to `immobilier.notaires.fr`.
- Does not store credentials, tokens, or user data.
- Does not execute arbitrary code from API responses.

The most likely security concern is **contact PII leakage** (negotiator phone /
email returned by the detail endpoint). See [`docs/ethics.md`](docs/ethics.md)
for the responsible-use policy around this data.
