"""Chat router — Nexus orchestration endpoint.

Delegates to the real Nexus agent (FSM session lifecycle + intent routing),
Centinela guardrail, Cerebrito RAG, and Auditor binary gate.
Offline, deterministic, no network.

Provider documentation (select_model_for_agent, see backend/app/core/llm_routing.py):
- Nexus:        provider="dynamic",   model="intent-based"   (runtime intent selection)
- Centinela:    provider="groq",      model="llama-3.1-8b-instant"
- Cerebrito:    provider="google_ai_studio", model="gemini-1.5-flash"
- Auditor:      provider="google_ai_studio", model="gemini-1.5-flash"
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Literal, Optional
import logging

from backend.app.agents import Nexus, Centinela, Cerebrito, Auditor
from backend.app.models import GuardrailVerdict, AuditVerdict

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

# Real agent instances wired in F3 T2. Deterministic stubs (F2), no network.
nexus = Nexus()
centinela = Centinela()
cerebrito = Cerebrito()
auditor = Auditor()


class ChatRequest(BaseModel):
    message: str
    intent_category: Literal[
        "TECHNICAL_PROFILE",
        "HARDWARE_SMT",
        "SOFTWARE_CASE_STUDY",
        "OFF_TOPIC",
        "PROMPT_INJECTION",
    ] = "TECHNICAL_PROFILE"
    language: Optional[str] = "auto"
    session_id: Optional[str] = "default"


# In-memory session tracking for multi-turn conversations and CV slot filling
chat_sessions: dict = {}


def get_chat_session(session_id: str) -> dict:
    if session_id not in chat_sessions:
        chat_sessions[session_id] = {
            "question_count": 0,
            "cv_flow": {
                "active": False,
                "company": None,
                "name": None,
                "phone": None,
                "email": None,
                "reason": None,
            },
        }
    return chat_sessions[session_id]


def is_cv_request(text: str) -> bool:
    import re
    from backend.app.core.llm_client import _normalize_text
    norm = _normalize_text(text)
    patterns = [
        r"\bcv\b",
        r"\bcurriculum\b",
        r"\bresume\b",
        r"\bhoja de vida\b",
        r"\bsolicitar cv\b",
        r"\bpedir cv\b",
        r"\benviar cv\b",
        r"\bpasame el cv\b",
        r"\bpasa el cv\b",
        r"\bquiero el cv\b",
    ]
    return any(re.search(p, norm) for p in patterns)


def is_personal_info_inquiry(text: str) -> bool:
    import re
    from backend.app.core.llm_client import _normalize_text
    norm = _normalize_text(text)
    patterns = [
        r"\bdonde vive\b",
        r"\bdonde vives\b",
        r"\btelefono personal\b",
        r"\btelefono de nilton\b",
        r"\bcuanto cobra\b",
        r"\bsalario\b",
        r"\bemail personal\b",
        r"\bcorreo personal\b",
        r"\bdireccion\b",
    ]
    return any(re.search(p, norm) for p in patterns)


class ChatResponse(BaseModel):
    response: str
    agent: Literal[
        "Nexus", "Cerebrito", "Centinela", "Radarito", "Mensajerito", "Auditor"
    ]
    grounding_score: Optional[float] = None
    audit_status: Optional[str] = None


@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Endpoint principal que enruta mensajes al orquestador Nexus.

    Chain: Centinela guardrail -> (if allowed) destination agent -> Auditor gate.
    """
    logger.info("Received chat message with intent: " + request.intent_category)

    # Detect language early
    from backend.app.core.llm_client import (
        LLMClient,
        detect_language,
        is_greeting,
        is_capability_inquiry,
        get_deterministic_greeting,
        get_deterministic_capability_intro,
        CONVERSATIONAL_SYSTEM_PROMPT,
    )
    lang = detect_language(request.message, hint=request.language)
    llm_client = LLMClient()

    # 1. Guardrail evaluation (Centinela)
    verdict: GuardrailVerdict = await centinela.evaluate(request.message)

    if not verdict.is_allowed:
        # Blocked by guardrail -> guardrail redirect, audit REJECTED.
        redirect_msg = verdict.redirect_message or "Solicitud bloqueada por el guardrail."
        if lang == "en":
            redirect_msg = (
                "I am sorry, I cannot process instruction modification requests. "
                "I am designed to assist with technical queries about SMT/THT engineering and software architecture."
            )
        return ChatResponse(
            response=redirect_msg,
            agent="Centinela",
            grounding_score=None,
            audit_status="REJECTED",
        )

    # 1.5. Session tracking & CV Request Slot-Filling Flow
    session = get_chat_session(request.session_id or "default")
    cv_flow = session["cv_flow"]

    if is_cv_request(request.message) or cv_flow["active"]:
        from backend.app.agents import Mensajerito
        from backend.app.routers.contact import notifier_adapter

        if not cv_flow["active"]:
            cv_flow["active"] = True
            cv_flow["company"] = None
            cv_flow["name"] = None
            cv_flow["phone"] = None
            cv_flow["email"] = None
            cv_flow["reason"] = None

            if lang == "en":
                response_text = (
                    "To process your request for Nilton Bedoya's official CV, please provide a few details so he can review and follow up:\n\n"
                    "1. What is the **name of your company** or organization?"
                )
            else:
                response_text = (
                    "Para tramitar la solicitud del CV oficial de Nilton Bedoya, te pediré unos datos para que él pueda contactarte:\n\n"
                    "1. ¿Cuál es el **nombre de tu empresa** u organización?"
                )
            agent_output = {"agent": "Nexus", "response": response_text}
            audit: AuditVerdict = await auditor.audit(agent_output, output_type="general")
            return ChatResponse(
                response=response_text,
                agent="Nexus",
                grounding_score=1.0,
                audit_status=audit.status,
            )

        # Slot filling turn: fill the next missing slot
        msg_clean = request.message.strip()
        if cv_flow["company"] is None:
            cv_flow["company"] = msg_clean
        elif cv_flow["name"] is None:
            cv_flow["name"] = msg_clean
        elif cv_flow["phone"] is None:
            cv_flow["phone"] = msg_clean
        elif cv_flow["email"] is None:
            cv_flow["email"] = msg_clean
        elif cv_flow["reason"] is None:
            cv_flow["reason"] = msg_clean

        # Now check which slot is still missing
        if cv_flow["company"] is None:
            prompt = (
                "1. What is the **name of your company**?"
                if lang == "en"
                else "1. ¿Cuál es el **nombre de la empresa**?"
            )
        elif cv_flow["name"] is None:
            prompt = (
                "Thank you. 2. What is the **contact person's name**?"
                if lang == "en"
                else "Gracias. 2. ¿Cuál es el **nombre de la persona de contacto**?"
            )
        elif cv_flow["phone"] is None:
            prompt = (
                "Understood. 3. What is your **contact phone number**?"
                if lang == "en"
                else "Entendido. 3. ¿Un **número de teléfono** de contacto?"
            )
        elif cv_flow["email"] is None:
            prompt = (
                "Great. 4. What is your **contact email address**?"
                if lang == "en"
                else "Perfecto. 4. ¿Cuál es tu **correo electrónico**?"
            )
        elif cv_flow["reason"] is None:
            prompt = (
                "Lastly, 5. What is the **reason for requesting the CV** (job offer, consulting, project)?"
                if lang == "en"
                else "Por último, 5. ¿Cuál es el **motivo de la solicitud** de CV (oferta de empleo, proyecto, consultoría)?"
            )
        else:
            # All 5 slots collected! Dispatch email notification
            mensajerito = Mensajerito(notifier_adapter=notifier_adapter)
            transcript = (
                f"Destinatario: niltonbedoya@hotmail.com. "
                f"Tipo: Solicitud de CV Oficial via Chat RAG. "
                f"Empresa: {cv_flow['company']}. "
                f"Persona de Contacto: {cv_flow['name']}. "
                f"Telefono: {cv_flow['phone']}. "
                f"Email: {cv_flow['email']}. "
                f"Motivo: {cv_flow['reason']}."
            )
            await mensajerito.evaluate(
                transcript,
                form_data={
                    "name": cv_flow["name"],
                    "email": cv_flow["email"],
                    "company": cv_flow["company"],
                    "phone": cv_flow["phone"],
                    "reason": cv_flow["reason"],
                    "recipient": "niltonbedoya@hotmail.com",
                    "opportunity_type": "JOB_OFFER",
                },
            )

            # Reset flow
            cv_flow["active"] = False
            cv_flow["company"] = None
            cv_flow["name"] = None
            cv_flow["phone"] = None
            cv_flow["email"] = None
            cv_flow["reason"] = None

            if lang == "en":
                prompt = (
                    "Thank you very much! I have gathered all your details and sent a direct notification to Nilton Bedoya. "
                    "Nilton will review the request and get in touch with you shortly."
                )
            else:
                prompt = (
                    "¡Muchas gracias! He recopilado todos los datos y enviado la solicitud de CV directamente a Nilton Bedoya. "
                    "Nilton revisará la información y se pondrá en contacto contigo a la brevedad."
                )

        agent_output = {"agent": "Nexus", "response": prompt}
        audit: AuditVerdict = await auditor.audit(agent_output, output_type="general")
        return ChatResponse(
            response=prompt,
            agent="Nexus",
            grounding_score=1.0,
            audit_status=audit.status,
        )

    # Increment question count for normal conversation
    session["question_count"] += 1

    def _maybe_append_cv_note(text: str) -> str:
        if session["question_count"] >= 5 or is_personal_info_inquiry(request.message):
            if lang == "en":
                note = (
                    "\n\n*(Notice: If you are interested in Nilton's full profile or would like to discuss an opportunity, "
                    "you can request his official CV directly in this chat or via the contact form).*"
                )
            else:
                note = (
                    "\n\n*(Nota: Si deseas consultar la trayectoria completa o información personal de Nilton Bedoya, "
                    "puedes solicitar directamente su CV oficial en este chat o mediante el formulario de contacto).*"
                )
            if note not in text:
                return text + note
        return text

    # 2. Check for conversational openers (greetings / bot capability questions)
    lang_prompt = f"Respond in {('English' if lang == 'en' else 'Spanish')}. Keep it concise.\n\n" + CONVERSATIONAL_SYSTEM_PROMPT

    if is_greeting(request.message):
        live_response = None
        if llm_client.has_live_llm():
            live_response = await llm_client.generate_response(request.message, system_prompt=lang_prompt)
        response_text = live_response or get_deterministic_greeting(lang=lang)
        response_text = _maybe_append_cv_note(response_text)
        agent_output = {"agent": "Nexus", "response": response_text}
        audit: AuditVerdict = await auditor.audit(agent_output, output_type="general")
        return ChatResponse(
            response=response_text,
            agent="Nexus",
            grounding_score=1.0,
            audit_status=audit.status,
        )

    if is_capability_inquiry(request.message):
        live_response = None
        if llm_client.has_live_llm():
            live_response = await llm_client.generate_response(request.message, system_prompt=lang_prompt)
        response_text = live_response or get_deterministic_capability_intro(lang=lang)
        response_text = _maybe_append_cv_note(response_text)
        agent_output = {"agent": "Nexus", "response": response_text}
        audit: AuditVerdict = await auditor.audit(agent_output, output_type="general")
        return ChatResponse(
            response=response_text,
            agent="Nexus",
            grounding_score=1.0,
            audit_status=audit.status,
        )

    # 3. Route to destination agent (Nexus routing map)
    destination = await nexus.route(request.intent_category, {})

    # 4. Get response from the destination agent
    if destination == "Cerebrito":
        payload = await cerebrito.query(request.message)
        grounding_score = payload.grounding_score
        agent_name = "Cerebrito"
        agent_output = {
            "query": payload.query,
            "answer": payload.answer,
            "grounding_score": payload.grounding_score,
            "cited_sources": payload.cited_sources,
            "is_fully_grounded": payload.is_fully_grounded,
        }
        output_type = "rag"
        if payload.is_fully_grounded:
            if lang == "en" and llm_client.has_live_llm():
                # Synthesize / translate technical answer into English
                translated = await llm_client.generate_response(
                    f"Translate and synthesize this technical answer accurately into English in 2-3 lines: {payload.answer}",
                    rag_context="\n".join(c.get("content", "") for c in payload.cited_sources) if payload.cited_sources else None,
                    system_prompt=lang_prompt,
                )
                response_text = translated or payload.answer
            else:
                response_text = payload.answer
            output_type = "rag"
        else:
            live_response = None
            if llm_client.has_live_llm():
                live_response = await llm_client.generate_response(
                    request.message,
                    rag_context="\n".join(c.get("content", "") for c in payload.cited_sources) if payload.cited_sources else None,
                    system_prompt=lang_prompt,
                )
            if live_response:
                response_text = live_response
                output_type = "general"
                agent_output = {"agent": "Nexus", "response": response_text}
                agent_name = "Nexus"
                grounding_score = 1.0
            else:
                if lang == "en":
                    response_text = (
                        "I do not have specific details on that topic in the verified corpus.\n\n"
                        "To explore Nilton Bedoya's technical experience, I suggest asking about:\n"
                        "• SMT/THT Electronics (Parmi/Marantz 3D inspection, Matrix X-Ray, Ersa reflow ovens).\n"
                        "• Software & AI (Tire Counter, Service Ticketing, CardioNutri, commercial ERP).\n"
                        "• Zero-cost Gentle-AI architecture and methodology.\n\n"
                        "Would you like to know more about any of these topics?"
                    )
                else:
                    response_text = (
                        "No dispongo de detalles específicos sobre ese punto en el corpus verificado.\n\n"
                        "Para conocer la experiencia técnica de Nilton Bedoya, te sugiero consultar sobre:\n"
                        "• Electrónica SMT/THT (Inspección 3D Parmi/Marantz, Rayos X Matrix, hornos Ersa).\n"
                        "• Software & AI (Proyectos Tire Counter, Servicio de Tickets, CardioNutri, KRONENBLUMEN).\n"
                        "• Arquitectura y Metodología Gentle-AI de costo cero.\n\n"
                        "¿Te gustaría consultar sobre alguno de estos temas?"
                    )
                output_type = "rag"
    else:
        # Other destination agents (Centinela, etc.): generic routed response.
        response_text = "Mensaje recibido - enrutado a " + destination
        grounding_score = None
        agent_name = destination
        agent_output = {"agent": destination, "response": response_text}
        output_type = "general"

    # 4.5. Append CV suggestion if user asks personal details or exceeds 5 questions
    response_text = _maybe_append_cv_note(response_text)
    if isinstance(agent_output, dict):
        if "response" in agent_output:
            agent_output["response"] = response_text
        elif "answer" in agent_output:
            agent_output["answer"] = response_text

    # 5. Audit with Auditor (binary gate: APPROVED / REJECTED)
    audit: AuditVerdict = await auditor.audit(agent_output, output_type=output_type)

    return ChatResponse(
        response=response_text,
        agent=agent_name,
        grounding_score=grounding_score,
        audit_status=audit.status,
    )
