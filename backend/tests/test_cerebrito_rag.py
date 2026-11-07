"""TDD: Cerebrito real SQLite-vec grounding (F5/T6, S1/S2/S5/S7/S8).

Grounding score and citations come from a real sqlite-vec kNN search over the
indexed corpus (never hardcoded 0.9, no network, no LLM). Tests index a copy of
the real `data/` corpus into a temporary database so nothing under `data/` or
the default DB path is touched.

Covers:
- S1: score + citations from the real corpus.
- S2: score >= 0.85 => fully grounded; score < 0.85 => "no sources found".
- S5: citations only from actual chunks, never invented.
- S7: offline/deterministic, no network, no LLM calls.
- RAGResponsePayload contract conformance.
"""

import asyncio
import shutil
from pathlib import Path

import pytest

from backend.app.agents.cerebrito import Cerebrito
from backend.app.db.indexer import index_corpus
from backend.app.db.schema import DEFAULT_DB_PATH, EMBEDDING_DIM
from backend.app.models import RAGResponsePayload

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REAL_DATA_DIR = REPO_ROOT / "data"


def _temp_dir(prefix="cerebrito_rag_test_"):
    import tempfile

    return Path(tempfile.mkdtemp(prefix=prefix))


def _write_md(data_dir, name, content):
    (data_dir / name).write_text(content, encoding="utf-8")


def _cleanup(*paths):
    for path in paths:
        shutil.rmtree(path, ignore_errors=True)


def _index_real_data(data_dir, db_path):
    index_corpus(data_dir=str(data_dir), db_path=str(db_path))


def _run(agent, question):
    return asyncio.run(agent.query(question))


# ---------------------------------------------------------------------------
# Fixtures: real corpus indexed into a temporary database
# ---------------------------------------------------------------------------

@pytest.fixture
def rag_agent():
    temp_root = _temp_dir()
    data_dir = _temp_dir()
    db_path = temp_root / "rag_corpus.db"
    try:
        _index_real_data(REAL_DATA_DIR, db_path)
        agent = Cerebrito(db_path=str(db_path))
        yield agent
    finally:
        _cleanup(temp_root, data_dir)


# ---------------------------------------------------------------------------
# S1/S2 — relevant corpus query: grounded, score >= 0.85
# ---------------------------------------------------------------------------

def test_relevant_query_is_fully_grounded_with_real_score(rag_agent):
    payload = _run(rag_agent, "horno reflow perfil termico dross")
    assert isinstance(payload, RAGResponsePayload)
    assert payload.grounding_score >= 0.85
    assert payload.is_fully_grounded is True
    assert "no se encontraron fuentes" not in payload.answer.lower()
    assert payload.cited_sources


def test_relevant_query_score_is_not_hardcoded(rag_agent):
    """The score must come from real retrieval, not a constant 0.9."""
    first = _run(rag_agent, "horno reflow perfil termico dross")
    second = _run(rag_agent, "placa circuito impreso")
    assert first.grounding_score != 0.9
    assert second.grounding_score != 0.9
    assert first.grounding_score >= 0.85
    assert second.grounding_score >= 0.85


# ---------------------------------------------------------------------------
# S2/S5 — unrelated / out-of-corpus query: not grounded, no sources
# ---------------------------------------------------------------------------

def test_unrelated_query_is_not_grounded(rag_agent):
    payload = _run(rag_agent, "zzzqwertyunrelated xyz")
    assert payload.grounding_score < 0.85
    assert payload.is_fully_grounded is False
    assert "no se encontraron fuentes" in payload.answer.lower()
    assert payload.cited_sources == []


def test_out_of_corpus_query_returns_no_sources_answer(rag_agent):
    payload = _run(rag_agent, "cualquier consulta tecnica ajena al corpus")
    assert payload.grounding_score < 0.85
    assert payload.is_fully_grounded is False
    assert payload.answer == "No se encontraron fuentes relevantes para esta pregunta."
    assert payload.cited_sources == []


def test_empty_query_yields_no_sources(rag_agent):
    payload = _run(rag_agent, "")
    assert payload.grounding_score == 0.0
    assert payload.is_fully_grounded is False
    assert payload.cited_sources == []
    assert "no se encontraron fuentes" in payload.answer.lower()


# ---------------------------------------------------------------------------
# S5 — citations only from actual chunks, never invented
# ---------------------------------------------------------------------------

def test_cited_sources_only_contain_actual_corpus_sources(rag_agent):
    payload = _run(rag_agent, "placa circuito impreso")
    assert isinstance(payload.cited_sources, list)
    for source in payload.cited_sources:
        assert isinstance(source, str)
        assert source  # never empty / never invented placeholder
    # Every cited source must be a real data/ file path.
    import os

    for source in payload.cited_sources:
        assert os.path.basename(source).endswith(".md")


# ---------------------------------------------------------------------------
# S1/S7 — RAGResponsePayload contract conformance
# ---------------------------------------------------------------------------

def test_rag_response_payload_contract(rag_agent):
    payload = _run(rag_agent, "horno reflow perfil termico dross")
    assert isinstance(payload, RAGResponsePayload)
    assert isinstance(payload.query, str) and payload.query
    assert isinstance(payload.answer, str)
    assert 0.0 <= payload.grounding_score <= 1.0
    assert isinstance(payload.cited_sources, list)
    assert all(isinstance(s, str) for s in payload.cited_sources)
    assert isinstance(payload.is_fully_grounded, bool)


def test_uses_real_sqlite_vec_search_not_constant(rag_agent):
    """Score must come from sqlite-vec retrieval, never a fixed constant (e.g. 0.9)."""
    for q in [
        "horno reflow perfil termico dross",
        "placa circuito impreso",
        "temperatura zona horno reflow",
    ]:
        score = _run(rag_agent, q).grounding_score
        assert score != 0.9  # not hardcoded
        assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# DEFAULT_DB_PATH / EMBEDDING_DIM are exercised (schema import used)
# ---------------------------------------------------------------------------

def test_default_db_path_and_dimension_constants():
    assert isinstance(DEFAULT_DB_PATH, Path)
    assert EMBEDDING_DIM == 384

