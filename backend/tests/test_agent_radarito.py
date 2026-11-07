"""TDD: Radarito news-curation agent (F2, S5/S8). Dedup, noise filter,
summary truncation, category validation, NewsItemPayload conformance.
"""

from backend.app.agents import Radarito
from backend.app.models import NewsItemPayload


def _news(title="Título técnico", category="THT_SOLDERING", source_url="https://example.com/noticia",
          summary="Resumen breve", tags=None):
    return dict(
        id="news-001",
        title=title,
        source_url=source_url,
        published_at="2024-01-01T00:00:00",
        summary=summary,
        tags=tags or ["tech"],
    )


def test_ingest_duplicate_title_and_url_is_rejected():
    agent = Radarito()
    feed = _news()
    assert agent.ingest_feed(feed, "THT_SOLDERING") is not None
    assert agent.ingest_feed(feed, "THT_SOLDERING") is None


def test_ingest_same_title_different_url_is_accepted():
    agent = Radarito()
    first = _news(source_url="https://example.com/a")
    second = _news(source_url="https://example.com/b")
    assert agent.ingest_feed(first, "SMD_INSPECTION") is not None
    assert agent.ingest_feed(second, "SMD_INSPECTION") is not None


def test_ingest_commercial_noise_is_filtered():
    agent = Radarito()
    for title in ["SALE: SMT equipment discount", "Buy now reflow ovens cheap!", "Sponsored ad: AOI machines"]:
        assert agent.ingest_feed(_news(title=title), "AI_SOFTWARE") is None


def test_ingest_emits_newsitempayload():
    agent = Radarito()
    payload = agent.ingest_feed(_news(), "THT_SOLDERING")
    assert isinstance(payload, NewsItemPayload)
    assert payload.category == "THT_SOLDERING"
    assert payload.title == "Título técnico"


def test_ingest_summary_truncated_to_300_chars():
    agent = Radarito()
    long_summary = "x" * 500
    payload = agent.ingest_feed(_news(summary=long_summary), "THT_SOLDERING")
    assert len(payload.summary) == 300


def test_ingest_invalid_category_does_not_store_invalid_payload():
    agent = Radarito()
    feed = _news(category="INVALID_CHANNEL")
    # Radarito validates through Pydantic; must never return an object with
    # an invalid category Literal value.
    result = agent.ingest_feed(feed, "INVALID_CHANNEL")
    assert result is None or result.category in ("THT_SOLDERING", "SMD_INSPECTION", "AI_SOFTWARE")


def test_synthesize_summary_empty_channel():
    agent = Radarito()
    result = agent.synthesize_summary("AI_SOFTWARE")
    assert "No hay artículos nuevos" in result


def test_synthesize_summary_max_three_lines():
    agent = Radarito()
    for i in range(5):
        agent.ingest_feed(_news(title=f"News {i}"), "AI_SOFTWARE")
    result = agent.synthesize_summary("AI_SOFTWARE")
    lines = [l for l in result.splitlines() if l.strip()]
    assert len(lines) <= 3
