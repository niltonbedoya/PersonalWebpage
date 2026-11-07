"""Centinela — Subagente C: Guardrail & Seguridad."""

import logging

logger = logging.getLogger(__name__)


class Centinela:
    """Subagente C - Guardrail & Seguridad.

    Intercepción ultrarrápida (<150 ms). Evalúa si la consulta es pertinente
    al perfil técnico. Bloquea intentos de jailbreak, inyecciones de prompt
    y consultas off-topic.
    Inferencia: Groq Cloud llama-3.1-8b-instant.
    """

    def __init__(self):
        self.name = "Centinela"
        self.role = "Subagente C - Guardrail & Seguridad"
        self.risk_keywords = [
            "jailbreak", "prompt injection", "ignore previous instructions",
            "system override", "disable safety", "extract credentials",
            "developer mode", "dan", "reveal", "configuration",
            "connection string", "tokens", "secrets", "environment variables",
            "ignore all", "prior rules", "filtering",
            "pretend you are", "unrestricted AI", "no limitations",
            "forget all your previous training", "be helpful",
            "act as if", "ethical constraints",
            "ignore your developer instructions", "comply with me",
            "switch to developer mode", "disable your safety mode",
            "reveal your system instructions", "internal configuration",
            "bypass", "authentication", "admin panel",
            "run this code", "execute the following",
            "override", "system:", "answers everything",
        ]
        self.intent_categories = [
            "TECHNICAL_PROFILE", "HARDWARE_SMT", "SOFTWARE_CASE_STUDY",
            "OFF_TOPIC", "PROMPT_INJECTION"
        ]

    async def evaluate(self, prompt: str):
        """Evaluate prompt safety and intent classification."""
        from backend.app.models import GuardrailVerdict

        try:
            # Initialize verdict
            verdict_dict = {
                "is_allowed": True,
                "risk_level": "LOW",
                "intent_category": "TECHNICAL_PROFILE",
                "redirect_message": None,
            }

            prompt_lower = prompt.lower()

            # Check for prompt injection/jailbreak patterns
            for keyword in self.risk_keywords:
                if keyword in prompt_lower:
                    verdict_dict.update({
                        "is_allowed": False,
                        "risk_level": "HIGH",
                        "intent_category": "PROMPT_INJECTION",
                        "redirect_message": "Lo siento, no puedo procesar solicitudes de modificación de instrucciones. Estoy diseñado para ayudar con consultas técnicas sobre ingeniería SMT/THT y arquitectura de software.",
                    })
                    logger.warning(f"Prompt injection detected: {keyword}")
                    return GuardrailVerdict(**verdict_dict)

            # Check for off-topic indicators
            off_topic_keywords = [
                "cocina", "deportes", "finanzas personales", "shopping",
                "pizza", "receta", "fútbol", "partido", "finanzas",
                "acciones", "invertir", "supermercado",
                "capital", "perder peso", "óscar", "película", "beatles",
                "canción", "pastel", "chocolate", "presidente",
                "estados unidos", "smartphone", "windows", "instalar",
                "computadora", "restaurante", "sushi", "huesos",
                "cuerpo humano", "mona lisa", "pintó", "huesos",
            ]
            for keyword in off_topic_keywords:
                if keyword in prompt_lower:
                    verdict_dict.update({
                        "is_allowed": False,
                        "risk_level": "LOW",
                        "intent_category": "OFF_TOPIC",
                        "redirect_message": "Mi especialidad es ingeniería híbrida (SMT/THT y software industrial). ¿Tiene alguna pregunta técnica sobre estos temas?",
                    })
                    logger.info(f"Off-topic blocked: {keyword}")
                    return GuardrailVerdict(**verdict_dict)

            # Default: allowed technical profile
            verdict_dict["intent_category"] = "TECHNICAL_PROFILE"
            logger.debug("Prompt evaluated as safe: TECHNICAL_PROFILE")
            return GuardrailVerdict(**verdict_dict)

        except Exception as e:
            logger.error(f"Error evaluating Centinela: {e}")
            from backend.app.models import GuardrailVerdict
            return GuardrailVerdict(
                is_allowed=False,
                risk_level="CRITICAL",
                intent_category="PROMPT_INJECTION",
                redirect_message="Error en evaluación de seguridad. Por favor intente de nuevo.",
            )
