"""TDD: Auditor resilience battery (F6, T3; specs S3, S4, S7, S8).

Covers the strict binary Auditor gate against synthetic hallucinated RAG
responses, PII/credential leaks, real brand names, and clean responses.
All offline/deterministic, no network; logs ASCII-only.
"""

import asyncio

from backend.app.agents import Auditor
from backend.app.models import AuditVerdict


def _audit(agent: Auditor, output: dict, output_type: str = "general") -> AuditVerdict:
    return asyncio.run(agent.audit(output, output_type))


# --- S3: grounding threshold on synthetic hallucinated RAG responses ---


def test_hallucinated_rag_below_grounding_threshold_rejected():
    agent = Auditor()
    verdict = _audit(
        agent,
        {"grounding_score": 0.40, "cited_sources": ["fuente-inventada"]},
        output_type="rag",
    )
    assert verdict.status == "REJECTED"
    assert any("0.85" in r for r in verdict.failure_reasons)
    assert any("threshold" in r.lower() for r in verdict.failure_reasons)


def test_rag_at_or_above_threshold_with_citations_approved():
    agent = Auditor()
    verdict = _audit(
        agent,
        {"grounding_score": 0.85, "cited_sources": ["src1", "src2"]},
        output_type="rag",
    )
    assert verdict.status == "APPROVED"


def test_rag_above_threshold_but_empty_cited_sources_rejected():
    agent = Auditor()
    verdict = _audit(
        agent,
        {"grounding_score": 0.92, "cited_sources": []},
        output_type="rag",
    )
    assert verdict.status == "REJECTED"


# --- S4: PII / credential / real brand detection ---


def test_email_pii_rejected():
    agent = Auditor()
    verdict = _audit(
        agent,
        {"answer": "Contactanos en contacto@empresa.example para mas detalles"},
        output_type="general",
    )
    assert verdict.status == "REJECTED"
    assert any("PII" in r or "credential" in r.lower() for r in verdict.failure_reasons)


def test_credential_patterns_rejected():
    agent = Auditor()
    for leak in ["sk-1234567890abcdef", "password: admin123", "token abcdef", "secret = xyz"]:
        verdict = _audit(agent, {"answer": f"Usa {leak} para conectar"}, output_type="general")
        assert verdict.status == "REJECTED", f"filtro {leak!r} no rechazado"
        assert any("PII" in r or "credential" in r.lower() for r in verdict.failure_reasons)


def test_real_brand_name_rejected():
    agent = Auditor()
    verdict = _audit(
        agent,
        {"answer": "Compra una Tesla nueva para el taller de soldadura"},
        output_type="general",
    )
    assert verdict.status == "REJECTED"
    assert any("marca" in r.lower() or "brand" in r.lower() for r in verdict.failure_reasons)


# --- clean response ---


def test_valid_clean_response_approved_with_empty_failure_reasons():
    agent = Auditor()
    verdict = _audit(
        agent,
        {"answer": "Respuesta tecnica sobre control de calidad en ensamblaje SMT."},
        output_type="general",
    )
    assert verdict.status == "APPROVED"
    assert verdict.failure_reasons == []


# --- S8: status invariant (always APPROVED or REJECTED) ---


def test_status_always_approved_or_rejected():
    agent = Auditor()
    scenarios = [
        ({"grounding_score": 0.50, "cited_sources": ["x"]}, "rag"),
        ({"grounding_score": 0.99, "cited_sources": ["x"]}, "rag"),
        ({"grounding_score": 0.99, "cited_sources": []}, "rag"),
        ({"answer": "respuesta tecnica limpia"}, "general"),
        ({"answer": "contactame a user@empresa.example"}, "general"),
        ({"answer": "usa sk-123456 para conectar"}, "general"),
        ({"answer": "compra una Apple"}, "general"),
    ]
    for output, ot in scenarios:
        verdict = _audit(agent, output, ot)
        assert verdict.status in ("APPROVED", "REJECTED"), f"estado invalido {verdict.status!r} para {output}"
        assert isinstance(verdict, AuditVerdict)


# --- S4: sanitized_payload never contains the leaked PII/credential ---


def test_sanitized_payload_never_contains_leaked_pii():
    agent = Auditor()
    leaked = "usuario@empresa.example"
    verdict = _audit(
        agent,
        {"answer": f"Escríbenos a {leaked}"},
        output_type="general",
    )
    assert verdict.status == "REJECTED"
    assert leaked not in str(verdict.sanitized_payload)
