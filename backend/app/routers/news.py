"""News router — Radarito curated feed endpoint.

Returns NewsItemPayload-conformant items per category.
Daily RSS items are preferred when the runtime cache is available.
The deterministic curated list remains the offline fallback.
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel
from typing import Literal, Optional, List
import logging

from backend.app.agents import Radarito
from backend.app.models import NewsItemPayload
from backend.app.services.news_refresh import DEFAULT_NEWS_CACHE

logger = logging.getLogger(__name__)

news_router = APIRouter(prefix="/news", tags=["news"])

_radarito = Radarito()
_seeded = False
_news_cache = DEFAULT_NEWS_CACHE


# Deterministic, curated news items linking directly to exact articles & releases:
# 1. PCB Manufacturing & EMS (Automotive, Aerospace, Defense, Consumer Electronics)
# 2. Partner Equipment Nilton works with (PARMI, ERSA, NORDSON, MARANTZ/Mek)
# 3. AI Software (Skills, Frameworks, MCPs and modern AI Models)
_SEED_ITEMS: dict[str, List[dict]] = {
    "THT_SOLDERING": [
        {
            "id": "partner-002",
            "category": "THT_SOLDERING",
            "sub_category": "partner_equipment",
            "title": "Kurtz Ersa VERSAFLOW FIVE: Redefinición de la soldadura selectiva",
            "title_es": "Kurtz Ersa VERSAFLOW FIVE: Redefinición de la soldadura selectiva",
            "title_en": "Kurtz Ersa VERSAFLOW FIVE: Redefining selective soldering",
            "source_url": "https://kurtzersa.com/news/all/ersa-versaflow-five-redefinition-of-selective-soldering",
            "published_at": "2026-11-07T10:15:00",
            "summary": "Kurtz Ersa presenta su nueva plataforma VERSAFLOW FIVE con módulo VERSAFLEX 2.0 para procesamiento paralelo independiente de dos PCBs y optimización drástica de consumo de nitrógeno.",
            "summary_es": "Kurtz Ersa presenta su nueva plataforma VERSAFLOW FIVE con módulo VERSAFLEX 2.0 para procesamiento paralelo independiente de dos PCBs y optimización drástica de consumo de nitrógeno.",
            "summary_en": "Kurtz Ersa introduces its new VERSAFLOW FIVE platform with VERSAFLEX 2.0 module for independent parallel dual-PCB processing and dramatic nitrogen savings.",
            "tags": ["ersa", "versaflow-five", "selective-soldering", "tht"],
        },
        {
            "id": "tht-002",
            "category": "THT_SOLDERING",
            "sub_category": "partner_equipment",
            "title": "Marantz Electronics (Mek) SpectorBOX: Inspección modular 3D AOI en THT",
            "title_es": "Marantz Electronics (Mek) SpectorBOX: Inspección modular 3D AOI en THT",
            "title_en": "Marantz Electronics (Mek) SpectorBOX: Modular 3D AOI for THT inspection",
            "source_url": "https://marantz-electronics.com/3d-modular-aoi/",
            "published_at": "2026-11-03T16:20:00",
            "summary": "Marantz Electronics despliega SpectorBOX para inspección óptica 3D directa de meniscos de soldadura e inserción de pines THT en transportadores existentes sin modificar la línea.",
            "summary_es": "Marantz Electronics despliega SpectorBOX para inspección óptica 3D directa de meniscos de soldadura e inserción de pines THT en transportadores existentes sin modificar la línea.",
            "summary_en": "Marantz Electronics deploys SpectorBOX for direct 3D optical inspection of solder fillets and THT pin insertion on existing conveyors without line retooling.",
            "tags": ["marantz", "mek", "spectorbox", "tht-aoi"],
        },
    ],
    "SMD_INSPECTION": [
        {
            "id": "pcb-001",
            "category": "SMD_INSPECTION",
            "sub_category": "pcb_manufacturing",
            "title": "in4ma: El estado de la industria EMS europea y la volatilidad en automoción",
            "title_es": "in4ma: El estado de la industria EMS europea y la volatilidad en automoción",
            "title_en": "in4ma: The state of the European EMS industry and automotive volatility",
            "source_url": "https://evertiq.com/news/56857",
            "published_at": "2026-11-06T09:00:00",
            "summary": "Informe sectorial sobre la transición hacia la movilidad eléctrica, requisitos de trazabilidad individual y demanda de manufactura electrónica de alta fiabilidad en plantas EMS.",
            "summary_es": "Informe sectorial sobre la transición hacia la movilidad eléctrica, requisitos de trazabilidad individual y demanda de manufactura electrónica de alta fiabilidad en plantas EMS.",
            "summary_en": "Sector report on the transition to electric mobility, individual traceability requirements, and demand for high-reliability electronics manufacturing across EMS plants.",
            "tags": ["ems", "automotive", "pcb-assembly", "in4ma"],
        },
        {
            "id": "partner-001",
            "category": "SMD_INSPECTION",
            "sub_category": "partner_equipment",
            "title": "PARMI: Los mejores sistemas 3D AOI para 2026 y criterios de selección",
            "title_es": "PARMI: Los mejores sistemas 3D AOI para 2026 y criterios de selección",
            "title_en": "PARMI: Best 3D AOI Systems for 2026 and selection criteria",
            "source_url": "https://parmi.com/blog/best-3d-aoi-system/",
            "published_at": "2026-11-08T08:30:00",
            "summary": "Análisis técnico de cabezales de escaneo láser dual, reducción de falsos rechazos en ensambles de alta densidad y criterios de selección de sistemas 3D AOI para 2026.",
            "summary_es": "Análisis técnico de cabezales de escaneo láser dual, reducción de falsos rechazos en ensambles de alta densidad y criterios de selección de sistemas 3D AOI para 2026.",
            "summary_en": "Technical analysis of dual-laser scanning heads, false call reduction on high-density assemblies, and 3D AOI evaluation criteria for 2026.",
            "tags": ["parmi", "spi-3d", "aoi-3d", "xceed"],
        },
        {
            "id": "partner-003",
            "category": "SMD_INSPECTION",
            "sub_category": "partner_equipment",
            "title": "NORDSON DAGE 4000Plus: Ensayos de Wire Pull y Ball Shear en microelectrónica",
            "title_es": "NORDSON DAGE 4000Plus: Ensayos de Wire Pull y Ball Shear en microelectrónica",
            "title_en": "NORDSON DAGE 4000Plus: Wire Pull and Ball Shear mechanical bond testing",
            "source_url": "https://www.nordson.com/en/products/test-and-inspection-products/dage-4000plus-bondtester",
            "published_at": "2026-11-05T14:00:00",
            "summary": "Plataforma de ensayo mecánico Bond Tester con calibración multieje automática para validar adherencia de soldadura e intermetálicos bajo normas automotrices MIL-STD e IPC.",
            "summary_es": "Plataforma de ensayo mecánico Bond Tester con calibración multieje automática para validar adherencia de soldadura e intermetálicos bajo normas automotrices MIL-STD e IPC.",
            "summary_en": "Bond Tester mechanical platform with automated multi-axis calibration to validate solder adhesion and intermetallics compliance under automotive MIL-STD and IPC standards.",
            "tags": ["nordson", "dage", "bond-tester", "wire-pull"],
        },
        {
            "id": "pcb-002",
            "category": "SMD_INSPECTION",
            "sub_category": "pcb_manufacturing",
            "title": "SEMI impulsa iniciativas de energía y sostenibilidad en la cadena de PCB y chips",
            "title_es": "SEMI impulsa iniciativas de energía y sostenibilidad en la cadena de PCB y chips",
            "title_en": "SEMI unveils low-carbon energy initiatives across PCB and semiconductor supply chains",
            "source_url": "https://evertiq.com/news/54820",
            "published_at": "2026-11-04T11:00:00",
            "summary": "Consorcios internacionales de semiconductores y fabricación de circuitos impresos refuerzan la eficiencia energética y la resiliencia en la cadena de valor global de electrónica.",
            "summary_es": "Consorcios internacionales de semiconductores y fabricación de circuitos impresos refuerzan la eficiencia energética y la resiliencia en la cadena de valor global de electrónica.",
            "summary_en": "International semiconductor and PCB manufacturing consortiums strengthen energy efficiency and resilience across the global electronics value chain.",
            "tags": ["semi", "pcb-supply-chain", "semiconductor", "sustainability"],
        },
        {
            "id": "partner-004",
            "category": "SMD_INSPECTION",
            "sub_category": "partner_equipment",
            "title": "Marantz Electronics (Mek) SpectorBOX: Inspección modular 3D AOI en SMT y THT",
            "title_es": "Marantz Electronics (Mek) SpectorBOX: Inspección modular 3D AOI en SMT y THT",
            "title_en": "Marantz Electronics (Mek) SpectorBOX: Modular 3D AOI for SMT and THT",
            "source_url": "https://marantz-electronics.com/3d-modular-aoi/",
            "published_at": "2026-11-03T16:20:00",
            "summary": "Los sistemas modulares SpectorBOX de Mek combinan cámaras cenitales y laterales para verificar levantamiento de terminales, polaridad y meniscos de soldadura tanto en PCB inferior como superior.",
            "summary_es": "Los sistemas modulares SpectorBOX de Mek combinan cámaras cenitales y laterales para verificar levantamiento de terminales, polaridad y meniscos de soldadura tanto en PCB inferior como superior.",
            "summary_en": "Mek SpectorBOX modular systems combine top and side cameras to verify lead protrusion, polarity, and solder fillets on both bottom and top PCB surfaces.",
            "tags": ["marantz", "mek", "spectorbox", "3d-aoi"],
        },
    ],
    "AI_SOFTWARE": [
        {
            "id": "ai-001",
            "category": "AI_SOFTWARE",
            "sub_category": "skills_frameworks_mcps",
            "title": "Model Context Protocol (MCP): El estándar abierto para conectar datos con agentes de AI",
            "title_es": "Model Context Protocol (MCP): El estándar abierto para conectar datos con agentes de AI",
            "title_en": "Model Context Protocol (MCP): Open standard to connect data with AI agents",
            "source_url": "https://www.anthropic.com/news/model-context-protocol",
            "published_at": "2026-11-08T12:00:00",
            "summary": "Especificación abierta para conectar sistemas de inteligencia artificial con repositorios de código, bases de datos vectoriales y herramientas locales de forma segura y estandarizada.",
            "summary_es": "Especificación abierta para conectar sistemas de inteligencia artificial con repositorios de código, bases de datos vectoriales y herramientas locales de forma segura y estandarizada.",
            "summary_en": "Open specification to securely connect artificial intelligence systems with codebases, vector databases, and local enterprise tools without proprietary lock-in.",
            "tags": ["mcp", "anthropic", "ai-agents", "protocols"],
        },
        {
            "id": "ai-003",
            "category": "AI_SOFTWARE",
            "sub_category": "ai_models",
            "title": "Modelos Gemini: Inferencia compacta y multimodal para desarrolladores",
            "title_es": "Modelos Gemini: Inferencia compacta y multimodal para desarrolladores",
            "title_en": "Gemini Models: Compact and multimodal inference for developers",
            "source_url": "https://aistudio.google.com/docs/models",
            "published_at": "2026-11-07T17:00:00",
            "summary": "Guía oficial de modelos de lenguaje compactos como Gemini Flash-Lite con soporte para llamadas a funciones estructuradas, contexto extenso e inferencia de alta velocidad.",
            "summary_es": "Guía oficial de modelos de lenguaje compactos como Gemini Flash-Lite con soporte para llamadas a funciones estructuradas, contexto extenso e inferencia de alta velocidad.",
            "summary_en": "Official documentation for compact language models like Gemini Flash-Lite featuring structured function calling, long-context windows, and high-speed inference.",
            "tags": ["gemini", "flash-lite", "llm-models", "inference"],
        },
        {
            "id": "ai-002",
            "category": "AI_SOFTWARE",
            "sub_category": "skills_frameworks_mcps",
            "title": "Arquitectura de servicios asíncronos y contratos Pydantic v2 en FastAPI",
            "title_es": "Arquitectura de servicios asíncronos y contratos Pydantic v2 en FastAPI",
            "title_en": "Async service architectures and Pydantic v2 contracts in FastAPI",
            "source_url": "https://fastapi.tiangolo.com/tutorial/",
            "published_at": "2026-11-06T15:30:00",
            "summary": "Patrones de desarrollo para APIs de baja latencia con validación estricta de esquemas, concurrencia asíncrona y orquestación multiagente desacoplada.",
            "summary_es": "Patrones de desarrollo para APIs de baja latencia con validación estricta de esquemas, concurrencia asíncrona y orquestación multiagente desacoplada.",
            "summary_en": "Development patterns for low-latency APIs with strict schema validation, asynchronous concurrency, and decoupled multi-agent orchestration.",
            "tags": ["fastapi", "pydantic", "multi-agent", "async"],
        },
        {
            "id": "ai-004",
            "category": "AI_SOFTWARE",
            "sub_category": "ai_models",
            "title": "El estado de la visión artificial en Hugging Face: De transformers a modelos edge",
            "title_es": "El estado de la visión artificial en Hugging Face: De transformers a modelos edge",
            "title_en": "The State of Computer Vision at Hugging Face: From transformers to edge models",
            "source_url": "https://huggingface.co/blog/cv_state",
            "published_at": "2026-11-05T09:45:00",
            "summary": "Panorama completo de arquitecturas de visión por computador, modelos de detección y segmentación en tiempo real para aplicaciones industriales y robótica en el borde.",
            "summary_es": "Panorama completo de arquitecturas de visión por computador, modelos de detección y segmentación en tiempo real para aplicaciones industriales y robótica en el borde.",
            "summary_en": "Comprehensive overview of computer vision architectures, real-time object detection, and segmentation models for industrial workflows and edge robotics.",
            "tags": ["huggingface", "computer-vision", "edge-ai", "yolo"],
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
    lang: Optional[Literal["es", "en"]] = Query("es"),
    body: Optional[NewsQuery] = Body(None),
):
    """Endpoint de noticias curadas por Radarito (soporta query parameters y body)."""
    selected_category = category if category is not None else (body.category if body else None)
    selected_limit = limit if category is not None else (body.limit if body and body.limit is not None else limit)
    if not selected_category:
        raise HTTPException(status_code=422, detail="Field 'category' is required via query param or body")
    logger.info("News request for category: %s, limit: %s, lang: %s", selected_category, selected_limit, lang)
    _ensure_seed()
    live_items = _news_cache.items(lang or "es", selected_category)
    raw_items = live_items or [item for item in _SEED_ITEMS[selected_category]]
    if selected_limit is not None:
        raw_items = raw_items[: selected_limit]

    processed = []
    for item in raw_items:
        data = dict(item)
        if lang == "en":
            data["title"] = item.get("title_en", item["title"])
            data["summary"] = item.get("summary_en", item["summary"])
        else:
            data["title"] = item.get("title_es", item["title"])
            data["summary"] = item.get("summary_es", item["summary"])
        processed.append(NewsItemPayload(**data).model_dump())

    return processed
