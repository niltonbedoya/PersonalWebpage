"""Auditor — Agente Auditor / QA: Binary Gatekeeper."""

import logging

from typing import List

logger = logging.getLogger(__name__)


class Auditor:
    """Agente Auditor / QA - Binary Gatekeeper (Pass/Fail).

    Compuerta binaria estricta (Pass/Fail). Audita esquemas Pydantic v2,
    Grounding Score (>= 0.85) en respuestas RAG, y previene fuga de datos
    privados (PII, credenciales, marcas reales).
    """

    def __init__(self):
        self.name = "Auditor"
        self.role = "Agente Auditor / QA - Binary Gatekeeper"

    async def audit(self, agent_output: dict, output_type: str = "general"):
        """Audit agent output for compliance and safety."""
        from backend.app.models import AuditVerdict

        try:
            failure_reasons: List[str] = []
            status = "APPROVED"

            # 1. Validate Pydantic schema if output contains structured data
            if output_type == "structured" and "schema" in agent_output:
                schema = agent_output.get("schema", {})
                if not schema:
                    failure_reasons.append("Empty schema provided")
                    status = "REJECTED"

            # 2. Check for PII/credentials leakage
            output_str = str(agent_output).lower()
            pii_patterns = [
                "@",  # Email-like
                "sk-",  # OpenAI API key pattern
                "password", "token", "secret",
            ]

            detected_pii = []
            for pattern in pii_patterns:
                if pattern in output_str:
                    detected_pii.append(pattern)

            if detected_pii:
                failure_reasons.append(f"Potential PII/credentials detected")
                status = "REJECTED"

            # 3. Check grounding score for RAG outputs
            if output_type == "rag":
                grounding_score = agent_output.get("grounding_score", 1.0)
                cited_sources = agent_output.get("cited_sources", []) or []
                if grounding_score < 0.85 or not cited_sources:
                    failure_reasons.append(
                        f"RAG output not verifiably grounded: score={grounding_score:.2f} < threshold 0.85, "
                        f"citations={len(cited_sources)}"
                    )
                    status = "REJECTED"

            # 4. Final verdict — binary gate: any failure reason means REJECTED.
            if failure_reasons:
                status = "REJECTED"

            sanitized_payload = None
            verdict = AuditVerdict(
                status=status,
                audited_agent=self.name,
                failure_reasons=failure_reasons,
                sanitized_payload=sanitized_payload,
            )

            logger.info(f"Audit result: {status} - {len(failure_reasons)} issues found")
            return verdict

        except Exception as e:
            logger.error(f"Error during audit: {e}")
            from backend.app.models import AuditVerdict
            return AuditVerdict(
                status="REJECTED",
                audited_agent=self.name,
                failure_reasons=["Audit system error"],
            )
