"""Shared fixtures for the test suite."""

import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture()
def search_payload() -> dict:
    return json.loads((FIXTURES / "search-response.json").read_text())


@pytest.fixture()
def detail_payload() -> dict:
    return json.loads((FIXTURES / "detail-response.json").read_text())


@pytest.fixture()
def contacts_payload() -> dict:
    return json.loads((FIXTURES / "contacts-response.json").read_text())
