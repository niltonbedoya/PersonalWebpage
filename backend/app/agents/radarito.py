"""Radarito — Subagente A: Curación Contextual de Noticias."""

import logging

from typing import Any, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class Radarito:
    """Subagente A - Curación Contextual de Noticias.

    Consume RSS/APIs técnicas en 3 canales (THT_SOLDERING, SMD_INSPECTION, AI_SOFTWARE),
    deduplica, filtra ruido comercial y genera síntesis neutral de 2-3 líneas.
    Inferencia: Cloudflare Workers AI / OpenRouter Free.
    """

    def __init__(self, mcp_registry: Any = None):
        self.name = "Radarito"
        self.role = "Subagente A - Curación Contextual de Noticias"
        self.mcp_registry = mcp_registry
        self.channels: Dict[str, List[dict]] = {
            "THT_SOLDERING": [],
            "SMD_INSPECTION": [],
            "AI_SOFTWARE": [],
        }
        self.filter_keywords = ["ad", "sale", "buy", "commercial"]  # Noise filters

    def ingest_feed(self, feed_data: dict, category: str):
        """Ingest and curate a technical feed item."""
        from backend.app.models import NewsItemPayload

        try:
            # Basic filtering and deduplication
            title = feed_data.get("title", "")
            source_url = feed_data.get("source_url", "")

            # Check for noise/commercial content
            if any(kw in title.lower() for kw in self.filter_keywords):
                logger.info(f"Filtered out commercial content: {title[:50]}")
                return None

            # Deduplication check (compare as strings: stored value may be an
            # HttpUrl object while the incoming value is a plain string).
            for existing in self.channels.get(category, []):
                if (str(existing.get("title")) == str(title)
                        and str(existing.get("source_url")) == str(source_url)):
                    logger.info(f"Duplicate filtered: {title[:50]}")
                    return None

            # Create NewsItemPayload
            payload = NewsItemPayload(
                id=feed_data.get("id", f"news-{len(self.channels[category])}"),
                category=category,
                title=title,
                source_url=source_url,
                published_at=feed_data.get("published_at", datetime.utcnow()),
                summary=feed_data.get("summary", "")[:300],  # Max 300 chars
                tags=feed_data.get("tags", []),
            )

            self.channels.setdefault(category, []).append({
                "id": payload.id,
                "title": payload.title,
                "source_url": payload.source_url,
            })

            logger.info(f"News item curated: {payload.title[:50]}")
            return payload

        except Exception as e:
            logger.error(f"Error curating news: {e}")
            return None

    def synthesize_summary(self, category: str) -> str:
        """Generate 2-3 line neutral synthesis for a news category."""
        items = self.channels.get(category, [])
        if not items:
            return f"No hay artículos nuevos en {category}"

        # Take most recent 3 items
        recent = items[:3]
        lines = [f"- {item['title']}" for item in recent]

        if len(lines) == 1:
            return lines[0]
        elif len(lines) == 2:
            return f"{lines[0]}\n{lines[1]}"
        else:
            return f"{lines[0]}\n{lines[1]}\n{lines[2]}"
