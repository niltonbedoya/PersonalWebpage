"""Cerebrito — Subagente B: Motor RAG Técnico."""

import logging

from typing import Any, List, Optional

logger = logging.getLogger(__name__)


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
