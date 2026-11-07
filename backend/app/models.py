"""Pydantic v2 Models for Multi-Agent Contracts

This module defines all the data contracts used by the multi-agent framework.
Each model is validated against the specifications in the architecture document.

Models:
- NewsItemPayload: News item from Radarito feed curation
- RAGResponsePayload: Technical query response from Cerebrito motor RAG
- GuardrailVerdict: Safety verdict from Centinela guardrails
- LeadAlertPayload: Lead detection from Mensajerito triage
- AuditVerdict: Binary quality gate from Auditor QA
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import Literal, Optional, List
from datetime import datetime


class NewsItemPayload(BaseModel):
    """Payload for technical news items curated by Radarito."""
    id: str
    """Unique identifier for the news item."""
    category: Literal["THT_SOLDERING", "SMD_INSPECTION", "AI_SOFTWARE"]
    """Source category: THT_SOLDERING, SMD_INSPECTION, or AI_SOFTWARE."""
    title: str
    """Headline title of the news item."""
    source_url: HttpUrl
    """URL source of the original news article."""
    published_at: datetime
    """ISO 8601 publication timestamp."""
    summary: str = Field(..., max_length=300)
    """Brief summary of the news item (max 300 chars)."""
    tags: List[str]
    """List of tags for categorization and filtering."""


class RAGResponsePayload(BaseModel):
    """Payload for RAG technical queries answered by Cerebrito."""
    query: str
    """The user's technical query string."""
    answer: str
    """The generated answer based on the indexed corpus."""
    grounding_score: float = Field(..., ge=0.0, le=1.0)
    """Grounding score (0.0 to 1.0) verifying source attribution."""
    cited_sources: List[str]
    """List of source identifiers or URLs that support the answer."""
    is_fully_grounded: bool
    """Whether the answer is fully grounded in the provided sources."""


class GuardrailVerdict(BaseModel):
    """Verdict from Centinela's perimetral guardrail interception."""
    is_allowed: bool
    """Whether the request is permitted to proceed."""
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    """Risk level assessment of the query intent."""
    intent_category: Literal[
        "TECHNICAL_PROFILE",
        "HARDWARE_SMT",
        "SOFTWARE_CASE_STUDY",
        "OFF_TOPIC",
        "PROMPT_INJECTION",
    ]
    """Category of user intent detected."""
    redirect_message: Optional[str] = None
    """Optional message to redirect the user if off-topic or blocked."""


class LeadAlertPayload(BaseModel):
    """Payload for lead opportunities detected by Mensajerito."""
    priority: Literal["P1_HIGH", "P2_MEDIUM", "P3_LOW"]
    """Priority level of the detected opportunity."""
    opportunity_type: Literal[
        "JOB_OFFER",
        "CONSULTING",
        "EVENT_TRANSLATION",
        "GENERAL_INQUIRY",
    ]
    """Type of opportunity identified."""
    sender_name: Optional[str]
    """Optional name of the person who sent the inquiry."""
    sender_contact: str
    """Contact information (email or messaging handle)."""
    summary_notes: str
    """Structured summary of the opportunity details."""
    raw_transcript_snippet: str
    """Raw text excerpt from the conversation or form submission."""


class AuditVerdict(BaseModel):
    """Binary verdict from the Auditor QA gatekeeper."""
    status: Literal["APPROVED", "REJECTED"]
    """Pass/Fail decision on the audited agent output."""
    audited_agent: str
    """Name of the agent whose output was audited."""
    failure_reasons: List[str] = []
    """List of failure reasons if status is REJECTED."""
    sanitized_payload: Optional[dict] = None
    """Optional sanitized version of the payload if approved with modifications."""