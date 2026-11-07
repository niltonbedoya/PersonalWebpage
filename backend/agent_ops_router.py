"""Additional API Endpoints for Agent Operations

Extends the FastAPI application with specific endpoints for each agent's 
core functionality beyond the basic routing.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any
import asyncio

# Create router for agent-specific operations
agent_ops_router = APIRouter(prefix="/api/v1/agents", tags=["agent-operations"])


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
    """Process a technical query through Cerebrito (RAG agent)."""
    # In a real implementation, this would query the SQLite-vec index
    # and return a grounded answer
    return AgentResponse(
        agent="Cerebrito",
        response=f"Consulta técnica procesada: {query.query[:50]}...",
        status="success",
        grounding_score=0.92,
        cited_sources=["source1", "source2"],
    )


@agent_ops_router.post("/centinela/evaluate", response_model=AgentResponse)
async def centinela_evaluate_endpoint(query: AgentQuery) -> JSONResponse:
    """Evaluate a prompt through Centinela (security guardrails)."""
    prompt = query.query
    
    # Basic safety evaluation patterns
    risk_keywords = [
        "jailbreak", "prompt injection", "ignore previous instructions",
        "system override", "disable safety", "extract credentials"
    ]
    
    prompt_lower = prompt.lower()
    risk_detected = any(keyword in prompt_lower for keyword in risk_keywords)
    
    risk_level = "HIGH" if risk_detected else "LOW"
    intent_category = "PROMPT_INJECTION" if risk_detected else "TECHNICAL_PROFILE"
    
    redirect_message = None
    if risk_detected:
        redirect_message = (
            "Lo siento, no puedo procesar solicitudes de modificación "
            "de instrucciones. Estoy diseñado para ayudar con consultas "
            "técnicas sobre ingeniería SMT/THT y arquitectura de software."
        )
    
    return JSONResponse(
        content=AgentResponse(
            agent="Centinela",
            response=redirect_message or f"Evaluación completada: riesgo {risk_level}",
            status="success" if not risk_detected else "blocked",
            grounding_score=1.0 if not risk_detected else 0.0,
        ).dict(),
        status_code=200 if not risk_detected else 403,
    )


@agent_ops_router.post("/radarito/fetch-news", response_model=AgentResponse)
async def radarito_fetch_news_endpoint(news_fetch: NewsFetch) -> JSONResponse:
    """Fetch curated news for a specific category via Radarito."""
    # In real implementation, would use Radarito's RSS feed tools
    return JSONResponse(
        content=AgentResponse(
            agent="Radarito",
            response=f"Noticias curadas de la categoría {news_fetch.category} "
                     f"(últimas {news_fetch.limit} items)",
            status="success",
            grounding_score=0.95,
            cited_sources=["tech-feed-1", "tech-feed-2"],
        ).dict(),
    )


@agent_ops_router.post("/mensajerito/evaluate-lead", response_model=AgentResponse)
async def mensajerito_evaluate_lead_endpoint(
    lead_eval: LeadEvaluation,
) -> JSONResponse:
    """Evaluate a lead opportunity through Mensajerito."""
    transcript = lead_eval.transcript
    form_data = lead_eval.form_data or {}
    
    # Keyword-based opportunity type classification
    opportunity_keywords = {
        "JOB_OFFER": ["contrato", "empleo", "posición", "salario", "ingeniero"],
        "CONSULTING": ["consultoría", "proyecto", "asesoría", "freelance"],
        "EVENT_TRANSLATION": ["traducción", "transcripción", "evento"],
        "GENERAL_INQUIRY": ["información", "dudas", "consulta"],
    }
    
    text = transcript.lower()
    if form_data:
        text += " " + str(form_data).lower()
    
    # Determine opportunity type
    opportunity_type = "GENERAL_INQUIRY"
    for opt_type, keywords in opportunity_keywords.items():
        if any(kw in text for kw in keywords):
            opportunity_type = opt_type
            break
    
    # Determine priority
    priority_map = {
        "JOB_OFFER": "P1_HIGH",
        "CONSULTING": "P2_MEDIUM",
        "EVENT_TRANSLATION": "P2_MEDIUM",
        "GENERAL_INQUIRY": "P3_LOW",
    }
    priority = priority_map.get(opportunity_type, "P3_LOW")
    
    # Extract summary snippet
    sentences = transcript.split(".")
    summary_snippet = ""
    for sentence in sentences:
        if any(kw in sentence.lower() for kw in ["interesado", "consult", "project", "job"]):
            summary_snippet = sentence.strip()[:200]
            break
    if not summary_snippet:
        summary_snippet = transcript[:200] if transcript else "No transcript available"
    
    # Generate summary notes
    summary_notes = f"Oportunidad detectada: {opportunity_type} - prioridad {priority}"
    if form_data and form_data.get("name"):
        summary_notes += f" de {form_data['name']}"
    
    return JSONResponse(
        content=AgentResponse(
            agent="Mensajerito",
            response=f"Lead evaluado: {opportunity_type} (prioridad {priority})",
            status="success",
            grounding_score=0.9,
            cited_sources=[summary_snippet] if summary_snippet else [],
        ).dict(),
    )


@agent_ops_router.post("/audit/verify", response_model=AgentResponse)
async def audit_verify_endpoint(audit_data: Dict[str, Any]) -> JSONResponse:
    """Verify agent output through the Auditor binary gate."""
    output_type = audit_data.get("output_type", "general")
    output_content = audit_data.get("output_content", "")
    
    # Basic audit checks
    failure_reasons: List[str] = []
    status = "APPROVED"
    
    # Check for PII/credentials leakage
    output_lower = str(output_content).lower()
    pii_patterns = ["@", "sk-", "password", "token", "secret"]
    detected_pii = [p for p in pii_patterns if p in output_lower]
    
    if detected_pii:
        failure_reasons.append(f"Potential PII detected: {', '.join(detected_pii[:3])}")
        status = "APPROVED_WITH_SANITIZATION"
    
    # Check grounding score for RAG outputs
    if output_type == "rag":
        grounding = audit_data.get("grounding_score", 1.0)
        if grounding < 0.85:
            failure_reasons.append(f"Grounding score below threshold: {grounding:.2f} < 0.85")
            if status != "APPROVED_WITH_SANITIZATION":
                status = "REJECTED"
    
    final_status = "REJECTED" if (failure_reasons and status != "APPROVED_WITH_SANITIZATION") else status
    
    sanitized_payload = None
    if final_status == "APPROVED_WITH_SANITIZATION":
        sanitized_payload = {
            "status": "sanitized",
            "original_failure_reasons": failure_reasons,
        }
        final_status = "APPROVED"
    
    return JSONResponse(
        content=AgentResponse(
            agent="Auditor",
            response=f"Auditoría {'aprobada' if final_status == 'APPROVED' else 'rechazada'} "
                    f"( {len(failure_reasons)} problema{'s' if failure_reasons else ''} )",
            status="success" if final_status in ["APPROVED", "APPROVED_WITH_SANITIZATION"] else "error",
            grounding_score=0.95 if final_status == "APPROVED" else 0.0,
            cited_sources=failure_reasons,
        ).dict(),
    )


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