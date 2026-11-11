"""Daily RSS refresh service for Radarito news.

The service uses public Google News RSS searches, requires no API key, writes
an atomic runtime cache, and keeps the previous cache when a refresh is
incomplete. The static curated items in the news router remain the final
offline fallback.
"""

from __future__ import annotations

import asyncio
import hashlib
import html
import json
import logging
import os
import re
import tempfile
import threading
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from backend.app.models import NewsItemPayload

logger = logging.getLogger(__name__)

ROOT = Path(__file__).resolve().parent.parent.parent.parent
DEFAULT_CACHE_PATH = Path(
    os.getenv("NEWS_CACHE_PATH", str(ROOT / "logs" / "news_cache.json"))
)
MADRID_TZ = ZoneInfo("Europe/Madrid")
GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"
USER_AGENT = "ShowcasePlatform-Radarito/1.0"


@dataclass(frozen=True)
class FeedSpec:
    """A bounded RSS search mapped to a frontend news slot."""

    category: str
    sub_category: str
    query: str
    tags: tuple[str, ...]


FEED_SPECS = (
    FeedSpec(
        category="SMD_INSPECTION",
        sub_category="pcb_manufacturing",
        query=(
            '("printed circuit board" OR PCB OR EMS) '
            "(manufacturing OR assembly) electronics when:7d"
        ),
        tags=("pcb", "ems", "electronics-manufacturing"),
    ),
    FeedSpec(
        category="SMD_INSPECTION",
        sub_category="partner_equipment",
        query='"Mek AOI" inspection',
        tags=("mek", "aoi", "inspection"),
    ),
    FeedSpec(
        category="THT_SOLDERING",
        sub_category="partner_equipment",
        query='"Kurtz Ersa" soldering OR "Mek" THT inspection',
        tags=("ersa", "marantz", "tht", "soldering"),
    ),
    FeedSpec(
        category="AI_SOFTWARE",
        sub_category="skills_frameworks_mcps",
        query=(
            '("Model Context Protocol" OR MCP OR "AI agents") '
            "(framework OR release OR developers) when:7d"
        ),
        tags=("mcp", "ai-agents", "frameworks"),
    ),
    FeedSpec(
        category="AI_SOFTWARE",
        sub_category="ai_models",
        query=(
            '("AI model" OR LLM OR Gemini OR Claude) '
            "(release OR developers) when:7d"
        ),
        tags=("ai-models", "llm", "inference"),
    ),
)

_TAG_RE = re.compile(r"<[^>]+>")
_SPACE_RE = re.compile(r"\s+")


def _clean_text(value: str | None) -> str:
    text = html.unescape(value or "")
    text = _TAG_RE.sub(" ", text)
    return _SPACE_RE.sub(" ", text).strip()


def _child_text(node: ET.Element, name: str) -> str:
    child = node.find(name)
    return child.text.strip() if child is not None and child.text else ""


def _published_at(value: str) -> str:
    try:
        parsed = parsedate_to_datetime(value)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=MADRID_TZ)
        return parsed.isoformat()
    except (TypeError, ValueError):
        return datetime.now(MADRID_TZ).isoformat()


def parse_rss_items(
    payload: bytes,
    *,
    spec: FeedSpec,
    lang: str,
    limit: int = 6,
) -> list[dict[str, Any]]:
    """Parse RSS items into validated NewsItemPayload dictionaries."""

    root = ET.fromstring(payload)
    result: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for node in root.findall("./channel/item"):
        title = _clean_text(_child_text(node, "title"))
        source_url = _child_text(node, "link")
        if not title or not source_url or source_url in seen_urls:
            continue

        source = _clean_text(_child_text(node, "source"))
        description = _clean_text(_child_text(node, "description"))
        if not description:
            description = title
        prefix = f"{source}: " if source else ""
        summary = (prefix + description)[:300].rstrip()
        published_at = _published_at(_child_text(node, "pubDate"))
        digest = hashlib.sha256(
            f"{lang}|{spec.category}|{spec.sub_category}|{source_url}".encode("utf-8")
        ).hexdigest()[:16]

        data: dict[str, Any] = {
            "id": f"rss-{digest}",
            "category": spec.category,
            "sub_category": spec.sub_category,
            "title": title,
            "source_url": source_url,
            "published_at": published_at,
            "summary": summary,
            "tags": list(spec.tags),
            "title_es": title if lang == "es" else None,
            "title_en": title if lang == "en" else None,
            "summary_es": summary if lang == "es" else None,
            "summary_en": summary if lang == "en" else None,
        }
        result.append(NewsItemPayload(**data).model_dump(mode="json"))
        seen_urls.add(source_url)
        if len(result) >= limit:
            break

    return result


def _rss_url(spec: FeedSpec, lang: str) -> str:
    locale = (
        {"hl": "es", "gl": "ES", "ceid": "ES:es"}
        if lang == "es"
        else {"hl": "en", "gl": "US", "ceid": "US:en"}
    )
    return GOOGLE_NEWS_RSS + "?" + urllib.parse.urlencode(
        {"q": spec.query, **locale}
    )


def fetch_feed(spec: FeedSpec, lang: str, timeout: float = 15.0) -> list[dict]:
    """Download and parse one public RSS query."""

    request = urllib.request.Request(
        _rss_url(spec, lang),
        headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return parse_rss_items(response.read(), spec=spec, lang=lang)


class NewsCache:
    """Atomic JSON cache shared by the scheduler and API router."""

    def __init__(self, path: Path = DEFAULT_CACHE_PATH):
        self.path = Path(path)
        self._lock = threading.RLock()

    def read(self) -> dict[str, Any]:
        with self._lock:
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (FileNotFoundError, json.JSONDecodeError, OSError):
                return {}

    def write(self, payload: dict[str, Any]) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, temp_name = tempfile.mkstemp(
                prefix="news-cache-",
                suffix=".json",
                dir=str(self.path.parent),
            )
            try:
                with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                    json.dump(payload, handle, ensure_ascii=False, indent=2)
                    handle.write("\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temp_name, self.path)
            finally:
                if os.path.exists(temp_name):
                    os.unlink(temp_name)

    def items(self, lang: str, category: str) -> list[dict[str, Any]]:
        payload = self.read()
        languages = payload.get("languages", {})
        return list(languages.get(lang, {}).get(category, []))


_refresh_lock = threading.Lock()
DEFAULT_NEWS_CACHE = NewsCache()


def _has_all_slots(items: dict[str, list[dict]]) -> bool:
    return all(
        any(item.get("sub_category") == spec.sub_category for item in items.get(spec.category, []))
        for spec in FEED_SPECS
    )


def refresh_news_cache(cache: NewsCache = DEFAULT_NEWS_CACHE) -> bool:
    """Refresh both languages; preserve the previous cache on partial failure."""

    if not _refresh_lock.acquire(blocking=False):
        logger.info("News refresh already running")
        return False

    try:
        languages: dict[str, dict[str, list[dict]]] = {}
        for lang in ("es", "en"):
            grouped = {
                "THT_SOLDERING": [],
                "SMD_INSPECTION": [],
                "AI_SOFTWARE": [],
            }
            language_complete = True
            for spec in FEED_SPECS:
                items: list[dict] = []
                try:
                    items = fetch_feed(spec, lang)
                except Exception as exc:
                    logger.warning(
                        "RSS refresh failed for %s/%s: %s",
                        lang,
                        spec.query,
                        exc,
                    )

                if not items and lang == "es":
                    # Niche industrial publishers primarily syndicate in
                    # English. Keep the Spanish slot current instead of
                    # rejecting the entire daily refresh.
                    try:
                        items = fetch_feed(spec, "en")
                        for item in items:
                            item["title_es"] = item["title"]
                            item["summary_es"] = item["summary"]
                    except Exception as exc:
                        logger.warning(
                            "English RSS fallback failed for %s: %s",
                            spec.query,
                            exc,
                        )

                if not items:
                    language_complete = False
                    logger.warning(
                        "RSS refresh returned no items for %s/%s",
                        lang,
                        spec.query,
                    )
                    continue
                grouped[spec.category].extend(items)

            for category in grouped:
                grouped[category].sort(
                    key=lambda item: item.get("published_at", ""),
                    reverse=True,
                )
            if not language_complete or not _has_all_slots(grouped):
                logger.warning("RSS refresh incomplete for language %s; cache preserved", lang)
                return False
            languages[lang] = grouped

        cache.write(
            {
                "updated_at": datetime.now(MADRID_TZ).isoformat(),
                "timezone": "Europe/Madrid",
                "languages": languages,
            }
        )
        logger.info("Daily RSS news cache refreshed")
        return True
    finally:
        _refresh_lock.release()


def seconds_until_next_refresh(
    now: datetime | None = None,
    *,
    hour: int = 8,
) -> float:
    """Return seconds until the next 08:00 Europe/Madrid refresh."""

    current = now.astimezone(MADRID_TZ) if now else datetime.now(MADRID_TZ)
    target = current.replace(hour=hour, minute=0, second=0, microsecond=0)
    if target <= current:
        target += timedelta(days=1)
    return (
        target.astimezone(timezone.utc) - current.astimezone(timezone.utc)
    ).total_seconds()


class DailyNewsScheduler:
    """One in-process daily scheduler for the deployed FastAPI worker."""

    def __init__(self, cache: NewsCache = DEFAULT_NEWS_CACHE):
        self.cache = cache
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run(), name="daily-news-refresh")
            logger.info("Daily news refresh scheduled for 08:00 Europe/Madrid")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None

    async def _run(self) -> None:
        while True:
            await asyncio.sleep(seconds_until_next_refresh())
            try:
                await asyncio.to_thread(refresh_news_cache, self.cache)
            except Exception:
                logger.exception("Unexpected daily news refresh failure")


daily_news_scheduler = DailyNewsScheduler()


if __name__ == "__main__":
    raise SystemExit(0 if refresh_news_cache() else 1)
