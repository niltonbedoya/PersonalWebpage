"""TDD: Contact router (F3, S3/S8) — honeypot, lead dispatch, Pydantic 422.

FastAPI TestClient integration against the real contact router wired to
Mensajerito with a deterministic notifier stub. Offline, no network, ASCII
logs only.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.models import LeadAlertPayload
from backend.app.routers.contact import contact_router, set_notifier_adapter


def _make_app() -> FastAPI:
    app = FastAPI()
    app.include_router(contact_router)
    return app


class _TolerantNotifier:
    """Mock notifier: records pending_leads, tolerates LeadAlertPayload.

    The real NotifierMCPAdapter.dispatch_lead_notification calls .get() on the
    payload, which crashes on a pydantic v2 LeadAlertPayload (pre-existing F2
    defect, out of scope for this surface). The mock uses attribute access.
    """

    def __init__(self):
        self.pending_leads = []
        self.dispatch_calls = 0

    def dispatch_lead_notification(self, payload: LeadAlertPayload) -> None:
        self.dispatch_calls += 1
        self.pending_leads.append(payload)


@pytest.fixture
def notifier():
    """Fresh tolerant notifier per test (test seam)."""
    adapter = _TolerantNotifier()
    set_notifier_adapter(adapter)
    yield adapter
    set_notifier_adapter(_TolerantNotifier())


def _client() -> TestClient:
    return TestClient(_make_app())


# --- Honeypot: filled honeypot => blocked, zero dispatch --------------------


def test_honeypot_filled_blocks_and_no_dispatch(notifier):
    client = _client()
    resp = client.post(
        "/contact/",
        json={
            "name": "Spam Bot",
            "email": "spam@example.com",
            "message": "compra barato",
            "honeypot": "filled-by-bot",
        },
    )
    assert resp.status_code == 200
    assert resp.json() == {"status": "blocked", "reason": "spam_detected"}
    # Zero lead dispatched even though contact info was provided.
    assert notifier.pending_leads == []


# --- Valid submission: lead created, classified, dispatched -----------------


def test_valid_submission_dispatches_lead_once(notifier):
    client = _client()
    resp = client.post(
        "/contact/",
        json={
            "name": "Ana Torres",
            "email": "ana@example.com",
            "message": "Oferta de empleo para ingeniero senior, contrato a plazo.",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["lead_priority"] == "P1_HIGH"
    # Notifier dispatched exactly once.
    assert len(notifier.pending_leads) == 1
    payload = notifier.pending_leads[0]
    assert isinstance(payload, LeadAlertPayload)
    assert payload.opportunity_type == "JOB_OFFER"
    assert payload.priority == "P1_HIGH"
    assert payload.sender_name == "Ana Torres"
    assert payload.sender_contact == "ana@example.com"


def test_consulting_message_classifies_p2_medium(notifier):
    client = _client()
    resp = client.post(
        "/contact/",
        json={
            "name": "Luis",
            "email": "luis@example.com",
            "message": "Consulta sobre proyecto de consultoria SMT.",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["lead_priority"] == "P2_MEDIUM"
    assert len(notifier.pending_leads) == 1
    assert notifier.pending_leads[0].opportunity_type == "CONSULTING"


# --- sender_contact stored but never leaked into chat-facing response -------


def test_sender_contact_stored_but_not_leaked_in_response(notifier):
    client = _client()
    resp = client.post(
        "/contact/",
        json={
            "name": "Luis",
            "email": "luis@example.com",
            "message": "Duda general sobre servicios.",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    # Contact stored in the payload contract...
    assert notifier.pending_leads[0].sender_contact == "luis@example.com"
    # ...but never exposed in the chat-facing response body.
    assert "luis@example.com" not in resp.text
    assert body["lead_priority"] == "P3_LOW"


# --- Pydantic rejection -----------------------------------------------------


def test_invalid_email_returns_422(notifier):
    client = _client()
    resp = client.post(
        "/contact/",
        json={"name": "Ana", "email": "not-an-email", "message": "Hola."},
    )
    assert resp.status_code == 422
    assert notifier.pending_leads == []


def test_missing_required_field_returns_422(notifier):
    client = _client()
    resp = client.post(
        "/contact/",
        json={"email": "ana@example.com", "message": "Hola."},
    )
    assert resp.status_code == 422
    assert notifier.pending_leads == []
