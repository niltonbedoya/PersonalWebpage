"""TDD: Auditor binary gatekeeper (F2, S3/S8).

BASELINE DEFECT (logged in odd/f2-agents-mocks.md L1): Auditor.audit()
emits "APPROVED_WITH_SANITIZATION", which is NOT a valid Literal of the
frozen AuditVerdict contract ("APPROVED"/"REJECTED" only). These tests pin
the binary gate: every scenario must end APPROVED or REJECTED — never
anything else.
"""

from backend.app.agents import Auditor
from backend.app.models import AuditVerdict


def _audit(agent: Auditor, output: dict, output_type: str = "general") -> AuditVerdict:
    import asyncio

    return asyncio.run(agent.audit(output, output_type))


def test_valid_structured_payload_approved():
    agent = Auditor()
    verdict = _audit(agent, {"schema": {"type": "object"}}, output_type="structured")

    assert verdict.status == "APPROVED"
    assert verdict.audited_agent == "Auditor"
    assert isinstance(verdict.failure_reasons, list)


def test_empty_schema_in_structured_output_rejected():
    agent = Auditor()
    verdict = _audit(agent, {"schema": {}}, output_type="structured")

    assert verdict.status == "REJECTED"
    assert "Empty schema" in verdict.failure_reasons[0]


def test_rag_below_grounding_threshold_rejected():
    agent = Auditor()
    verdict = _audit(agent, {"grounding_score": 0.50, "cited_sources": ["src1"]}, output_type="rag")

    assert verdict.status == "REJECTED"
    assert any("0.85" in r for r in verdict.failure_reasons)


def test_rag_above_threshold_with_citations_approved():
    agent = Auditor()
    verdict = _audit(
        agent,
        {"grounding_score": 0.92, "cited_sources": ["src1", "src2"]},
        output_type="rag",
    )

    assert verdict.status == "APPROVED"


def test_rag_above_threshold_but_no_citations_rejected():
    agent = Auditor()
    verdict = _audit(agent, {"grounding_score": 0.92, "cited_sources": []}, output_type="rag")

    assert verdict.status == "REJECTED"


def test_credential_pattern_in_output_rejected():
    agent = Auditor()
    verdict = _audit(
        agent,
        {"answer": "Use API key sk-1234567890abcdef to connect"},
        output_type="general",
    )

    assert verdict.status == "REJECTED"
    assert any("PII" in r or "credential" in r.lower() for r in verdict.failure_reasons)


def test_status_always_approved_or_rejected():
    agent = Auditor()
    scenarios = [
        ({"schema": {"type": "object"}}, "structured"),
        ({"schema": {}}, "structured"),
        ({"grounding_score": 0.3, "cited_sources": ["x"]}, "rag"),
        ({"grounding_score": 0.99, "cited_sources": ["x"]}, "rag"),
        ({"answer": "normal technical answer"}, "general"),
        ({"answer": "token abcdef123456 leaked"}, "general"),
        ({"answer": "contact me at user@empresa.example"}, "general"),
    ]
    for output, ot in scenarios:
        verdict = _audit(agent, output, ot)
        assert verdict.status in ("APPROVED", "REJECTED"), f"invalid status {verdict.status!r} for {output}"
        assert isinstance(verdict, AuditVerdict)
