"""TDD: News router integration (F3, T3, S2/S8).

Offline, deterministic, no network. FastAPI TestClient against the real
news_router wired to Radarito. Covers S2: /news — devuelve NewsItemPayload
válidos, sin PII, categoría filtrada. Logs ASCII-only.

RED first: run this file before modifying backend/app/routers/news.py.

Note: `news_endpoint(query: NewsQuery)` keeps its frozen signature; because
NewsQuery is a Pydantic model on a GET route, FastAPI binds it from the
request body, so tests issue GET with a JSON body.
"""

import re

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.models import NewsItemPayload
from backend.app.routers.news import news_router


def _build_app() -> FastAPI:
    app = FastAPI()
    app.include_router(news_router)
    return app


@pytest.fixture
def client() -> TestClient:
    return TestClient(_build_app())


def _get_news(client: TestClient, category: str):
    return client.request("GET", "/news/", json={"category": category})


# --- Valid payload returned -----------------------------------------------


def test_news_endpoint_returns_list_of_newsitempayload(client: TestClient):
    response = _get_news(client, "THT_SOLDERING")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    for item in items:
        payload = NewsItemPayload(**item)
        assert isinstance(payload, NewsItemPayload)


def test_news_category_literal_valid(client: TestClient):
    response = _get_news(client, "AI_SOFTWARE")
    assert response.status_code == 200
    items = response.json()
    for item in items:
        assert item["category"] in ("THT_SOLDERING", "SMD_INSPECTION", "AI_SOFTWARE")


def test_news_title_non_empty(client: TestClient):
    response = _get_news(client, "SMD_INSPECTION")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    for item in items:
        assert isinstance(item["title"], str) and len(item["title"]) > 0


def test_news_source_url_valid_httpurl(client: TestClient):
    response = _get_news(client, "THT_SOLDERING")
    assert response.status_code == 200
    items = response.json()
    assert len(items) >= 1
    for item in items:
        assert item["source_url"].startswith(("http://", "https://"))


def test_news_summary_at_most_300_chars(client: TestClient):
    response = _get_news(client, "AI_SOFTWARE")
    assert response.status_code == 200
    items = response.json()
    for item in items:
        assert len(item["summary"]) <= 300


def test_news_tags_is_list(client: TestClient):
    response = _get_news(client, "THT_SOLDERING")
    assert response.status_code == 200
    items = response.json()
    for item in items:
        assert isinstance(item["tags"], list)


# --- Category filtering -----------------------------------------------------


def test_news_category_filtering_returns_only_requested_category(client: TestClient):
    response = _get_news(client, "THT_SOLDERING")
    assert response.status_code == 200
    items = response.json()
    for item in items:
        assert item["category"] == "THT_SOLDERING"


def test_news_category_filtering_ai_software(client: TestClient):
    response = _get_news(client, "AI_SOFTWARE")
    assert response.status_code == 200
    items = response.json()
    for item in items:
        assert item["category"] == "AI_SOFTWARE"


def test_news_category_filtering_smd_inspection(client: TestClient):
    response = _get_news(client, "SMD_INSPECTION")
    assert response.status_code == 200
    items = response.json()
    for item in items:
        assert item["category"] == "SMD_INSPECTION"


# --- No PII in response -----------------------------------------------------


def test_news_response_contains_no_pii(client: TestClient):
    email_re = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    phone_re = re.compile(r"\+?\d{1,3}[\s\-]?\(?\d{2,4}\)?[\s\-]?\d{3,4}[\s\-]?\d{4}")
    body = _get_news(client, "THT_SOLDERING").text
    assert not email_re.search(body), "email found in news response"
    assert not phone_re.search(body), "phone found in news response"


# --- Empty channel handled gracefully --------------------------------------


def test_news_empty_channel_returns_empty_structure():
    """A fresh Radarito channel with no items yields an empty structure."""
    from backend.app.agents import Radarito

    agent = Radarito()
    items = agent.channels.get("AI_SOFTWARE", [])
    assert items == []
    summary = agent.synthesize_summary("AI_SOFTWARE")
    assert "No hay artículos nuevos" in summary


# --- Invalid category -> 422 -------------------------------------------------


def test_news_invalid_category_returns_422(client: TestClient):
    response = _get_news(client, "NO_EXISTE")
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any(err.get("loc") == ["body", "category"] for err in detail)
