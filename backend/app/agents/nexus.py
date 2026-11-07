"""Nexus — Orquestador Central & Router (FSM)."""

import logging

from typing import Dict, Any

logger = logging.getLogger(__name__)


class Nexus:
    """FSM asíncrona. Gestiona el ciclo de vida de sesiones, enruta tráfico
    hacia subagentes y selecciona el proveedor LLM gratuito idóneo.

    Responsabilidades:
    - FSM asíncrona de estados de sesión
    - Enrutamiento dinámico a subagentes
    - Selección de proveedor LLM gratuito según tarea
    - Sincronización de estado mediante Engram MCP
    """

    def __init__(self, mcp_registry: Any = None):
        self.name = "Nexus"
        self.role = "Orquestador Central & Router"
        self.mcp_registry = mcp_registry
        self.session_fsm: Dict[str, str] = {}  # session_id -> state
        self.agent_routing: Dict[str, str] = {}  # intent -> agent_name
        self.llm_providers = {
            "guardrails": "Groq Cloud llama-3.1-8b-instant",
            "reasoning": "Google AI Studio gemini-1.5-flash / 2.0-flash",
            "news": "Cloudflare Workers AI / OpenRouter Free Tier",
        }

    async def route(self, intent: str, context: dict) -> str:
        """Route an incoming request to the appropriate agent based on intent."""
        logger.info(f"Nexus routing intent: {intent}")

        routing_map = {
            "TECHNICAL_PROFILE": "Cerebrito",
            "HARDWARE_SMT": "Centinela",
            "SOFTWARE_CASE_STUDY": "Cerebrito",
            "OFF_TOPIC": "Centinela",
            "PROMPT_INJECTION": "Centinela",
        }

        target_agent = routing_map.get(intent, "Cerebrito")
        self.agent_routing[intent] = target_agent
        return target_agent

    async def session_lifecycle(self, action: str, session_id: str, data: dict = None) -> dict:
        """Manage session lifecycle: create, update, terminate."""
        if action == "create":
            self.session_fsm[session_id] = "active"
            logger.info(f"Session created: {session_id}")
            return {"status": "created", "session_id": session_id, "state": "active"}
        elif action == "update":
            if session_id in self.session_fsm:
                self.session_fsm[session_id] = "updated"
                return {"status": "updated", "session_id": session_id}
        elif action == "terminate":
            self.session_fsm.pop(session_id, None)
            logger.info(f"Session terminated: {session_id}")
            return {"status": "terminated", "session_id": session_id}

        return {"status": "unknown_action", "action": action}
