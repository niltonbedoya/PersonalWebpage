"""TDD: Cerebrito RAG agent — grounding score from fixture chunks (F2, T5, S2/S9).

Grounding score is computed from token overlap between the query and the
retrieved chunks, never hardcoded. No network, no LLM calls — deterministic
fixture-based test.

Cerebrito model assignment (documented via select_model_for_agent("Cerebrito")):
provider google_ai_studio, primary gemini-1.5-flash, fallback gemini-2.0-flash.
"""

import asyncio

from backend.app.agents import Cerebrito
from backend.app.core.llm_routing import select_model_for_agent
from backend.app.models import RAGResponsePayload


def _run(agent: Cerebrito, question: str, chunks):
    return asyncio.run(agent.query(question, context_chunks=chunks))


RELATED_CHUNKS = [
    {
        "content": "Soldadura por onda THT: el horno de reflow funde la pasta de soldadura sobre placas mediante zonas de temperatura.",
        "source": "docs/smt-tht.md",
    },
    {
        "content": "Inspeccion AOI de juntas de soldadura THT y componentes de montaje superficial SMD.",
        "source": "docs/aoi-inspeccion.md",
    },
]

UNRELATED_CHUNKS = [
    {
        "content": "Desarrollo web con Django y Python: APIs REST, modelos de base de datos y plantillas.",
        "source": "docs/django.md",
    },
    {
        "content": "Despliegue de aplicaciones FastAPI en contenedores Docker con nginx.",
        "source": "docs/fastapi.md",
    },
]


# S2 — RAGResponsePayload contract conformance -----------------------------

def test_rag_response_payload_conformance():
    agent = Cerebrito()
    payload = _run(agent, "soldadura por onda THT reflow", RELATED_CHUNKS)
    assert isinstance(payload, RAGResponsePayload)
    assert 0.0 <= payload.grounding_score <= 1.0
    assert isinstance(payload.cited_sources, list)
    assert isinstance(payload.is_fully_grounded, bool)


# S2 — grounding score computed from chunks, never hardcoded 0.9 ----------

def test_grounding_score_from_related_chunks_is_high():
    agent = Cerebrito()
    payload = _run(
        agent, "soldadura por onda THT reflow horno temperatura pasta", RELATED_CHUNKS
    )
    assert payload.grounding_score >= 0.85
    assert payload.is_fully_grounded is True


def test_grounding_score_from_unrelated_chunks_is_low():
    # A hardcoded grounding_score (e.g. 0.9) would wrongly satisfy >= 0.85
    # here; the score must drop below 0.85 when chunks share no query terms.
    agent = Cerebrito()
    payload = _run(agent, "soldadura por onda THT reflow horno", UNRELATED_CHUNKS)
    assert payload.grounding_score < 0.85
    assert payload.is_fully_grounded is False


# S2 — no answer outside the corpus ----------------------------------------

def test_no_answer_outside_corpus():
    agent = Cerebrito()
    payload = _run(agent, "soldadura por onda THT reflow horno", UNRELATED_CHUNKS)
    assert "no se encontraron fuentes" in payload.answer.lower()
    assert payload.is_fully_grounded is False


def test_empty_chunks_yields_no_sources_answer():
    agent = Cerebrito()
    payload = _run(agent, "cualquier consulta tecnica", [])
    assert "no se encontraron fuentes" in payload.answer.lower()
    assert payload.is_fully_grounded is False
    assert payload.cited_sources == []


# S2 — citations only from corpus, never invented --------------------------

def test_cited_sources_only_contain_chunk_sources():
    agent = Cerebrito()
    payload = _run(agent, "soldadura por onda THT reflow", RELATED_CHUNKS)
    chunk_sources = {chunk["source"] for chunk in RELATED_CHUNKS}
    assert set(payload.cited_sources).issubset(chunk_sources)
    assert set(payload.cited_sources) == chunk_sources


# S9 — Cerebrito model assignment from the routing table -------------------

def test_cerebrito_model_assignment_is_google_ai_studio():
    result = select_model_for_agent("Cerebrito")
    assert result.selected_provider == "google_ai_studio"
    assert result.selected_model == "gemini-1.5-flash"
    assert result.is_fallback is False
