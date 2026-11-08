"""FastAPI Main Application - Showcase Platform

Main application assembling all routers, WebSocket support, and the multi-agent framework.
"""

import os
import time
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import RedirectResponse
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.routers import router, news_router, contact_router, health_router
from backend.app.routers.admin import admin_router
from backend.app.mcp.adapters import MCPRegistry
from backend.app import models  # noqa: F401
from backend.websockets import manager, websocket_route, websocket_status
from backend.agent_ops_router import agent_ops_router
from backend.app.core.security_headers import SecurityHardeningMiddleware
from backend.app.core.logging_config import setup_logging
from backend.app.db.analytics import analytics_db

# Inicializar logger rotativo bounded
setup_logging()

# Create FastAPI app
app = FastAPI(
    title="Showcase Platform Multi-Agente",
    description="Runtime multiagente hibrido - FastAPI con routing de LLM de costo cero y agentes autonomos con WebSockets en tiempo real",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Inyectar middleware defensivo de cabeceras HTTP y rate limiting
app.add_middleware(SecurityHardeningMiddleware)

# Middleware de telemetría y registro de visitas por IP
@app.middleware("http")
async def analytics_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - start) * 1000

    path = request.url.path
    # Filtrar estáticos secundarios para no saturar la base de datos de visitas
    ignored_exts = (".css", ".js", ".png", ".jpg", ".jpeg", ".ico", ".svg", ".woff2", ".ttf")
    if not any(path.endswith(ext) for ext in ignored_exts) and not path.startswith("/static/src/"):
        # Extraer IP real (Cloudflare Tunnel o cliente)
        cf_ip = request.headers.get("cf-connecting-ip")
        fwd_ip = request.headers.get("x-forwarded-for")
        client_ip = cf_ip or (fwd_ip.split(",")[0].strip() if fwd_ip else None) or (request.client.host if request.client else "127.0.0.1")
        country = request.headers.get("cf-ipcountry", "XX")
        user_agent = request.headers.get("user-agent", "")

        try:
            analytics_db.record_visit(
                ip=client_ip,
                country=country,
                path=path,
                user_agent=user_agent,
                status_code=response.status_code,
                response_time_ms=elapsed_ms,
            )
        except Exception:
            pass  # El logging no debe jamás romper la respuesta al usuario

    return response

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prevent browser caching of static assets during development
@app.middleware("http")
async def no_cache_static_middleware(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static"):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

# Serve static HTML pages.
# BASE_DIR = project root (backend/ is one level below it).
# HTML pages physically live at <project>/web/public/pages/>.
BASE_DIR = Path(__file__).resolve().parent.parent
PUBLIC_DIR = BASE_DIR / "web" / "public"

if PUBLIC_DIR.is_dir():
    app.mount("/static/src", StaticFiles(directory=str(BASE_DIR / "web" / "src")), name="src")
    app.mount("/static", StaticFiles(directory=str(PUBLIC_DIR)), name="static")
    print(f"[OK] Static files mounted from: {PUBLIC_DIR}")
else:
    print(f"[WARN] Static dir not found: {PUBLIC_DIR}")

# Incluir routers API (los routers ya definen sus prefijos internamente)
app.include_router(router)
app.include_router(news_router)
app.include_router(contact_router)
app.include_router(health_router)
app.include_router(admin_router)

# Agent operations endpoints under /api/v1/agents/* (F3, S6/S7)
app.include_router(agent_ops_router)

# WebSocket endpoint - routed by agent name
@app.websocket("/ws/{agent_name}")
async def websocket_endpoint(websocket: WebSocket, agent_name: str):
    await websocket_route(websocket, agent_name)

# Health check WebSocket status endpoint
@app.websocket("/ws/status")
async def websocket_status_endpoint(websocket: WebSocket):
    await websocket.accept()
    status = await websocket_status()
    await websocket.send_json(status)

# Root endpoint
@app.get("/")
async def root(request: Request):
    """Root endpoint: redirects browser to the interactive dashboard, returns JSON for API clients."""
    accept = request.headers.get("accept", "")
    if "text/html" in accept or "*/*" in accept:
        return RedirectResponse(url="/static/pages/index.html", status_code=307)
    return {
        "message": "Showcase Platform API with WebSockets",
        "version": "0.1.0",
        "status": "operational",
        "endpoints": {
            "http": "/, /health, /chat, /news, /contact",
            "websockets": "/ws/{agent_name}, /ws/status",
            "static": "/static/pages/... (HTML pages)"
        },
        "llm_routing": {
            "centinela_mensajerito": "Groq Cloud llama-3.1-8b-instant",
            "cerebrito_auditor": "Google AI Studio gemini-1.5-flash",
            "radarito": "Cloudflare Workers AI / OpenRouter Free Tier"
        },
        "websocket_support": "Enabled - real-time agent communication"
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check for all agents."""
    from backend.app.models import (
        NewsItemPayload,
        RAGResponsePayload,
        GuardrailVerdict,
        LeadAlertPayload,
        AuditVerdict,
    )
    return {
        "status": "healthy",
        "pydantic_contracts": [
            "NewsItemPayload",
            "RAGResponsePayload",
            "GuardrailVerdict",
            "LeadAlertPayload",
            "AuditVerdict",
        ],
        "active_agents": ["Nexus", "Radarito", "Cerebrito", "Centinela", "Mensajerito", "Auditor"],
        "zero_cost_routing": True,
        "websocket_connections": await websocket_status(),
    }


# Agent role and description constants
AGENT_ROLES = {
    "Nexus": "Orquestador Central & Router",
    "Radarito": "Subagente A - Curacion Contextual de Noticias",
    "Cerebrito": "Subagente B - Motor RAG Tecnico",
    "Centinela": "Subagente C - Guardrail & Seguridad",
    "Mensajerito": "Subagente D - Triage & Despacho de Oportunidades",
    "Auditor": "Agente Auditor / QA - Binary Gatekeeper",
}

AGENT_DESCRIPTIONS = {
    "Nexus": "FSM asincrona. Gestiona el ciclo de vida de sesiones, enruta trafico hacia subagentes y selecciona el proveedor LLM gratuito idoneo.",
    "Radarito": "Consume RSS/APIs tecnicas en 3 canales (THT_SOLDERING, SMD_INSPECTION, AI_SOFTWARE). Deduplica, filtra ruido comercial y genera sintesis neutral de 2-3 lineas.",
    "Cerebrito": "Responde consultas sobre maquinaria, procesos termicos y proyectos de software basandose exclusivamente en el corpus indexado en SQLite-vec.",
    "Centinela": "Intercepcion ultrarrapida (<150 ms). Evalua si la consulta es pertinente al perfil tecnico. Bloquea intentos de jailbreak, inyecciones de prompt y reconduce consultas off-topic.",
    "Mensajerito": "Evalua el historial del chat y envios del formulario. Extrae leads de interes tecnico o laboral. Despacha alerta asincrona cifrada a correo personal.",
    "Auditor": "Compuerta binaria estricta (Pass/Fail). Audita esquemas Pydantic v2, Grounding Score (>= 0.85) en respuestas RAG, y previene fuga de datos privados (PII, credenciales, marcas reales).",
}


@app.get("/agent/{agent_name}")
async def agent_info_endpoint(agent_name: str) -> dict:
    """Endpoint to get info about a specific agent."""
    return {
        "agent": agent_name,
        "role": AGENT_ROLES.get(agent_name, "Unknown"),
        "status": "ready",
        "description": AGENT_DESCRIPTIONS.get(agent_name, ""),
    }


if __name__ == "__main__":
    import uvicorn
    print("Starting Showcase Platform with WebSocket support...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
