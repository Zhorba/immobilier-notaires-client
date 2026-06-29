"""Pagination helpers for the search endpoint."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass
class PageRange:
    start: int = 1
    end: int | None = None  # inclusive; None = until API says stop


def iter_page_numbers(first_page: int, total_pages: int) -> Iterator[int]:
    """Yield page numbers from ``first_page`` to ``total_pages`` inclusive."""
    for p in range(first_page, total_pages + 1):
        yield p
