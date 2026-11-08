"""Contact router — Mensajerito lead triage endpoint.

Secure contact form with honeypot and antispam.
Offline, deterministic, no network.
"""

from fastapi import APIRouter
from pydantic import BaseModel, Field
import logging

from backend.app.agents import Mensajerito
from backend.app.mcp.adapters import NotifierMCPAdapter

logger = logging.getLogger(__name__)

contact_router = APIRouter(prefix="/contact", tags=["contact"])

# Deterministic notifier stub (records pending_leads). Test seam: tests swap
# in a fresh adapter via set_notifier_adapter() so each test is isolated.
notifier_adapter = NotifierMCPAdapter()


def set_notifier_adapter(adapter: NotifierMCPAdapter) -> None:
    """Replace the notifier adapter (test seam; endpoint signature unchanged)."""
    global notifier_adapter
    notifier_adapter = adapter


class ContactForm(BaseModel):
    name: str
    email: str = Field(
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        description="Contact email (validated by pattern).",
    )
    message: str
    honeypot: str = ""


class CVRequestForm(BaseModel):
    company: str = Field(..., min_length=1, description="Company or organization requesting CV")
    name: str = Field(..., min_length=1, description="Contact person name")
    phone: str = Field(..., min_length=3, description="Contact phone number")
    email: str = Field(
        pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        description="Contact email address (validated by pattern).",
    )
    reason: str = Field(..., min_length=1, description="Reason for requesting Nilton's CV")
    honeypot: str = ""


@contact_router.post("/cv-request", response_model=dict)
async def cv_request_endpoint(form: CVRequestForm):
    """Endpoint especifico para procesar solicitudes del CV de Nilton Bedoya."""
    if form.honeypot:
        logger.info("CV request blocked: honeypot field filled")
        return {"status": "blocked", "reason": "spam_detected"}

    recipient = "niltonbedoya@hotmail.com"
    transcript = (
        f"Destinatario: {recipient}. "
        f"Tipo: Solicitud de CV Oficial. "
        f"Empresa: {form.company}. "
        f"Persona de Contacto: {form.name}. "
        f"Telefono: {form.phone}. "
        f"Email: {form.email}. "
        f"Motivo: {form.reason}."
    )

    mensajerito = Mensajerito(notifier_adapter=notifier_adapter)
    payload = await mensajerito.evaluate(
        transcript,
        form_data={
            "name": form.name,
            "email": form.email,
            "company": form.company,
            "phone": form.phone,
            "reason": form.reason,
            "recipient": recipient,
            "opportunity_type": "JOB_OFFER",
        },
    )

    return {
        "status": "ok",
        "message": "Solicitud de CV registrada. Notificacion enviada a Nilton Bedoya.",
        "lead_priority": payload.priority if payload else "P1_HIGH",
    }


@contact_router.post("/", response_model=dict)
async def contact_endpoint(form: ContactForm):
    """Endpoint de contacto con honeypot y proteccion antispam."""
    if form.honeypot:
        logger.info("Contact form blocked: honeypot field filled")
        return {"status": "blocked", "reason": "spam_detected"}

    mensajerito = Mensajerito(notifier_adapter=notifier_adapter)
    transcript = f"Nombre: {form.name}. Correo: {form.email}. Mensaje: {form.message}"
    payload = await mensajerito.evaluate(transcript, form_data=form.model_dump())
    if payload is None:
        logger.error("Mensajerito evaluate returned None")
        return {"status": "error", "lead_priority": "P3_LOW"}
    return {"status": "ok", "lead_priority": payload.priority}
