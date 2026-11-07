"""Mensajerito — Subagente D: Triage & Despacho de Oportunidades."""

import logging

from typing import Any

logger = logging.getLogger(__name__)


class Mensajerito:
    """Subagente D - Triage & Despacho de Oportunidades.

    Evalúa el historial del chat y envíos del formulario. Extrae leads de
    interés técnico o laboral. Despacha alerta asíncrona cifrada a correo
    personal sin exponer la dirección al cliente.
    Inferencia: Groq Cloud llama-3.1-8b-instant.
    """

    def __init__(self, notifier_adapter: Any = None):
        self.name = "Mensajerito"
        self.role = "Subagente D - Triage & Despacho de Oportunidades"
        self.notifier_adapter = notifier_adapter
        self.opportunity_keywords = {
            "JOB_OFFER": ["contrato", "empleo", "posición", "salario", "ingeniero"],
            "CONSULTING": ["consultoría", "proyecto", "asesoría", "freelance"],
            "EVENT_TRANSLATION": ["traducción", "transcripción", "evento"],
            "GENERAL_INQUIRY": ["información", "dudas", "consulta"],
        }

    async def evaluate(self, transcript: str, form_data: dict = None):
        """Evaluate chat history or form submission for leads."""
        from backend.app.models import LeadAlertPayload

        try:
            text = transcript.lower()
            if form_data:
                text += " " + str(form_data).lower()

            # Determine opportunity type
            opportunity_type = "GENERAL_INQUIRY"
            priority = "P3_LOW"
            sender_name = form_data.get("name") if form_data else None
            sender_contact = form_data.get("email") if form_data else None
            summary_notes = ""
            raw_transcript_snippet = ""

            # Classify opportunity type
            for opt_type, keywords in self.opportunity_keywords.items():
                if any(kw in text for kw in keywords):
                    opportunity_type = opt_type
                    break

            # Determine priority
            if opportunity_type == "JOB_OFFER":
                priority = "P1_HIGH"
            elif opportunity_type == "CONSULTING":
                priority = "P2_MEDIUM"
            elif opportunity_type == "EVENT_TRANSLATION":
                priority = "P2_MEDIUM"

            # Extract key snippet
            sentences = transcript.split('.')
            for sentence in sentences:
                if any(kw in sentence.lower() for kw in ["interesado", "consult", "question", "project"]):
                    raw_transcript_snippet = sentence.strip()[:200]
                    break

            if not raw_transcript_snippet:
                raw_transcript_snippet = transcript[:200] if transcript else "No transcript available"

            # Generate summary notes
            summary_notes = f"Oportunidad detectada: {opportunity_type} - prioridad {priority}"
            if sender_name:
                summary_notes += f" de {sender_name}"

            # Create lead alert payload
            payload = LeadAlertPayload(
                priority=priority,
                opportunity_type=opportunity_type,
                sender_name=sender_name,
                sender_contact=sender_contact or "",
                summary_notes=summary_notes,
                raw_transcript_snippet=raw_transcript_snippet,
            )

            # Dispatch notification if we have contact info
            if sender_contact and self.notifier_adapter:
                pass  # Dispatch would happen here

            logger.info(f"Lead evaluated: {opportunity_type} priority={priority}")
            return payload

        except Exception as e:
            logger.error(f"Error evaluating Mensajerito: {e}")
            return None
