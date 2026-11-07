"""Health router — global status + Pydantic contracts + WebSocket status.

Offline, deterministic, no network.

Wires real runtime data into the /health/status endpoint:
- active agents (the six runtime agents)
- frozen Pydantic contracts (the five payload/verdict models)
- zero_cost_routing flag
- live WebSocket connection status from backend.websockets
"""

from fastapi import APIRouter
from typing import List
import logging

from backend.app.models import (
    AuditVerdict,
    GuardrailVerdict,
    LeadAlertPayload,
    NewsItemPayload,
    RAGResponsePayload,
)
from backend.websockets import manager, websocket_status

logger = logging.getLogger(__name__)

health_router = APIRouter(prefix="/health", tags=["health"])

ACTIVE_AGENTS: List[str] = [
    "Nexus",
    "Radarito",
    "Cerebrito",
    "Centinela",
    "Mensajerito",
    "Auditor",
]

PYDANTIC_CONTRACTS: List[str] = [
    "NewsItemPayload",
    "RAGResponsePayload",
    "GuardrailVerdict",
    "LeadAlertPayload",
    "AuditVerdict",
]


@health_router.get("/status")
async def health_status():
    """Health check para el runtime multiagente."""
    logger.info("Health status requested")
    return {
        "status": "healthy",
        "active_agents": ACTIVE_AGENTS,
        "contracts": PYDANTIC_CONTRACTS,
        "zero_cost_routing": True,
        "websocket_connections": await websocket_status(),
    }
