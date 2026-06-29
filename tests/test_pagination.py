"""Tests for pagination logic against the search fixture."""

from notaires_immo.models import SearchResult
from notaires_immo.pagination import iter_page_numbers


def test_iter_page_numbers_single():
    assert list(iter_page_numbers(1, 1)) == [1]


def test_iter_page_numbers_multi():
    assert list(iter_page_numbers(1, 5)) == [1, 2, 3, 4, 5]


def test_iter_page_numbers_from_two():
    # iter_search fetches page 1, then iterates 2..N
    assert list(iter_page_numbers(2, 5)) == [2, 3, 4, 5]


def test_iter_page_numbers_already_last():
    # no extra pages when already on the last
    assert list(iter_page_numbers(5, 5)) == [5]


def test_search_result_total_pages(search_payload):
    result = SearchResult.from_api(search_payload)
    assert result.total_pages == 1263
    assert result.page == 1
    # with parPage=1 there are as many pages as there are total listings
    assert result.total == result.total_pages


def test_search_result_per_page(search_payload):
    result = SearchResult.from_api(search_payload)
    assert result.per_page == 1
