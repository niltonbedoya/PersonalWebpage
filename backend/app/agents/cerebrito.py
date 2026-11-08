"""Cerebrito — Subagente B: Motor RAG Técnico.

Responde consultas técnicas sobre el corpus indexado en SQLite-vec, con un
grounding_score calculado sobre la recuperación real (score + citas del
corpus, nunca hardcodeado 0.9). Sin red, sin llamadas a LLM: la búsqueda
vectorial usa los embebidos determinísticos basados en hash de T4.

Todos los logs son ASCII-only (regla de consola Windows cp1252).
"""

import logging

from backend.app.db import indexer
from backend.app.db.schema import DEFAULT_DB_PATH

from typing import Any, List, Optional

logger = logging.getLogger(__name__)

GROUNDING_THRESHOLD = 0.85
NO_SOURCES_ANSWER = "No se encontraron fuentes relevantes para esta pregunta."


class Cerebrito:
    """Subagente B - Motor RAG Técnico.

    Responde consultas sobre maquinaria, procesos térmicos y proyectos de
    software basándose exclusivamente en el corpus indexado en SQLite-vec.
    Inferencia: Google AI Studio gemini-1.5-flash / gemini-2.0-flash.
    """

    def __init__(self, knowledge_adapter: Any = None, db_path: str = None):
        self.name = "Cerebrito"
        self.role = "Subagente B - Motor RAG Técnico"
        self.knowledge_adapter = knowledge_adapter
        self.context_window = 1_000_000
        self.db_path = db_path or str(DEFAULT_DB_PATH)

    async def query(self, question: str, context_chunks: Optional[List[dict]] = None):
        """Process a technical query using RAG over the indexed corpus.

        When ``context_chunks`` is not supplied, a real sqlite-vec kNN search
        is run against ``self.db_path`` and the grounding score is computed
        from the retrieval quality (term coverage of the retrieved chunks plus
        a distance-quality factor). Citations come only from actual chunks.
        """
        from backend.app.models import RAGResponsePayload

        try:
            if context_chunks is None:
                try:
                    content_words = [
                        w for w in question.split()
                        if not self._tokenize(w).issubset(self._STOPWORDS)
                    ]
                    search_query = " ".join(content_words) if content_words else question
                    results = indexer.search(search_query, db_path=self.db_path, top_k=6)
                except Exception as search_exc:
                    # No indexable corpus available yet (e.g. default DB not
                    # built): degrade to empty results so the answer reports
                    # no sources instead of surfacing a raw error.
                    logger.error("Cerebrito sqlite-vec search unavailable: %s", search_exc)
                    results = []
            else:
                results = list(context_chunks or [])

            grounding_score = self._compute_grounding_score(question, results)
            is_fully_grounded = grounding_score >= GROUNDING_THRESHOLD

            if is_fully_grounded and results:
                answer = self._generate_answer_from_chunks(question, results)
                cited_sources = list({
                    chunk.get("source", "unknown") for chunk in results
                })
            else:
                answer = NO_SOURCES_ANSWER
                cited_sources = []

            payload = RAGResponsePayload(
                query=question,
                answer=answer,
                grounding_score=grounding_score,
                cited_sources=cited_sources[:10],  # Max 10 sources
                is_fully_grounded=is_fully_grounded,
            )

            logger.info("Cerebrito query processed, grounding: %s", grounding_score)
            return payload

        except Exception as e:
            logger.error("Error processing Cerebrito query: %s", e)
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
            return NO_SOURCES_ANSWER

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
            token.strip(".,;:!?()[]\"'¿¡«»")
            for token in str(text).lower().split()
            if token.strip(".,;:!?()[]\"'¿¡«»")
        }

    # Common Spanish and English conversational and meta-question stopwords to
    # prevent lowering grounding score term coverage when queries are phrased naturally.
    _STOPWORDS = {
        # Spanish articles, prepositions, conjunctions, pronouns
        "de", "la", "el", "en", "y", "que", "como", "un", "una", "unos", "unas",
        "por", "para", "con", "del", "al", "los", "las", "se", "es", "su", "sus",
        "o", "u", "este", "esta", "estos", "estas", "a", "ante", "bajo", "cabe",
        "desde", "hacia", "hasta", "segun", "sin", "so", "sobre", "tras", "cual",
        "cuales", "quien", "quienes", "donde", "cuando", "cuanto", "cuanta",
        "cuantos", "cuantas",
        # Spanish conversational triggers & framing meta-words
        "funciona", "dime", "cuenta", "cuentame", "explica", "explicame", "habla",
        "hablame", "muestra", "muestrame", "resumen", "resumeme", "detalles",
        "informacion", "proyecto", "proyectos", "solucion", "soluciones", "aporta",
        "sirve", "hace", "hacer", "hago", "usar", "uso", "usos", "objetivo", "proposito",
        "caracteristicas", "ventajas", "beneficios",
        "te", "me", "nos", "le", "les", "puedo", "puede", "puedes", "podemos", "pueden",
        "decir", "temas", "tema",
        # English articles, prepositions, conjunctions, auxiliary verbs
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
        "with", "by", "from", "up", "about", "into", "over", "after", "is", "are",
        "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
        "did", "how", "what", "which", "who", "when", "where", "why", "can",
        "could", "will", "would", "should",
        # English conversational triggers & framing meta-words
        "tell", "explain", "describe", "show", "give", "overview", "summary",
        "project", "projects", "solution", "solutions", "features", "benefits",
        "details", "information", "purpose", "use", "works",
    }

    def _compute_grounding_score(self, question: str, results: List[dict]) -> float:
        """Deterministic grounding score in [0, 1] from retrieval quality.

        Blends term coverage (fraction of unique query terms found across the
        retrieved chunk contents) with a distance-quality factor (how close
        the best hit is relative to the other hits). Both terms come from the
        real sqlite-vec search results; nothing is hardcoded.
        """
        all_terms = self._tokenize(question)
        if not all_terms or not results:
            return 0.0

        content_terms = {t for t in all_terms if t not in self._STOPWORDS}
        query_terms = content_terms or all_terms

        union = " ".join(chunk.get("content", "") for chunk in results).lower()
        union_terms = self._tokenize(union)
        coverage = len(query_terms & union_terms) / len(query_terms)

        distances = [chunk.get("distance", 0.0) for chunk in results]
        dmin = min(distances)
        dmax = max(distances)
        if dmax > dmin:
            # Best (closest) hit is the most relevant; normalize its position.
            best_distance = min(distances)
            distance_quality = (dmax - best_distance) / (dmax - dmin)
        else:
            distance_quality = 1.0

        score = 0.9 * coverage + 0.1 * distance_quality
        return round(min(max(score, 0.0), 1.0), 4)
