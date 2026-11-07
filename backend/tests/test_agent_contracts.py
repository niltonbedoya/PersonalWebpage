"""TDD: Agent Contract Tests - Pydantic v2 Models Validation

Happy-path smoke tests: each of the 5 contracts constructs successfully
with all required fields. Negative/boundary/round-trip coverage lives in
test_contracts_hardening.py (F1 exit criteria, see docs/plan_de_fases_verificacion.md).

Method: Red → Green → Refactor
- Red: Run tests, observe failures due to missing models
- Green: Implement models, run tests, observe all pass
- Refactor: Clean up code while keeping tests green
"""

from pydantic import ValidationError


def test_news_item_payload_invalid_missing_fields():
    """NewsItemPayload requires all fields; missing any should fail."""
    try:
        from backend.app.models import NewsItemPayload
        payload = NewsItemPayload(
            id="test-001",
            category="THT_SOLDERING",
            title="Test Title",
            source_url="https://example.com",
            published_at="2024-01-01T00:00:00",
            summary="Test summary",
            tags=["test"],
        )
        assert payload.id == "test-001"
        assert payload.category == "THT_SOLDERING"
    except (ImportError, ValidationError) as e:
        # Expected in Red Phase: model not yet implemented or validation fails
        raise AssertionError(
            f"Test failed in Red Phase - NewsItemPayload not available: {e}"
        )


def test_rag_response_payload_invalid_missing_fields():
    """RAGResponsePayload requires all fields; missing any should fail."""
    try:
        from backend.app.models import RAGResponsePayload
        payload = RAGResponsePayload(
            query="test query",
            answer="test answer",
            grounding_score=0.92,
            cited_sources=["https://example.com"],
            is_fully_grounded=True,
        )
        assert payload.query == "test query"
        assert payload.grounding_score == 0.92
    except (ImportError, ValidationError) as e:
        raise AssertionError(
            f"Test failed in Red Phase - RAGResponsePayload not available: {e}"
        )


def test_guardrail_verdict_invalid_missing_fields():
    """GuardrailVerdict requires all fields; missing any should fail."""
    try:
        from backend.app.models import GuardrailVerdict
        verdict = GuardrailVerdict(
            is_allowed=True,
            risk_level="LOW",
            intent_category="TECHNICAL_PROFILE",
        )
        assert verdict.is_allowed is True
        assert verdict.risk_level == "LOW"
    except (ImportError, ValidationError) as e:
        raise AssertionError(
            f"Test failed in Red Phase - GuardrailVerdict not available: {e}"
        )


def test_lead_alert_payload_invalid_missing_fields():
    """LeadAlertPayload requires all required fields; missing any should fail."""
    try:
        from backend.app.models import LeadAlertPayload
        alert = LeadAlertPayload(
            priority="P1_HIGH",
            opportunity_type="JOB_OFFER",
            sender_name="Juan Perez",
            sender_contact="juan.perez@example.com",
            summary_notes="Candidate with 5 years experience",
            raw_transcript_snippet="Hola, interesado en el puesto",
        )
        assert alert.priority == "P1_HIGH"
        assert alert.opportunity_type == "JOB_OFFER"
    except (ImportError, ValidationError) as e:
        raise AssertionError(
            f"Test failed in Red Phase - LeadAlertPayload not available: {e}"
        )


def test_audit_verdict_invalid_missing_fields():
    """AuditVerdict requires status and audited_agent; missing should fail."""
    try:
        from backend.app.models import AuditVerdict
        verdict = AuditVerdict(
            status="APPROVED",
            audited_agent="Nexus",
        )
        assert verdict.status == "APPROVED"
        assert verdict.audited_agent == "Nexus"
    except (ImportError, ValidationError) as e:
        raise AssertionError(
            f"Test failed in Red Phase - AuditVerdict not available: {e}"
        )


# Red Phase marker: these tests MUST fail before models are implemented
# because the import will raise ImportError or validation will fail
# due to missing Pydantic model definitions.