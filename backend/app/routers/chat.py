"""Chat router — Nexus orchestration endpoint.

Delegates to the real Nexus agent (FSM session lifecycle + intent routing),
Centinela guardrail, Cerebrito RAG, and Auditor binary gate.
Offline, deterministic, no network.

Provider documentation (select_model_for_agent, see backend/app/core/llm_routing.py):
- Nexus:        provider="dynamic",   model="intent-based"   (runtime intent selection)
- Centinela:    provider="groq",      model="llama-3.1-8b-instant"
- Cerebrito:    provider="google_ai_studio", model="gemini-1.5-flash"
- Auditor:      provider="google_ai_studio", model="gemini-1.5-flash"
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal, Optional
import logging

from backend.app.agents import Nexus, Centinela, Cerebrito, Auditor
from backend.app.models import GuardrailVerdict, AuditVerdict

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Real agent instances wired in F3 T2. Deterministic stubs (F2), no network.
nexus = Nexus()
centinela = Centinela()
cerebrito = Cerebrito()
auditor = Auditor()


class ChatRequest(BaseModel):
    message: str
    intent_category: Literal[
        "TECHNICAL_PROFILE",
        "HARDWARE_SMT",
        "SOFTWARE_CASE_STUDY",
        "OFF_TOPIC",
        "PROMPT_INJECTION",
    ] = "TECHNICAL_PROFILE"


class ChatResponse(BaseModel):
    response: str
    agent: Literal[
        "Nexus", "Cerebrito", "Centinela", "Radarito", "Mensajerito", "Auditor"
    ]
    grounding_score: Optional[float] = None
    audit_status: Optional[str] = None


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Endpoint principal que enruta mensajes al orquestador Nexus.

    Chain: Centinela guardrail -> (if allowed) destination agent -> Auditor gate.
    """
    logger.info("Received chat message with intent: " + request.intent_category)

    # 1. Guardrail evaluation (Centinela)
    verdict: GuardrailVerdict = await centinela.evaluate(request.message)

    if not verdict.is_allowed:
        # Blocked by guardrail -> guardrail redirect, audit REJECTED.
        # The guardrail itself rejected the prompt, so the binary gate is
        # REJECTED regardless of the redirect text's general-output assessment.
        return ChatResponse(
            response=verdict.redirect_message
            or "Solicitud bloqueada por el guardrail.",
            agent="Centinela",
            grounding_score=None,
            audit_status="REJECTED",
        )

    # 2. Route to destination agent (Nexus routing map)
    destination = await nexus.route(request.intent_category, {})

    # 3. Get response from the destination agent
    if destination == "Cerebrito":
        payload = await cerebrito.query(request.message)
        response_text = payload.answer
        grounding_score = payload.grounding_score
        agent_name = "Cerebrito"
        agent_output = {
            "query": payload.query,
            "answer": payload.answer,
            "grounding_score": payload.grounding_score,
            "cited_sources": payload.cited_sources,
            "is_fully_grounded": payload.is_fully_grounded,
        }
        output_type = "rag"
    else:
        # Other destination agents (Centinela, etc.): generic routed response.
        response_text = "Mensaje recibido - enrutado a " + destination
        grounding_score = None
        agent_name = destination
        agent_output = {"agent": destination, "response": response_text}
        output_type = "general"

    # 4. Audit with Auditor (binary gate: APPROVED / REJECTED)
    audit: AuditVerdict = await auditor.audit(agent_output, output_type=output_type)

    return ChatResponse(
        response=response_text,
        agent=agent_name,
        grounding_score=grounding_score,
        audit_status=audit.status,
    )
