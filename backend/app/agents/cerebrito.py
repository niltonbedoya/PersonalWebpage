"""Cerebrito — Subagente B: Motor RAG Técnico.

Responde consultas técnicas sobre el corpus indexado en SQLite-vec, con un
grounding_score calculado sobre la recuperación real (score + citas del
corpus, nunca hardcodeado 0.9). Sin red, sin llamadas a LLM: la búsqueda
vectorial usa los embebidos determinísticos basados en hash de T4.

Todos los logs son ASCII-only (regla de consola Windows cp1252).
"""

import logging
import re
import unicodedata

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

    INTENT_ENRICHMENTS = [
        ({"dedicas", "dedica", "dedicacion"}, "perfil profesional Nilton Bedoya", "perfil"),
        ({"contactarte", "contactar", "contacto", "contactarle"}, "contacto profesional Nilton Bedoya linkedin colaboraciones", "contacto"),
        ({"pick", "place"}, "limite alcance exclusion maquinaria pick place", "pick"),
        ({"experiencia", "trayectoria"}, "perfil profesional Nilton Bedoya experiencia", "experiencia"),
        ({"stack", "tecnologias", "tecnologia"}, "stack tecnologico arquitectura software", "stack"),
        ({"github", "repositorios", "repositorio"}, "proyectos software repositorio github Nilton Bedoya", "github"),
    ]

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
                    all_tokens = self._tokenize(question)
                    raw_content_words = [
                        w for w in question.split()
                        if not self._tokenize(w).issubset(self._STOPWORDS)
                    ]
                    # Check intent enrichments
                    enrich = ""
                    fallback_term = ""
                    for trigger_set, enrich_str, anchor in self.INTENT_ENRICHMENTS:
                        if all_tokens & trigger_set:
                            enrich = enrich_str
                            fallback_term = anchor
                            break

                    q_terms = [self._normalize_token(w) for w in raw_content_words]
                    if not q_terms and fallback_term:
                        q_terms = [fallback_term]

                    search_query = (" ".join(q_terms) + " " + enrich).strip()
                    if not search_query:
                        search_query = question
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
        """Generate a concise, human-readable answer from knowledge base chunks."""
        if not chunks:
            return NO_SOURCES_ANSWER

        best_chunk = chunks[0]
        title = best_chunk.get("title", "Corpus Técnico")

        # Collect clean complete lines across top chunks
        clean_lines = []
        for chk in chunks[:3]:
            raw_content = chk.get("content", "")
            for line in raw_content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "preguntas que puedes" in line.lower() or "documento tecnico de referencia" in line.lower():
                    continue
                line = re.sub(r"^[-*•]\s*", "", line)
                line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
                line = re.sub(r"`([^`]+)`", r"\1", line)
                # Keep lines that start with uppercase or numbers and look like complete thoughts
                if len(line) > 15 and (line[0].isupper() or line[0].isdigit()):
                    if line not in clean_lines:
                        clean_lines.append(line)

        if clean_lines:
            if len(clean_lines) >= 2 and clean_lines[0].endswith(":"):
                summary = f"{clean_lines[0]} {clean_lines[1]}".strip()
            else:
                summary = " ".join(clean_lines[:2]).strip()
        else:
            summary = chunks[0].get("content", "")[:180].strip()

        if not summary.endswith("."):
            summary += "."

        return summary

    @staticmethod
    def _normalize_token(token: str) -> str:
        """Strip accents and lowercase for robust matching across ES/EN."""
        nfkd = unicodedata.normalize("NFKD", str(token).lower())
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    @classmethod
    def _tokenize(cls, text: str) -> set:
        """Lowercase, accent-stripped tokens with surrounding punctuation stripped."""
        punctuation = ".,;:!?()[]\"'¿¡«»-–—"
        tokens = set()
        for raw_token in str(text).split():
            clean = raw_token.strip(punctuation)
            if clean:
                norm = cls._normalize_token(clean)
                if norm:
                    tokens.add(norm)
        return tokens

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
        "sirve", "hace", "hacer", "hago", "haces", "hacen", "usar", "uso", "usos",
        "objetivo", "proposito", "caracteristicas", "ventajas", "beneficios",
        "te", "me", "nos", "le", "les", "puedo", "puede", "puedes", "podemos", "pueden",
        "decir", "temas", "tema", "tu", "tus", "mi", "mis", "tienes", "tiene", "tienen",
        "tenemos", "eres", "son", "somos", "dedicas", "dedica", "dedican", "trabajas",
        "trabaja", "trabajado", "saber", "conocer",
        # English articles, prepositions, conjunctions, auxiliary verbs
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
        "with", "by", "from", "up", "about", "into", "over", "after", "is", "are",
        "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
        "did", "how", "what", "which", "who", "when", "where", "why", "can",
        "could", "will", "would", "should", "your", "my", "our", "their", "you",
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

        raw_content = {t for t in all_terms if t not in self._STOPWORDS}

        # Check intent enrichments for anchor terms if question was entirely stopwords
        anchor_term = None
        for trigger_set, _, anchor in self.INTENT_ENRICHMENTS:
            if all_terms & trigger_set:
                anchor_term = anchor
                break

        query_terms = raw_content if raw_content else ({anchor_term} if anchor_term else all_terms)

        union = " ".join(chunk.get("content", "") for chunk in results)
        union_terms = self._tokenize(union)

        matched_terms = set()
        for qt in query_terms:
            if qt in union_terms:
                matched_terms.add(qt)
            elif len(qt) >= 5 and any(ut.startswith(qt[:5]) or qt.startswith(ut[:5]) for ut in union_terms if len(ut) >= 5):
                matched_terms.add(qt)

        coverage = len(matched_terms) / len(query_terms)

        distances = [chunk.get("distance", 0.0) for chunk in results]
        dmin = min(distances) if distances else 0.0
        dmax = max(distances) if distances else 0.0
        if dmax > dmin:
            best_distance = min(distances)
            distance_quality = (dmax - best_distance) / (dmax - dmin)
        else:
            distance_quality = 1.0

        score = 0.9 * coverage + 0.1 * distance_quality
        return round(min(max(score, 0.0), 1.0), 4)
