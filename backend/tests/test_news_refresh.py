"""TDD coverage for the daily live-news refresh service."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from backend.app.services.news_refresh import (
    FeedSpec,
    NewsCache,
    parse_rss_items,
    refresh_news_cache,
    seconds_until_next_refresh,
)


RSS_SAMPLE = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>New inspection platform - Industry Source</title>
      <link>https://example.com/inspection-platform</link>
      <pubDate>Tue, 10 Nov 2026 07:30:00 GMT</pubDate>
      <source>Industry Source</source>
      <description>New inspection platform for electronics manufacturing.</description>
    </item>
  </channel>
</rss>
"""


def test_parse_rss_items_builds_valid_localized_news():
    spec = FeedSpec(
        category="SMD_INSPECTION",
        sub_category="partner_equipment",
        query="PARMI AOI",
        tags=("parmi", "aoi"),
    )

    items = parse_rss_items(RSS_SAMPLE, spec=spec, lang="en")

    assert len(items) == 1
    item = items[0]
    assert item["category"] == "SMD_INSPECTION"
    assert item["sub_category"] == "partner_equipment"
    assert item["source_url"] == "https://example.com/inspection-platform"
    assert item["published_at"] == "2026-11-10T07:30:00Z"
    assert item["title"] == item["title_en"]
    assert item["summary"] == item["summary_en"]


def test_news_cache_replaces_all_tabs_atomically(tmp_path: Path):
    path = tmp_path / "news_cache.json"
    cache = NewsCache(path)
    payload = {
        "updated_at": "2026-11-11T08:00:00+01:00",
        "languages": {
            "es": {
                "THT_SOLDERING": [{"id": "tht"}],
                "SMD_INSPECTION": [{"id": "smd"}],
                "AI_SOFTWARE": [{"id": "ai"}],
            },
            "en": {
                "THT_SOLDERING": [{"id": "tht-en"}],
                "SMD_INSPECTION": [{"id": "smd-en"}],
                "AI_SOFTWARE": [{"id": "ai-en"}],
            },
        },
    }

    cache.write(payload)

    assert json.loads(path.read_text(encoding="utf-8")) == payload
    assert cache.items("es", "THT_SOLDERING")[0]["id"] == "tht"
    assert cache.items("es", "SMD_INSPECTION")[0]["id"] == "smd"
    assert cache.items("es", "AI_SOFTWARE")[0]["id"] == "ai"


def test_next_refresh_is_0800_europe_madrid():
    madrid = ZoneInfo("Europe/Madrid")
    before = datetime(2026, 11, 11, 7, 30, tzinfo=madrid)
    after = datetime(2026, 11, 11, 8, 30, tzinfo=madrid)

    assert seconds_until_next_refresh(before) == 30 * 60
    assert seconds_until_next_refresh(after) == 23 * 60 * 60 + 30 * 60


def test_next_refresh_preserves_0800_across_dst_boundaries():
    madrid = ZoneInfo("Europe/Madrid")
    spring_change = datetime(2026, 3, 28, 8, 0, tzinfo=madrid)
    autumn_change = datetime(2026, 10, 24, 8, 0, tzinfo=madrid)

    assert seconds_until_next_refresh(spring_change) == 23 * 60 * 60
    assert seconds_until_next_refresh(autumn_change) == 25 * 60 * 60


def test_partial_feed_failure_preserves_previous_cache(monkeypatch, tmp_path: Path):
    from backend.app.services import news_refresh

    cache = NewsCache(tmp_path / "news_cache.json")
    cache.write({"sentinel": "previous-valid-cache"})
    original = cache.path.read_bytes()

    def fake_fetch(spec, lang, timeout=15.0):
        if (
            spec.category == "SMD_INSPECTION"
            and spec.sub_category == "partner_equipment"
        ):
            return []
        return [
            {
                "id": f"{lang}-{spec.category}-{spec.sub_category}",
                "category": spec.category,
                "sub_category": spec.sub_category,
                "published_at": "2026-11-11T08:00:00+01:00",
            }
        ]

    monkeypatch.setattr(news_refresh, "fetch_feed", fake_fetch)

    assert refresh_news_cache(cache) is False
    assert cache.path.read_bytes() == original


def test_frontend_requests_enough_items_before_tab_filtering():
    root = Path(__file__).resolve().parent.parent.parent
    source = (root / "web" / "src" / "js" / "news-feed.js").read_text(
        encoding="utf-8"
    )

    assert source.count("&limit=50") == 6
