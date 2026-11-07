"""TDD: Mensajerito lead-triage agent (F2, S2/S6/S9).

Lead classification from transcript/form, priority by opportunity type,
mock notifier dispatch, and sender_contact never leaked into chat-facing
output. No network, no LLM calls — deterministic heuristic test.
"""

import asyncio

import pytest

from backend.app.agents import Mensajerito
from backend.app.core.llm_routing import select_model_for_agent
from backend.app.models import LeadAlertPayload


class _FakeNotifier:
    """Deterministic mock notifier adapter for Mensajerito dispatch tests."""

    def __init__(self):
        self.pending_leads = []
        self.dispatch_calls = 0

    def dispatch_lead_notification(self, payload: LeadAlertPayload) -> None:
        self.dispatch_calls += 1
        self.pending_leads.append(payload)


def _evaluate(agent: Mensajerito, transcript: str, form_data: dict = None):
    return asyncio.run(agent.evaluate(transcript, form_data))


# --- Lead classification battery ------------------------------------------


def test_job_offer_transcript_classifies_p1_high():
    agent = Mensajerito()
    payload = _evaluate(agent, "Busco ingeniero para contrato a tiempo completo, oferta de empleo.")

    assert payload.opportunity_type == "JOB_OFFER"
    assert payload.priority == "P1_HIGH"


def test_consulting_transcript_classifies_p2_medium():
    agent = Mensajerito()
    payload = _evaluate(agent, "Necesito una consultoria para un proyecto de asesoria industrial.")

    assert payload.opportunity_type == "CONSULTING"
    assert payload.priority == "P2_MEDIUM"


def test_event_translation_transcript_classifies_p2_medium():
    agent = Mensajerito()
    payload = _evaluate(agent, "Se requiere traduccion para el evento de soldadura.")

    assert payload.opportunity_type == "EVENT_TRANSLATION"
    assert payload.priority == "P2_MEDIUM"


def test_general_inquiry_default_p3_low():
    agent = Mensajerito()
    payload = _evaluate(agent, "Hola, buenos dias, como esta usted.")

    assert payload.opportunity_type == "GENERAL_INQUIRY"
    assert payload.priority == "P3_LOW"


# --- LeadAlertPayload contract conformance --------------------------------


def test_lead_alert_payload_is_conformant():
    agent = Mensajerito()
    payload = _evaluate(
        agent,
        "Oferta de empleo para ingeniero senior.",
        form_data={"name": "Ana Torres", "email": "ana@example.com"},
    )

    assert isinstance(payload, LeadAlertPayload)
    assert payload.priority in ("P1_HIGH", "P2_MEDIUM", "P3_LOW")
    assert payload.opportunity_type in (
        "JOB_OFFER",
        "CONSULTING",
        "EVENT_TRANSLATION",
        "GENERAL_INQUIRY",
    )
    assert payload.sender_name == "Ana Torres"
    assert payload.sender_contact == "ana@example.com"


def test_evaluate_without_form_data_still_returns_payload():
    agent = Mensajerito()
    payload = _evaluate(agent, "Ingeniero busca contrato.")

    assert isinstance(payload, LeadAlertPayload)
    assert payload.sender_name is None
    assert payload.sender_contact == ""


# --- sender_contact must never leak into chat-facing output ---------------


def test_sender_contact_stored_but_not_in_summary_notes():
    agent = Mensajerito()
    payload = _evaluate(
        agent,
        "Proyecto de consultoria SMT.",
        form_data={"name": "Luis", "email": "luis@example.com"},
    )

    # Contact is stored in the payload contract field...
    assert payload.sender_contact == "luis@example.com"
    # ...but never exposed in the chat-facing summary notes.
    assert "luis@example.com" not in payload.summary_notes
    assert payload.sender_contact not in payload.summary_notes


# --- Mock notifier dispatch -----------------------------------------------


def test_notifier_dispatch_called_once_when_contact_present():
    notifier = _FakeNotifier()
    agent = Mensajerito(notifier_adapter=notifier)
    payload = _evaluate(
        agent,
        "Oferta de empleo para ingeniero.",
        form_data={"name": "Ana", "email": "ana@example.com"},
    )

    assert notifier.dispatch_calls == 1
    assert len(notifier.pending_leads) == 1
    assert notifier.pending_leads[0] is payload


def test_notifier_not_called_when_no_contact():
    notifier = _FakeNotifier()
    agent = Mensajerito(notifier_adapter=notifier)
    payload = _evaluate(agent, "Solo una duda sobre sus servicios.")

    assert notifier.dispatch_calls == 0
    assert notifier.pending_leads == []
    assert isinstance(payload, LeadAlertPayload)


# --- Provider/model assignment (documented via routing table) -------------


def test_mensajerito_provider_is_groq_llama_3_1_8b_instant():
    # Mensajerito is assigned Groq llama-3.1-8b-instant (fallback
    # llama-3.1-70b-instant) per select_model_for_agent("Mensajerito").
    result = select_model_for_agent("Mensajerito")

    assert result.selected_provider == "groq"
    assert result.selected_model == "llama-3.1-8b-instant"
    assert result.is_fallback is False
