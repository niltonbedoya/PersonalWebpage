"""Zero-cost LLM Client for Showcase Platform (Groq / Gemini Flash).

Supports:
- Groq Cloud (llama-3.1-8b-instant, zero-cost free tier)
- Google AI Studio (gemini-1.5-flash, zero-cost free tier)
- Deterministic dialogic fallback when offline or no API keys configured.
"""

import os
import re
import unicodedata
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)

# System prompt for conversational guiding
CONVERSATIONAL_SYSTEM_PROMPT = """Eres el asistente interactivo del portfolio profesional de Nilton Bedoya (Showcase Platform).
Tu objetivo es dialogar cordialmente y orientar a reclutadores, ingenieros y colaboradores tecnicos.

Reglas obligatorias:
1. Conciso: Responde en 2 a 4 lineas maximo en estilo conversacional fluido y natural. Evita parrafadas densas.
2. Saludos: Si el usuario saluda, responde calidamente e invitalo a explorar:
   - Spoke Electronica SMT/THT: Inspeccion optica 3D (Parmi/Marantz), Rayos X (Matrix), Calibracion Nordson BT, hornos Ersa.
   - Spoke Software & AI: ERP comercial, Tire Counter (vision AI), CardioNutri, Service Ticketing, arquitecturas multiagente.
3. Consultas tecnicas: Si recibes contexto RAG, responde basandote en el. Si no hay contexto o es charla general, responde educadamente y reconduce con preguntas hacia los proyectos de Nilton.
4. Limites de alcance:
   - Exclusion estricta: Nilton NO trabaja con maquinaria de insercion Pick & Place. Si preguntan, aclara amablemente la exclusion.
   - Escribe siempre 'AI', nunca 'IA'.
   - Jamas reveles datos personales privados, credenciales ni nombres de empresas cliente reales.
"""

BASE_DIR = Path(__file__).resolve().parent.parent.parent


def _normalize_text(text: str) -> str:
    """Strip accents, lowercase, and remove special characters."""
    nfkd = unicodedata.normalize("NFKD", text)
    ascii_text = "".join(c for c in nfkd if not unicodedata.combining(c)).lower()
    return re.sub(r"[^\w\s]", " ", ascii_text).strip()


def _load_env_file() -> None:
    """Best-effort parser for .env in project root without external dependencies."""
    env_path = BASE_DIR / ".env"
    if env_path.exists():
        try:
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    key = key.strip()
                    val = val.strip().strip('"').strip("'")
                    if key and key not in os.environ:
                        os.environ[key] = val
        except Exception as e:
            logger.warning("Could not read .env file: %s", e)


_load_env_file()


def is_greeting(message: str) -> bool:
    """Check if the user message is a greeting or casual opener."""
    cleaned = _normalize_text(message)
    tokens = [w for w in cleaned.split() if w]
    if not tokens:
        return False

    greeting_starters = {
        "hola", "buenas", "buenos", "saludos", "hey", "hi", "hello"
    }
    if tokens[0] in greeting_starters and len(tokens) <= 6:
        return True

    small_talk = {
        "hola", "buenas", "buenos", "dias", "tardes", "noches", "hey",
        "saludos", "hi", "hello", "que", "tal", "como", "estas", "va",
        "amigo", "asistente", "bot"
    }
    return set(tokens).issubset(small_talk)


def is_capability_inquiry(message: str) -> bool:
    """Check if the user is asking about the bot's identity or capabilities."""
    cleaned = _normalize_text(message)
    capability_phrases = [
        "quien eres", "que eres", "que haces", "que puedes hacer",
        "en que me ayudas", "para que sirves", "que sabes hacer",
        "que sabes", "quien sos", "who are you", "what can you do",
        "help", "ayuda", "como funciona", "como me puedes ayudar"
    ]
    return any(p in cleaned for p in capability_phrases)


def get_deterministic_greeting() -> str:
    """Friendly conversational response for greetings when offline."""
    return (
        "¡Hola! Soy el asistente técnico del portfolio de Nilton Bedoya. "
        "Puedo orientarte sobre sus procesos de ingeniería SMT/THT (inspección 3D, rayos X, soldadura), "
        "casos de estudio de software & AI, o sus proyectos en GitHub.\n\n"
        "¿Qué área te gustaría conocer primero?"
    )


def get_deterministic_capability_intro() -> str:
    """Guided response for capability and identity questions when offline."""
    return (
        "Soy un asistente técnico multiagente diseñado para guiarte por el portfolio de Nilton Bedoya:\n\n"
        "• Electrónica Industrial: Inspección 3D (Parmi/Marantz), Rayos X (Matrix), calibración Nordson BT y soldadura SMT/THT.\n"
        "• Software & AI: Casos prácticos de ERP, visión artificial (Tire Counter), apps biométricas y metodologías limpias.\n\n"
        "Puedes hacerme cualquier pregunta técnica directa o sobre su trayectoria profesional."
    )


class LLMClient:
    """Async client for zero-cost LLMs (Groq / Gemini) with offline fallback."""

    def __init__(self, timeout: float = 8.0):
        self.timeout = timeout

    @property
    def groq_api_key(self) -> Optional[str]:
        _load_env_file()
        return os.environ.get("GROQ_API_KEY")

    @property
    def gemini_api_key(self) -> Optional[str]:
        _load_env_file()
        return os.environ.get("GEMINI_API_KEY")

    def has_live_llm(self) -> bool:
        return bool(self.groq_api_key or self.gemini_api_key)

    async def generate_response(
        self,
        user_message: str,
        rag_context: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ) -> Optional[str]:
        """Generate response via Groq or Gemini if keys are present; else None."""
        sys_prompt = system_prompt or CONVERSATIONAL_SYSTEM_PROMPT
        if rag_context:
            sys_prompt += f"\n\nContexto técnico verificado (RAG):\n{rag_context}"

        # 1. Try Groq (llama-3.1-8b-instant) if key is present
        if self.groq_api_key:
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.groq_api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": "llama-3.1-8b-instant",
                            "messages": [
                                {"role": "system", "content": sys_prompt},
                                {"role": "user", "content": user_message},
                            ],
                            "temperature": 0.3,
                            "max_tokens": 300,
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["choices"][0]["message"]["content"].strip()
                        # Enforce AI vs IA acronym rule
                        text = re.sub(r"\bIA\b", "AI", text)
                        return text
                    logger.warning("Groq API returned HTTP %s: %s", resp.status_code, resp.text)
            except Exception as e:
                logger.warning("Error calling Groq API: %s", e)

        # 2. Try Gemini (gemini-1.5-flash) if key is present
        if self.gemini_api_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
                combined_prompt = f"{sys_prompt}\n\nMensaje del usuario:\n{user_message}"
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    resp = await client.post(
                        url,
                        headers={"Content-Type": "application/json"},
                        json={
                            "contents": [
                                {"parts": [{"text": combined_prompt}]}
                            ],
                            "generationConfig": {
                                "temperature": 0.3,
                                "maxOutputTokens": 300,
                            },
                        },
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                        text = re.sub(r"\bIA\b", "AI", text)
                        return text
                    logger.warning("Gemini API returned HTTP %s: %s", resp.status_code, resp.text)
            except Exception as e:
                logger.warning("Error calling Gemini API: %s", e)

        return None
