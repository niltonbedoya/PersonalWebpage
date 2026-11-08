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


# Deterministic, sanitized seed items per Radarito channel.
# Pillars:
# 1. PCB Manufacturing & EMS (Automotive, Aerospace, Defense, Consumer Electronics)
# 2. Partner Equipment Nilton works with (PARMI, ERSA, NORDSON, MARANTZ/Mek)
# 3. AI Software (Skills, Frameworks, MCPs and modern AI Models)
_SEED_ITEMS: dict[str, List[dict]] = {
    "THT_SOLDERING": [
        {
            "id": "partner-002",
            "category": "THT_SOLDERING",
            "sub_category": "partner_equipment",
            "title": "Kurtz Ersa optimiza el control de atmósfera inerte N2 en soldadura selectiva",
            "title_es": "Kurtz Ersa optimiza el control de atmósfera inerte N2 en soldadura selectiva",
            "title_en": "Kurtz Ersa optimizes N2 inert atmosphere management in selective soldering",
            "source_url": "https://www.kurtzersa.com/electronics-production-equipment/selective-soldering.html",
            "published_at": "2026-11-07T10:15:00",
            "summary": "Ersa presenta mejoras en su serie Versaflow con toberas electromagnéticas de alta precisión y reducción del 40% en consumo de nitrógeno y formación de escoria para uniones THT de potencia.",
            "summary_es": "Ersa presenta mejoras en su serie Versaflow con toberas electromagnéticas de alta precisión y reducción del 40% en consumo de nitrógeno y formación de escoria para uniones THT de potencia.",
            "summary_en": "Ersa unveils Versaflow series enhancements with high-precision electromagnetic nozzles, cutting nitrogen consumption and dross formation by 40% in high-power THT joints.",
            "tags": ["ersa", "selective-soldering", "nitrogen-atmosphere", "tht"],
        },
        {
            "id": "tht-002",
            "category": "THT_SOLDERING",
            "sub_category": "partner_equipment",
            "title": "Perfilado térmico Ramp-to-Soak y aleaciones SAC305 en ensamblaje THT",
            "title_es": "Perfilado térmico Ramp-to-Soak y aleaciones SAC305 en ensamblaje THT",
            "title_en": "Ramp-to-Soak thermal profiling and SAC305 alloys in THT assembly",
            "source_url": "https://www.ipc.org/ipc-a-610-tht-inspection-criteria",
            "published_at": "2026-10-25T08:00:00",
            "summary": "Guía técnica sobre perfiles térmicos y control de precalentamiento para garantizar el llenado de taladros pasantes según IPC-A-610 en placas multicapa de alta disipación térmica.",
            "summary_es": "Guía técnica sobre perfiles térmicos y control de precalentamiento para garantizar el llenado de taladros pasantes según IPC-A-610 en placas multicapa de alta disipación térmica.",
            "summary_en": "Technical guide on thermal profiling and preheating control to ensure through-hole fill according to IPC-A-610 on high-dissipation multilayer boards.",
            "tags": ["thermal-profiling", "sac305", "tht", "ipc-a-610"],
        },
    ],
    "SMD_INSPECTION": [
        {
            "id": "pcb-001",
            "category": "SMD_INSPECTION",
            "sub_category": "pcb_manufacturing",
            "title": "Auge de plantas EMS en automoción y demanda de trazabilidad total de PCB",
            "title_es": "Auge de plantas EMS en automoción y demanda de trazabilidad total de PCB",
            "title_en": "Surge in automotive EMS plants and demand for full PCB traceability",
            "source_url": "https://www.evertiq.com/news/54820",
            "published_at": "2026-11-06T09:00:00",
            "summary": "Grandes plantas de manufactura electrónica aceleran la adopción de trazabilidad a nivel de componente individual en ensambles críticos para automoción y movilidad eléctrica bajo estándares IATF 16949.",
            "summary_es": "Grandes plantas de manufactura electrónica aceleran la adopción de trazabilidad a nivel de componente individual en ensambles críticos para automoción y movilidad eléctrica bajo estándares IATF 16949.",
            "summary_en": "Tier-1 electronics manufacturing plants accelerate individual component-level traceability in critical automotive and e-mobility assemblies under IATF 16949 standards.",
            "tags": ["ems", "automotive", "iatf-16949", "pcb-assembly"],
        },
        {
            "id": "partner-001",
            "category": "SMD_INSPECTION",
            "sub_category": "partner_equipment",
            "title": "PARMI introduce metrología láser dual para inspección 3D de pasta SPI y AOI",
            "title_es": "PARMI introduce metrología láser dual para inspección 3D de pasta SPI y AOI",
            "title_en": "PARMI introduces dual laser metrology for 3D SPI paste and AOI inspection",
            "source_url": "https://parmi.com/sigmax-spi-dual-laser-inspection/",
            "published_at": "2026-11-08T08:30:00",
            "summary": "Los nuevos cabezales de escaneo láser inteligente de PARMI permiten medir volumen, altura y coplanaridad en componentes 01005 y micro-BGAs con cero falsos rechazos en líneas de alta velocidad.",
            "summary_es": "Los nuevos cabezales de escaneo láser inteligente de PARMI permiten medir volumen, altura y coplanaridad en componentes 01005 y micro-BGAs con cero falsos rechazos en líneas de alta velocidad.",
            "summary_en": "PARMI new intelligent laser scanning heads measure volume, height, and coplanarity on 01005 and micro-BGA components with zero false calls on high-speed SMT lines.",
            "tags": ["parmi", "spi-3d", "aoi-3d", "metrology"],
        },
        {
            "id": "partner-003",
            "category": "SMD_INSPECTION",
            "sub_category": "partner_equipment",
            "title": "NORDSON BT revoluciona los ensayos de Wire Pull y Ball Shear en microelectrónica",
            "title_es": "NORDSON BT revoluciona los ensayos de Wire Pull y Ball Shear en microelectrónica",
            "title_en": "NORDSON BT transforms Wire Pull and Ball Shear mechanical testing in microelectronics",
            "source_url": "https://www.nordson.com/en/divisions/dage/bond-testers",
            "published_at": "2026-11-05T14:00:00",
            "summary": "Las plataformas de ensayo mecánico Bond Tester de Nordson incorporan calibración multieje automática para validar adherencia de soldadura e intermetálicos bajo normas automotrices MIL-STD e IPC.",
            "summary_es": "Las plataformas de ensayo mecánico Bond Tester de Nordson incorporan calibración multieje automática para validar adherencia de soldadura e intermetálicos bajo normas automotrices MIL-STD e IPC.",
            "summary_en": "Nordson Bond Tester platforms add automated multi-axis calibration to validate solder adhesion and intermetallics compliance under automotive MIL-STD and IPC standards.",
            "tags": ["nordson", "bond-tester", "wire-pull", "ball-shear"],
        },
        {
            "id": "pcb-002",
            "category": "SMD_INSPECTION",
            "sub_category": "pcb_manufacturing",
            "title": "Fabricación de PCBs de alta fiabilidad para el sector aeroespacial y defensa",
            "title_es": "Fabricación de PCBs de alta fiabilidad para el sector aeroespacial y defensa",
            "title_en": "High-reliability PCB fabrication for aerospace and defense sectors",
            "source_url": "https://www.ipc.org/aerospace-defense-pcb-class3-reliability",
            "published_at": "2026-11-04T11:00:00",
            "summary": "Empresas de fabricación de circuitos impresos refuerzan la certificación IPC Clase 3 y ensayos destructivos y no destructivos para módulos de misión crítica y satélites LEO.",
            "summary_es": "Empresas de fabricación de circuitos impresos refuerzan la certificación IPC Clase 3 y ensayos destructivos y no destructivos para módulos de misión crítica y satélites LEO.",
            "summary_en": "PCB manufacturers tighten IPC Class 3 certification and destructive/non-destructive testing for mission-critical electronic modules and LEO satellites.",
            "tags": ["aerospace", "defense", "ipc-class-3", "high-reliability"],
        },
        {
            "id": "partner-004",
            "category": "SMD_INSPECTION",
            "sub_category": "partner_equipment",
            "title": "Marantz Electronics (Mek) expande la inspección 3D estereoscópica para THT y SMD",
            "title_es": "Marantz Electronics (Mek) expande la inspección 3D estereoscópica para THT y SMD",
            "title_en": "Marantz Electronics (Mek) expands stereoscopic 3D inspection for THT and SMD",
            "source_url": "https://www.marantz-electronics.com/3d-aoi/",
            "published_at": "2026-11-03T16:20:00",
            "summary": "Los sistemas modulares SpectorBOX de Mek combinan cámaras cenitales y laterales para verificar levantamiento de terminales, polaridad y meniscos de soldadura tanto en PCB inferior como superior.",
            "summary_es": "Los sistemas modulares SpectorBOX de Mek combinan cámaras cenitales y laterales para verificar levantamiento de terminales, polaridad y meniscos de soldadura tanto en PCB inferior como superior.",
            "summary_en": "Mek SpectorBOX modular systems combine top and side cameras to verify lead protrusion, polarity, and solder fillets on both bottom and top PCB surfaces.",
            "tags": ["marantz", "mek", "aoi-inspection", "tht-smd"],
        },
    ],
    "AI_SOFTWARE": [
        {
            "id": "ai-001",
            "category": "AI_SOFTWARE",
            "sub_category": "skills_frameworks_mcps",
            "title": "Model Context Protocol (MCP) se consolida como estándar para agentes de software",
            "title_es": "Model Context Protocol (MCP) se consolida como estándar para agentes de software",
            "title_en": "Model Context Protocol (MCP) solidifies as standard for autonomous software agents",
            "source_url": "https://modelcontextprotocol.io/",
            "published_at": "2026-11-08T12:00:00",
            "summary": "La especificación abierta MCP y frameworks como FastAPI permiten conectar LLMs con herramientas locales, bases de datos vectoriales y APIs empresariales sin acoplamiento propietario.",
            "summary_es": "La especificación abierta MCP y frameworks como FastAPI permiten conectar LLMs con herramientas locales, bases de datos vectoriales y APIs empresariales sin acoplamiento propietario.",
            "summary_en": "The open MCP specification and frameworks like FastAPI allow LLMs to securely connect with local tools, vector databases, and enterprise APIs without vendor lock-in.",
            "tags": ["mcp", "frameworks", "ai-agents", "fastapi"],
        },
        {
            "id": "ai-003",
            "category": "AI_SOFTWARE",
            "sub_category": "ai_models",
            "title": "Nuevos modelos de lenguaje compactos ofrecen inferencia ultrarrápida y coste cero",
            "title_es": "Nuevos modelos de lenguaje compactos ofrecen inferencia ultrarrápida y coste cero",
            "title_en": "New compact language models deliver ultra-fast inference at zero operational cost",
            "source_url": "https://ai.google.dev/gemini-api/docs/models/gemini",
            "published_at": "2026-11-07T17:00:00",
            "summary": "Familias como Gemini Flash-Lite, Gemma y LLaMA optimizan la cuantización a 4 bits para ejecutar razonamiento estructurado y llamadas a funciones en servidores locales sin GPUs dedicadas.",
            "summary_es": "Familias como Gemini Flash-Lite, Gemma y LLaMA optimizan la cuantización a 4 bits para ejecutar razonamiento estructurado y llamadas a funciones en servidores locales sin GPUs dedicadas.",
            "summary_en": "Model families like Gemini Flash-Lite, Gemma, and LLaMA optimize 4-bit quantization to run structured reasoning and function calling on local servers without dedicated GPUs.",
            "tags": ["gemini", "llama", "llm-models", "inference"],
        },
        {
            "id": "ai-002",
            "category": "AI_SOFTWARE",
            "sub_category": "skills_frameworks_mcps",
            "title": "Arquitectura de Skills desacopladas y TDD estricto en sistemas multiagente",
            "title_es": "Arquitectura de Skills desacopladas y TDD estricto en sistemas multiagente",
            "title_en": "Decoupled Skills architecture and strict TDD in multi-agent systems",
            "source_url": "https://fastapi.tiangolo.com/",
            "published_at": "2026-11-06T15:30:00",
            "summary": "Nuevos patrones de desarrollo promueven agentes especializados de bajo coste con herramientas acotadas, guardrails perimetrales de baja latencia y verificación continua mediante suites offline.",
            "summary_es": "Nuevos patrones de desarrollo promueven agentes especializados de bajo coste con herramientas acotadas, guardrails perimetrales de baja latencia y verificación continua mediante suites offline.",
            "summary_en": "Emerging development patterns promote specialized low-cost agents with bounded tools, low-latency perimeter guardrails, and continuous offline test verification.",
            "tags": ["skills", "multi-agent", "tdd", "zero-cost"],
        },
        {
            "id": "ai-004",
            "category": "AI_SOFTWARE",
            "sub_category": "ai_models",
            "title": "Modelos multimodales y visión artificial en tiempo real para procesos industriales",
            "title_es": "Modelos multimodales y visión artificial en tiempo real para procesos industriales",
            "title_en": "Multimodal models and real-time computer vision for industrial workflows",
            "source_url": "https://huggingface.co/blog",
            "published_at": "2026-11-05T09:45:00",
            "summary": "Modelos de visión ligeros procesan transmisiones de vídeo en el edge para conteo de inventario, detección de microdefectos y verificación de ensamblajes en menos de 50 milisegundos.",
            "summary_es": "Modelos de visión ligeros procesan transmisiones de vídeo en el edge para conteo de inventario, detección de microdefectos y verificación de ensamblajes en menos de 50 milisegundos.",
            "summary_en": "Lightweight vision models process video streams at the edge for automated inventory counting, micro-defect detection, and assembly inspection under 50 milliseconds.",
            "tags": ["computer-vision", "multimodal", "edge-ai", "yolo"],
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
    raw_items = [item for item in _SEED_ITEMS[selected_category]]
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
