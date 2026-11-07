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

            context_chunks = context_chunks or []

            # Deterministic grounding score from token overlap between the
            # query and the retrieved chunks (never hardcoded; no LLM call).
            grounding_score = self._compute_grounding_score(question, context_chunks)
            is_fully_grounded = grounding_score >= 0.85

            # Only answer from the corpus when the chunks actually ground the
            # query; otherwise report that no sources were found.
            if is_fully_grounded and context_chunks:
                answer = self._generate_answer_from_chunks(question, context_chunks)
                cited_sources = list({
                    chunk.get("source", "unknown") for chunk in context_chunks
                })
            else:
                answer = "No se encontraron fuentes relevantes para esta pregunta."
                cited_sources = []

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

    @staticmethod
    def _tokenize(text: str) -> set:
        """Lowercase whitespace tokens with surrounding punctuation stripped."""
        return {
            token.strip(".,;:!?()[]\"'")
            for token in text.lower().split()
            if token.strip(".,;:!?()[]\"'")
        }

    def _compute_grounding_score(self, question: str, chunks: List[dict]) -> float:
        """Deterministic grounding score in [0, 1] from token overlap.

        Ratio of query terms found in the best-matching chunk, computed purely
        from chunk text vs query terms. No hardcoded value, no LLM call.
        """
        query_terms = self._tokenize(question)
        if not query_terms or not chunks:
            return 0.0
        best = 0.0
        for chunk in chunks:
            content_terms = self._tokenize(chunk.get("content", ""))
            if not content_terms:
                continue
            overlap = len(query_terms & content_terms)
            best = max(best, overlap / len(query_terms))
        return round(min(best, 1.0), 4)
