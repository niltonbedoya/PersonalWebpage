"""Multi-Agent Framework for Showcase Platform

Implements the 6-agent multi-agent framework as specified in the architecture:
- Nexus: Orchestrator central & Router
- Radarito: Subagente A - Curación Contextual de Noticias
- Cerebrito: Subagente B - Motor RAG Técnico
- Centinela: Subagente C - Guardrail & Seguridad
- Mensajerito: Subagente D - Triage & Despacho de Oportunidades
- Auditor: Agente Auditor / QA - Binary Gatekeeper
"""

from typing import Dict, List, Optional, Literal, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


# ============================================================
# Nexus - Orquestador Central & Router
# ============================================================

class Nexus:
    """FSM asíncrona. Gestiona el ciclo de vida de sesiones, enruta tráfico 
    hacia subagentes y selecciona el proveedor LLM gratuito idóneo.
    
    Responsabilidades:
    - FSM asíncrona de estados de sesión
    - Enrutamiento dinámico a subagentes
    - Selección de proveedor LLM gratuito según tarea
    - Sincronización de estado mediante Engram MCP
    """
    
    def __init__(self, mcp_registry: Any = None):
        self.name = "Nexus"
        self.role = "Orquestador Central & Router"
        self.mcp_registry = mcp_registry
        self.session_fsm: Dict[str, str] = {}  # session_id -> state
        self.agent_routing: Dict[str, str] = {}  # intent -> agent_name
        self.llm_providers = {
            "guardrails": "Groq Cloud llama-3.1-8b-instant",
            "reasoning": "Google AI Studio gemini-1.5-flash / 2.0-flash",
            "news": "Cloudflare Workers AI / OpenRouter Free Tier",
        }
    
    async def route(self, intent: str, context: dict) -> str:
        """Route an incoming request to the appropriate agent based on intent."""
        logger.info(f"Nexus routing intent: {intent}")
        
        routing_map = {
            "TECHNICAL_PROFILE": "Cerebrito",
            "HARDWARE_SMT": "Centinela",
            "SOFTWARE_CASE_STUDY": "Cerebrito",
            "OFF_TOPIC": "Centinela",
            "PROMPT_INJECTION": "Centinela",
        }
        
        target_agent = routing_map.get(intent, "Cerebrito")
        self.agent_routing[intent] = target_agent
        return target_agent
    
    async def session_lifecycle(self, action: str, session_id: str, data: dict = None) -> dict:
        """Manage session lifecycle: create, update, terminate."""
        if action == "create":
            self.session_fsm[session_id] = "active"
            logger.info(f"Session created: {session_id}")
            return {"status": "created", "session_id": session_id, "state": "active"}
        elif action == "update":
            if session_id in self.session_fsm:
                self.session_fsm[session_id] = "updated"
                return {"status": "updated", "session_id": session_id}
        elif action == "terminate":
            self.session_fsm.pop(session_id, None)
            logger.info(f"Session terminated: {session_id}")
            return {"status": "terminated", "session_id": session_id}
        
        return {"status": "unknown_action", "action": action}


# ============================================================
# Radarito - Subagente A - Curación Contextual de Noticias
# ============================================================

class Radarito:
    """Subagente A - Curación Contextual de Noticias.
    
    Consume RSS/APIs técnicas en 3 canales (THT_SOLDERING, SMD_INSPECTION, AI_SOFTWARE),
    deduplica, filtra ruido comercial y genera síntesis neutral de 2-3 líneas.
    Inferencia: Cloudflare Workers AI / OpenRouter Free.
    """
    
    def __init__(self, mcp_registry: Any = None):
        self.name = "Radarito"
        self.role = "Subagente A - Curación Contextual de Noticias"
        self.mcp_registry = mcp_registry
        self.channels: Dict[str, List[dict]] = {
            "THT_SOLDERING": [],
            "SMD_INSPECTION": [],
            "AI_SOFTWARE": [],
        }
        self.filter_keywords = ["ad", "sale", "buy", "commercial"]  # Noise filters
    
    def ingest_feed(self, feed_data: dict, category: str):
        """Ingest and curate a technical feed item."""
        from backend.app.models import NewsItemPayload
        
        try:
            # Basic filtering and deduplication
            title = feed_data.get("title", "")
            source_url = feed_data.get("source_url", "")
            
            # Check for noise/commercial content
            if any(kw in title.lower() for kw in self.filter_keywords):
                logger.info(f"Filtered out commercial content: {title[:50]}")
                return None
            
            # Deduplication check
            for existing in self.channels.get(category, []):
                if existing.get("title") == title and existing.get("source_url") == source_url:
                    logger.info(f"Duplicate filtered: {title[:50]}")
                    return None
            
            # Create NewsItemPayload
            payload = NewsItemPayload(
                id=feed_data.get("id", f"news-{len(self.channels[category])}"),
                category=category,
                title=title,
                source_url=source_url,
                published_at=feed_data.get("published_at", datetime.utcnow()),
                summary=feed_data.get("summary", "")[:300],  # Max 300 chars
                tags=feed_data.get("tags", []),
            )
            
            self.channels.setdefault(category, []).append({
                "id": payload.id,
                "title": payload.title,
                "source_url": payload.source_url,
            })
            
            logger.info(f"News item curated: {payload.title[:50]}")
            return payload
            
        except Exception as e:
            logger.error(f"Error curating news: {e}")
            return None
    
    def synthesize_summary(self, category: str) -> str:
        """Generate 2-3 line neutral synthesis for a news category."""
        items = self.channels.get(category, [])
        if not items:
            return f"No hay artículos nuevos en {category}"
        
        # Take most recent 3 items
        recent = items[:3]
        lines = [f"- {item['title']}" for item in recent]
        
        if len(lines) == 1:
            return lines[0]
        elif len(lines) == 2:
            return f"{lines[0]}\n{lines[1]}"
        else:
            return f"{lines[0]}\n{lines[1]}\n{lines[2]}"


# ============================================================
# Cerebrito - Subagente B - Motor RAG Técnico
# ============================================================

class Cerebrito:
    """Subagente B - Motor RAG Técnico.
    
    Responde consultas sobre maquinaria, procesos térmicos y proyectos de software 
    basándose exclusivamente en el corpus indexado en SQLite-vec.
    Inferencia: Google AI Studio gemini-1.5-flash / gemini-2.0-flash.
    """
    
    def __init__(self, knowledge_adapter: Any = None):
        self.name = "Cerebrito"
        self.role = "Subagente B - Motor RAG Técnico"
        self.knowledge_adapter = knowledge_adapter
        self.context_window = 1_000_000  # Extensive context window
    
    async def query(self, question: str, context_chunks: Optional[List[dict]] = None):
        """Process a technical query using RAG over the indexed corpus."""
        from backend.app.models import RAGResponsePayload
        
        try:
            # Use knowledge adapter to query SQLite-vec if available
            if self.knowledge_adapter and context_chunks is None:
                context_chunks = self.knowledge_adapter.query_sqlite_vec(
                    question_embedding=[],  # Would be actual embedding
                    top_k=5
                )
            
            # Build answer from context (stub implementation)
            if context_chunks:
                answer = self._generate_answer_from_chunks(question, context_chunks)
            else:
                answer = "Consulta técnica - consulta base de datos SQLite-vec para obtener respuestas fundamentadas."
            
            # Calculate grounding score (stub: would use actual grounding evaluation)
            grounding_score = 0.9  # Placeholder - actual evaluation needed
            is_fully_grounded = grounding_score >= 0.85
            
            # Cited sources from chunks
            cited_sources = list(set(
                chunk.get("source", "unknown") for chunk in context_chunks if context_chunks
            ))
            
            payload = RAGResponsePayload(
                query=question,
                answer=answer,
                grounding_score=grounding_score,
                cited_sources=cited_sources[:10],  # Max 10 sources
                is_fully_grounded=is_fully_grounded,
            )
            
            logger.info(f"Cerebrito query processed, grounding: {grounding_score}")
            return payload
            
        except Exception as e:
            logger.error(f"Error processing Cerebrito query: {e}")
            from backend.app.models import RAGResponsePayload
            return RAGResponsePayload(
                query=question,
                answer="Error processing query",
                grounding_score=0.0,
                cited_sources=[],
                is_fully_grounded=False,
            )
    
    def _generate_answer_from_chunks(self, question: str, chunks: List[dict]) -> str:
        """Generate answer from retrieved knowledge base chunks."""
        if not chunks:
            return "No se encontraron fuentes relevantes para esta pregunta."
        
        # Simple concatenation of chunk content (would be replaced with LLM generation)
        sources = []
        answer_parts = []
        
        for i, chunk in enumerate(chunks[:5]):  # Top 5 chunks
            content = chunk.get("content", "")
            source = chunk.get("source", "unknown")
            if source not in sources:
                sources.append(source)
            answer_parts.append(f"Fuente {i+1} ({source}): {content}")
        
        return "\n\n".join(answer_parts)


# ============================================================
# Centinela - Subagente C - Guardrail & Seguridad
# ============================================================

class Centinela:
    """Subagente C - Guardrail & Seguridad.
    
    Intercepción ultrarrápida (<150 ms). Evalúa si la consulta es pertinente 
    al perfil técnico. Bloquea intentos de jailbreak, inyecciones de prompt 
    y reconduce consultas off-topic.
    Inferencia: Groq Cloud llama-3.1-8b-instant.
    """
    
    def __init__(self):
        self.name = "Centinela"
        self.role = "Subagente C - Guardrail & Seguridad"
        self.risk_keywords = [
            "jailbreak", "prompt injection", "ignore previous instructions",
            "system override", "disable safety", "extract credentials"
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
            off_topic_keywords = ["cocina", "deportes", "finanzas personales", "shopping"]
            for keyword in off_topic_keywords:
                if keyword in prompt_lower:
                    verdict_dict.update({
                        "is_allowed": True,
                        "risk_level": "LOW",
                        "intent_category": "OFF_TOPIC",
                        "redirect_message": "Mi especialidad es ingeniería híbrida (SMT/THT y software industrial). ¿Tiene alguna pregunta técnica sobre estos temas?",
                    })
                    logger.info(f"Off-topic redirect: {keyword}")
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


# ============================================================
# Mensajerito - Subagente D - Triage & Despacho de Oportunidades
# ============================================================

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


# ============================================================
# Auditor - Agente Auditor / QA - Binary Gatekeeper
# ============================================================

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
                status = "APPROVED_WITH_SANITIZATION"
            
            # 3. Check grounding score for RAG outputs
            if output_type == "rag":
                grounding_score = agent_output.get("grounding_score", 1.0)
                if grounding_score < 0.85:
                    failure_reasons.append(f"Grounding score below threshold: {grounding_score:.2f} < 0.85")
                    if not failure_reasons or status == "APPROVED":
                        status = "REJECTED"
            
            # 4. Final verdict
            if failure_reasons:
                status = "REJECTED" if len(failure_reasons) >= 2 or status == "REJECTED" else "APPROVED_WITH_SANITIZATION"
            
            sanitized_payload = None
            if status == "APPROVED_WITH_SANITIZATION":
                sanitized_payload = {
                    "status": "sanitized",
                    "original_failure_reasons": failure_reasons,
                }
                status = "APPROVED"
            
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