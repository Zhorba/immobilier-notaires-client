"""HTTP session with polite defaults and retry/backoff."""

from __future__ import annotations

import time
from typing import Any

import httpx

from .exceptions import ApiBadRequest, NotFound, NotairesError, RateLimited

_BASE = "https://www.immobilier.notaires.fr/pub-services"
_VERSION = "0.1.0"
_REPO = "https://github.com/Zhorba/immobilier-notaires-client"
_USER_AGENT = f"immobilier-notaires-client/{_VERSION} (+{_REPO})"

_DEFAULT_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
    "User-Agent": _USER_AGENT,
}

_RETRY_STATUSES = {429, 500, 502, 503, 504}
_MAX_RETRIES = 3
_BACKOFF_BASE = 2.0  # seconds


def _make_client(timeout: float = 20.0) -> httpx.Client:
    return httpx.Client(
        base_url=_BASE,
        headers=_DEFAULT_HEADERS,
        timeout=timeout,
        follow_redirects=True,
    )


def get_json(
    client: httpx.Client,
    path: str,
    *,
    params: dict[str, str] | None = None,
    referer: str | None = None,
) -> Any:
    """GET ``path``, retry on transient errors, return parsed JSON.

    Raises ``NotairesError`` subclasses for known HTTP error codes.
    """
    headers = {}
    if referer:
        headers["Referer"] = referer

    last_exc: Exception | None = None
    for attempt in range(_MAX_RETRIES):
        try:
            resp = client.get(path, params=params, headers=headers)
        except httpx.TransportError as exc:
            last_exc = exc
            time.sleep(_BACKOFF_BASE ** attempt)
            continue

        if resp.status_code == 400:
            raise ApiBadRequest(resp.text)
        if resp.status_code == 404:
            raise NotFound(f"Not found: {path}")
        if resp.status_code == 429:
            raise RateLimited("HTTP 429 — slow down or increase min_delay")
        if resp.status_code in _RETRY_STATUSES:
            last_exc = NotairesError(f"HTTP {resp.status_code}")
            time.sleep(_BACKOFF_BASE ** attempt)
            continue

        resp.raise_for_status()
        return resp.json()

    raise NotairesError(f"Request failed after {_MAX_RETRIES} retries") from last_exc
