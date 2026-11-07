"""Additional API Endpoints for Agent Operations

Extends the FastAPI application with specific endpoints for each agent's 
core functionality beyond the basic routing.

Endpoints are wired to the real runtime agents from backend.app.agents (F2).
All logic is offline and deterministic: no LLM calls, no network.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any
import asyncio
import logging

from backend.app.agents import Auditor, Cerebrito, Centinela, Mensajerito, Radarito
from backend.app.core.llm_routing import select_model_for_agent

# Create router for agent-specific operations
agent_ops_router = APIRouter(prefix="/api/v1/agents", tags=["agent-operations"])

logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class AgentQuery(BaseModel):
    """Base model for agent queries."""
    query: str = Field(..., description="The query or command for the agent")
    context: Optional[Dict[str, Any]] = Field(
        None, description="Optional context information"
    )
    session_id: Optional[str] = Field(
        None, description="Optional session identifier"
    )


class AgentResponse(BaseModel):
    """Base model for agent responses."""
    agent: str = Field(..., description="Name of the agent")
    response: str = Field(..., description="Agent's response")
    status: Literal["success", "error", "pending"] = Field(
        "pending", description="Status of the operation"
    )
    grounding_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Grounding score if applicable"
    )
    cited_sources: Optional[List[str]] = Field(
        None, description="Cited sources or references"
    )


class NewsFetch(BaseModel):
    """Model for news fetch requests."""
    category: Literal["THT_SOLDERING", "SMD_INSPECTION", "AI_SOFTWARE"] = Field(
        "AI_SOFTWARE", description="News category"
    )
    limit: Optional[int] = Field(10, ge=1, le=50, description="Max results")
    time_filter: Optional[str] = Field(
        None, description="Optional time filter"
    )


class LeadEvaluation(BaseModel):
    """Model for lead evaluation requests."""
    transcript: str = Field(..., description="Chat transcript or form data")
    form_data: Optional[Dict[str, Any]] = Field(
        None, description="Optional form submission data"
    )
    priority: Literal["P1_HIGH", "P2_MEDIUM", "P3_LOW"] = Field(
        "P3_LOW", description="Priority level"
    )


# ---- Agent Operation Endpoints ----

@agent_ops_router.post("/cerebrito/query", response_model=AgentResponse)
async def cerebrito_query_endpoint(query: AgentQuery):
    """Process a technical query through Cerebrito (RAG agent).

    Provider/model: select_model_for_agent("Cerebrito") ->
    google_ai_studio / gemini-1.5-flash (zero-cost). Real agent: grounding
    score is computed from token overlap between query and context chunks.
    """
    model = select_model_for_agent("Cerebrito")
    logger.info(
        "cerebrito/query using %s/%s (primary=%s)",
        model.selected_provider,
        model.selected_model,
        model.is_fallback,
    )
    agent = Cerebrito()
    context_chunks = None
    if isinstance(query.context, dict):
        maybe_chunks = query.context.get("chunks")
        context_chunks = maybe_chunks if isinstance(maybe_chunks, list) else None
    payload = await agent.query(query.query, context_chunks)

    return AgentResponse(
        agent="Cerebrito",
        response=payload.answer,
        status="success",
        grounding_score=payload.grounding_score,
        cited_sources=list(payload.cited_sources or []),
    )


@agent_ops_router.post("/centinela/evaluate", response_model=AgentResponse)
async def centinela_evaluate_endpoint(query: AgentQuery) -> JSONResponse:
    """Evaluate a prompt through Centinela (security guardrails).

    Provider/model: select_model_for_agent("Centinela") ->
    groq / llama-3.1-8b-instant (zero-cost). Real agent: GuardrailVerdict
    with is_allowed / intent_category / risk_level / redirect_message.
    """
    prompt = query.query
    model = select_model_for_agent("Centinela")
    logger.info(
        "centinela/evaluate using %s/%s (primary=%s)",
        model.selected_provider,
        model.selected_model,
        model.is_fallback,
    )
    agent = Centinela()
    verdict = await agent.evaluate(prompt)

    blocked = not verdict.is_allowed
    base = AgentResponse(
        agent="Centinela",
        response=verdict.redirect_message
        or f"Evaluación completada: riesgo {verdict.risk_level}",
        status="error" if blocked else "success",
        grounding_score=0.0 if blocked else 1.0,
        cited_sources=[verdict.intent_category],
    ).dict()
    # "blocked" is not a Literal of AgentResponse.status, so expose it as an
    # extra payload field (JSONResponse bypasses response_model validation).
    base["status"] = "blocked" if blocked else "success"
    base["intent_category"] = verdict.intent_category
    base["risk_level"] = verdict.risk_level
    base["redirect_message"] = verdict.redirect_message

    return JSONResponse(
        content=base,
        status_code=403 if blocked else 200,
    )


@agent_ops_router.post("/radarito/fetch-news", response_model=AgentResponse)
async def radarito_fetch_news_endpoint(news_fetch: NewsFetch) -> JSONResponse:
    """Fetch curated news for a specific category via Radarito.

    Provider/model: select_model_for_agent("Radarito") ->
    cloudflare_workers_ai / qwen-2.5-7b (zero-cost, OpenRouter free fallback).
    Real agent: Radarito.synthesize_summary for the requested channel.
    """
    model = select_model_for_agent("Radarito")
    logger.info(
        "radarito/fetch-news using %s/%s (primary=%s)",
        model.selected_provider,
        model.selected_model,
        model.is_fallback,
    )
    agent = Radarito()
    summary = agent.synthesize_summary(news_fetch.category)
    items = agent.channels.get(news_fetch.category, [])
    cited_sources = [str(item.get("source_url", "")) for item in items[: news_fetch.limit]]

    return JSONResponse(
        content=AgentResponse(
            agent="Radarito",
            response=summary,
            status="success",
            grounding_score=0.95,
            cited_sources=cited_sources,
        ).dict(),
    )


@agent_ops_router.post("/mensajerito/evaluate-lead", response_model=AgentResponse)
async def mensajerito_evaluate_lead_endpoint(
    lead_eval: LeadEvaluation,
) -> JSONResponse:
    """Evaluate a lead opportunity through Mensajerito.

    Provider/model: select_model_for_agent("Mensajerito") ->
    groq / llama-3.1-8b-instant (zero-cost). Real agent: LeadAlertPayload
    with opportunity_type and priority.
    """
    model = select_model_for_agent("Mensajerito")
    logger.info(
        "mensajerito/evaluate-lead using %s/%s (primary=%s)",
        model.selected_provider,
        model.selected_model,
        model.is_fallback,
    )
    agent = Mensajerito()
    payload = await agent.evaluate(lead_eval.transcript, lead_eval.form_data or None)

    base = AgentResponse(
        agent="Mensajerito",
        response=f"Lead evaluado: {payload.opportunity_type} (prioridad {payload.priority})",
        status="success",
        grounding_score=0.9,
        cited_sources=[payload.raw_transcript_snippet]
        if payload.raw_transcript_snippet
        else [],
    ).dict()
    base["opportunity_type"] = payload.opportunity_type
    base["priority"] = payload.priority
    base["sender_name"] = payload.sender_name

    return JSONResponse(content=base)


@agent_ops_router.post("/audit/verify", response_model=AgentResponse)
async def audit_verify_endpoint(audit_data: Dict[str, Any]) -> JSONResponse:
    """Verify agent output through the Auditor binary gate.

    Provider/model: select_model_for_agent("Auditor") ->
    google_ai_studio / gemini-1.5-flash (zero-cost). Real agent: AuditVerdict
    with strict binary status APPROVED / REJECTED only. Any failure reason
    (PII/credentials leakage, RAG grounding < 0.85, empty RAG citations)
    -> REJECTED. APPROVED_WITH_SANITIZATION is never emitted.
    """
    model = select_model_for_agent("Auditor")
    logger.info(
        "audit/verify using %s/%s (primary=%s)",
        model.selected_provider,
        model.selected_model,
        model.is_fallback,
    )
    output_type = audit_data.get("output_type", "general")
    output_content = audit_data.get("output_content", "")

    agent = Auditor()
    verdict = await agent.audit(audit_data, output_type=output_type)

    approved = verdict.status == "APPROVED"
    base = AgentResponse(
        agent="Auditor",
        response=f"Auditoria {'aprobada' if approved else 'rechchada'} "
                f"({len(verdict.failure_reasons)} problema"
                f"{'s' if verdict.failure_reasons else ''})",
        status="success" if approved else "error",
        grounding_score=0.95 if approved else 0.0,
        cited_sources=list(verdict.failure_reasons or []),
    ).dict()
    base["audit_status"] = verdict.status
    base["audited_agent"] = verdict.audited_agent
    base["failure_reasons"] = list(verdict.failure_reasons or [])

    return JSONResponse(content=base)


# Include the router in the main app would be done in main.py
# app.include_router(agent_ops_router)

# For now, export the router
router_exports = {
    "agent_ops_router": agent_ops_router,
    "endpoints": [
        "/api/v1/agents/cerebrito/query",
        "/api/v1/agents/centinela/evaluate",
        "/api/v1/agents/radarito/fetch-news",
        "/api/v1/agents/mensajerito/evaluate-lead",
        "/api/v1/agents/audit/verify",
    ],
}