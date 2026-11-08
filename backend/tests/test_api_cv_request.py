"""TDD: CV Request form and multi-turn conversational slot filling (S1-S5).

Tests:
1. POST /contact/cv-request validates company, name, phone, email, reason.
2. Honeypot blocks /contact/cv-request with 200 and spam_detected.
3. Successful /contact/cv-request dispatches formatted email notification to notifier_adapter.
4. Missing required field in /contact/cv-request returns 422.
5. In /chat, inquiring about CV triggers step-by-step questions until all 5 fields are collected.
6. Once all 5 fields are gathered via chat, notification is dispatched and user is confirmed.
7. After 5 questions in /chat, the assistant invites the user to request the official CV.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.app.routers.contact import set_notifier_adapter
from backend.app.models import LeadAlertPayload


class _MockNotifier:
    def __init__(self):
        self.dispatched = []

    def dispatch_lead_notification(self, payload) -> None:
        self.dispatched.append(payload)


@pytest.fixture
def mock_notifier():
    notifier = _MockNotifier()
    set_notifier_adapter(notifier)
    yield notifier
    set_notifier_adapter(_MockNotifier())


@pytest.fixture
def client():
    return TestClient(app)


# --- 1. POST /contact/cv-request endpoints -----------------------------------

def test_cv_request_success_dispatches_notification(client, mock_notifier):
    payload = {
        "company": "Tech Innovations SL",
        "name": "Carlos Gomez",
        "phone": "+34 600 123 456",
        "email": "cgomez@techinnovations.es",
        "reason": "Interesados en perfil de Nilton para puesto de Lead Industrial SMT y Software AI.",
    }
    response = client.post("/contact/cv-request", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "notificación" in data["message"].lower() or "notificacion" in data["message"].lower() or "registrada" in data["message"].lower()

    # Verify notifier received the lead with target email mentioned in raw transcript / notes
    assert len(mock_notifier.dispatched) == 1
    dispatched_lead = mock_notifier.dispatched[0]
    assert dispatched_lead.sender_contact == "cgomez@techinnovations.es"
    assert "Tech Innovations SL" in dispatched_lead.raw_transcript_snippet or "Tech Innovations SL" in dispatched_lead.summary_notes
    assert "niltonbedoya@hotmail.com" in dispatched_lead.summary_notes or "niltonbedoya@hotmail.com" in dispatched_lead.raw_transcript_snippet


def test_cv_request_honeypot_blocks_submission(client, mock_notifier):
    payload = {
        "company": "Spam Corp",
        "name": "Bot",
        "phone": "0000000",
        "email": "bot@spam.com",
        "reason": "Buy crypto",
        "honeypot": "spam-trap",
    }
    response = client.post("/contact/cv-request", json=payload)
    assert response.status_code == 200
    assert response.json() == {"status": "blocked", "reason": "spam_detected"}
    assert len(mock_notifier.dispatched) == 0


def test_cv_request_missing_field_returns_422(client):
    payload = {
        "company": "Incomplete SA",
        "name": "Ana",
        # missing phone, email, reason
    }
    response = client.post("/contact/cv-request", json=payload)
    assert response.status_code == 422


def test_cv_request_invalid_email_returns_422(client):
    payload = {
        "company": "Tech Corp",
        "name": "Ana",
        "phone": "123456789",
        "email": "not-an-email",
        "reason": "Recruitment",
    }
    response = client.post("/contact/cv-request", json=payload)
    assert response.status_code == 422


# --- 2. Conversational Slot-Filling in /chat ----------------------------------

def test_chat_cv_inquiry_starts_slot_filling_flow(client):
    session_id = "test-session-cv-1"
    
    # User asks for CV
    resp1 = client.post("/chat/", json={"message": "¿Me puedes pasar el CV de Nilton?", "session_id": session_id})
    assert resp1.status_code == 200
    body1 = resp1.json()
    assert body1["audit_status"] == "APPROVED"
    assert "empresa" in body1["response"].lower() or "company" in body1["response"].lower()

    # User gives company
    resp2 = client.post("/chat/", json={"message": "Trabajo en SMT Manufacturing Europa", "session_id": session_id})
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["audit_status"] == "APPROVED"
    assert "nombre" in body2["response"].lower() or "contacto" in body2["response"].lower()

    # User gives name
    resp3 = client.post("/chat/", json={"message": "Me llamo Laura Martínez", "session_id": session_id})
    assert resp3.status_code == 200
    body3 = resp3.json()
    assert body3["audit_status"] == "APPROVED"
    assert "teléfono" in body3["response"].lower() or "telefono" in body3["response"].lower() or "phone" in body3["response"].lower()

    # User gives phone
    resp4 = client.post("/chat/", json={"message": "+34 611 222 333", "session_id": session_id})
    assert resp4.status_code == 200
    body4 = resp4.json()
    assert body4["audit_status"] == "APPROVED"
    assert "correo" in body4["response"].lower() or "email" in body4["response"].lower()

    # User gives email
    resp5 = client.post("/chat/", json={"message": "laura.martinez@smteuropa.com", "session_id": session_id})
    assert resp5.status_code == 200
    body5 = resp5.json()
    assert body5["audit_status"] == "APPROVED"
    assert "motivo" in body5["response"].lower() or "reason" in body5["response"].lower()

    # User gives reason
    resp6 = client.post("/chat/", json={"message": "Estamos buscando un especialista para liderar la línea de inspección 3D y automatización.", "session_id": session_id})
    assert resp6.status_code == 200
    body6 = resp6.json()
    assert body6["audit_status"] == "APPROVED"
    assert "nilton" in body6["response"].lower()
    # Auditor must NOT reject (no @ in response)
    assert "@" not in body6["response"]


def test_chat_suggests_cv_after_five_questions(client):
    session_id = "test-session-5q"
    # Send 5 technical/profile questions
    questions = [
        "¿Qué experiencia tiene Nilton con Parmi?",
        "¿Y con rayos X de Matrix?",
        "¿Qué hornos de refusión conoce?",
        "¿Tiene experiencia en visión artificial?",
        "¿Qué proyectos de software ha desarrollado?",
    ]
    last_resp = None
    for q in questions:
        last_resp = client.post("/chat/", json={"message": q, "session_id": session_id})
        assert last_resp.status_code == 200

    # The 5th response should invite the user to request the official CV
    assert "cv" in last_resp.json()["response"].lower() or "currículum" in last_resp.json()["response"].lower()
