"""News router — Radarito curated feed endpoint.

Returns NewsItemPayload-conformant items per category.
Offline, deterministic, no network.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import Literal, Optional, List
import logging

from backend.app.agents import Radarito
from backend.app.models import NewsItemPayload

logger = logging.getLogger(__name__)

news_router = APIRouter(prefix="/news", tags=["news"])

_radarito = Radarito()
_seeded = False


# Deterministic, sanitized seed items per Radarito channel. No PII, no real
# names, emails or phones; source URLs use example.com.
_SEED_ITEMS: dict[str, List[dict]] = {
    "THT_SOLDERING": [
        {
            "id": "tht-001",
            "category": "THT_SOLDERING",
            "title": "Lead-free soldering guidelines for through-hole assembly",
            "source_url": "https://example.com/tht-soldering-guide",
            "published_at": "2024-03-15T00:00:00",
            "summary": "Best practices for manual through-hole soldering including temperature profiles and flux selection.",
            "tags": ["soldering", "through-hole", "tht"],
        },
        {
            "id": "tht-002",
            "category": "THT_SOLDERING",
            "title": "Selecting flux-core wire for electronics assembly",
            "source_url": "https://example.com/flux-core-wire",
            "published_at": "2024-04-10T00:00:00",
            "summary": "Comparison of rosin and no-clean flux core solder wires for THT production.",
            "tags": ["flux", "solder wire", "electronics"],
        },
        {
            "id": "tht-003",
            "category": "THT_SOLDERING",
            "title": "Thermal profiling and dross prevention in selective soldering",
            "source_url": "https://example.com/selective-soldering-dross",
            "published_at": "2024-08-20T00:00:00",
            "summary": "Nitrogen atmosphere management and precise nozzle positioning reduce dross formation and bridging in SAC305 selective soldering.",
            "tags": ["selective soldering", "sac305", "nitrogen"],
        },
        {
            "id": "tht-004",
            "category": "THT_SOLDERING",
            "title": "High-reliability through-hole metallurgical joint integrity",
            "source_url": "https://example.com/tht-metallurgy-integrity",
            "published_at": "2024-10-05T00:00:00",
            "summary": "Intermetallic compound layer analysis and hole fill inspection for mission-critical industrial power modules.",
            "tags": ["metallurgy", "intermetallics", "reliability"],
        },
    ],
    "SMD_INSPECTION": [
        {
            "id": "smd-001",
            "category": "SMD_INSPECTION",
            "title": "Automated optical inspection for SMT solder joints",
            "source_url": "https://example.com/smd-aoi-inspection",
            "published_at": "2024-02-20T00:00:00",
            "summary": "AOI systems detect bridging, tombstoning and insufficient solder on SMD boards.",
            "tags": ["aoi", "smt", "inspection"],
        },
        {
            "id": "smd-002",
            "category": "SMD_INSPECTION",
            "title": "X-ray inspection of BGA solder joints",
            "source_url": "https://example.com/smd-bga-xray",
            "published_at": "2024-05-05T00:00:00",
            "summary": "Computed tomography and 2D X-ray reveal voids under BGA packages invisible to optical inspection.",
            "tags": ["xray", "bga", "inspection"],
        },
        {
            "id": "smd-003",
            "category": "SMD_INSPECTION",
            "title": "True 3D SPI height and volume measurement for 0201 passives",
            "source_url": "https://example.com/smd-3d-spi-measurement",
            "published_at": "2024-09-12T00:00:00",
            "summary": "Moiré projection and dual-frequency phase-shift metrology provide volumetric paste deposition accuracy down to micro-meter scale.",
            "tags": ["spi", "3d metrology", "solder paste"],
        },
        {
            "id": "smd-004",
            "category": "SMD_INSPECTION",
            "title": "Wire pull and ball shear mechanical testing under IPC standards",
            "source_url": "https://example.com/bond-tester-adhesion-methods",
            "published_at": "2024-11-01T00:00:00",
            "summary": "Bond tester methodology for validating destructive and non-destructive joint adhesion in high-density electronic assemblies.",
            "tags": ["bond tester", "wire pull", "ball shear"],
        },
    ],
    "AI_SOFTWARE": [
        {
            "id": "ai-001",
            "category": "AI_SOFTWARE",
            "title": "Fine-tuning small code models for embedded toolchains",
            "source_url": "https://example.com/ai-embedded-toolchain",
            "published_at": "2024-06-01T00:00:00",
            "summary": "Domain-specific fine-tuning improves code generation for C and Python embedded toolchains.",
            "tags": ["ai", "code-models", "embedded"],
        },
        {
            "id": "ai-002",
            "category": "AI_SOFTWARE",
            "title": "Local LLM inference on CPU for edge devices",
            "source_url": "https://example.com/ai-cpu-inference",
            "published_at": "2024-07-12T00:00:00",
            "summary": "Quantized models run inference on CPU-class edge hardware without GPU acceleration.",
            "tags": ["llm", "cpu", "edge"],
        },
        {
            "id": "ai-003",
            "category": "AI_SOFTWARE",
            "title": "Decoupled multi-agent architectures with FastAPI and zero-cost LLMs",
            "source_url": "https://example.com/multiagent-zero-cost-fastapi",
            "published_at": "2024-09-28T00:00:00",
            "summary": "Asynchronous finite state machines and perimeter guardrails enable robust, defensive AI multi-agent orchestration at zero operational cost.",
            "tags": ["multi-agent", "fastapi", "ai architecture"],
        },
        {
            "id": "ai-004",
            "category": "AI_SOFTWARE",
            "title": "Real-time edge computer vision for automated inventory counting",
            "source_url": "https://example.com/edge-vision-tire-counter",
            "published_at": "2024-10-18T00:00:00",
            "summary": "Lightweight YOLO models on localized video streams provide sub-second tracking and export packing list automated generation.",
            "tags": ["computer vision", "yolo", "logistics"],
        },
    ],
}


def _ensure_seed() -> None:
    """Lazy-init: curate seed items through real Radarito once."""
    global _seeded
    if _seeded:
        return
    for category, items in _SEED_ITEMS.items():
        for feed in items:
            _radarito.ingest_feed(feed, category)
    _seeded = True
    logger.info("Radarito seed curation complete")


class NewsQuery(BaseModel):
    category: Literal["THT_SOLDERING", "SMD_INSPECTION", "AI_SOFTWARE"]
    limit: Optional[int] = 10


@news_router.get("/", response_model=List[dict])
async def news_endpoint(
    category: Optional[Literal["THT_SOLDERING", "SMD_INSPECTION", "AI_SOFTWARE"]] = Query(None),
    limit: Optional[int] = Query(10),
    body: Optional[NewsQuery] = Body(None),
):
    """Endpoint de noticias curadas por Radarito (soporta query parameters y body)."""
    selected_category = category if category is not None else (body.category if body else None)
    selected_limit = limit if category is not None else (body.limit if body and body.limit is not None else limit)
    if not selected_category:
        raise HTTPException(status_code=422, detail="Field 'category' is required via query param or body")
    logger.info("News request for category: %s, limit: %s", selected_category, selected_limit)
    _ensure_seed()
    items = [item for item in _SEED_ITEMS[selected_category]]
    if selected_limit is not None:
        items = items[: selected_limit]
    return [NewsItemPayload(**item).model_dump() for item in items]
