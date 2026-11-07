"""TDD: Contract hardening tests (F1 per docs/plan_de_fases_verificacion.md)

Negative, boundary and round-trip coverage for the 5 Pydantic v2 contracts.
The rejection IS the assertion: an expected ValidationError must happen,
so no try/except wrapping is used per the F1 exit criteria.

Method per plan: these tests pin the frozen spec contracts. A failure here
reveals a spec divergence (fix in models, keep tests green afterwards).
"""

import pytest
from pydantic import ValidationError

from backend.app.models import (
    AuditVerdict,
    GuardrailVerdict,
    LeadAlertPayload,
    NewsItemPayload,
    RAGResponsePayload,
)

VALID_NEWS = dict(
    id="test-001",
    category="THT_SOLDERING",
    title="Test Title",
    source_url="https://example.com/article",
    published_at="2024-01-01T00:00:00",
    summary="Summary",
    tags=["tag"],
)


# --- round-trip: dump -> validate -> dump is identical --------------------


def test_news_payload_round_trip():
    payload = NewsItemPayload(**VALID_NEWS)
    dumped = payload.model_dump(mode="json")
    rebuilt = NewsItemPayload.model_validate(dumped)
    assert rebuilt.model_dump(mode="json") == dumped


def test_rag_payload_round_trip():
    data = dict(
        query="q",
        answer="a",
        grounding_score=0.9,
        cited_sources=["https://example.com"],
        is_fully_grounded=True,
    )
    dumped = RAGResponsePayload(**data).model_dump(mode="json")
    assert RAGResponsePayload.model_validate(dumped).model_dump(mode="json") == dumped


# --- missing required fields are rejected (no defaults allowed) -----------


@pytest.mark.parametrize(
    "field_to_drop",
    ["id", "category", "title", "source_url", "published_at", "summary", "tags"],
)
def test_news_payload_missing_required_field_fails(field_to_drop):
    data = {k: v for k, v in VALID_NEWS.items() if k != field_to_drop}
    with pytest.raises(ValidationError):
        NewsItemPayload(**data)


@pytest.mark.parametrize("drop", [{"answer"}, {"grounding_score"}, {"cited_sources"}])
def test_rag_payload_missing_required_field_fails(drop):
    data = dict(query="q", answer="a", grounding_score=0.5, cited_sources=[], is_fully_grounded=False)
    with pytest.raises(ValidationError):
        RAGResponsePayload(**{k: v for k, v in data.items() if k not in drop})


def test_guardrail_missing_required_field_fails():
    with pytest.raises(ValidationError):
        GuardrailVerdict(is_allowed=True)  # risk_level and intent_category missing


# --- invalid Literal values are rejected -----------------------------------


def test_news_payload_invalid_category_fails():
    with pytest.raises(ValidationError):
        NewsItemPayload(**{**VALID_NEWS, "category": "NOT_A_CHANNEL"})


def test_guardrail_invalid_risk_level_fails():
    with pytest.raises(ValidationError):
        GuardrailVerdict(is_allowed=True, risk_level="INSANE", intent_category="OFF_TOPIC")


def test_audit_invalid_status_fails():
    with pytest.raises(ValidationError):
        AuditVerdict(status="MAYBE", audited_agent="Nexus")


# --- invalid types are rejected ---------------------------------------------


def test_news_payload_invalid_url_fails():
    with pytest.raises(ValidationError):
        NewsItemPayload(**{**VALID_NEWS, "source_url": "not a url"})


def test_news_payload_invalid_datetime_fails():
    with pytest.raises(ValidationError):
        NewsItemPayload(**{**VALID_NEWS, "published_at": "yesterday"})


# --- boundary values ---------------------------------------------------------


@pytest.mark.parametrize("score", [0.0, 1.0])
def test_rag_grounding_score_bounds_accept(score):
    payload = RAGResponsePayload(
        query="q", answer="a", grounding_score=score, cited_sources=[], is_fully_grounded=True
    )
    assert payload.grounding_score == score


@pytest.mark.parametrize("score", [-0.1, 1.0001])
def test_rag_grounding_score_bounds_reject(score):
    with pytest.raises(ValidationError):
        RAGResponsePayload(
            query="q", answer="a", grounding_score=score, cited_sources=[], is_fully_grounded=True
        )


def test_news_summary_300_chars_accepted():
    payload = NewsItemPayload(**{**VALID_NEWS, "summary": "x" * 300})
    assert len(payload.summary) == 300


def test_news_summary_301_chars_rejected():
    with pytest.raises(ValidationError):
        NewsItemPayload(**{**VALID_NEWS, "summary": "x" * 301})


def test_audit_failure_reasons_defaults_to_empty_list():
    verdict = AuditVerdict(status="APPROVED", audited_agent="Nexus")
    assert verdict.failure_reasons == []
    assert verdict.sanitized_payload is None


def test_lead_alert_sender_name_is_optional():
    alert = LeadAlertPayload(
        priority="P2_MEDIUM",
        opportunity_type="CONSULTING",
        sender_name=None,
        sender_contact="someone@empresa.example",
        summary_notes="notes",
        raw_transcript_snippet="snippet",
    )
    assert alert.sender_name is None


def test_guardrail_redirect_message_defaults_to_none():
    verdict = GuardrailVerdict(
        is_allowed=False, risk_level="CRITICAL", intent_category="PROMPT_INJECTION"
    )
    assert verdict.redirect_message is None
